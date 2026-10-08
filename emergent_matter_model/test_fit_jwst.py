"""Unit and integration tests for JWST high-redshift kinematics evaluation engine."""

from pathlib import Path
import pytest

try:
    from fit_jwst import (
        A0_ZERO_SI,
        critical_acceleration_z,
        evaluate_high_z_kinematics,
        hubble_expansion_factor,
        load_high_z_catalog,
        predict_flat_velocity_kms,
    )
except ImportError:
    from emergent_matter_model.fit_jwst import (
        A0_ZERO_SI,
        critical_acceleration_z,
        evaluate_high_z_kinematics,
        hubble_expansion_factor,
        load_high_z_catalog,
        predict_flat_velocity_kms,
    )


@pytest.fixture
def jwst_catalog_path() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "synthetic" / "jwst_kinematics_synthetic.csv"


class TestCosmologicalEvolution:
    def test_hubble_factor_at_z_zero(self):
        # E(0) = sqrt(0.315 + 0.685) = 1.0
        e0 = hubble_expansion_factor(0.0)
        assert e0 == pytest.approx(1.0, rel=1e-5)

    def test_hubble_factor_monotonically_increases(self):
        e1 = hubble_expansion_factor(1.0)
        e2 = hubble_expansion_factor(2.0)
        e4 = hubble_expansion_factor(4.0)
        assert 1.0 < e1 < e2 < e4

    def test_negative_redshift_raises(self):
        with pytest.raises(ValueError):
            hubble_expansion_factor(-0.5)

    def test_critical_acceleration_at_z_zero(self):
        a0 = critical_acceleration_z(0.0)
        assert a0 == pytest.approx(A0_ZERO_SI, rel=1e-5)

    def test_critical_acceleration_at_high_z(self):
        # At z=2, E(z) ~ 3.35 with default parameters
        a0_z2 = critical_acceleration_z(2.0)
        assert a0_z2 > 2.5 * A0_ZERO_SI


class TestBTFRPrediction:
    def test_predict_flat_velocity_scaling(self):
        # M = 1e10 M_sun, a0 = 1.2e-10
        v1 = predict_flat_velocity_kms(1.0e10, A0_ZERO_SI)
        assert 100.0 < v1 < 160.0

        # When M is quadrupled, V_flat must increase by factor of 4^(1/4) = sqrt(2) ~ 1.4142
        v4 = predict_flat_velocity_kms(4.0e10, A0_ZERO_SI)
        assert v4 / v1 == pytest.approx(2.0 ** 0.5, rel=1e-4)


class TestJWSTCatalogAndEvaluation:
    def test_load_catalog(self, jwst_catalog_path: Path):
        catalog = load_high_z_catalog(jwst_catalog_path)
        assert len(catalog) == 10
        assert catalog[0].galaxy_id == "SYN-Z01"
        assert catalog[0].redshift_z == pytest.approx(1.52)
        assert all(g.v_rot_kms > 0 for g in catalog)
        assert all(g.v_rot_err_kms > 0 for g in catalog)

    def test_evaluate_kinematics_evolving_favored(self, jwst_catalog_path: Path):
        catalog = load_high_z_catalog(jwst_catalog_path)
        report = evaluate_high_z_kinematics(catalog)
        assert report["n_galaxies"] == 10
        # Evolving a0(z) must decisively outperform static a0
        assert report["models"]["evolving_a0_z"]["chi2"] < report["models"]["static_a0"]["chi2"]
        assert report["model_comparison"]["delta_bic"] < -50.0
        assert "decisively favored" in report["model_comparison"]["verdict"]
