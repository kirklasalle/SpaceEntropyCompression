"""Selected Candidate B: width-matched CMS heavy-scalar ZZ comparison (extended test B).

Applies ``knowledgebase/candidate_b_extended_test_preregistration.json``. Each heavy
eigenstate of the restricted brane Higgs-portal model is produced like an SM-like heavy
scalar scaled by its Higgs fraction u_a^2. It decays to ZZ with the SM-like partial width
scaled by u_a^2, against a total width that also contains tree-level decays to scalar
pairs. The predicted sigma x BR(ZZ) is compared, separately for ggF and VBF, with the
CMS-HIG-24-002 observed 95% CL limits for the bracketing width hypotheses. mu4 = 0 is the
SM limit, so the test can only bound mu4; it cannot confirm or exclude Candidate B.
"""

from __future__ import annotations

import importlib.util
import json
import math
import re
import sys
import time
import zipfile
from pathlib import Path
from types import ModuleType
from typing import Any

import numpy as np
import yaml  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(f"{name}.py"))
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, module)
    spec.loader.exec_module(module)
    return module


prep = _load("prepare_candidate_b_test")
contour = _load("evaluate_candidate_b_atlas_contour")
rate = _load("evaluate_candidate_b_higgs_rate_likelihood")

PREREGISTRATION = rate.PREREGISTRATION
FROZEN_PREREGISTRATION_SHA256 = rate.FROZEN_PREREGISTRATION_SHA256
THEORY_INPUTS = ROOT / "knowledgebase" / "candidate_b_theory_inputs.json"
THEORY_INPUTS_SHA256 = "bc2ec81ca932d9d1364c9d8f23324bf46f00f51b8e0f5ea39dab64e01f5c7833"
CMS_ZIP = ROOT / "data" / "external" / "candidate_b" / "raw" / \
    "hepdata_ins3161000_v1_original.zip"
DATASET_IDS = ("cms-hig-24-002-heavy-scalar-zz", "hxswg-sm-like-heavy-higgs-13tev")
FIRST_TEST = contour.OUTPUT
RATE_TEST = rate.OUTPUT
OUTPUT = ROOT / "results" / "candidate_b_cms_resonance_test.json"

WIDTH_TABLES = (("NWA", 0.0), ("W1", 1.0), ("W10", 10.0), ("W100", 100.0))
WIDTH_VALUES = np.array([width for _, width in WIDTH_TABLES])
PRODUCTIONS = (("ggF", "ggH"), ("VBF", "VBFH"))
COLUMNS = {"observed": "Observed", "expected": "Expected median"}
MASS_MIN_GEV, MASS_MAX_GEV = 130.0, 3000.0
TABULATED_MAX_GEV = 1000.0
SCAN_KAPPA = 0.90
SCAN_STEPS = 100
BISECTION_STEPS = 30
CLUSTER_WIDTHS_GEV = (10.0, 100.0)
VARIANTS: dict[str, dict[str, Any]] = {
    "primary": {"column": "observed", "mass_rule": "envelope", "sigma": "nominal",
                "extrapolated": False},
    "expected_median": {"column": "expected", "mass_rule": "envelope", "sigma": "nominal",
                        "extrapolated": False},
    "mass_interpolation": {"column": "observed", "mass_rule": "log_linear",
                           "sigma": "nominal", "extrapolated": False},
    "theory_low": {"column": "observed", "mass_rule": "envelope", "sigma": "low",
                   "extrapolated": False},
    "including_extrapolated": {"column": "observed", "mass_rule": "envelope",
                               "sigma": "nominal", "extrapolated": True},
}


# --- CMS limit tables --------------------------------------------------------

