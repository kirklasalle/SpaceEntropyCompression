"""Run Candidate A's frozen all-option gates; never fit incomplete density data."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import scipy
from numpy.polynomial.legendre import leggauss
from scipy.special import ellipe, ellipkm1

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from emergent_matter_model.fetch_real_data import (  # noqa: E402
    EXTERNAL_DIR,
    _record,
    download,
)
from tools import check_candidate_a_definitions as definitions  # noqa: E402
from tools import evaluate_candidate_a_sparc_baryonic as a2  # noqa: E402

PROTOCOL = ROOT / "knowledgebase" / "candidate_a_all_options_protocol.json"
PROTOCOL_SHA256 = "99bb1ab4be277a9683bbf9c2391196cf27f6e7b548f940abec992ed274fb3847"
OUTPUT = ROOT / "results" / "candidate_a_all_options.json"
DENSITY_DIR = EXTERNAL_DIR / "candidate_a" / "leroy2008"
SOURCE_PATHS = (
    "tools/evaluate_candidate_a_all_options.py",
    "tools/evaluate_candidate_a_sparc_baryonic.py",
    "tools/check_candidate_a_definitions.py",
    "emergent_matter_model/physics_baseline.py",
    *a2.SOURCE_DEPENDENCIES,
)
Density = Callable[[np.ndarray, np.ndarray], np.ndarray]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_protocol() -> dict[str, Any]:
    if sha256(PROTOCOL) != PROTOCOL_SHA256:
        raise ValueError("All-option protocol differs from its frozen SHA-256")
    protocol: dict[str, Any] = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    return protocol


def positive(value: float, name: str) -> None:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")


def effective_density(rho_bar: np.ndarray, alpha: float, rho0: float) -> np.ndarray:
    """Invert rho_bar/rho0=(rho_eff/rho0)**alpha, after summing volume densities."""
    positive(alpha, "alpha")
    positive(rho0, "rho0")
    rho = np.asarray(rho_bar, dtype=float)
    if not np.all(np.isfinite(rho)) or np.any(rho < 0):
        raise ValueError("Baryonic volume density must be finite and nonnegative")
    if alpha == 1:
        return rho.copy()
    result = np.zeros_like(rho)
    mask = rho > 0
    with np.errstate(over="raise", invalid="raise", under="raise"):
        result[mask] = np.exp(
            math.log(rho0) + (np.log(rho[mask]) - math.log(rho0)) / alpha)
    return result


@lru_cache(maxsize=8)
def quadrature(order: int) -> tuple[np.ndarray, np.ndarray]:
    if isinstance(order, bool) or not isinstance(order, int) or order < 8:
        raise ValueError("Quadrature order must be an integer >= 8")
    x, w = leggauss(order)
    return (x + 1) / 2, w / 2


def axisymmetric_v2(density: Density, radii: np.ndarray, *, order: int,
                    r_scale: float = 1.0, z_scale: float = 0.2,
                    gravitational_constant: float = 1.0) -> np.ndarray:
    """Midplane R*dPhi/dR for an even-in-z volume density; units must be consistent.

    The azimuthal integral is analytic. Rational maps integrate both remaining
    coordinates to infinity. Split at R'=R to resolve the integrable kernel.
    A negative result is an outward radial force, not a speed to clip to zero.
    """
    for value, name in ((r_scale, "r_scale"), (z_scale, "z_scale"),
                        (gravitational_constant, "G")):
        positive(value, name)
    field = np.asarray(radii, dtype=float)
    if field.ndim != 1 or not len(field) or np.any(field <= 0) or not np.isfinite(field).all():
        raise ValueError("Field radii must be a nonempty vector of finite positive values")
    t, w = quadrature(order)
    z = z_scale * t / (1 - t)
    wz = w * z_scale / (1 - t) ** 2
    result = []
    for radius in field:
        split = radius / (radius + r_scale)
        tr = np.r_[t * split, split + t * (1 - split)]
        wr = np.r_[w * split, w * (1 - split)] * r_scale / (1 - tr) ** 2
        source_r = (r_scale * tr / (1 - tr))[:, None]
        source_z = z[None, :]
        plus = (radius + source_r) ** 2 + source_z**2
        minus = (radius - source_r) ** 2 + source_z**2
        complement = minus / plus
        kernel = (ellipkm1(complement)
                  + (radius**2 - source_r**2 - source_z**2) / minus
                  * ellipe(1 - complement)) / np.sqrt(plus)
        rho = density(source_r, source_z)
        if rho.shape != kernel.shape or not np.isfinite(rho).all() or np.any(rho < 0):
            raise ValueError("Density callback must return finite nonnegative volume densities")
        v2 = 4 * gravitational_constant * np.sum(
            kernel * rho * source_r * wr[:, None] * wz[None, :])
        if not math.isfinite(v2):
            raise ArithmeticError("Non-finite axisymmetric Poisson integral")
        result.append(float(v2))
    return np.asarray(result)


def miyamoto_nagai_density(r: np.ndarray, z: np.ndarray) -> np.ndarray:
    """Stipulated M=a=G=1, b=0.2 analytic benchmark, not observational input."""
    b2 = 0.2**2
    s = np.sqrt(z**2 + b2)
    rho: np.ndarray = b2 * (r**2 + (1 + 3 * s) * (1 + s)**2) / (
        4 * math.pi * (r**2 + (1 + s)**2)**2.5 * s**3)
    return rho


def max_relative(actual: np.ndarray, expected: np.ndarray) -> float:
    if not np.isfinite(actual).all() or not np.isfinite(expected).all() or np.any(expected == 0):
        raise ArithmeticError("Relative-error check requires finite values and nonzero reference")
    return float(np.max(np.abs(actual / expected - 1)))


def check_option1() -> dict[str, Any]:
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    factor = 8 * math.pi * definitions.G / definitions.C_LIGHT**4
    cosmological_constant = 1e-52
    errors = []
    for epsilon in (1e-10, 1.0, 1e10):
        for eos in (0.0, 1 / 3, -1.0):
            pressure = eos * epsilon
            stress = np.diag([epsilon, pressure, pressure, pressure])
            ricci = np.diag([
                factor * (epsilon + 3 * pressure) / 2 - cosmological_constant,
                *([factor * (epsilon - pressure) / 2 + cosmological_constant] * 3),
            ])
            scalar = factor * (epsilon - 3 * pressure) + 4 * cosmological_constant
            einstein = ricci - scalar * eta / 2 + cosmological_constant * eta
            for beta in (0.0, 0.3, 0.9):
                observer = np.array([1.0, beta, 0.0, 0.0]) / math.sqrt(1 - beta**2)
                if not math.isclose(float(observer @ eta @ observer), -1.0, abs_tol=1e-12):
                    raise ArithmeticError("Observer is not unit timelike")
                rho = float(observer @ stress @ observer) / definitions.C_LIGHT**2
                cm = float(observer @ einstein @ observer)
                for c0 in (1e-50, 1e-20, 1e-5):
                    mapped = definitions.normalization_for_projection(c0) * cm / c0
                    errors.append(abs(mapped / rho - 1))
    if max(errors) > 1e-12:
        raise ArithmeticError("Option-1 projected GR identity check failed")
    prior = definitions.build_report()
    for row in prior["vacuum_and_quasilocal"]:
        if row["local_stress_energy_mass_density_kg_m3"] != 0 or row["kretschmann_m_minus4"] <= 0:
            raise ArithmeticError("Vacuum tidal/local-density distinction failed")
    vacuum = definitions.perfect_fluid_curvatures(0.0, 0.0, cosmological_constant)
    if vacuum["einstein_projection_minus_lambda_m_minus2"] != 0:
        raise ArithmeticError("Lambda vacuum incorrectly counted as material energy")
    return {
        "outcome": "consistency_checks_passed",
        "evidence_class": "conditional_GR_algebra_not_empirical_discrimination",
        "fluid_observer_normalization_cases": len(errors),
        "max_relative_identity_error": max(errors),
        "vacuum_and_regional_checks": len(prior["vacuum_and_quasilocal"]),
        "independent_observational_confirmation": False,
    }


def check_option3() -> dict[str, Any]:
    ratios = np.array([0.0, 0.01, 0.1, 1.0, 10.0, 100.0])
    mappings = []
    for alpha in (0.25, 0.5, 1.0, 2.0, 4.0):
        eff = effective_density(ratios, alpha, 1.0)
        if not np.allclose(eff**alpha, ratios, rtol=1e-12, atol=0):
            raise ArithmeticError("Full-density inversion failed")
        a, b = np.array([0.2, 2.0]), np.array([0.3, 3.0])
        additive = np.allclose(effective_density(a + b, alpha, 1),
                               effective_density(a, alpha, 1) + effective_density(b, alpha, 1))
        changes_sign = bool(np.any(eff < ratios) and np.any(eff > ratios))
        if additive != (alpha == 1) or changes_sign != (alpha != 1):
            raise ArithmeticError("Density-law additivity or effective-excess sign gate failed")
        mappings.append({"alpha": alpha, "rho_bar_over_rho0": ratios.tolist(),
                         "rho_eff_over_rho0": eff.tolist(),
                         "component_mapping_is_additive": bool(additive),
                         "effective_excess_changes_sign": changes_sign})
    radii = np.array([0.5, 1.0, 2.0, 4.0])
    expected = radii**2 / (radii**2 + 1.2**2)**1.5
    coarse = axisymmetric_v2(miyamoto_nagai_density, radii, order=64)
    fine = axisymmetric_v2(miyamoto_nagai_density, radii, order=128)
    errors = {
        "coarse_vs_analytic": max_relative(coarse, expected),
        "fine_vs_analytic": max_relative(fine, expected),
        "coarse_vs_fine": max_relative(coarse, fine),
    }
    nonlinear = []
    for alpha in (0.5, 1.0, 2.0):
        def density(r: np.ndarray, z: np.ndarray, alpha: float = alpha) -> np.ndarray:
            # Evaluate the analytic transformed exponential without underflowing
            # the baryonic input before taking a fractional power.
            return np.exp(-r / alpha - z / (0.2 * alpha))

        low = axisymmetric_v2(density, radii, order=64)
        high = axisymmetric_v2(density, radii, order=128)
        error = max_relative(low, high)
        nonlinear.append({"alpha": alpha, "v2": high.tolist(),
                          "coarse_vs_fine_relative_error": error})
    if max([*errors.values(), *(r["coarse_vs_fine_relative_error"] for r in nonlinear)]) >= 0.005:
        raise ArithmeticError("Full-density solver failed the frozen 0.5% accuracy gate")
    return {
        "mathematical_outcome": "density_mapping_and_solver_checks_passed",
        "evidence_class": "stipulated_full_density_benchmarks_not_observations",
        "density_mappings": mappings,
        "poisson_benchmark": {"radii": radii.tolist(), "analytic_v2": expected.tolist(),
                              "numerical_v2": fine.tolist(), "relative_errors": errors,
                              "required_max_relative_error": 0.005},
        "nonlinear_disc_benchmarks": nonlinear,
        "gr_identity_gate": "only_alpha_1_is_the_same_baryons_only_GR_source",
        "observational_fit_performed": False,
    }


def verify_density_data(protocol: dict[str, Any], fetch: bool = False) -> list[dict[str, Any]]:
    spec = protocol["new_data"]
    holdings = []
    for holding in spec["holdings"]:
        name = holding["name"]
        path = DENSITY_DIR / name
        url = spec["base_url"] + name
        if not path.exists() and fetch:
            download(url, path)
        if not path.is_file() or path.stat().st_size != holding["bytes"] or (
                sha256(path) != holding["sha256"]):
            raise ValueError(f"Missing or modified Leroy input: {name}; use --fetch-density-data "
                             "for missing files; modified files are never overwritten")
        if fetch:
            _record(f"candidate_a/leroy2008/{name}", url, path, spec["citation"])
        holdings.append({**holding, "url": url})
    return holdings


def optional_number(line: str, start: int, end: int) -> float | None:
    value = line[start:end].strip()
    if not value:
        return None
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError("Non-finite Leroy table value")
    return parsed


def audit_density_profiles(primary_names: set[str]) -> dict[str, Any]:
    catalog_names = {
        "".join(line[:8].split())
        for line in (DENSITY_DIR / "table4.dat").read_text(encoding="ascii").splitlines()
    }
    counts: dict[str, dict[str, Any]] = {}
    for line in (DENSITY_DIR / "table7.dat").read_text(encoding="ascii").splitlines():
        name = "".join(line[:8].split())
        if name not in catalog_names:
            raise ValueError(f"Density profile has no catalog entry: {name}")
        if name not in primary_names:
            continue
        row = counts.setdefault(name, {
            "galaxy": name, "radial_rows": 0, "rows_missing_any_component": 0,
            "missing": {"HI": 0, "H2": 0, "stars": 0},
            "negative_component_values": 0, "nonpositive_or_missing_radii": 0,
            "upper_limit_flags": {"HI": 0, "stars": 0},
        })
        row["radial_rows"] += 1
        radius = optional_number(line, 9, 13)
        row["nonpositive_or_missing_radii"] += radius is None or radius <= 0
        missing = False
        for label, start, end in (("HI", 19, 24), ("H2", 29, 35), ("stars", 41, 48)):
            value = optional_number(line, start, end)
            row["missing"][label] += value is None
            row["negative_component_values"] += value is not None and value < 0
            missing |= value is None
        row["rows_missing_any_component"] += missing
        for label, start, end in (("HI", 25, 28), ("stars", 49, 54)):
            row["upper_limit_flags"][label] += optional_number(line, start, end) == 1.0
    overlap = catalog_names & primary_names
    if set(counts) != overlap or not counts:
        raise ValueError("Missing profiles for catalog/SPARC overlap, or empty overlap")
    return {
        "galaxies_in_catalog": len(catalog_names),
        "overlap_galaxies": len(counts),
        "galaxies_with_complete_tabulated_components": sum(
            row["rows_missing_any_component"] == 0 for row in counts.values()),
        "profiles": [counts[name] for name in sorted(counts)],
        "vertical_volume_profiles_supplied": False,
        "missing_measurements_replaced_with_zero": False,
        "gas_includes_helium": True,
        "outcome": "blocked_pending_density_reconstruction_and_observational_protocol",
    }


def compare_results(expected: Any, actual: Any, path: str = "result") -> int:
    """Refuse scientific drift; count compared leaves, not just summary numbers."""
    if isinstance(expected, dict) and isinstance(actual, dict):
        if expected.keys() != actual.keys():
            raise ValueError(f"Reproduction keys differ at {path}")
        return sum(compare_results(expected[k], actual[k], f"{path}.{k}") for k in expected)
    if isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            raise ValueError(f"Reproduction length differs at {path}")
        return sum(compare_results(x, y, f"{path}[{i}]")
                   for i, (x, y) in enumerate(zip(expected, actual, strict=True)))
    if isinstance(expected, float) and isinstance(actual, float):
        equal = math.isfinite(expected) and math.isfinite(actual) and math.isclose(
            expected, actual, rel_tol=1e-8, abs_tol=1e-8)
    else:
        equal = type(expected) is type(actual) and expected == actual
    if not equal:
        raise ValueError(f"Reproduction mismatch at {path}: {expected!r} != {actual!r}")
    return 1


def reproduce_option2(evaluate: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    expected = json.loads(a2.OUTPUT.read_text(encoding="utf-8"))
    actual = evaluate()
    if actual["outcome"] == "incomplete":
        raise ValueError(f"Option-2 reproduction incomplete: {actual['incomplete_reason']}")
    excluded = {"revision", "environment"}
    leaves = compare_results(
        {k: v for k, v in expected.items() if k not in excluded},
        {k: v for k, v in actual.items() if k not in excluded})
    return {
        "outcome": actual["outcome"],
        "reproduction": "passed",
        "compared_leaves": leaves,
        "float_tolerance": {"rtol": 1e-8, "atol": 1e-8},
        "original_artifact": str(a2.OUTPUT.relative_to(ROOT)).replace("\\", "/"),
        "original_artifact_sha256": sha256(a2.OUTPUT),
        "populations": actual["populations"],
        "secondary_q3_outcome": actual["secondary_q3_outcome"],
        "protocol_deviations": actual["protocol_deviations"],
        "new_independent_observational_test": False,
        "current_authorization": "author_requested_testing_of_all_three_options",
        "historical_artifact_status": actual["operationalization_status"],
    }


def run(fetch: bool = False, evaluate_a2: Callable[[], dict[str, Any]] = a2.run
        ) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema_version": 1, "protocol_id": "candidate-a-all-options-gates-v1",
        "protocol_sha256": PROTOCOL_SHA256, "candidate_a_confirmed": False,
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "scipy": scipy.__version__},
    }
    try:
        protocol = verify_protocol()
        report["revision"] = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        report["source_sha256"] = {name: sha256(ROOT / name) for name in SOURCE_PATHS}
        report["data"] = verify_density_data(protocol, fetch)
        a2.verify_preregistration()
        sparc = a2.fetch_sparc()
        report["sparc_data"] = a2.verify_data(sparc)
        report["option_1"] = check_option1()
        report["option_3"] = check_option3()
        primary = a2.load_sparc(sparc)
        report["option_3"]["data_readiness"] = audit_density_profiles({g.name for g in primary})
        report["option_3"]["requirements_before_fit"] = (
            protocol["option_3"]["data_gate"]["requirements_before_fit"])
        report["option_2"] = reproduce_option2(evaluate_a2)
        report["outcome"] = "partial_option3_observational_test_blocked"
    except (OSError, ValueError, ArithmeticError, a2.IncompleteTestError,
            subprocess.CalledProcessError) as error:
        report.update(outcome="incomplete", incomplete_reason=str(error))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--fetch-density-data", action="store_true")
    args = parser.parse_args(argv)
    report = run(args.fetch_density_data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"{report['outcome']}: {args.output}")
    if report["outcome"] == "incomplete":
        print(report["incomplete_reason"], file=sys.stderr)
        return 1
    print("Option 3: no observational fit; density reconstruction and a new protocol are required.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
