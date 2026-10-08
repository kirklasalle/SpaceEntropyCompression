"""Check algebraic identities in historical horizon demos, not empirical validation."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from emergent_matter_model.black_hole_horizon_entropy import (
    BlackHoleEntropyEngine,
)
from emergent_matter_model.quantum_vibrational_compression import (
    PARTICLE_BENCHMARKS,
    QuantumVibrationalEngine,
)


def audit() -> dict:
    engine = QuantumVibrationalEngine()
    particles = []
    for particle in PARTICLE_BENCHMARKS:
        reported, error = engine.compute_emergent_mass_integral(particle.rest_mass_kg)
        particles.append({
            "name": particle.name,
            "input_mass_kg": particle.rest_mass_kg,
            "reported_mass_kg": reported,
            "relative_difference": error,
            "interpretation": "input mass recovered by explicit normalization; not a prediction",
        })
    bh = BlackHoleEntropyEngine()
    mass = 4.297e6 * bh.M_SUN
    area = bh.horizon_area(mass)
    entropy = bh.bekenstein_hawking_entropy_exact(mass)
    sources = [
        ROOT / "emergent_matter_model" / "quantum_vibrational_compression.py",
        ROOT / "emergent_matter_model" / "black_hole_horizon_entropy.py",
        Path(__file__),
    ]
    return {
        "evidence_type": "software_algebra_diagnostics_not_observations",
        "empirical_validation": False,
        "quantum_mass_normalization": particles,
        "black_hole_identity": {
            "input_mass_msun": 4.297e6,
            "area_m2": area,
            "entropy_J_per_K": entropy,
            "coefficient_S_lP2_over_kBA": entropy * bh.planck_area / (bh.K_B * area),
            "interpretation": "quarter coefficient assumed in standard formula, not derived",
        },
        "temperature_equality": {
            "a_over_cH": 1.0,
            "hypothesis_a0_over_cH": 1.0 / (2 * math.pi),
            "interpretation": "equating the two temperatures cancels both 2pi factors",
        },
        "conditional_density_scaling": {
            "rho_power": "-3 alpha if C proportional to sqrt(K) proportional to r^-3",
            "V2_power": "2 - 3 alpha under stated spherical integral assumptions",
            "flat_speed_alpha": 2.0 / 3.0,
            "interpretation": "conditional algebra, not self-consistent field solution",
        },
        "source_sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sources
        },
    }


def main() -> None:
    result = audit()
    output = ROOT / "results" / "real_data_v1" / "compression_algebra.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Wrote {output}: algebra diagnostics only; no empirical validation.")


if __name__ == "__main__":
    main()