def load_limit_table(archive: zipfile.ZipFile, submissions: dict[str, Any], width_key: str,
                     width: float, production: str, suffix: str) -> dict[str, Any]:
    """Read one fixed-width limit table and check every label the test relies on."""
    data_file = f"Limits_{width_key}_{suffix}.yaml"
    doc = submissions.get(data_file)
    if doc is None:
        raise ValueError(f"{data_file}: not described in submission.yaml")
    description = " ".join(doc.get("description", "").split())
    process = (f"upper limits on the {production} production cross section times branching "
               "fraction for the process pp --> X --> ZZ")
    width_text = "narrow" if width_key == "NWA" else f"GammaX = {width:g} GeV"
    if process not in description or width_text not in description:
        raise ValueError(f"{data_file}: unexpected description: {description}")
    keywords = {k["name"]: k["values"] for k in doc.get("keywords", [])}
    if keywords.get("cmenergies") != [13000] or \
            keywords.get("reactions") != ["P P --> X --> Z Z"]:
        raise ValueError(f"{data_file}: not a 13 TeV pp -> X -> ZZ table")
    table = yaml.safe_load(archive.read(data_file))
    (independent,) = table["independent_variables"]
    if independent["header"] != {"name": "$m_X$", "units": "GeV"}:
        raise ValueError(f"{data_file}: unexpected mass header")
    width_label = "NWA" if width_key == "NWA" else f"$\\Gamma_X = {width:g}$ GeV"
    columns: dict[str, np.ndarray] = {}
    for dependent in table["dependent_variables"]:
        qualifiers = {q["name"]: q["value"] for q in dependent.get("qualifiers", [])}
        if qualifiers.get("Production") != production or \
                qualifiers.get("Width") != width_label or \
                float(qualifiers.get("LUMINOSITY", 0)) != 138:
            raise ValueError(f"{data_file}: unexpected qualifiers {qualifiers}")
        name = dependent["header"]["name"]
        if name in COLUMNS.values():
            if dependent["header"].get("units") != "pb" or name in columns:
                raise ValueError(f"{data_file}: bad or repeated column {name}")
            columns[name] = np.array([float(v["value"]) for v in dependent["values"]])
    mass = np.array([float(v["value"]) for v in independent["values"]])
    if set(columns) != set(COLUMNS.values()):
        raise ValueError(f"{data_file}: missing observed or expected-median column")
    if not np.all(np.diff(mass) > 0):
        raise ValueError(f"{data_file}: masses not strictly increasing")
    for values in columns.values():
        if values.shape != mass.shape or not np.all(np.isfinite(values) & (values > 0)):
            raise ValueError(f"{data_file}: non-finite or non-positive limits")
    return {"data_file": data_file, "name": doc.get("name"), "description": description,
            "width_GeV": width, "production": production, "mass": mass,
            **{key: columns[label] for key, label in COLUMNS.items()}}


def load_limit_tables(path: Path = CMS_ZIP) -> dict[tuple[str, str], dict[str, Any]]:
    with zipfile.ZipFile(path) as archive:
        submissions = {doc["data_file"]: doc
                       for doc in yaml.safe_load_all(archive.read("submission.yaml"))
                       if doc and doc.get("data_file")}
        return {(width_key, production): load_limit_table(archive, submissions, width_key,
                                                          width, production, suffix)
                for width_key, width in WIDTH_TABLES for production, suffix in PRODUCTIONS}


def bracket(grid: np.ndarray, x: float) -> list[int] | None:
    """Indices of grid[i] <= x <= grid[j]; one index on an exact match; None outside."""
    if not grid[0] <= x <= grid[-1]:
        return None
    upper = int(np.searchsorted(grid, x))
    return [upper] if grid[upper] == x else [upper - 1, upper]


def table_limit(table: dict[str, Any], mass: float, column: str = "observed",
                mass_rule: str = "envelope") -> float | None:
    found = bracket(table["mass"], mass)
    if found is None:
        return None
    limits = table[column][found]
    if mass_rule == "envelope" or len(found) == 1:
        return float(limits.max())
    low, high = table["mass"][found]
    t = (mass - low) / (high - low)
    return float(math.exp((1 - t) * math.log(limits[0]) + t * math.log(limits[1])))


