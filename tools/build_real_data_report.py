"""Generate manuscript numbers from fresh versioned artifacts, never historical JSON."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def main():
    results = ROOT / "results" / "real_data_v1"
    source = results / "sparc_profile_validation.json"
    data = json.loads(source.read_text())
    gauntlet = json.loads((results / "gauntlet.json").read_text())
    if not data.get("complete") or not data.get("numerically_verified"):
        raise RuntimeError("Cannot publish an incomplete or numerically unverified profile run")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if gauntlet.get("sparc_profile", {}).get("sha256") != digest:
        raise RuntimeError("Gauntlet must be refreshed to reference this exact SPARC run")
    influence = json.loads((results / "sparc_influence_crosscheck.json").read_text())
    if influence["parent_sha256"] != digest or not influence["matches_profile_subtraction"]:
        raise RuntimeError("Influence cross-check must match the verified profile artifact")
    lines = ["## Fresh computed results", "", "All acceleration scales below are in 10^-10 m/s².",
             "Grid minima are not continuous maximum-likelihood estimates. Intervals are conditional",
             "ΔQ = 1 grid crossings, not calibrated significance intervals.", "",
             "| Sample | Galaxies / points | Grid minimum | ΔQ=1 interval | Descriptive reduced χ² |",
             "|---|---:|---:|---|---:|"]
    tex = [r"\begin{center}\begin{tabular}{lrrr}\toprule",
           r"Sample & $N_g$ & $a_0/(10^{-10}\,\mathrm{m\,s^{-2}})$ & $\chi^2/(N-k)$\\\midrule"]
    fig, ax = plt.subplots(figsize=(7, 4))
    for name, sample in data["samples"].items():
        a = sample["a0_grid_minimum"] / 1e-10
        interval = ["not bracketed" if x is None else f"{x / 1e-10:.3f}"
                    for x in sample["delta_Q_1_interval"]]
        reduced = sample["chi2_reduced_descriptive"]
        label = name.replace("_", " ")
        lines.append(f"| {label} | {sample['n_galaxies']} / {sample['n_points']} | "
                     f"{a:.3f} | {' to '.join(interval)} | {reduced:.3f} |")
        tex.append(f"{label} & {sample['n_galaxies']} & {a:.3f} & {reduced:.3f}" + r"\\")
        if name in ("all", "gas_dominated", "star_bulgeless", "star_bulge"):
            q = sample["objective_grid"]
            ax.plot([x/1e-10 for x in data["a0_grid"]], [x-min(q) for x in q], label=label)
    tex += [r"\bottomrule\end{tabular}\end{center}",
            "These are grid minima from fresh penalized profiles, not Bayesian posterior estimates.",
            "The descriptive reduced chi-square values expose substantial fit inadequacy."]
    lines += ["", "### Fixed stellar reference (distances/inclinations fixed)", ""]
    for name, item in data["fixed_stellar_baselines"].items():
        lines.append(f"- {name}: a₀ = {item['a0']/1e-10:.4f}; data χ² = {item['chi2']:.2f}.")
    ref = data["fixed_stellar_baselines"]["rar_exponential"]["a0"]/1e-10
    tex.append(f"The fixed stellar RAR reference gives $a_0={ref:.4f}\\times10^{{-10}}$ m s$^{{-2}}$.")
    lines += ["", "### Fixed-horizon objective differences", "",
              "These ΔQ values include nuisance penalties; they are not ΔBIC or discovery significances."]
    conversion = 299792458.0 * 1000 / 3.085677581e22 / (2 * math.pi)
    horizon = {
        label: {"H0": mean, "quoted_uncertainty": error, "a0_m_s2": conversion*mean,
                "a0_uncertainty_m_s2": conversion*error, "source": url}
        for label, mean, error, url in (
            ("Planck base LCDM", 67.4, .5, "https://arxiv.org/abs/1807.06209"),
            ("SH0ES Cepheid-SN", 73.04, 1.04, "https://arxiv.org/abs/2112.04510"))
    }
    (results / "horizon_reference_propagation.json").write_text(
        json.dumps({"method": "linear propagation sigma(a0)=c sigma(H0)/(2pi)",
                    "H0_units": "km/s/Mpc", "acceleration_units": "m/s^2",
                    "not_combined_with_SPARC_profiles": True, "references": horizon},
                   indent=2, allow_nan=False)+"\n", encoding="utf-8")
    for label, reference in horizon.items():
        lines.append(f"- {label}: a₀,H = {reference['a0_m_s2']/1e-10:.5f} ± "
                     f"{reference['a0_uncertainty_m_s2']/1e-10:.5f} from quoted external "
                     f"H₀ uncertainty ([source]({reference['source']})).")
        tex.append(f"{label}: externally propagated $a_{{0,H}}="
                   f"({reference['a0_m_s2']/1e-10:.5f}\\pm "
                   f"{reference['a0_uncertainty_m_s2']/1e-10:.5f})"
                   r"\times10^{-10}$ m s$^{-2}$.")
    lines.append("The grid comparisons use the historical rounded SH0ES reference 73.0, "
                 "not 73.04. These external errors are propagated separately, not integrated "
                 "into a joint SPARC likelihood or used to claim a detection significance.")
    for name, sample in data["samples"].items():
        if "fixed_horizon_delta_Q" in sample:
            lines.append(f"- {name}: {sample['fixed_horizon_delta_Q']} (H₀ in km/s/Mpc).")
    lines += ["", "### Robustness checks", ""]
    for name, sample in data["sensitivity"].items():
        lines.append(f"- {name}: grid minimum {sample['a0_grid_minimum']/1e-10:.3f}; "
                     f"descriptive reduced χ² {sample['chi2_reduced_descriptive']:.3f}; "
                     f"grid-edge minimum: {sample['at_grid_edge']} (edge minima are not resolved estimates).")
    original_deep = data["samples"]["star_bulge_deep"]["a0_grid_minimum"]/1e-10
    excluded_deep = influence["a0_grid_minimum"]/1e-10
    lines += ["", "### Independently checked single-galaxy influence", "",
              (f"Removing **{influence['removed']}** changes the deep-bulge sample's grid optimum "
              f"from **{original_deep:.2f} to {excluded_deep:.2f}**. An independent full-grid "
              f"refit of the remaining {influence['n_galaxies']} galaxies / "
              f"{influence['n_points']} observed points reproduces the subtraction result."),
              ("This is an exploratory influence diagnostic, not a reason to discard that galaxy. "
              "It prevents describing the deep-bulge excess as a robust population discovery.")]
    tex.append(f"Removing {influence['removed']} shifts the deep-bulge grid optimum from "
               f"${original_deep:.2f}$ to ${excluded_deep:.2f}$ in units of "
               r"$10^{-10}$ m s$^{-2}$. "
               f"An independent full-grid refit of {influence['n_galaxies']} galaxies and "
               f"{influence['n_points']} points confirms this influence diagnostic. "
               "This does not justify excluding the galaxy or claiming nonuniversality.")
    lines += ["", "### Other-law nuisance profiles", "",
              "Same observed sample and nuisance constraints; these are not unpenalized BIC fits."]
    for name, sample in data["other_law_profiles"].items():
        lines.append(f"- {name}: a₀ grid minimum {sample['a0_grid_minimum']/1e-10:.3f}; "
                     f"Q = {sample['minimum_Q']:.3f}; descriptive reduced χ² "
                     f"{sample['chi2_reduced_descriptive']:.3f}; grid edge {sample['at_grid_edge']}.")
    for name, sample in data["samples"].items():
        lines.append(f"- {name} leave-one-galaxy-out grid range: "
                     f"{[x/1e-10 for x in sample['loo_a0_range']] }.")
    reverse = data["reverse_scan_max_total_Q_difference"]
    lines += [f"- Maximum forward/reverse total-objective difference: {reverse:.6g}.",
              f"- Scan-order differences below 0.1 objective units: {reverse < .1}. If false, intervals need additional numerical refinement.", "",
              "A scan-direction check tests numerical consistency, not statistical coverage.",
              "No full Bayesian marginalization, raw tracking-data fit or",
              "calibrated discovery significance is supplied. External H₀ uncertainty is not integrated",
              "into these profiles; the horizon comparisons are conditional on reference H₀ values.", ""]
    tex += [f"The maximum forward/reverse total-objective difference is {reverse:.6g}.",
            r"Full numerical profiles, conditional crossings, influence ranges and sensitivity variants are in \texttt{docs/SPARC\_FRESH\_RESULTS.md} and the JSON artifact.",
            r"No $\Delta\mathrm{BIC}$ or calibrated discovery significance is asserted. External $H_0$ uncertainty is not integrated in these profiles.",
            r"\begin{figure}[ht]\centering\includegraphics[width=.85\linewidth]{figures/sparc_fresh_profiles.png}",
            r"\caption{Fresh penalized objective profiles. The plotted differences are not discovery significances.}\end{figure}"]
    ax.set(xlabel="a₀ / 10⁻¹⁰ m s⁻²", ylabel="ΔQ (penalized objective)", ylim=(0, 25))
    ax.legend()
    fig.tight_layout()
    fig.savefig(ROOT / "paper" / "figures" / "sparc_fresh_profiles.png", dpi=160)
    plt.close(fig)
    lines += [f"Source SHA-256: `{hashlib.sha256(source.read_bytes()).hexdigest()}`."]
    (ROOT / "docs" / "SPARC_FRESH_RESULTS.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    (ROOT / "paper" / "sparc_horizon_results.tex").write_text("\n".join(tex)+"\n", encoding="utf-8")
    audit = ["# Executed gauntlet results", "", "| Case | Status | Source retrieval | Remaining blocker |",
             "|---|---|---|---|"]
    for case in gauntlet["cases"]:
        audit.append(f"| {case['id']} {case['name']} | {case['status']} | "
                     f"{'retrieved' if case['source_retrieved'] else 'failed'} | {case['blocker']} |")
    audit += ["", "Source/abstract retrieval is not ingestion of a measurement table.", "",
              f"- Authenticated SPARC: {gauntlet['sparc']['galaxies']} galaxies and {gauntlet['sparc']['points']} selected points."]
    if "pantheon_observed_summary" in gauntlet:
        p = gauntlet["pantheon_observed_summary"]
        audit.append(f"- Official Pantheon+ table: {p['rows']} measurement rows; zHD {p['zHD_min']}–{p['zHD_max']}; no covariance likelihood fitted.")
    if "desi_transcription_check" in gauntlet:
        check = gauntlet["desi_transcription_check"]
        audit.append(f"- Local DESI table matches the retrieved means to two-decimal rounding: {check['consistent_with_two_decimal_rounding']}; maximum absolute difference {check['max_absolute_rounding_difference']:.6f}.")
    if "desi_summary" in gauntlet:
        d = gauntlet["desi_summary"]
        audit.append(f"- Version-pinned DESI likelihood distribution: {d['measurements']} means and {d['covariance_shape']} positive-definite covariance; no EMRF cosmological likelihood fitted.")
    if "desi_baseline" in gauntlet:
        baseline = gauntlet["desi_baseline"]
        audit.append(f"- Actual flat-ΛCDM BAO baseline using the full covariance: Ωm = "
                     f"{baseline['omega_m']:.5f}, c/(H₀ rd) = {baseline['c_over_H0_rd']:.4f}, "
                     f"χ² = {baseline['chi2']:.4f} for {baseline['degrees_of_freedom']} nominal "
                     "degrees of freedom. This is a baseline fit, not an EMRF prediction or success.")
    audit += ["- Solar high-acceleration correction is evaluated algebraically only; no mismatched Cassini bound is used to claim exclusion."]
    for case in gauntlet["cases"]:
        if not case["source_retrieved"]:
            audit.append(f"- {case['id']} source retrieval failed: {case['retrieval_error']}. "
                         "The source was not treated as successfully retrieved.")
    audit += ["", "See [artifact](../results/real_data_v1/gauntlet.json) for URLs, hashes and errors."]
    followup = ROOT / "results" / "real_data_followup" / "pantheon_baseline.json"
    if followup.exists():
        audit.insert(1, "\n> Follow-up: the full Pantheon+ covariance has now been "
                     "authenticated and fitted as a non-EMRF baseline. This table records "
                     "the earlier run. See the [current top-down audit]"
                     "(EMRF_TOP_DOWN_AUDIT_2026-10-08.md) and [new result]"
                     "(../results/real_data_followup/pantheon_baseline.json).\n")
    (ROOT / "docs" / "REAL_DATA_GAUNTLET_RESULTS.md").write_text("\n".join(audit)+"\n", encoding="utf-8")
    print("Generated manuscript supplement, profile figure and gauntlet summary.")


if __name__ == "__main__":
    main()
