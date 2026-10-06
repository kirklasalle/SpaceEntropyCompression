"""Unit and integration tests for SPARC galaxy rotation curve evaluation engine."""

from pathlib import Path
import pytest

try:
    from fit_sparc import (
        A0_CRITICAL,
        SPARCDataPoint,
        compute_baryonic_velocity,
        compute_emrf_entropic_velocity,
        compute_rar_velocity,
        evaluate_multi_sparc,
        evaluate_sparc_galaxy,
        load_sparc_galaxy,
        optimize_sparc_galaxy,
        get_all_sparc_galaxy_names,
    )
    from fetch_sparc import list_available_galaxies, validate_catalog, validate_sparc_table
except ImportError:
    from emergent_matter_model.fit_sparc import (
        A0_CRITICAL,
        SPARCDataPoint,
        compute_baryonic_velocity,
        compute_emrf_entropic_velocity,
        compute_rar_velocity,
        evaluate_multi_sparc,
        evaluate_sparc_galaxy,
        load_sparc_galaxy,
        optimize_sparc_galaxy,
        get_all_sparc_galaxy_names,
    )
    from emergent_matter_model.fetch_sparc import list_available_galaxies, validate_catalog, validate_sparc_table


@pytest.fixture
def sparc_data_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "sparc"


class TestSPARCLoader:
    def test_load_sparc_galaxy_ngc6503(self, sparc_data_dir: Path):
        csv_path = sparc_data_dir / "ngc6503.csv"
        name, points = load_sparc_galaxy(csv_path)
        assert name == "NGC6503"
        assert len(points) == 28
        assert points[0].radius_kpc == pytest.approx(0.47)
        assert points[-1].radius_kpc == pytest.approx(21.62)
        assert all(p.v_obs_kms > 0 for p in points)
        assert all(p.v_obs_err_kms > 0 for p in points)

    def test_load_all_ten_galaxies(self, sparc_data_dir: Path):
        galaxies = [
            "ddo154", "ic2574", "ngc1560", "ngc2403", "ngc2841",
            "ngc2903", "ngc3198", "ngc6503", "ngc7331", "ugc2885"
        ]
        for gal in galaxies:
            csv_path = sparc_data_dir / f"{gal}.csv"
            name, points = load_sparc_galaxy(csv_path)
            assert name == gal.upper()
            assert len(points) >= 15

    def test_load_sparc_missing_file_raises(self, sparc_data_dir: Path):
        with pytest.raises(FileNotFoundError):
            load_sparc_galaxy(sparc_data_dir / "non_existent_galaxy.csv")


class TestCatalogValidation:
    def test_list_available_galaxies(self, sparc_data_dir: Path):
        galaxies = list_available_galaxies(sparc_data_dir)
        assert len(galaxies) >= 10
        assert "DDO154" in galaxies
        assert "UGC2885" in galaxies

    def test_validate_sparc_table_valid(self, sparc_data_dir: Path):
        res = validate_sparc_table(sparc_data_dir / "ddo154.csv")
        assert res["valid"] is True
        assert res["galaxy"] == "DDO154"
        assert res["n_points"] == 18

    def test_validate_catalog_total_points(self, sparc_data_dir: Path):
        results = validate_catalog(sparc_data_dir)
        assert len(results) >= 10
        total_pts = sum(r["n_points"] for r in results)
        assert total_pts >= 214


class TestVelocityFormulations:
    def test_baryonic_velocity_positive(self):
        pt = SPARCDataPoint(radius_kpc=5.0, v_obs_kms=100.0, v_obs_err_kms=3.0, v_gas_kms=30.0, v_disk_kms=70.0, v_bulge_kms=0.0)
        v_bar = compute_baryonic_velocity(pt)
        assert v_bar > 0.0
        # Check expected value: sqrt(30^2 + 0.5 * 70^2) = sqrt(900 + 2450) = sqrt(3350) ~ 57.88
        assert v_bar == pytest.approx(57.879, rel=1e-3)

    def test_rar_velocity_exceeds_baryons_in_weak_acceleration(self):
        v_bar = 40.0
        r_kpc = 20.0
        v_rar = compute_rar_velocity(v_bar, r_kpc, a0=A0_CRITICAL)
        assert v_rar > v_bar

    def test_emrf_entropic_velocity_exceeds_baryons(self):
        v_bar = 40.0
        r_kpc = 20.0
        v_emrf = compute_emrf_entropic_velocity(v_bar, r_kpc, a_entropy=A0_CRITICAL)
        assert v_emrf > v_bar

    def test_boundary_zero_radius_or_velocity(self):
        assert compute_rar_velocity(0.0, 10.0) == 0.0
        assert compute_rar_velocity(50.0, 0.0) == 0.0
        assert compute_emrf_entropic_velocity(0.0, 10.0) == 0.0
        assert compute_emrf_entropic_velocity(50.0, 0.0) == 0.0


class TestModelComparison:
    def test_evaluate_single_galaxy_ngc6503(self, sparc_data_dir: Path):
        csv_path = sparc_data_dir / "ngc6503.csv"
        rep = evaluate_sparc_galaxy(csv_path)
        assert rep["galaxy"] == "NGC6503"
        assert rep["n_points"] == 28
        assert rep["models"]["emrf_entropic"]["chi2"] < rep["models"]["newtonian_baryon"]["chi2"]
        assert rep["model_comparison"]["delta_bic_emrf_vs_newton"] < -100.0

    def test_evaluate_gas_dominated_dwarf_ddo154(self, sparc_data_dir: Path):
        csv_path = sparc_data_dir / "ddo154.csv"
        rep = evaluate_sparc_galaxy(csv_path)
        assert rep["galaxy"] == "DDO154"
        assert rep["n_points"] == 18
        # Newtonian fails severely even in gas-rich dwarf
        assert rep["models"]["emrf_entropic"]["chi2"] < rep["models"]["newtonian_baryon"]["chi2"]

    def test_evaluate_multi_sparc_all_ten_galaxies(self, sparc_data_dir: Path):
        base_dir = sparc_data_dir.parent.parent
        galaxies = get_all_sparc_galaxy_names(sparc_data_dir)
        rep = evaluate_multi_sparc(galaxies, base_dir)
        assert rep["n_galaxies"] >= 10
        assert rep["total_data_points"] >= 214
        assert rep["joint_comparison"]["delta_bic_emrf_vs_newton"] < -50000.0


class TestParameterOptimization:
    def test_optimize_sparc_galaxy_ngc6503(self, sparc_data_dir: Path):
        csv_path = sparc_data_dir / "ngc6503.csv"
        opt = optimize_sparc_galaxy(csv_path, fit_upsilon_disk=True)
        assert opt["galaxy"] == "NGC6503"
        assert 0.05 <= opt["best_upsilon_disk"] <= 2.0
        # Optimization must reduce or equal default chi2
        default_rep = evaluate_sparc_galaxy(csv_path)
        assert opt["optimized_chi2"] <= default_rep["models"]["emrf_entropic"]["chi2"] + 1e-3
        assert "scipy.optimize" in opt["optimization_method"] or "fallback" in opt["optimization_method"]

    def test_optimize_gas_dominated_dwarf_ddo154(self, sparc_data_dir: Path):
        csv_path = sparc_data_dir / "ddo154.csv"
        opt = optimize_sparc_galaxy(csv_path, fit_upsilon_disk=True)
        assert opt["best_upsilon_disk"] < 0.2  # Gas dominates, stellar M/L is near bottom
