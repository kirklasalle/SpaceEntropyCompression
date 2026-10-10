from __future__ import annotations

import math

import astropy.units as u
import camb
import numpy as np
import pytest
from astropy.constants import M_sun, R_sun
from astropy.cosmology import FlatLambdaCDM
from black_hole_horizon_entropy import BlackHoleEntropyEngine
from cosmology_expansion import EMRFCosmologyParams, luminosity_distance_Mpc
from emrf.core.errors import NumericalError, UnitError
from emrf.physics.constants import CODATA_2022, CODATA_2022_REFERENCE
from emrf.physics.verification import (
    bekenstein_hawking_entropy,
    flat_lcdm_luminosity_distance,
    known_limit_report,
    ppn_light_deflection,
    schwarzschild_radius,
)
from physics_baseline import (
    AU,
    SOLAR_MASS,
    G,
    integrate_orbit_1pn,
    solve_kepler,
)
from scipy.signal import find_peaks


def test_codata_2022_constants_have_explicit_provenance() -> None:
    assert set(CODATA_2022) == {"G", "c", "h", "k_B"}
    assert all(item.reference == CODATA_2022_REFERENCE for item in CODATA_2022.values())
    assert CODATA_2022["G"].value == 6.67430e-11
    assert CODATA_2022["G"].uncertainty == 0.00015e-11
    assert CODATA_2022["c"].exact
    assert CODATA_2022["h"].exact
    assert CODATA_2022["k_B"].exact


def test_machine_readable_known_limit_certificate_passes() -> None:
    report = known_limit_report()
    assert report["evidence_class"] == "mixed"
    assert report["constants_reference"] == "NIST CODATA 2022"
    assert report["all_passed"]
    assert len(report["checks"]) == 10
    assert all(check["passed"] for check in report["checks"])
    assert {
        check["evidence_class"] for check in report["checks"]
    } == {"software", "illustrative"}


def test_unit_boundaries_reject_bare_and_incompatible_values() -> None:
    with pytest.raises(UnitError, match="astropy Quantity"):
        schwarzschild_radius(1.0)  # type: ignore[arg-type]
    with pytest.raises(UnitError, match="convertible"):
        schwarzschild_radius(1.0 * u.m)
    with pytest.raises(NumericalError, match="finite positive"):
        schwarzschild_radius(np.nan * u.kg)


def test_solar_schwarzschild_radius_known_limit() -> None:
    radius = schwarzschild_radius(M_sun)
    assert radius.to_value(u.km) == pytest.approx(2.95325, rel=2e-5)


def test_general_relativity_solar_limb_light_deflection() -> None:
    deflection = ppn_light_deflection(M_sun, R_sun, gamma=1.0)
    assert deflection.to_value(u.arcsec) == pytest.approx(1.7512, rel=5e-4)
    half_deflection = ppn_light_deflection(M_sun, R_sun, gamma=0.0)
    assert half_deflection.to_value(u.rad) == pytest.approx(
        0.5 * deflection.to_value(u.rad)
    )


def test_bekenstein_hawking_entropy_matches_legacy_engine_and_mass_scaling() -> None:
    mass = 10.0 * M_sun
    reference = bekenstein_hawking_entropy(mass)
    legacy = BlackHoleEntropyEngine().bekenstein_hawking_entropy_exact(
        mass.to_value(u.kg)
    )
    assert reference.to_value(u.J / u.K) == pytest.approx(legacy, rel=1e-9)
    doubled = bekenstein_hawking_entropy(2.0 * mass)
    assert doubled.to_value(u.J / u.K) == pytest.approx(
        4.0 * reference.to_value(u.J / u.K)
    )


@pytest.mark.parametrize("redshift", [0.01, 0.1, 0.5, 1.0, 2.0])
def test_flat_lcdm_distance_matches_astropy_and_existing_engine(redshift: float) -> None:
    h0 = 70.0 * u.km / (u.s * u.Mpc)
    reference = flat_lcdm_luminosity_distance(redshift, h0, 0.3)
    astropy_model = FlatLambdaCDM(H0=h0, Om0=0.3, Tcmb0=0.0 * u.K)
    assert reference.to_value(u.Mpc) == pytest.approx(
        astropy_model.luminosity_distance(redshift).to_value(u.Mpc),
        rel=2e-11,
    )

    params = EMRFCosmologyParams(
        H0=70.0,
        Omega_b=0.05,
        Omega_C_matter=0.25,
        Omega_r=0.0,
        w0=-1.0,
        wa=0.0,
    )
    assert luminosity_distance_Mpc(redshift, params) == pytest.approx(
        reference.to_value(u.Mpc),
        rel=2e-10,
    )


def test_rk4_orbit_refinement_recovers_fourth_order_convergence() -> None:
    radius = AU
    velocity = math.sqrt(G * SOLAR_MASS / radius)
    r0 = np.array([radius, 0.0])
    v0 = np.array([0.0, velocity])
    duration = 20.0 * 86400.0

    def endpoint(step: float) -> np.ndarray:
        _, positions, velocities = integrate_orbit_1pn(
            r0,
            v0,
            SOLAR_MASS,
            (0.0, duration),
            step,
        )
        return np.concatenate((positions[-1] / AU, velocities[-1] / velocity))

    reference = endpoint(225.0)
    errors = [
        np.linalg.norm(endpoint(step) - reference)
        for step in (86400.0, 43200.0, 21600.0)
    ]
    observed_orders = [
        math.log2(errors[index] / errors[index + 1])
        for index in range(2)
    ]
    assert min(observed_orders) > 3.9


@pytest.mark.parametrize(
    ("call", "message"),
    [
        (lambda: solve_kepler(float("nan"), 0.1), "Mean anomaly"),
        (
            lambda: integrate_orbit_1pn(
                np.array([AU, 0.0]),
                np.array([0.0, float("nan")]),
                SOLAR_MASS,
                (0.0, 1.0),
                0.1,
            ),
            "finite matching",
        ),
    ],
)
def test_non_finite_physics_inputs_fail_closed(call, message: str) -> None:
    with pytest.raises(NumericalError, match=message):
        call()


def test_cmb_reference_values_are_reproducible_with_camb() -> None:
    params = camb.CAMBparams()
    h = 0.674
    params.set_cosmology(
        H0=67.4,
        ombh2=0.049 * h**2,
        omch2=0.266 * h**2,
        mnu=0.06,
        omk=0.0,
        tau=0.054,
    )
    params.InitPower.set_params(As=2.1e-9, ns=0.965)
    params.set_for_lmax(1000, lens_potential_accuracy=0)
    results = camb.get_results(params)
    spectrum = results.get_cmb_power_spectra(
        params,
        CMB_unit="muK",
        raw_cl=False,
    )["unlensed_scalar"][:, 0]
    peak_indices, _ = find_peaks(
        spectrum[100:1000],
        distance=150,
        prominence=200,
    )
    peaks = peak_indices[:3] + 100
    derived = results.get_derived_params()

    assert peaks.tolist() == [220, 536, 813]
    assert derived["thetastar"] == pytest.approx(1.0424541939952765, rel=1e-8)
