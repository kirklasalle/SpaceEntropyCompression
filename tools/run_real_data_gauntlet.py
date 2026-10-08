"""Real-data evidence inventory: computation, source retrieval and explicit blockers."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize_scalar

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from emergent_matter_model.data_provenance import verify_observation_file
from emergent_matter_model.fetch_real_data import MANIFEST, fetch_sparc
from emergent_matter_model.sparc_real_analysis import a0_horizon, load_sparc

CASES = [
    ("R01", "Sgr A* S-stars", "https://arxiv.org/abs/2004.07187",
     "GRAVITY Collaboration (2020), Schwarzschild precession in S2",
     "Astrometric/RV time-series ingestion and a derived EMRF orbital deviation are absent."),
    ("R02", "Solar System", "https://arxiv.org/abs/1402.6950",
     "Hees et al. (2014), constraints on MOND using Cassini radio tracking",
     "Cassini external-field quadrupole constraint is not a direct constant-acceleration bound; no matching ephemeris likelihood."),
    ("R03", "SPARC", "https://astroweb.case.edu/SPARC/", "Lelli et al. (2016), SPARC",
     "Conditional profiles do not calibrate discovery significance; unknown radial covariance remains."),
    ("R04", "SLACS lensing", "https://arxiv.org/abs/0805.1931",
     "Bolton et al. (2008), SLACS V: full ACS strong-lens sample",
     "No derived EMRF lensing potential and joint stellar-dynamical likelihood."),
    ("R05", "Bullet Cluster", "https://arxiv.org/abs/astro-ph/0608407",
     "Clowe et al. (2006), direct empirical proof of dark matter",
     "No absolute EMRF shear/convergence prediction or calibrated aligned-map likelihood."),
    ("R06", "High-z disk kinematics", "https://almascience.nrao.edu/aq/",
     "ALMA Science Archive",
     "No frozen resolved-disk sample with pressure/beam/inclination likelihood; no new fit claimed."),
    ("R07", "GW170817 propagation", "https://arxiv.org/abs/1710.05834",
     "LIGO/Virgo et al. (2017), GW170817 and GRB 170817A",
     "No EMRF-derived tensor/photon propagation; imposed luminal speed is not evidence."),
    ("R08", "Gaia wide binaries", "https://arxiv.org/abs/2101.05282",
     "El-Badry et al. (2021), million-binary Gaia eDR3 catalogue",
     "Pair-level contamination, projection and external-field likelihood not implemented; no synthetic forward-model fallback."),
    ("R09", "Late expansion", "https://github.com/PantheonPlusSH0ES/DataRelease",
     "Pantheon+ public data release; Brout et al. (2022)",
     "Authentic SN measurements do not supply EMRF expansion dynamics; full covariance/calibration fit not performed."),
    ("R10", "CMB", "https://pla.esac.esa.int/",
     "ESA Planck Legacy Archive",
     "No EMRF perturbation spectrum; downloading spectra cannot fix copied-peak circularity."),
    ("H01", "Quantum matter", "https://physics.nist.gov/cuu/Constants/",
     "NIST CODATA reference constants", "Input mass is normalized back into the answer; no independent mass prediction."),
    ("H02", "Black-hole entropy", "https://doi.org/10.1103/PhysRevD.7.2333",
     "Bekenstein (1973), Black holes and entropy", "Quarter-area coefficient assumed, not independently derived; no direct horizon-entropy data."),
    ("H03", "JWST cosmic dawn", "https://arxiv.org/abs/2405.18485",
     "Carniani et al. (2024), two luminous galaxies at z about 14",
     "No assembly/population prediction; observed redshifts do not validate a chosen collapse time."),
]
PANTHEON = ("https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/"
            "c447f0fea703fcd0fff57de5000947b5ca81286b/Pantheon%2B_Data/"
            "4_DISTANCES_AND_COVAR/Pantheon%2BSH0ES.dat")


def desi_baseline(cache):
    """Fit a flat LCDM distance baseline with a free c/(H0 rd), not EMRF."""
    means = np.genfromtxt(cache / "desi_2024_gaussian_bao_ALL_GCcomb_mean.txt",
                          dtype=None, encoding="utf-8")
    covariance = np.loadtxt(cache / "desi_2024_gaussian_bao_ALL_GCcomb_cov.txt")
    if (covariance.shape != (len(means), len(means))
            or not np.all(np.isfinite(covariance))
            or not np.allclose(covariance, covariance.T, rtol=1e-12, atol=1e-12)):
        raise ValueError("Invalid DESI covariance")
    chol = np.linalg.cholesky(covariance)
    observed = np.array([row[1] for row in means], dtype=float)
    whitened = np.linalg.solve(chol, observed)

    def evaluate(omega_m):
        prediction = []
        for z, _, observable in means:
            inv_e = lambda redshift: 1 / np.sqrt(omega_m*(1+redshift)**3 + 1-omega_m)
            dm = quad(inv_e, 0, z, epsabs=1e-10)[0]
            dh = inv_e(z)
            values = {"DM_over_rs": dm, "DH_over_rs": dh,
                      "DV_over_rs": (z*dm**2*dh)**(1/3)}
            if observable not in values:
                raise ValueError(f"Unknown BAO observable {observable}")
            prediction.append(values[observable])
        vector = np.linalg.solve(chol, prediction)
        scale = float(vector @ whitened / (vector @ vector))
        residual = whitened - scale*vector
        return float(residual @ residual), scale

    fit = minimize_scalar(lambda om: evaluate(om)[0], bounds=(.05, .6), method="bounded",
                          options={"xatol": 1e-10})
    if not fit.success or not np.isfinite(fit.fun):
        raise RuntimeError("DESI baseline optimizer failed")
    chi2, scale = evaluate(fit.x)
    minus2log_l = chi2 + 2*np.log(np.diag(chol)).sum() + len(means)*np.log(2*np.pi)
    return {"model": "flat LCDM with free c/(H0 rd), negligible late-time radiation",
            "evidence_grade": "baseline_only_not_EMRF", "omega_m": float(fit.x),
            "c_over_H0_rd": scale, "chi2": chi2, "n": len(means), "k": 2,
            "degrees_of_freedom": len(means)-2, "covariance_used": True,
            "minus2log_likelihood": float(minus2log_l),
            "BIC": float(minus2log_l + 2*np.log(len(means))),
            "BIC_note": "single Gaussian-baseline score; no EMRF comparator or preference",
            "boundary_minimum": bool(fit.x < .0501 or fit.x > .5999)}


def retrieve(url, path, citation, kind):
    path.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "EMRF-real-data-audit/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read()
        final_url = response.geturl()
    if not raw:
        raise ValueError("Empty source response")
    path.write_bytes(raw)
    return {"url": url, "resolved_url": final_url, "citation": citation, "kind": kind,
            "file": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw), "retrieved_utc": datetime.now(timezone.utc).isoformat()}


def main():
    cache = ROOT / "data" / "external" / "real_data_v1"
    out = ROOT / "results" / "real_data_v1"
    out.mkdir(parents=True, exist_ok=True)
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh-profile-only", action="store_true")
    args = parser.parse_args()
    if args.refresh_profile_only:
        path = out / "gauntlet.json"
        result = json.loads(path.read_text())
        for entry in result["source_records"]:
            if hashlib.sha256((ROOT / entry["file"]).read_bytes()).hexdigest() != entry["sha256"]:
                raise ValueError("Cached gauntlet source bytes changed")
        profile_path = out / "sparc_profile_validation.json"
        profile = json.loads(profile_path.read_text())
        if not profile.get("complete") or not profile.get("numerically_verified"):
            raise ValueError("SPARC profile is incomplete or failed numerical verification")
        result["desi_baseline"] = desi_baseline(cache)
        result["sparc_profile"] = {"path": str(profile_path.relative_to(ROOT)),
                                   "sha256": hashlib.sha256(profile_path.read_bytes()).hexdigest(),
                                   "complete": True}
        result["cases"][2]["status"] = "conditional_model_comparison"
        result["profile_link_updated_utc"] = datetime.now(timezone.utc).isoformat()
        result["source_sha256"][str(Path(__file__).relative_to(ROOT))] = hashlib.sha256(
            Path(__file__).read_bytes()).hexdigest()
        path.write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
        print("Verified cached source hashes and linked completed fresh SPARC profiles")
        return
    fetch_sparc()
    manifest = json.loads(MANIFEST.read_text())
    for record in manifest.values():
        verify_observation_file(ROOT / record["file"], record)
    gals = load_sparc()
    result = {"generated_utc": datetime.now(timezone.utc).isoformat(),
              "python": platform.python_version(), "cases": [], "source_records": [],
              "scope": "real-data retrieval and computations; scientific blockers are not passes",
              "sparc": {"galaxies": len(gals), "points": sum(g.n for g in gals),
                        "raw_manifest": manifest},
              "solar_algebra_only": {"a0": a0_horizon(67.4),
                  "constant_high_acceleration_limit_m_s2": a0_horizon(67.4)/2,
                  "empirical_exclusion": False,
                  "reason": "No independently verified constant-acceleration constraint applied"}}
    for case_id, name, url, citation, blocker in CASES:
        case = {"id": case_id, "name": name, "source_url": url, "citation": citation,
                "status": "not_yet_testable", "blocker": blocker,
                "source_kind": "reference_or_archive_page_not_measurement_table"}
        if case_id == "R03":
            case["status"] = "observations_verified"
            case["source_kind"] = "official_measurement_archive"
        try:
            source = retrieve(url, cache / f"{case_id}_source.html", citation,
                              "reference_or_archive_page_not_measurement_table")
            result["source_records"].append(source)
            case["source_retrieved"] = True
        except (OSError, ValueError) as error:
            case["source_retrieved"] = False
            case["retrieval_error"] = str(error)
        result["cases"].append(case)
    try:
        entry = retrieve(PANTHEON, cache / "Pantheon+SH0ES.dat",
                         "PantheonPlusSH0ES/DataRelease official collaboration repository",
                         "published_measurement_table")
        verify_observation_file(cache / "Pantheon+SH0ES.dat", entry)
        table = np.genfromtxt(cache / "Pantheon+SH0ES.dat", names=True, dtype=None, encoding="utf-8")
        if "zHD" not in table.dtype.names or len(table) < 1000:
            raise ValueError("Unexpected Pantheon+ table schema")
        result["pantheon_observed_summary"] = {
            "rows": len(table), "zHD_min": float(np.min(table["zHD"])),
            "zHD_max": float(np.max(table["zHD"])),
            "likelihood_evaluated": False, "source": entry,
            "note": "Rows are observations, not necessarily unique supernovae; covariance fit absent"}
        result["source_records"].append(entry)
    except (OSError, ValueError) as error:
        result["pantheon_retrieval_error"] = str(error)
    try:
        base = ("https://raw.githubusercontent.com/CobayaSampler/bao_data/"
                "bb0c1c9009dc76d1391300e169e8df38fd1096db/")
        for suffix in ("mean", "cov"):
            name = f"desi_2024_gaussian_bao_ALL_GCcomb_{suffix}.txt"
            entry = retrieve(base + name, cache / name,
                             "DESI DR1 likelihood data distributed by CobayaSampler/bao_data",
                             "published_likelihood_distribution_not_raw_tracking")
            result["source_records"].append(entry)
        means = np.genfromtxt(cache / "desi_2024_gaussian_bao_ALL_GCcomb_mean.txt",
                              dtype=None, encoding="utf-8")
        covariance = np.loadtxt(cache / "desi_2024_gaussian_bao_ALL_GCcomb_cov.txt")
        np.linalg.cholesky(covariance)
        if covariance.shape != (len(means), len(means)):
            raise ValueError("DESI covariance dimension mismatch")
        local_path = ROOT / "data" / "cosmology" / "desi_2024_bao.csv"
        with local_path.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(line for line in handle if not line.startswith("#")))
        if len(rows) != len(means):
            raise ValueError("Local DESI transcription row count differs")
        residuals = []
        for row, official in zip(rows, means):
            if (abs(float(row["z_eff"]) - float(official[0])) > 1e-6
                    or row["observable"].replace("rd", "rs") != official[2]):
                raise ValueError("DESI observable identity differs")
            residuals.append(abs(float(row["value"]) - float(official[1])))
        result["desi_transcription_check"] = {
            "max_absolute_rounding_difference": max(residuals),
            "consistent_with_two_decimal_rounding": max(residuals) <= .0051,
            "local_sha256": hashlib.sha256(local_path.read_bytes()).hexdigest()}
        result["desi_summary"] = {"measurements": len(means),
                                  "covariance_shape": list(covariance.shape),
                                  "positive_definite": True, "likelihood_evaluated": False,
                                  "source_level": "version-pinned public likelihood distribution"}
        result["desi_baseline"] = desi_baseline(cache)
    except (OSError, ValueError, np.linalg.LinAlgError) as error:
        result["desi_retrieval_error"] = str(error)
    sparc_result = out / "sparc_profile_validation.json"
    if sparc_result.exists():
        profile = json.loads(sparc_result.read_text())
        result["sparc_profile"] = {"path": str(sparc_result.relative_to(ROOT)),
                                   "sha256": hashlib.sha256(sparc_result.read_bytes()).hexdigest(),
                                   "complete": profile.get("complete", False)}
        if profile.get("complete") and profile.get("numerically_verified"):
            result["cases"][2]["status"] = "conditional_model_comparison"
    result["source_sha256"] = {str(Path(__file__).relative_to(ROOT)):
                               hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (out / "gauntlet.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps({"case_count": len(result["cases"]), "SPARC": result["sparc"]["galaxies"],
                      "Pantheon": result.get("pantheon_observed_summary", {}).get("rows"),
                      "retrieval_errors": [c["id"] for c in result["cases"] if not c["source_retrieved"]]}))


if __name__ == "__main__":
    main()
