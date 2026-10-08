"""Software checks of prescribed Bullet Cluster maps, not empirical confirmations."""

from pathlib import Path

import numpy as np

from bullet_cluster_stress_test import (
    OBSERVED_OFFSET_KPC,
    BulletClusterSimulation,
    evaluate_bullet_cluster_stress_test,
)


class TestBulletClusterDistributions:
    def test_simulation_grid_dimensions(self):
        """Simulation grid must be symmetric and of expected resolution."""
        sim = BulletClusterSimulation(grid_size_kpc=500.0, resolution=101)
        assert sim.X.shape == (101, 101)
        assert sim.Y.shape == (101, 101)
        assert sim.coords[0] == -500.0
        assert sim.coords[-1] == 500.0

    def test_baryonic_gas_dominates_total_mass(self):
        """Baryonic gas must account for majority (~80-85%) of baryonic mass."""
        sim = BulletClusterSimulation()
        sigma_gas, sigma_stars, sigma_tot = sim.generate_baryonic_distributions()
        gas_integral = np.sum(sigma_gas)
        stars_integral = np.sum(sigma_stars)
        gas_fraction = gas_integral / (gas_integral + stars_integral)
        assert 0.75 < gas_fraction < 0.95

    def test_entropy_field_shock_enhancement(self):
        """Entropy field must be significantly higher in the central collision/shock region."""
        sim = BulletClusterSimulation()
        entropy = sim.generate_entropy_field()
        # Outskirts (e.g. x = -400, y = 0) vs shock front (x = +40, y = 0)
        idx_outskirt = (sim.resolution // 2, 10)
        idx_shock = (sim.resolution // 2, sim.resolution // 2 + 5)
        assert entropy[idx_shock] > 4.0 * entropy[idx_outskirt]


class TestIllustrativePeakSeparation:
    def test_naive_mond_fails_to_displace_lensing_peaks(self):
        """Naive modified gravity without entropy coupling must keep lensing peaks on gas."""
        report = evaluate_bullet_cluster_stress_test()
        naive = report["naive_mond"]
        assert naive["matches_observation"] is None
        assert not naive["illustrative_offset_exceeds_100_kpc"]
        assert naive["offset_from_gas_kpc"] < 20.0

    def test_prescribed_entropy_weighting_displaces_illustrative_peak(self):
        """Preserve the historical numerical illustration without declaring validation."""
        report = evaluate_bullet_cluster_stress_test()
        emrf = report["emrf_entropy_compression"]
        assert emrf["matches_observation"] is None
        assert emrf["illustrative_offset_exceeds_100_kpc"]
        assert emrf["offset_from_gas_kpc"] >= 120.0
        # Check proximity to empirical Clowe et al. observed offset (~215 kpc)
        assert abs(emrf["offset_from_gas_kpc"] - OBSERVED_OFFSET_KPC) < 70.0

    def test_evidence_status_cannot_masquerade_as_a_physics_pass(self):
        report = evaluate_bullet_cluster_stress_test()
        assert report["evidence"]["observations_ingested"] is False
        assert report["evidence"]["entropy_production_computed"] is False
        assert report["evidence"]["entropy_is_an_input"] is True
        for key in ("naive_mond", "emrf_entropy_compression"):
            assert report[key]["status"].startswith("NOT TESTED")

    def test_interactive_collision_view_discloses_prescribed_geometry(self):
        path = Path(__file__).resolve().parents[1] / "tools" / "interactive_visualizer.html"
        text = path.read_text(encoding="utf-8")
        assert "static schematic, not an observed fit" in text
        assert "Historical demonstrations only" in text
        assert "Drawn contour, not predicted lensing" in text