def cms_limit(tables: dict[tuple[str, str], dict[str, Any]], production: str, mass: float,
              width: float, column: str = "observed",
              mass_rule: str = "envelope") -> float | None:
    """Conservative width envelope of the bracketing fixed-width limits at (M, Gamma)."""
    found = bracket(WIDTH_VALUES, width)
    if found is None:
        return None
    values = [table_limit(tables[(WIDTH_TABLES[i][0], production)], mass, column, mass_rule)
              for i in found]
    if any(value is None for value in values):
        return None
    return max(float(value) for value in values if value is not None)


# --- SM-like heavy-scalar theory inputs -------------------------------------

def load_theory(constants: Any, path: Path = THEORY_INPUTS) -> dict[str, Any]:
    if prep.sha256_file(path) != THEORY_INPUTS_SHA256:
        raise RuntimeError("theory-input table changed after the freeze; stop")
    table = prep.load_json(path)
    theory: dict[str, Any] = {}
    for production, _ in PRODUCTIONS:
        rows = np.array([[np.nan if x is None else x for x in row] for row in table[production]],
                        dtype=float)
        mass, sigma, down, pdf, ew = rows[:, 0], rows[:, 1], rows[:, 3], rows[:, 4], rows[:, 5]
        ew_factor = np.where(np.isnan(ew), 1.0, np.minimum(1.0, ew)) \
            if production == "ggF" else np.ones_like(mass)
        low = sigma * (1 - np.hypot(down, pdf) / 100) * ew_factor
        if not (np.all(np.diff(mass) > 0) and np.all(sigma > 0) and np.all(low > 0)):
            raise ValueError(f"{production}: malformed theory cross sections")
        theory[production] = {"mass": mass, "log_sigma": np.log(sigma),
                              "log_sigma_low": np.log(low)}
    widths = np.array(table["sm_width"], dtype=float)
    if not np.all(np.diff(widths[:, 0]) > 0) or widths[-1, 0] != TABULATED_MAX_GEV:
        raise ValueError("SM width table must increase and end at the tabulated maximum")
    theory["width"] = {"mass": widths[:, 0], "br_zz": widths[:, 2],
                       "log_gamma": np.log(widths[:, 3])}
    tree = prep.sm_like_tree_widths(TABULATED_MAX_GEV, constants)
    theory["k_tot"] = float(widths[-1, 3] / sum(tree.values()))
    theory["k_zz"] = float(widths[-1, 3] * widths[-1, 2] / tree["ZZ"])
    return theory


def sm_like_widths(mass: float, theory: dict[str, Any], constants: Any) -> tuple[float, float]:
    """Total and ZZ widths of an SM-like scalar; continuity-scaled tree level above 1 TeV."""
    table = theory["width"]
    if mass <= TABULATED_MAX_GEV:
        if mass < table["mass"][0]:
            return math.nan, math.nan
        total = math.exp(float(np.interp(mass, table["mass"], table["log_gamma"])))
        return total, total * float(np.interp(mass, table["mass"], table["br_zz"]))
    tree = prep.sm_like_tree_widths(mass, constants)
    return theory["k_tot"] * sum(tree.values()), theory["k_zz"] * tree["ZZ"]


def sm_like_cross_section(mass: float, theory: dict[str, Any], production: str,
                          low: bool = False) -> float:
    table = theory[production]
    if not table["mass"][0] <= mass <= table["mass"][-1]:
        return math.nan
    key = "log_sigma_low" if low else "log_sigma"
    return math.exp(float(np.interp(mass, table["mass"], table[key])))


# --- model predictions -------------------------------------------------------

