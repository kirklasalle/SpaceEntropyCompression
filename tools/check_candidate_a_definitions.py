"""Analytic benchmark diagnostics for Candidate A, not an empirical gravity test.

This compares standard GR definitions on stipulated exact backgrounds. It does
not implement a new C field or use generated values as observational evidence.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from emergent_matter_model.physics_baseline import C_LIGHT, G, kretschmann_invariant


def finite_positive(value: float, name: str) -> None:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")


def perfect_fluid_curvatures(energy_density: float, pressure: float,
                             cosmological_constant: float = 0.) -> dict:
    """Units: epsilon and p in J/m^3, Lambda in m^-2; observer comoving."""
    if not all(math.isfinite(x) for x in (energy_density, pressure, cosmological_constant)):
        raise ValueError("Stress-energy and cosmological constant must be finite")
    factor = 8*math.pi*G/C_LIGHT**4
    return {
        "ricci_scalar_m_minus2": 4*cosmological_constant + factor*(energy_density-3*pressure),
        "einstein_projection_minus_lambda_m_minus2": factor*energy_density,
        "ricci_timelike_projection_m_minus2":
            .5*factor*(energy_density+3*pressure)-cosmological_constant,
        "observer_energy_mass_density_kg_m3": energy_density/C_LIGHT**2,
    }


def schwarzschild_diagnostics(mass_kg: float, areal_radius_m: float) -> dict:
    finite_positive(mass_kg, "mass")
    finite_positive(areal_radius_m, "areal radius")
    rs = 2*G*mass_kg/C_LIGHT**2
    if areal_radius_m <= rs:
        raise ValueError("Static exterior Brown-York benchmark requires r > r_s")
    f = 1-rs/areal_radius_m
    k = float(kretschmann_invariant(areal_radius_m, mass_kg))
    return {
        "mass_input_kg": mass_kg,
        "areal_radius_m": areal_radius_m,
        "r_over_rs": areal_radius_m/rs,
        "kretschmann_m_minus4": k,
        "tidal_curvature_sqrtK_m_minus2": math.sqrt(k),
        "ricci_scalar_m_minus2": 0.,
        "local_stress_energy_mass_density_kg_m3": 0.,
        "misner_sharp_mass_kg": C_LIGHT**2*areal_radius_m*(1-f)/(2*G),
        # Rationalized form avoids cancellation for r >> r_s.
        "brown_york_energy_over_c2_kg": 2*mass_kg/(1+math.sqrt(f)),
        "mass_from_K_and_areal_radius_kg":
            C_LIGHT**2*areal_radius_m**3*math.sqrt(k/48)/G,
    }


def normalization_for_projection(c0: float) -> float:
    finite_positive(c0, "C0")
    return C_LIGHT**2*c0/(8*math.pi*G)


def build_report() -> dict:
    epsilon = 9.e10
    dust = perfect_fluid_curvatures(epsilon, 0.)
    radiation = perfect_fluid_curvatures(epsilon, epsilon/3)
    c0 = 1.e-20
    k_scale = normalization_for_projection(c0)
    projected = dust["einstein_projection_minus_lambda_m_minus2"]
    mapped = k_scale*(projected/c0)
    if not math.isclose(mapped, epsilon/C_LIGHT**2, rel_tol=1e-13):
        raise ArithmeticError("Einstein-projection normalization identity failed")
    mass = 1.98847e30
    rs = 2*G*mass/C_LIGHT**2
    rows = [schwarzschild_diagnostics(mass, rs*x) for x in (1.01, 2., 10., 1000.)]
    equal_tidal = [schwarzschild_diagnostics(mass, 10*rs),
                   schwarzschild_diagnostics(8*mass, 20*rs)]
    if not math.isclose(equal_tidal[0]["kretschmann_m_minus4"],
                        equal_tidal[1]["kretschmann_m_minus4"], rel_tol=1e-13):
        raise ArithmeticError("Equal-curvature counterexample failed")
    return {
        "evidence_kind": "exact_background_algebra_not_observations",
        "physical_model_implemented": False,
        "author_selected_specific_functional": False,
        "assumptions": [
            "Four-dimensional GR, signature (-+++), unit timelike n.n=-1, x0=ct",
            "Einstein equation includes explicit cosmological constant",
            "Perfect-fluid probes use the comoving observer",
            "Schwarzschild probes have Lambda=0, spherical symmetry and r > r_s",
            "Brown-York uses the static slice, round boundary, flat reference and positive convention",
            "Mass/radius and fluid values are stipulated mathematical benchmarks, not measurements",
        ],
        "perfect_fluid_same_energy_density": {
            "input_epsilon_J_m3": epsilon, "dust": dust, "radiation": radiation,
            "conclusion": "Ricci scalar alone misses nonzero trace-free radiation energy",
        },
        "einstein_projection_mapping": {
            "alpha": 1., "C0_m_minus2": c0, "k_kg_m3": k_scale,
            "mapped_density_kg_m3": mapped,
            "meaning": "GR energy-density identity; not baryonic rest density or emergent-matter proof",
        },
        "vacuum_and_quasilocal": rows,
        "same_K_different_mass_and_radius": equal_tidal,
        "conclusions": [
            "sqrt(K)>0 can coexist with zero local material density",
            "Scalar K alone does not determine enclosed mass without further geometric information",
            "Brown-York and Misner-Sharp are different specified regional quantities",
            "Conventional curvature data do not determine a thermal entropy or heating rate alone",
            "These statements do not disprove every compression functional",
        ],
        "source_sha256": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (Path(__file__), ROOT / "emergent_matter_model" / "physics_baseline.py")
        },
    }


def main() -> None:
    report = build_report()
    destination = ROOT / "results" / "candidate_a_definition_checks.json"
    destination.write_text(json.dumps(report, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(f"Saved {destination}: exact-background diagnostics, not empirical evidence")
    print("Einstein projection: alpha=1 with fixed k/C0 reproduces epsilon/c^2.")
    print("Ricci radiation counterexample and nonzero-curvature vacuum checks completed.")


if __name__ == "__main__":
    main()
