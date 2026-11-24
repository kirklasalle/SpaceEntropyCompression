"""Persist model-only option-3 gate checks; this entry point cannot run a fit."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import scipy
from scipy.integrate import quad

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import candidate_a_option3_reconstruction as reconstruction
from tools import evaluate_candidate_a_all_options as reference
from tools.candidate_a_option3_gpu import (
    DeviceQuadrature,
    DeviceSegmentedQuadrature,
    device_info,
    require_gpu,
)
from tools.candidate_a_option3_quadrature import axisymmetric_segmented_v1

DEFAULT_OUTPUT = ROOT / "results" / "candidate_a_option3_validation_2026-11-04.json"
AMENDMENT_RELATIVE_PATH = (
    "knowledgebase/candidate_a_option3_reconstruction_protocol_v1_amendment_1_"
    "segmented_quadrature.json"
)
AMENDMENT_SHA256 = "d71702204520526730b78f2df0298db272cd1b210572f83e5a6d02aac2898c3c"
SOURCES = (
    "tools/candidate_a_option3_reconstruction.py",
    "tools/candidate_a_option3_gpu.py",
    "tools/candidate_a_option3_quadrature.py",
    "tools/validate_candidate_a_option3.py",
    "tools/evaluate_candidate_a_all_options.py",
)


def relative_error(actual: np.ndarray, expected: np.ndarray) -> float:
    if actual.shape != expected.shape or not len(actual):
        raise ValueError("Comparison requires matching nonempty arrays")
    if not np.isfinite(actual).all() or not np.isfinite(expected).all():
        raise ArithmeticError("Non-finite numerical comparison")
    return float(np.max(np.abs(actual - expected) / np.maximum(np.abs(expected), 0.01)))


def spherical_density_projection(radius: float, density_radii: np.ndarray,
                                 density: np.ndarray) -> float:
    if (radius < 0 or density_radii.ndim != 1
            or density.shape != density_radii.shape
            or not len(density_radii)
            or not np.isfinite(density_radii).all()
            or not np.isfinite(density).all()
            or np.any(density_radii < 0)
            or np.any(np.diff(density_radii) <= 0)):
        raise ValueError("Spherical projection inputs must be finite and strictly ordered")
    if radius >= density_radii[-1]:
        return 0.0
    if radius == 0:
        widths = np.diff(density_radii)
        return float(np.sum(widths * (density[:-1] + density[1:]), dtype=np.float64))

    edges = np.concatenate(([radius], density_radii[density_radii > radius]))
    values = np.interp(edges, density_radii, density)
    lower = edges[:-1]
    slope = np.diff(values) / np.diff(edges)
    intercept = values[:-1] - slope * lower

    def radial_root(value: np.ndarray) -> np.ndarray:
        return np.sqrt(np.maximum(value**2 - radius**2, 0.0))

    def second_moment(value: np.ndarray) -> np.ndarray:
        root = radial_root(value)
        return 0.5 * (
            value * root + radius**2 * np.arccosh(value / radius)
        )

    line_integrals = (
        slope * np.diff(second_moment(edges))
        + intercept * np.diff(radial_root(edges))
    )
    return float(2.0 * np.sum(line_integrals, dtype=np.float64))


def projection_error(source: reconstruction.Source) -> float:
    worst = 0.0
    for radius in source.radii_pc:
        expected = source.surface(radius)
        components: tuple[int, ...] = (0, 1, 2)
        if source.bulge_density_radii_pc is not None:
            if source.bulge_density is None or source.bulge_surface_radii_pc is None \
                    or source.bulge_surface_sigma is None:
                raise ValueError("Incomplete spherical bulge profile")
            bulge_surface = float(reconstruction.radial_values(
                radius, source.bulge_surface_radii_pc, source.bulge_surface_sigma,
                float(source.bulge_surface_radii_pc[-1]), linear=True,
            ))
            disk_surface = float(expected[0]) - bulge_surface
            projected_bulge = spherical_density_projection(
                float(radius), source.bulge_density_radii_pc, source.bulge_density)
            projected_stars = disk_surface + projected_bulge
            target_stars = float(expected[0])
            if target_stars == 0:
                if projected_stars != 0:
                    raise ArithmeticError("Nonzero projected stellar density for zero envelope")
            else:
                worst = max(worst, abs(projected_stars / target_stars - 1))
            components = (1, 2)
        for component in components:
            scale = source.vertical_scale(component, float(radius))
            actual, error = quad(
                lambda u, r=radius, s=scale, c=component: float(
                    source.components(r, u * s)[c]) * s,
                -np.inf, np.inf, epsabs=1e-7, epsrel=1e-7, limit=200,
            )
            target = float(expected[component])
            if target == 0:
                if actual != 0:
                    raise ArithmeticError("Nonzero projected density for a zero envelope")
                continue
            worst = max(worst, abs(actual / target - 1), error / target)
    return worst


def cpu_v2(source: reconstruction.Source, radii: np.ndarray,
           alpha: float, rho0: float, order: int,
           method: str = "legacy") -> np.ndarray:
    density = lambda r, z: reconstruction.mapped_density(source.density(r, z), alpha, rho0)
    if method == "segmented":
        breakpoints = np.r_[0.0, source.radii_pc]
        if not source.outer_exponential_tails:
            breakpoints = np.r_[breakpoints, source.cutoff_pc]
        return axisymmetric_segmented_v1(
            density, radii,
            source_breakpoints=np.unique(breakpoints),
            order=order, r_scale=source.scale_pc, z_scale=300.0,
            gravitational_constant=reconstruction.G,
            outer_tail_scale=source.scale_pc if source.outer_exponential_tails else None,
        )
    if method != "legacy":
        raise ValueError(f"Unknown quadrature method: {method}")
    return reference.axisymmetric_v2(
        density,
        radii, order=order, r_scale=source.scale_pc, z_scale=300.0,
        gravitational_constant=reconstruction.G,
    )


def model_radii(columns: np.ndarray, source: reconstruction.Source) -> np.ndarray:
    radii = columns[:, 0] * 1000 * source.field_radius_scale
    return radii[(radii >= source.radii_pc[0]) & (radii <= source.radii_pc[-1])]


def v5_summary(actual_v2: np.ndarray, reference_v2: np.ndarray) -> dict[str, float]:
    actual_vc = np.sqrt(np.maximum(actual_v2, 0.01))
    reference_vc = np.sqrt(np.maximum(reference_v2, 0.01))
    difference = actual_vc - reference_vc
    return {
        "max_absolute_delta_vc_kms": float(np.max(np.abs(difference))),
        "p95_absolute_delta_vc_kms": float(np.percentile(np.abs(difference), 95)),
        "max_relative_delta_vc": relative_error(actual_vc, reference_vc),
        "max_absolute_delta_v2_kms2": float(np.max(np.abs(actual_v2 - reference_v2))),
    }


def run_v4(primary: list[str], sources: dict[tuple[str, str, str], reconstruction.Source],
           root: Path, method: str) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for name in primary:
        columns = reconstruction.load_model_columns(root, name)
        for envelope in ("low", "high"):
            source = sources.get(("primary", name, envelope))
            if source is None:
                failures.append({"galaxy": name, "envelope": envelope,
                                 "reason": "primary source unavailable"})
                continue
            radii = model_radii(columns, source)
            selected = columns[
                (columns[:, 0] * 1000 * source.field_radius_scale >= source.radii_pc[0])
                & (columns[:, 0] * 1000 * source.field_radius_scale <= source.radii_pc[-1])
            ]
            if not len(radii) or len(selected) != len(radii):
                failures.append({"galaxy": name, "envelope": envelope,
                                 "reason": "no matching model-component radii"})
                continue
            gas, disk, bulge = selected[:, 1], selected[:, 2], selected[:, 3]
            component_v2 = np.sign(gas) * gas**2 + disk**2 + bulge**2
            try:
                reconstructed_v2 = cpu_v2(
                    source, radii, 1.0, 1.0, 64, method)
            except (ValueError, ArithmeticError, MemoryError) as exc:
                failures.append({"galaxy": name, "envelope": envelope,
                                 "reason": f"{type(exc).__name__}: {exc}"})
                continue
            differences = reconstructed_v2 - component_v2
            cases.append({
                "galaxy": name, "envelope": envelope, "radius_count": len(radii),
                "max_absolute_delta_v2_kms2": float(np.max(np.abs(differences))),
                "median_absolute_delta_v2_kms2": float(np.median(np.abs(differences))),
                "max_relative_delta_v2": float(np.max(
                    np.abs(differences) / np.maximum(np.abs(component_v2), 0.01))),
                "points": [
                    {"radius_pc": float(radius),
                     "reconstructed_vbar2_kms2": float(actual),
                     "sparc_components_v2_kms2": float(expected),
                     "delta_v2_kms2": float(actual - expected)}
                    for radius, actual, expected in zip(
                        radii, reconstructed_v2, component_v2, strict=True)
                ],
            })
    return {
        "status": "reported_model_only" if not failures else "incomplete",
        "evidence_class": "Newtonian_descriptive_model_component_comparison_not_a_fit",
        "method": "alpha=1, segmented order-64 solver; Vobs and errV are not parsed",
        "comparison": "signed Vgas^2 + Vdisk^2 + Vbul^2 versus reconstructed Vbar^2",
        "cases": cases,
        "failures": failures,
    }


def run_v5(
    variants: tuple[reconstruction.SensitivityVariant, ...],
    primary: list[str],
    sources: dict[tuple[str, str, str], reconstruction.Source],
    baseline_v2: dict[tuple[str, str, float, float], np.ndarray],
    root: Path,
    method: str,
) -> dict[str, Any]:
    grid = [(alpha, log_rho0) for alpha in (0.5, 1.0, 2.0)
            for log_rho0 in (-4.0, -1.0, 2.0)]
    variant_reports = []
    for variant in variants:
        rows: list[dict[str, Any]] = []
        failures: list[dict[str, Any]] = []
        for name in primary:
            columns = reconstruction.load_model_columns(root, name)
            for envelope in ("low", "high"):
                source = sources.get((variant.name, name, envelope))
                if source is None:
                    failures.append({
                        "galaxy": name, "envelope": envelope,
                        "reason": "source could not be constructed or passed V1",
                    })
                    continue
                radii = model_radii(columns, source)
                if not len(radii):
                    failures.append({
                        "galaxy": name, "envelope": envelope,
                        "reason": "no model-only radii inside density coverage",
                    })
                    continue
                primary_source = sources.get(("primary", name, envelope))
                if primary_source is None:
                    failures.append({
                        "galaxy": name, "envelope": envelope,
                        "reason": "primary source is unavailable",
                    })
                    continue
                primary_radii = model_radii(columns, primary_source)
                for alpha, log_rho0 in grid:
                    reference_values = baseline_v2.get(
                        (name, envelope, alpha, log_rho0))
                    if reference_values is None:
                        failures.append({
                            "galaxy": name, "envelope": envelope, "alpha": alpha,
                            "log10_rho0": log_rho0,
                            "reason": "primary V3 baseline is unavailable",
                        })
                        continue
                    try:
                        if not np.array_equal(radii, primary_radii):
                            reference_values = cpu_v2(
                                primary_source, radii, alpha, 10**log_rho0, 64, method)
                        actual = cpu_v2(
                            source, radii, alpha, 10**log_rho0, 64, method)
                        summary = v5_summary(actual, reference_values)
                    except (ValueError, ArithmeticError, MemoryError) as exc:
                        failures.append({
                            "galaxy": name, "envelope": envelope, "alpha": alpha,
                            "log10_rho0": log_rho0,
                            "reason": f"{type(exc).__name__}: {exc}",
                        })
                        continue
                    rows.append({
                        "galaxy": name, "envelope": envelope, "alpha": alpha,
                        "log10_rho0": log_rho0, "radius_count": len(radii),
                        **summary,
                    })
        if rows:
            variant_summary = {
                "max_absolute_delta_vc_kms": max(
                    row["max_absolute_delta_vc_kms"] for row in rows),
                "max_relative_delta_vc": max(row["max_relative_delta_vc"] for row in rows),
                "max_absolute_delta_v2_kms2": max(
                    row["max_absolute_delta_v2_kms2"] for row in rows),
            }
        else:
            variant_summary = {}
        variant_reports.append({
            "variant": variant.name,
            "status": "reported_model_only" if not failures else "incomplete",
            "case_count": len(rows),
            "expected_case_count": len(primary) * 2 * len(grid),
            **variant_summary,
            "cases": rows,
            "failures": failures,
        })
    return {
        "status": ("reported_model_only" if all(
            row["status"] == "reported_model_only" for row in variant_reports
        ) else "incomplete"),
        "evidence_class": "fixed_grid_model_only_sensitivity_not_inference",
        "method": ("approved segmented method, order 64, CPU; semi-infinite mapped panel "
                   "for outer exponential tails"),
        "grid": [{"alpha": alpha, "log10_rho0": log_rho0}
                 for alpha, log_rho0 in grid],
        "vc_definition": "sqrt(max(Vc^2, 0.01 km^2/s^2))",
        "inference_only_sensitivities": {
            "delta_Q_without_error_inflation": "not_applicable_to_model_only_Vc",
            "T1_prior_centers": "represented by fixed source brackets f_star=0.8 and 1.2",
        },
        "variants": variant_reports,
    }


def provenance(root: Path) -> dict[str, Any]:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True,
    ).stdout.strip()
    versions = {"python": platform.python_version(),
                "numpy": np.__version__, "scipy": scipy.__version__}
    for name in ("cupy-cuda12x", "cuda-toolkit", "nvidia-cuda-runtime-cu12",
                 "nvidia-cuda-nvrtc-cu12"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "not_installed"
    return {
        "git_head": commit,
        "source_sha256": {name: reference.sha256(root / name) for name in SOURCES},
        "runtime": versions,
        "note": "Source hashes, not HEAD alone, identify this implementation.",
    }


def load_protocol_amendment(root: Path) -> tuple[dict[str, Any], str]:
    path = root / AMENDMENT_RELATIVE_PATH
    digest = reference.sha256(path)
    if digest != AMENDMENT_SHA256:
        raise ValueError("Segmented protocol amendment hash mismatch")
    amendment = json.loads(path.read_text(encoding="utf-8"))
    if (amendment.get("protocol_id")
            != "candidate-a-option3-reconstruction-v1-amendment-1-segmented-quadrature"
            or amendment.get("status") != "approved_for_model_only_validation"
            or amendment.get("parent_protocol", {}).get("sha256")
            != reconstruction.PROTOCOL_SHA256
            or amendment.get("V3", {}).get("method_id") != "axisymmetric_segmented_v1"
            or amendment.get("V3b", {}).get("method_id") != "axisymmetric_segmented_v1"
            or amendment.get("fit_authorized") is not False
            or amendment.get("observed_velocities_parsed") is not False
            or amendment.get("observational_fit_performed") is not False):
        raise ValueError("Segmented protocol amendment contents are not authorized")
    return amendment, digest


def run(backend: str = "cpu", root: Path = ROOT,
        method: str = "legacy", amendment: bool = False) -> dict[str, Any]:
    if backend not in ("cpu", "gpu"):
        raise ValueError("Backend must be cpu or gpu")
    if method not in ("legacy", "segmented"):
        raise ValueError("Method must be legacy or segmented")
    if amendment and (backend != "gpu" or method != "segmented"):
        raise ValueError("The segmented amendment requires --backend gpu and --method segmented")
    report: dict[str, Any] = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "evidence_class": "model_only_numerical_validation_not_observational_inference",
        "protocol_sha256": reconstruction.PROTOCOL_SHA256,
        "observed_velocities_parsed": False,
        "observational_fit_performed": False,
        "outcome": "incomplete", "fit_permitted": False,
        "backend": backend, "method": method, "gates": {}, "blockers": [],
    }
    report["numerical_method"] = (
        {
            "status": "experimental_unapproved_candidate",
            "radial": ("order-n Gauss-Legendre independently on each finite source interval; "
                       "split at 0, every aligned profile ring centre, each field radius "
                       "inside the support, and the frozen outer cutoff"),
            "vertical": "frozen rational half-line map with order-n Gauss-Legendre nodes",
            "order_comparison": "n=64 versus n=128 on every radial panel and in z",
            "change_control": ("approved v1 amendment for model-only validation; no fit authorized"
                               if amendment else
                               "does not alter the frozen v1 protocol or clear its V3 gate"),
        }
        if method == "segmented" else
        {"status": "frozen_v1", "radial": "existing axisymmetric_v2 rational map"}
    )
    started = time.perf_counter()
    try:
        protocol = reconstruction.verify_inputs(root)
        report["provenance"] = provenance(root)
        report["input_pins"] = protocol["data"]
        report["parent_protocol"] = protocol["parent_protocol"]
        amendment_document = None
        if amendment:
            amendment_document, amendment_sha256 = load_protocol_amendment(root)
            report["protocol_sha256"] = amendment_sha256
            report["protocol_id"] = amendment_document["protocol_id"]
            report["protocol_amendment_path"] = AMENDMENT_RELATIVE_PATH
            report["parent_protocol_sha256"] = reconstruction.PROTOCOL_SHA256
            report["provenance"]["source_sha256"][AMENDMENT_RELATIVE_PATH] = amendment_sha256
            report["numerical_method"]["status"] = "approved_model_only_amendment"
            report["numerical_method"]["change_control"] = (
                "approved v1 amendment for model-only validation; no fit authorized"
            )
        report["numerical_method_status"] = (
            ("Approved separately versioned method for model-only validation; no fit is authorized."
             if amendment else
             "Experimental model-only candidate, not included in or authorized by the frozen v1 protocol.")
            if method == "segmented" else
            "The radial mapping in the frozen v1 protocol."
        )
        cp = None
        if backend == "gpu":
            cp = require_gpu()
            # Cap this process's CuPy pool, not the device or other users' allocations.
            cp.get_default_memory_pool().set_limit(size=1024**3)
            report["gpu"] = device_info(cp)
            report["gpu"]["pool_limit_bytes"] = 1024**3
            probe = cp.arange(10, dtype=cp.float64)
            if float(cp.sum(probe * probe).get()) != 285.0:
                raise ArithmeticError("Float64 GPU smoke test failed")
        primary = protocol["population"]["primary"]
        envelopes: tuple[reconstruction.Envelope, ...] = ("low", "high")
        names = set(primary) | set(protocol["population"]["excluded"])
        profiles = reconstruction.load_profiles(root, names)
        geometry = reconstruction.load_geometry(root, set(primary))
        report["density_audit"] = {
            "overlap_galaxies": len(profiles),
            "censored_hi_rows": sum(r.hi is None for p in profiles.values() for r in p.rings),
            "missing_h2_rows": sum(r.h2 is None for p in profiles.values() for r in p.rings),
            "missing_stellar_rows": 0,
            "stellar_rows_note": "Parser requires a measured stellar value in every row.",
        }
        report["radius_selection"] = (
            "All positive-radius SPARC rows inside aligned Leroy coverage: a superset "
            "of the primary fit selection, whose Vobs>0 cut is not evaluated here."
        )
        benchmark = reference.check_option3()
        report["analytic_benchmarks"] = benchmark
        cases: list[dict[str, Any]] = []
        projection_max = 0.0
        variants = reconstruction.sensitivity_variants()
        source_cache: dict[tuple[str, str, str], reconstruction.Source] = {}
        v1_variant_reports = []
        report["V1_sensitivity_cases"] = []
        for variant in variants:
            variant_errors = []
            variant_failures = []
            for name in primary:
                profile = profiles[name]
                for envelope in envelopes:
                    try:
                        source = reconstruction.build_source(
                            profile, geometry[name], envelope, variant=variant)
                        error = projection_error(source)
                        source_cache[(variant.name, name, envelope)] = source
                        projection_max = max(projection_max, error)
                        variant_errors.append(error)
                        report["V1_sensitivity_cases"].append({
                            "variant": variant.name, "galaxy": name,
                            "envelope": envelope, "max_relative_projection_error": error,
                            "outer_log_slopes_per_pc": list(source.outer_log_slopes),
                            "status": "passed" if error < 1e-3 else "failed",
                        })
                    except (ValueError, ArithmeticError, MemoryError) as exc:
                        failure = {
                            "variant": variant.name, "galaxy": name,
                            "envelope": envelope,
                            "reason": f"{type(exc).__name__}: {exc}",
                        }
                        variant_failures.append(failure)
                        report["V1_sensitivity_cases"].append({
                            **failure, "status": "failed",
                        })
            variant_max = max(variant_errors, default=None)
            if variant_failures or len(variant_errors) != len(primary) * len(envelopes):
                variant_status = "incomplete"
            elif variant_max is not None and variant_max >= 1e-3:
                variant_status = "failed"
            else:
                variant_status = "passed"
            v1_variant_reports.append({
                "variant": variant.name, "status": variant_status,
                "max_relative_projection_error": variant_max,
                "case_count": len(variant_errors),
                "expected_case_count": len(primary) * len(envelopes),
                "failures": variant_failures,
            })
        report["V1_variants"] = v1_variant_reports
        report["sensitivity_variant_definitions"] = [
            vars(variant) for variant in variants
        ]
        v1_status = (
            "failed" if any(row["status"] == "failed" for row in v1_variant_reports)
            else "incomplete" if any(
                row["status"] == "incomplete" for row in v1_variant_reports)
            else "passed"
        )
        v2_ok = True
        cpu_seconds, gpu_seconds = 0.0, 0.0
        report["cases"] = cases
        baseline_v2: dict[tuple[str, str, float, float], np.ndarray] = {}
        for name in primary:
            profile = profiles[name]
            columns = reconstruction.load_model_columns(root, name)
            for envelope in envelopes:
                primary_source = source_cache.get(("primary", name, envelope))
                if primary_source is None:
                    raise ValueError(f"{name}: primary source failed V1 construction")
                radii = model_radii(columns, primary_source)
                if not len(radii):
                    raise ValueError(f"{name}: no model-only radii inside density coverage")
                inclination_factor = np.cos(np.radians(geometry[name].inclination_deg)) / np.cos(
                    np.radians(profile.geometry.inclination_deg))
                measured = np.array([r.hi is not None for r in profile.rings])
                expected_hi = np.array([r.hi for r in profile.rings if r.hi is not None])
                v2_ok &= bool(np.allclose(primary_source.sigma[1, measured],
                                         expected_hi * inclination_factor, rtol=1e-14, atol=0))
                measured_h2 = np.array([r.h2 is not None for r in profile.rings])
                expected_h2 = np.array([r.h2 for r in profile.rings if r.h2 is not None])
                co_factor = 0.7 if envelope == "low" else 1.3
                v2_ok &= bool(np.allclose(primary_source.sigma[2, measured_h2],
                                         expected_h2 * inclination_factor * co_factor,
                                         rtol=1e-14, atol=0))
                for alpha in (0.5, 1.0, 2.0):
                    for log_rho0 in (-4.0, -1.0, 2.0):
                        timer = time.perf_counter()
                        coarse = cpu_v2(
                            primary_source, radii, alpha, 10**log_rho0, 64, method)
                        fine = cpu_v2(
                            primary_source, radii, alpha, 10**log_rho0, 128, method)
                        cpu_seconds += time.perf_counter() - timer
                        baseline_v2[(name, envelope, alpha, log_rho0)] = coarse
                        case: dict[str, Any] = {
                            "galaxy": name, "envelope": envelope, "alpha": alpha,
                            "log10_rho0": log_rho0, "radius_count": len(radii),
                            "v3_relative_error": relative_error(coarse, fine),
                        }
                        if cp is not None:
                            cp.cuda.Device().synchronize()
                            timer = time.perf_counter()
                            errors = []
                            device_solver = (
                                DeviceSegmentedQuadrature if method == "segmented"
                                else DeviceQuadrature
                            )
                            for order, expected in ((64, coarse), (128, fine)):
                                actual = device_solver(
                                    cp, order, primary_source.scale_pc).evaluate(
                                        primary_source, radii, alpha, 10**log_rho0)
                                errors.append(relative_error(actual, expected))
                            cp.cuda.Device().synchronize()
                            gpu_seconds += time.perf_counter() - timer
                            case["v3b_relative_error"] = max(errors)
                        cases.append(case)
        v3 = max(row["v3_relative_error"] for row in cases)
        v3_status = "passed" if v3 < 0.005 else "failed"
        if method == "segmented" and not amendment and v3_status == "passed":
            v3_status = "candidate_passed_not_authorized"
        report["gates"] = {
            "V1": {"status": v1_status, "max_relative_error": projection_max,
                   "passed": v1_status == "passed", "threshold": 1e-3,
                   "variant_count": len(v1_variant_reports),
                   "reason": ("All frozen source sensitivities were projected."
                              if v1_status == "passed" else
                              "At least one sensitivity source could not be constructed "
                              "or did not meet the projection threshold.")},
            "V2": {"status": "passed" if v2_ok else "failed",
                   "scope": "Measured HI/H2 unchanged except geometry and one CO factor; synthetic mass exceptions tested separately."},
            "V3": {"status": v3_status,
                   "max_relative_error": v3, "threshold": 0.005,
                   "cases": len(cases),
                   "interpretation": (
                       "segmented quadrature under separately approved model-only amendment"
                       if amendment else
                       "experimental segmented candidate; not an authorized amendment to frozen v1"
                       if method == "segmented" else "frozen v1 radial map")},
            "V3b": {"status": "not_run", "reason": "CPU-only execution"},
            "V4": {"status": "not_run", "reason": "Await successful prerequisite gates."},
            "V5": {"status": "not_run", "reason": "Await successful prerequisite gates."},
        }
        if cp is not None:
            v3b = max(row["v3b_relative_error"] for row in cases)
            report["gates"]["V3b"] = {
                "status": ("passed" if v3b < 1e-10 else "failed"),
                "max_relative_error": v3b, "threshold": 1e-10,
                "scope": "Both orders on every primary-source V3 case, not sensitivity variants.",
            }
            report["gpu"]["pool_peak_not_measured"] = True
            report["gpu"]["pool_reserved_bytes_at_end"] = cp.get_default_memory_pool().total_bytes()
        report["V4"] = run_v4(primary, source_cache, root, method)
        report["V5"] = run_v5(
            variants, primary, source_cache, baseline_v2, root, method)
        report["gates"]["V4"] = {"status": report["V4"]["status"]}
        report["gates"]["V5"] = {
            "status": report["V5"]["status"],
            "variant_count": len(report["V5"]["variants"]),
            "complete_variant_count": sum(
                row["status"] == "reported_model_only"
                for row in report["V5"]["variants"]),
        }
        report["timing"] = {
            "cpu_v3_seconds": cpu_seconds,
            "gpu_v3b_seconds_including_first_use_and_transfers": gpu_seconds,
            "fit_runtime_estimate": None,
            "note": "Validation execution timings, not a warmed optimizer benchmark.",
        }
        report["blockers"] = [
            f"{gate}: {report['gates'][gate]['status']}"
            for gate in ("V1", "V2", "V3", "V3b")
            if report["gates"][gate]["status"] != "passed"
        ]
        if report["V4"]["status"] == "incomplete":
            report["blockers"].append("V4: descriptive computation incomplete")
        if report["V5"]["status"] == "incomplete":
            report["blockers"].append("V5: at least one source sensitivity is incomplete")
    except (ValueError, ArithmeticError, OSError, RuntimeError, MemoryError,
            subprocess.CalledProcessError) as exc:
        report["incomplete_reason"] = f"{type(exc).__name__}: {exc}"
        report["blockers"].append(report["incomplete_reason"])
    report["elapsed_seconds"] = time.perf_counter() - started
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=("cpu", "gpu"), default="cpu")
    parser.add_argument("--method", choices=("legacy", "segmented"), default="legacy")
    parser.add_argument(
        "--amendment", action="store_true",
        help="use the hash-pinned segmented protocol amendment for model-only validation",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    if args.amendment and (args.backend != "gpu" or args.method != "segmented"):
        parser.error("--amendment requires --backend gpu and --method segmented")
    if args.output.exists():
        parser.error("Output already exists; choose a new path to preserve the earlier evidence")
    report = run(args.backend, ROOT, args.method, args.amendment)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"outcome": report["outcome"], "gates": report["gates"],
                      "blockers": report["blockers"], "output": str(args.output)}, indent=2))
    return 1 if "incomplete_reason" in report else 2


if __name__ == "__main__":
    raise SystemExit(main())