def heavy_states(mu4: float, radius: float, m5: float, cutoff: float, constants: Any,
                 theory: dict[str, Any]) -> dict[str, Any]:
    """Masses, widths, BR(ZZ) and SM-like-scaled cross sections of every state a >= 1."""
    spectrum = prep.diagonalize(mu4, radius, m5, cutoff, constants)
    masses, vectors = spectrum["masses"], spectrum["vectors"]
    u = vectors[0]
    w = spectrum["mu"] @ vectors[1:]
    hhh = 3.0 * spectrum["mh0_sq"] / constants.vev
    rows = []
    for a in range(1, len(masses)):
        lu, lw = u[:a], w[:a]
        # Leading a x a block of prep.cubic_tensor_slice(a, ...), which is all the width uses.
        coupling = (hhh * u[a] + w[a]) * np.outer(lu, lu) + u[a] * (np.outer(lw, lu)
                                                                     + np.outer(lu, lw))
        scalar = prep.two_scalar_width(a, masses, coupling)
        mass, u2 = float(masses[a]), float(u[a] ** 2)
        gamma_sm, gamma_zz = sm_like_widths(mass, theory, constants)
        width = u2 * gamma_sm + scalar
        rows.append((mass, u2, scalar, width, u2 * gamma_zz / width,
                     *(u2 * sm_like_cross_section(mass, theory, p) for p, _ in PRODUCTIONS),
                     *(u2 * sm_like_cross_section(mass, theory, p, True) for p, _ in PRODUCTIONS)))
    data = np.array(rows, dtype=float).reshape(-1, 9)
    return {"mass": data[:, 0], "higgs_fraction": data[:, 1], "scalar_width": data[:, 2],
            "width": data[:, 3], "br_zz": data[:, 4],
            "sigma": {"ggF": data[:, 5], "VBF": data[:, 6]},
            "sigma_low": {"ggF": data[:, 7], "VBF": data[:, 8]},
            "extrapolated": data[:, 0] > TABULATED_MAX_GEV}


def state_summary(states: dict[str, Any], index: int, limits: dict[str, float],
                  sigma_key: str = "sigma") -> dict[str, Any]:
    signals = {p: float(states[sigma_key][p][index] * states["br_zz"][index])
               for p, _ in PRODUCTIONS}
    ratios = {p: signals[p] / limits[p] for p, _ in PRODUCTIONS}
    production = max(ratios, key=lambda p: ratios[p])
    return {"mass_GeV": float(states["mass"][index]),
            "width_GeV": float(states["width"][index]),
            "scalar_pair_width_GeV": float(states["scalar_width"][index]),
            "higgs_fraction": float(states["higgs_fraction"][index]),
            "br_zz": float(states["br_zz"][index]),
            "extrapolated": bool(states["extrapolated"][index]),
            "sigma_br_pb": signals, "limit_pb": limits, "ratio": ratios,
            "leading_production": production, "leading_ratio": ratios[production]}


