"""Selected Candidate B: correlated Higgs-rate likelihood test (extended test A).

Applies ``knowledgebase/candidate_b_extended_test_preregistration.json``. The
restricted model predicts that every production x decay rate of the 125 GeV
state is kappa^2 times its SM value, which is exactly the ATLAS global
signal-strength hypothesis. The published observed profile likelihood
-2 ln Lambda(mu) (HEPData ins2104706, Aux Figure 8) is therefore a valid
correlated likelihood for this model. The result is an asymptotic one-sided 95%
CL lower limit on mu = kappa^2, translated into mu4 on the parent grid. It is a
bound on the restricted model, not confirmation of Candidate B.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
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

PREREGISTRATION = ROOT / "knowledgebase" / "candidate_b_extended_test_preregistration.json"
FROZEN_PREREGISTRATION_SHA256 = "fc23f2e389a9b761bf8747fe125c44ae93beb191384a79b11eb4d517764890a2"
ATLAS_ZIP = ROOT / "data" / "external" / "candidate_b" / "raw" / \
    "hepdata_ins2104706_v1_original.zip"
FIRST_TEST = ROOT / "results" / "candidate_b_atlas_contour_test.json"
OUTPUT = ROOT / "results" / "candidate_b_higgs_rate_likelihood_test.json"
ONE_SIDED_95 = 2.706
TWO_SIDED_95 = 3.841
SCANS = {
    "AuxFig1.yaml": ("total", "with all systematic uncertainties included"),
    "AuxFig1_2.yaml": ("background_theory_fixed", "theory uncertainties in background"),
    "AuxFig1_3.yaml": ("signal_and_background_theory_fixed",
                       "theory uncertainties in background and signal"),
    "AuxFig1_4.yaml": ("statistical_only", "all systematic uncertainties fixed"),
}


def load_scan(archive: zipfile.ZipFile, data_file: str) -> dict[str, Any]:
    """Read one observed -2 ln Lambda(mu) scan and check its labels."""
    submission = [doc for doc in yaml.safe_load_all(archive.read("submission.yaml"))
                  if doc and doc.get("data_file") == data_file]
    if len(submission) != 1:
        raise ValueError(f"{data_file}: not described exactly once in submission.yaml")
    description = " ".join(submission[0].get("description", "").split())
    if "Observed variations of" not in description or SCANS[data_file][1] not in description:
        raise ValueError(f"{data_file}: unexpected description: {description}")
    table = yaml.safe_load(archive.read(data_file))
    (independent,), (dependent,) = table["independent_variables"], table["dependent_variables"]
    qualifiers = {q["name"]: q["value"] for q in dependent.get("qualifiers", [])}
    if independent["header"]["name"] != "$\\mu$" or "ln" not in dependent["header"]["name"]:
        raise ValueError(f"{data_file}: unexpected headers")
    if float(qualifiers.get("SQRT(S)", 0)) != 13000:
        raise ValueError(f"{data_file}: not a 13 TeV scan")
    mu = np.array([float(v["value"]) for v in independent["values"]])
    nll = np.array([float(v["value"]) for v in dependent["values"]])
    order = np.argsort(mu)
    mu, nll = mu[order], nll[order]
    if not (np.all(np.isfinite(nll)) and np.all(np.diff(mu) > 0)):
        raise ValueError(f"{data_file}: non-finite values or repeated mu")
    return {"data_file": data_file, "name": submission[0].get("name"),
            "description": description, "qualifiers": qualifiers, "mu": mu, "nll": nll}


def crossing_below(mu: np.ndarray, nll: np.ndarray, start: float,
                   level: float) -> float | None:
    """Largest mu below ``start`` where the piecewise-linear scan reaches ``level``."""
    xs = [start, *mu[mu < start][::-1].tolist()]
    ys = [float(np.interp(start, mu, nll)), *nll[mu < start][::-1].tolist()]
    for (x0, y0), (x1, y1) in zip(zip(xs[:-1], ys[:-1], strict=True),
                                  zip(xs[1:], ys[1:], strict=True), strict=True):
        if y1 >= level > y0:
            return float(x0 + (level - y0) * (x1 - x0) / (y1 - y0))
    return None


def analyse_scan(mu: np.ndarray, nll: np.ndarray) -> dict[str, Any]:
    best = int(np.argmin(nll))
    mu_hat, nll_min = float(mu[best]), float(nll[best])
    mu_ref = min(mu_hat, 1.0)
    nll_ref = float(np.interp(mu_ref, mu, nll))
    q_family = float(np.interp(1.0, mu, nll)) - nll_min if mu_hat > 1.0 else 0.0
    below = mu[mu < mu_ref]
    tail = nll[mu <= mu_ref][::-1]
    return {
        "scan_range": [float(mu[0]), float(mu[-1])], "points": len(mu),
        "mu_hat": mu_hat, "nll_min": nll_min, "mu_ref": mu_ref, "nll_ref": nll_ref,
        "q_family": q_family,
        "points_below_reference": len(below),
        "monotone_below_reference": bool(np.all(np.diff(tail) >= 0)),
        "mu_lo_primary": crossing_below(mu, nll, mu_ref, nll_ref + ONE_SIDED_95),
        "mu_lo_unbounded_one_sided": crossing_below(mu, nll, mu_hat, nll_min + ONE_SIDED_95),
        "mu_lo_two_sided": crossing_below(mu, nll, mu_hat, nll_min + TWO_SIDED_95),
    }


def classify(scan: dict[str, Any]) -> str:
    if scan["points_below_reference"] < 2:
        return "ambiguous_data"
    if scan["q_family"] > ONE_SIDED_95:
        return "incompatible"
    if scan["mu_lo_primary"] is None:
        return "not_determinable"
    return "compatible_with_limit"


def build_report() -> dict[str, Any]:
    prereg_sha = prep.sha256_file(PREREGISTRATION)
    if prereg_sha != FROZEN_PREREGISTRATION_SHA256:
        raise RuntimeError("extended preregistration changed after it was frozen; stop")
    parent_sha = prep.sha256_file(prep.PREREGISTRATION)
    if parent_sha != contour.FROZEN_PREREGISTRATION_SHA256:
        raise RuntimeError("parent preregistration changed after it was frozen; stop")
    parent = prep.load_json(prep.PREREGISTRATION)
    holdings = prep.verify_holdings(prep.load_json(prep.CATALOG), prep.DATASET_IDS[:1])
    if not all(row["sha256_matches"] for row in holdings):
        raise RuntimeError("ATLAS holdings missing or changed; stop")
    with zipfile.ZipFile(ATLAS_ZIP) as archive:
        scans = {name: load_scan(archive, name) for name in SCANS}
    analyses = {name: analyse_scan(s["mu"], s["nll"]) for name, s in scans.items()}
    primary = analyses["AuxFig1.yaml"]
    outcome = classify(primary)
    first = json.loads(FIRST_TEST.read_text(encoding="utf-8"))
    report: dict[str, Any] = {
        "schema_version": 1,
        "artifact": "candidate_b_higgs_rate_likelihood_test",
        "source": Path(__file__).relative_to(ROOT).as_posix(),
        "source_sha256": prep.sha256_file(Path(__file__)),
        "model_source_sha256": prep.sha256_file(ROOT / "tools" / "prepare_candidate_b_test.py"),
        "preregistration_sha256": prereg_sha,
        "parent_preregistration_sha256": parent_sha,
        "data": {"record": "HEPData ins2104706 v1 (ATLAS, Nature 607 (2022) 52)",
                 "holdings": holdings,
                 "scans": {name: {"label": SCANS[name][0], "name": s["name"],
                                  "description": s["description"],
                                  "qualifiers": s["qualifiers"]}
                           for name, s in scans.items()}},
        "thresholds": {"one_sided_95": ONE_SIDED_95, "two_sided_95": TWO_SIDED_95},
        "primary_scan": primary,
        "sensitivity_scans": {SCANS[name][0]: {**analyses[name],
                                               "outcome": classify(analyses[name])}
                              for name in SCANS if name != "AuxFig1.yaml"},
        "sensitivity_note": "Scans with theory or systematic uncertainties fixed understate the "
                            "uncertainty and are never the result. Their outcome labels show how "
                            "much the conclusion depends on those uncertainties.",
        "evidence_kind": "asymptotic one-sided 95% CL bound from a published collaboration "
                         "profile likelihood, under the restricted model's global-mu prediction",
        "likelihood_evaluated": True,
        "one_parameter_interval_claimed": True,
        "interval_kind": "lower limit on mu = kappa^2, translated to mu4_max at fixed "
                         "(R, m5, Lambda); not a joint interval over the grid",
        "candidate_b_confirmed": False,
        "outcome": outcome,
    }
    if outcome == "incompatible":
        report["interpretation"] = ("The published likelihood disfavours every mu <= 1 at "
                                    "asymptotic 95% CL, so the restricted family is "
                                    "disfavoured by this product.")
        return report
    if outcome != "compatible_with_limit":
        report["interpretation"] = ("No primary limit is reported; see the outcome rule in the "
                                    "preregistration.")
        return report
    mu_lo = float(primary["mu_lo_primary"])
    kappa_lo = math.sqrt(mu_lo)
    grid = parent["parameter_grid"]
    constants = prep.constants_from_preregistration(parent)
    rows = [contour.grid_point(r, m5, grid["cutoff_GeV"], [[kappa_lo, 1.0]], constants)
            for r in grid["inverse_radius_GeV"] for m5 in grid["m5_GeV"]]
    first_rows = {(r["inverse_radius_GeV"], r["m5_GeV"]): r for r in first["grid"]}
    for row in rows:
        if row["valid"]:
            previous = first_rows[(row["inverse_radius_GeV"], row["m5_GeV"])]["mu4_max_GeV"]
            row["mu4_max_contour_first_test_GeV"] = previous
            row["stronger_rate_bound"] = ("likelihood" if row["mu4_max_GeV"] < previous
                                          else "contour")
    sensitivity = []
    for mass in parent["constants"]["M_H_sensitivity_GeV"]:
        shifted = prep.constants_from_preregistration(parent, mass)
        for row in rows:
            if row["valid"]:
                alt = prep.mu4_for_kappa(kappa_lo, 1 / row["inverse_radius_GeV"],
                                         row["m5_GeV"], grid["cutoff_GeV"], shifted)
                sensitivity.append({"M_H_GeV": mass,
                                    "inverse_radius_GeV": row["inverse_radius_GeV"],
                                    "m5_GeV": row["m5_GeV"],
                                    "relative_change_mu4_max": alt / row["mu4_max_GeV"] - 1})
    report.update({
        "mu_lo": mu_lo,
        "kappa_lo": kappa_lo,
        "kappa_lo_contour_first_test": first["kappa_lo"],
        "interpretation": (
            "The restricted model's universal rate suppression mu = kappa^2 is bounded below by "
            "the published ATLAS global-mu likelihood. Parameter points with mu < mu_lo are "
            "disfavoured at asymptotic one-sided 95% CL; mu4_max translates this for each "
            "preregistered grid point. mu4 = 0 (the SM limit) is always allowed, so this bounds "
            "the coupling and does not test Candidate B's broader claims."),
        "grid": rows,
        "higgs_mass_sensitivity": sensitivity,
        "max_abs_relative_change_mu4_max": max(abs(s["relative_change_mu4_max"])
                                               for s in sensitivity),
    })
    return report


def main() -> None:
    report = build_report()
    prep.write_json(OUTPUT, report)
    print(f"Saved {OUTPUT}: outcome={report['outcome']}")
    primary = report["primary_scan"]
    print(f"mu_hat = {primary['mu_hat']:.3f}; q_family = {primary['q_family']:.3f}")
    if report["outcome"] == "compatible_with_limit":
        print(f"mu_lo = {report['mu_lo']:.4f}; kappa_lo = {report['kappa_lo']:.5f} "
              f"(contour test: {report['kappa_lo_contour_first_test']:.5f})")
    print("Asymptotic bound on the restricted model only; Candidate B is not confirmed.")


if __name__ == "__main__":
    main()