def evaluate(mu4: float, radius: float, m5: float, cutoff: float, constants: Any,
             theory: dict[str, Any], tables: dict[tuple[str, str], dict[str, Any]]
             ) -> dict[str, Any]:
    """Apply every preregistered comparison at one mu4."""
    states = heavy_states(mu4, radius, m5, cutoff, constants, theory)
    count = len(states["mass"])
    covered = np.zeros(count, dtype=bool)
    uncovered = {"mass_below_130_GeV": 0, "mass_above_3000_GeV": 0, "width_above_100_GeV": 0,
                 "no_bracketing_limit": 0}
    ratios = {name: np.full(count, -math.inf) for name in VARIANTS}
    limits: dict[int, dict[tuple[str, str], dict[str, float]]] = {}
    for i in range(count):
        mass, width = float(states["mass"][i]), float(states["width"][i])
        if mass < MASS_MIN_GEV:
            uncovered["mass_below_130_GeV"] += 1
            continue
        if mass > MASS_MAX_GEV:
            uncovered["mass_above_3000_GeV"] += 1
            continue
        if not width <= WIDTH_VALUES[-1]:
            uncovered["width_above_100_GeV"] += 1
            continue
        rules = {(v["column"], v["mass_rule"]) for v in VARIANTS.values()}
        raw = {rule: {p: cms_limit(tables, p, mass, width, *rule) for p, _ in PRODUCTIONS}
               for rule in rules}
        if any(value is None for values in raw.values() for value in values.values()):
            uncovered["no_bracketing_limit"] += 1
            continue
        found = {rule: {p: float(value) for p, value in values.items() if value is not None}
                 for rule, values in raw.items()}
        covered[i] = True
        limits[i] = found
        for name, variant in VARIANTS.items():
            sigma = states["sigma_low" if variant["sigma"] == "low" else "sigma"]
            rule_limits = found[(variant["column"], variant["mass_rule"])]
            ratios[name][i] = max(sigma[p][i] * states["br_zz"][i] / rule_limits[p]
                                  for p, _ in PRODUCTIONS)
    tabulated = covered & ~states["extrapolated"]
    result: dict[str, Any] = {"mu4_GeV": mu4, "R": {}, "leading": {},
                              "covered": {"tabulated": int(tabulated.sum()),
                                          "all": int(covered.sum())},
                              "uncovered": uncovered, "cluster_R": {}}
    for name, variant in VARIANTS.items():
        eligible = covered if variant["extrapolated"] else tabulated
        if not eligible.any():
            result["R"][name] = None
            continue
        index = int(np.argmax(np.where(eligible, ratios[name], -math.inf)))
        result["R"][name] = float(ratios[name][index])
        result["leading"][name] = (index, (variant["column"], variant["mass_rule"]),
                                   "sigma_low" if variant["sigma"] == "low" else "sigma")
    for window in CLUSTER_WIDTHS_GEV:
        key = {width: name for name, width in WIDTH_TABLES}[window]
        for scope, centres in (("tabulated", tabulated), ("including_extrapolated", covered)):
            members = (states["width"] <= window) & np.isfinite(states["sigma"]["ggF"]) & \
                np.isfinite(states["sigma"]["VBF"])
            if scope == "tabulated":
                members &= ~states["extrapolated"]
            best: float | None = None
            for j in np.flatnonzero(centres):
                near = members & (np.abs(states["mass"] - states["mass"][j]) <= window / 2)
                for production, _ in PRODUCTIONS:
                    limit = table_limit(tables[(key, production)], float(states["mass"][j]))
                    if limit is None:
                        continue
                    total = float(np.sum(states["sigma"][production][near]
                                         * states["br_zz"][near]))
                    best = total / limit if best is None else max(best, total / limit)
            result["cluster_R"][f"W{window:g}_{scope}"] = best
    result["states"], result["limits"] = states, limits
    return result


def leading_summary(result: dict[str, Any], variant: str) -> dict[str, Any] | None:
    if variant not in result["leading"]:
        return None
    index, rule, sigma_key = result["leading"][variant]
    return state_summary(result["states"], index, result["limits"][index][rule], sigma_key)


def scan_columns(results: list[dict[str, Any]]) -> dict[str, Any]:
    return {"mu4_GeV": [r["mu4_GeV"] for r in results],
            "R": {name: [r["R"][name] for r in results] for name in VARIANTS},
            "cluster_R": {key: [r["cluster_R"][key] for r in results]
                          for key in results[0]["cluster_R"]},
            "covered_tabulated": [r["covered"]["tabulated"] for r in results],
            "covered_all": [r["covered"]["all"] for r in results]}


def excluded_steps(values: list[float | None]) -> list[int]:
    return [k for k, value in enumerate(values, start=1) if is_excluded(value)]


def is_excluded(value: float | None) -> bool:
    return value is not None and value > 1.0


def grid_point(inverse_radius: float, m5: float, cutoff: float, constants: Any,
               theory: dict[str, Any], tables: dict[tuple[str, str], dict[str, Any]],
               rate_bounds: dict[str, float | None]) -> dict[str, Any]:
    radius = 1.0 / inverse_radius
    mu4_top = prep.mu4_for_kappa(SCAN_KAPPA, radius, m5, cutoff, constants)
    results = [evaluate(k * mu4_top / SCAN_STEPS, radius, m5, cutoff, constants, theory,
                        tables) for k in range(1, SCAN_STEPS + 1)]
    scan = scan_columns(results)
    known = [bound for bound in rate_bounds.values() if bound is not None]
    rate_min = min(known) if known else None
    row: dict[str, Any] = {
        "inverse_radius_GeV": inverse_radius, "m5_GeV": m5, "cutoff_GeV": cutoff,
        "mu4_scan_top_GeV": mu4_top, "scan_kappa": SCAN_KAPPA,
        "rate_mu4_max_GeV": rate_bounds, "rate_mu4_max_smaller_GeV": rate_min,
        "covered_any_scan_point": any(n > 0 for n in scan["covered_tabulated"]),
        "leading_state_at_scan_top": {name: leading_summary(results[-1], name)
                                      for name in ("primary", "including_extrapolated")},
        "uncovered_at_scan_top": results[-1]["uncovered"],
    }
    variants: dict[str, Any] = {}
    for name in VARIANTS:
        excluded = excluded_steps(scan["R"][name])
        first = excluded[0] * mu4_top / SCAN_STEPS if excluded else None
        variants[name] = {
            "max_R": max((r for r in scan["R"][name] if r is not None), default=None),
            "excluded_scan_steps": excluded,
            "first_excluded_scan_mu4_GeV": first,
            "contiguous": excluded == list(range(excluded[0], excluded[-1] + 1))
            if excluded else None,
            "first_excluded_below_smaller_rate_bound": None if first is None or rate_min is None
            else first < rate_min,
        }
    row["variants"] = variants
    clusters: dict[str, Any] = {}
    for key, values in scan["cluster_R"].items():
        excluded = excluded_steps(values)
        clusters[key] = {
            "max_ratio": max((r for r in values if r is not None), default=None),
            "first_exceeding_scan_mu4_GeV": excluded[0] * mu4_top / SCAN_STEPS
            if excluded else None,
            "first_exceeding_below_smaller_rate_bound": None
            if not excluded or rate_min is None else excluded[0] * mu4_top / SCAN_STEPS < rate_min,
            "label": "heuristic: a cluster of narrow states is treated as one resonance of "
                     "width W and interference is neglected"}
    row["heuristic_tower_clusters"] = clusters
    excluded = variants["primary"]["excluded_scan_steps"]
    if excluded:
        k = excluded[0]
        low = 0.0 if k == 1 else (k - 1) * mu4_top / SCAN_STEPS
        high = k * mu4_top / SCAN_STEPS
        for _ in range(BISECTION_STEPS):
            middle = 0.5 * (low + high)
            if is_excluded(evaluate(middle, radius, m5, cutoff, constants, theory,
                                    tables)["R"]["primary"]):
                high = middle
            else:
                low = middle
        at_limit = evaluate(high, radius, m5, cutoff, constants, theory, tables)
        row.update({
            "mu4_excl_min_GeV": high,
            "mu4_excl_bisection_bracket_GeV": [low, high],
            "kappa_at_mu4_excl_min": prep.matched_kappa(high, radius, m5, cutoff, constants),
            "leading_state_at_mu4_excl_min": leading_summary(at_limit, "primary"),
        })
    if not row["covered_any_scan_point"]:
        outcome = "not_covered"
    elif not excluded:
        outcome = "no_exclusion_in_scan"
    elif rate_min is not None and row["mu4_excl_min_GeV"] >= rate_min:
        outcome = "exclusion_above_rate_bounds"
    else:
        outcome = "exclusion_within_rate_allowed_region"
    bounds = {**{f"rate_{name}": value for name, value in rate_bounds.items()
                 if value is not None},
              **({"cms_direct": row["mu4_excl_min_GeV"]} if excluded else {})}
    binding = min(bounds, key=lambda name: bounds[name]) if bounds else None
    row.update({"outcome": outcome,
                "combined_mu4_bound_GeV": bounds[binding] if binding else None,
                "combined_binding_constraint": binding,
                "scan": scan})
    return row


# --- report ------------------------------------------------------------------

def rate_bounds_by_point() -> dict[tuple[float, float], dict[str, float | None]]:
    first = prep.load_json(FIRST_TEST)
    likelihood = prep.load_json(RATE_TEST)
    if likelihood.get("preregistration_sha256") != FROZEN_PREREGISTRATION_SHA256:
        raise RuntimeError("Higgs-rate likelihood artifact is not from the frozen rules; stop")
    usable = likelihood.get("outcome") == "compatible_with_limit"
    bounds: dict[tuple[float, float], dict[str, float | None]] = {}
    for row in first["grid"]:
        if row.get("valid"):
            key = (row["inverse_radius_GeV"], row["m5_GeV"])
            bounds[key] = {"contour": row["mu4_max_GeV"], "likelihood": None}
    if usable:
        for row in likelihood["grid"]:
            key = (row["inverse_radius_GeV"], row["m5_GeV"])
            if row.get("valid") and key in bounds:
                bounds[key]["likelihood"] = row["mu4_max_GeV"]
    return bounds


def interpretation(rows: list[dict[str, Any]]) -> str:
    def count(outcome: str) -> int:
        return sum(r["outcome"] == outcome for r in rows)

    clusters = sum(any(c["first_exceeding_below_smaller_rate_bound"]
                       for c in r["heuristic_tower_clusters"].values()) for r in rows)
    text = (f"Of {len(rows)} grid points, the CMS direct search is the stronger bound on mu4 at "
            f"{count('exclusion_within_rate_allowed_region')}, excludes only couplings already "
            f"removed by the Higgs-rate bounds at {count('exclusion_above_rate_bounds')}, "
            f"excludes nothing in the scanned range at {count('no_exclusion_in_scan')}, and has "
            f"no tabulated covered state at {count('not_covered')} (all heavy states above "
            "1 TeV; see the including_extrapolated variant).")
    if clusters:
        text += (f" The heuristic tower-cluster comparison exceeds a limit below the Higgs-rate "
                 f"bound at {clusters} grid points; it is labelled heuristic and is not the "
                 "result.")
    return text + (" mu4 = 0 (the SM limit) is always allowed, so these are bounds on the "
                   "restricted coupling; they do not confirm or exclude Candidate B.")


def build_report(progress: bool = False) -> dict[str, Any]:
    prereg_sha = prep.sha256_file(PREREGISTRATION)
    if prereg_sha != FROZEN_PREREGISTRATION_SHA256:
        raise RuntimeError("extended preregistration changed after it was frozen; stop")
    parent_sha = prep.sha256_file(prep.PREREGISTRATION)
    if parent_sha != contour.FROZEN_PREREGISTRATION_SHA256:
        raise RuntimeError("parent preregistration changed after it was frozen; stop")
    holdings = prep.verify_holdings(prep.load_json(prep.CATALOG), DATASET_IDS)
    if not all(row["sha256_matches"] for row in holdings):
        raise RuntimeError("CMS or HXSWG holdings missing or changed; stop")
    prereg = prep.load_json(PREREGISTRATION)
    parent = prep.load_json(prep.PREREGISTRATION)
    constants = prep.constants_from_preregistration(parent)
    theory = load_theory(constants)
    tables = load_limit_tables()
    rate_bounds = rate_bounds_by_point()
    grid = parent["parameter_grid"]
    rows = []
    for inverse_radius in grid["inverse_radius_GeV"]:
        for m5 in grid["m5_GeV"]:
            key = (inverse_radius, m5)
            if key not in rate_bounds:
                rows.append({"inverse_radius_GeV": inverse_radius, "m5_GeV": m5,
                             "valid": False, "outcome": "not_evaluated_invalid_parent_point"})
                continue
            started = time.perf_counter()
            row = grid_point(inverse_radius, m5, grid["cutoff_GeV"], constants, theory, tables,
                             rate_bounds[key])
            rows.append({"valid": True, **row})
            if progress:
                print(f"R^-1={inverse_radius:g} m5={m5:g}: {row['outcome']} "
                      f"({time.perf_counter() - started:.0f} s)", flush=True)
    evaluated = [r for r in rows if r.get("valid")]
    outcomes: dict[str, int] = {}
    for r in evaluated:
        outcomes[r["outcome"]] = outcomes.get(r["outcome"], 0) + 1
    test_b = prereg["test_b_cms_direct_resonance"]
    return {
        "schema_version": 1,
        "artifact": "candidate_b_cms_resonance_test",
        "source": Path(__file__).relative_to(ROOT).as_posix(),
        "source_sha256": prep.sha256_file(Path(__file__)),
        "model_source_sha256": prep.sha256_file(ROOT / "tools" / "prepare_candidate_b_test.py"),
        "preregistration_sha256": prereg_sha,
        "parent_preregistration_sha256": parent_sha,
        "theory_inputs_sha256": THEORY_INPUTS_SHA256,
        "data": {
            "record": "HEPData ins3161000 v1 (CMS-HIG-24-002)",
            "holdings": holdings,
            "tables": {t["data_file"]: {"name": t["name"], "description": t["description"],
                                        "width_GeV": t["width_GeV"],
                                        "production": t["production"],
                                        "mass_range_GeV": [float(t["mass"][0]),
                                                           float(t["mass"][-1])],
                                        "points": len(t["mass"])}
                       for t in tables.values()},
        },
        "theory": {"tabulated_max_GeV": TABULATED_MAX_GEV, "k_tot": theory["k_tot"],
                   "k_zz": theory["k_zz"],
                   "extrapolation": prereg["theory_inputs"]["extrapolation_above_1000_GeV"]},
        "rules": {"limit_rule": test_b["limit_rule"], "coverage": test_b["coverage"],
                  "state_ratio": test_b["state_ratio"], "mu4_scan": test_b["mu4_scan"],
                  "variants": VARIANTS,
                  "variant_resolution": "sensitivity variants and heuristic clusters are "
                                        "reported at scan resolution; only the primary "
                                        "mu4_excl_min is bisected"},
        "grid": rows,
        "summary": {"outcomes": outcomes,
                    "outcome_rules": test_b["outcome_rules_per_grid_point"]},
        "combined_statement": prereg["combined_statement"],
        "overall_scope": test_b["overall_scope"],
        "caveats": prereg["caveats"],
        "evidence_kind": "comparison of model sigma x BR(ZZ) with published 95% CL upper "
                         "limits; per-state, per-production, no joint likelihood",
        "likelihood_evaluated": False,
        "candidate_b_confirmed": False,
        "interpretation": interpretation(evaluated),
    }


NUMERIC_LIST = re.compile(r"\[(?:\s*(?:-?\d[\d.eE+-]*|null|true|false)\s*,?)+\s*\]")


def write_report(path: Path, payload: dict[str, Any]) -> None:
    """Indented JSON with each list of scalars on one line, to keep the scan compact."""
    text = NUMERIC_LIST.sub(lambda m: " ".join(m.group(0).split()).replace("[ ", "[")
                            .replace(" ]", "]"), json.dumps(payload, indent=2))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + "\n", encoding="utf-8")


def main() -> None:
    started = time.perf_counter()
    report = build_report(progress=True)
    write_report(OUTPUT, report)
    print(f"Saved {OUTPUT} in {time.perf_counter() - started:.0f} s")
    print(f"Outcomes: {report['summary']['outcomes']}")
    for row in report["grid"]:
        if row.get("valid"):
            excl = row.get("mu4_excl_min_GeV")
            print(f"  R^-1={row['inverse_radius_GeV']:g} m5={row['m5_GeV']:g}: "
                  f"{row['outcome']}; rate mu4_max={row['rate_mu4_max_smaller_GeV']:.4g}; "
                  f"cms mu4_excl_min={'none' if excl is None else f'{excl:.4g}'}")
    print("Bounds on the restricted coupling only; Candidate B is not confirmed.")


if __name__ == "__main__":
    main()
