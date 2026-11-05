"""Model-only regression coverage; never load observed rotation velocities."""

import dataclasses
import json
import math
import os

import numpy as np
import pytest
from scipy.integrate import quad
from tools import candidate_a_option3_gpu as gpu
from tools import candidate_a_option3_quadrature as quadrature
from tools import candidate_a_option3_reconstruction as model
from tools import evaluate_candidate_a_all_options as reference
from tools import validate_candidate_a_option3 as validation


@pytest.fixture
def profile():
    return model.Profile(
        "test", model.Geometry(5, 60), 1000, 1500, 7.3, False,
        (model.Ring(500, 5, 1, 2, 100),
         model.Ring(1000, None, 1, None, 50),
         model.Ring(1500, 3, 0.5, 1, 25)),
    )


def test_frozen_hash_preserved():
    assert reference.sha256(model.PROTOCOL) == model.PROTOCOL_SHA256


def test_segmented_amendment_is_hash_pinned_and_model_only():
    amendment, digest = validation.load_protocol_amendment(model.ROOT)
    assert digest == validation.AMENDMENT_SHA256
    assert amendment["parent_protocol"]["sha256"] == model.PROTOCOL_SHA256
    assert amendment["V3"]["method_id"] == "axisymmetric_segmented_v1"
    assert amendment["V3b"]["method_id"] == "axisymmetric_segmented_v1"
    assert amendment["fit_authorized"] is False
    assert amendment["observed_velocities_parsed"] is False
    assert amendment["observational_fit_performed"] is False


def test_segmented_amendment_requires_gpu_backend():
    with pytest.raises(ValueError, match="requires --backend gpu"):
        validation.run("cpu", model.ROOT, "segmented", amendment=True)


def test_ring_flags_do_not_censor_measured_rms_one():
    row = list(" " * 82)
    for start, end, value in ((0, 8, "test"), (9, 13, "0.5"), (19, 24, "5.0"),
                              (25, 28, "1.0"), (29, 35, "2.0"), (41, 48, "100.0")):
        row[start:end] = value.rjust(end - start)
    rows = []
    for radius in ("0.5", "1.0", "1.5"):
        row[9:13] = radius.rjust(4)
        rows.append("".join(row))
    parsed = model.parse_rings("\n".join(rows), {"test"})
    assert all(r.hi == 5 for r in parsed["test"])
    rows[1] = rows[1][:19] + " " * 5 + rows[1][24:]
    assert model.parse_rings("\n".join(rows), {"test"})["test"][1].hi is None
    rows[1] = rows[1][:25] + "0.5" + rows[1][28:]
    with pytest.raises(ValueError, match="missing HI"):
        model.parse_rings("\n".join(rows), {"test"})


def test_velocity_fields_are_not_parsed():
    data = model.parse_model_columns("1 NOT_A_NUMBER DO_NOT_PARSE 2 3 4\n")
    np.testing.assert_array_equal(data, [[1, 2, 3, 4]])
    with pytest.raises(ValueError, match="non-finite"):
        model.parse_model_columns("1 secret secret nan 3 4")


def test_envelopes_and_single_co_no_second_helium(profile):
    low = model.build_source(profile, profile.geometry, "low")
    high = model.build_source(profile, profile.geometry, "high")
    np.testing.assert_array_equal(low.sigma[1], [5, 0, 3])
    np.testing.assert_array_equal(high.sigma[1], [5, 1, 3])
    np.testing.assert_allclose(low.sigma[2], [1.4, 0, 0.7])
    np.testing.assert_allclose(high.sigma[2], [2.6, 1.3, 1.3])
    np.testing.assert_array_equal(high.sigma[0], [100, 50, 25])


@pytest.mark.parametrize("limit", [False, True])
def test_synthetic_mass_normalized_inside_cutoff_once(profile, limit):
    synthetic = dataclasses.replace(
        profile, h2_mass_is_limit=limit,
        rings=tuple(dataclasses.replace(r, h2=None) for r in profile.rings),
    )
    source = model.build_source(synthetic, synthetic.geometry, "high")
    integral = quad(lambda r: 2 * math.pi * r * source.surface(r)[2],
                    0, source.cutoff_pc, points=source.radii_pc.tolist())[0]
    assert integral == pytest.approx(1.3 * 1.36 * 10**7.3, rel=1e-10)
    assert not model.build_source(synthetic, synthetic.geometry, "low").sigma[2].any()


def test_no_h2_bound_is_error_not_zero(profile):
    missing = dataclasses.replace(
        profile, log_h2_mass=None,
        rings=tuple(dataclasses.replace(r, h2=None) for r in profile.rings),
    )
    with pytest.raises(ValueError, match="no molecular bound"):
        model.build_source(missing, missing.geometry, "low")


def test_radial_projection_and_units(profile):
    for envelope in ("low", "high"):
        source = model.build_source(profile, profile.geometry, envelope)
        np.testing.assert_allclose(source.surface(source.radii_pc), source.sigma, rtol=1e-14)
        assert validation.projection_error(source) < 1e-3
        assert source.surface(0)[0] == pytest.approx(100)
        assert source.surface(750)[0] == pytest.approx(math.sqrt(100 * 50))
        assert source.surface(source.cutoff_pc)[0] == pytest.approx(25)
        assert not source.surface(np.nextafter(source.cutoff_pc, np.inf)).any()
        doubled = model.build_source(profile, profile.geometry, envelope, f_distance=2)
        np.testing.assert_array_equal(doubled.sigma, source.sigma)
        np.testing.assert_array_equal(doubled.radii_pc, 2 * source.radii_pc)
        assert doubled.z0_pc == 2 * source.z0_pc
        np.testing.assert_array_equal(doubled.hi_sigma_pc, source.hi_sigma_pc)


def test_nonlinear_map_matches_reference_and_explicit_underflow():
    rho = np.array([0, 1e-4, 0.1, 1, 10.0])
    for alpha in (0.5, 1, 2):
        np.testing.assert_allclose(
            model.mapped_density(rho, alpha, 0.1),
            reference.effective_density(rho, alpha, 0.1), rtol=1e-14, atol=0)
    assert model.mapped_density(np.array([1e-250]), 0.5, 1)[0] == 0
    for invalid in (-1, np.nan, np.inf):
        with pytest.raises(ValueError):
            model.mapped_density(np.array([invalid]), 1, 1)
    with pytest.raises(ArithmeticError):
        model.mapped_density(np.array([1e250]), 0.5, 1)


def test_geometry_and_nuisance_rules(profile):
    base = model.build_source(profile, profile.geometry, "high")
    aligned = model.build_source(profile, model.Geometry(10, 45), "high",
                                 f_star=2, delta_q=0.19)
    factor = math.cos(math.radians(45)) / math.cos(math.radians(60))
    np.testing.assert_allclose(aligned.sigma[1:], base.sigma[1:] * factor)
    np.testing.assert_allclose(aligned.sigma[0], base.sigma[0] * factor * 2)
    np.testing.assert_array_equal(aligned.radii_pc, 2 * base.radii_pc)
    expected_q = 10**(0.367 * math.log10(2) + 0.708 + 0.19)
    assert aligned.z0_pc == pytest.approx(4000 / expected_q)
    np.testing.assert_array_equal(aligned.h2_sigma_pc, base.h2_sigma_pc)


def test_sensitivity_family_defines_every_frozen_source_variant():
    variants = model.sensitivity_variants()
    assert [variant.name for variant in variants] == [
        "primary", "delta_q_minus_0.19", "delta_q_plus_0.19",
        "gas_hwhm_minus_1sigma", "gas_hwhm_plus_1sigma",
        "hydrostatic_gas_flaring", "inward_stellar_exponential",
        "outer_exponential_tails", "spherical_inner_bulge", "leroy_geometry",
        "t1_upsilon_k_0.4", "t1_upsilon_k_0.6",
    ]
    assert variants[-2].f_star == pytest.approx(0.8)
    assert variants[-1].f_star == pytest.approx(1.2)


def test_source_sensitivities_change_only_the_declared_source_terms(profile):
    baseline = model.build_source(profile, profile.geometry, "high")
    variants = {variant.name: variant for variant in model.sensitivity_variants()}
    thin = model.build_source(
        profile, profile.geometry, "high", variant=variants["gas_hwhm_minus_1sigma"])
    thick = model.build_source(
        profile, profile.geometry, "high", variant=variants["gas_hwhm_plus_1sigma"])
    assert thin.hi_sigma_pc[0] == pytest.approx(174 / math.sqrt(2 * math.log(2)))
    assert thin.h2_sigma_pc[0] == pytest.approx(52 / math.sqrt(2 * math.log(2)))
    assert thick.hi_sigma_pc[0] == pytest.approx(230 / math.sqrt(2 * math.log(2)))
    assert thick.h2_sigma_pc[0] == pytest.approx(76 / math.sqrt(2 * math.log(2)))
    np.testing.assert_array_equal(thin.sigma, baseline.sigma)
    plus = model.build_source(
        profile, profile.geometry, "high", variant=variants["delta_q_plus_0.19"])
    assert plus.z0_pc < baseline.z0_pc
    inner = model.build_source(
        profile, profile.geometry, "high",
        variant=variants["inward_stellar_exponential"])
    assert inner.surface(0)[0] > baseline.surface(0)[0]
    tails = model.build_source(
        profile, profile.geometry, "high", variant=variants["outer_exponential_tails"])
    assert tails.surface(tails.radii_pc[-1] + 100)[0] > 0
    assert not baseline.surface(baseline.cutoff_pc + 1)[0]
    leroy = model.build_source(
        profile, model.Geometry(10, 45), "high",
        variant=variants["leroy_geometry"])
    np.testing.assert_array_equal(leroy.radii_pc, baseline.radii_pc)
    np.testing.assert_array_equal(leroy.sigma, baseline.sigma)
    sparc_aligned = model.build_source(
        profile, model.Geometry(10, 45), "high")
    assert sparc_aligned.field_radius_scale == pytest.approx(0.5)
    assert leroy.field_radius_scale == pytest.approx(1.0)
    low_ml = model.build_source(
        profile, profile.geometry, "high", variant=variants["t1_upsilon_k_0.4"])
    assert low_ml.sigma[0, 0] == pytest.approx(0.8 * baseline.sigma[0, 0])


def test_hydrostatic_flaring_converges_and_preserves_projection(profile):
    variant = next(v for v in model.sensitivity_variants() if v.hydrostatic_flaring)
    source = model.build_source(profile, profile.geometry, "high", variant=variant)
    assert np.all(source.hi_sigma_pc > 0)
    assert np.all(source.h2_sigma_pc > 0)
    assert validation.projection_error(source) < 1e-3
    hi, h2 = model.hydrostatic_gas_widths(
        source.radii_pc, source.sigma, source.z0_pc,
        source.hi_sigma_pc, source.h2_sigma_pc,
    )
    np.testing.assert_allclose(hi, source.hi_sigma_pc, rtol=1e-8)
    np.testing.assert_allclose(h2, source.h2_sigma_pc, rtol=1e-8)
    with pytest.raises(ValueError, match="finite, aligned"):
        model.hydrostatic_gas_widths(
            source.radii_pc, source.sigma, source.z0_pc,
            np.zeros_like(source.hi_sigma_pc), source.h2_sigma_pc,
        )


def test_spherical_inner_bulge_projects_to_the_stellar_profile(profile):
    variant = next(v for v in model.sensitivity_variants() if v.spherical_inner_bulge)
    bulged = dataclasses.replace(
        profile,
        rings=(
            dataclasses.replace(profile.rings[0], stars=200),
            profile.rings[1],
            profile.rings[2],
        ),
    )
    source = model.build_source(bulged, bulged.geometry, "high", variant=variant)
    assert validation.projection_error(source) < 1e-3


def test_spherical_density_projection_exact_for_constant_sphere():
    radii = np.array([0.0, 500.0, 1000.0])
    density = np.ones(3)
    assert validation.spherical_density_projection(0.0, radii, density) == pytest.approx(
        2000.0)
    projected = validation.spherical_density_projection(500.0, radii, density)
    assert projected == pytest.approx(2 * math.sqrt(1000**2 - 500**2), rel=1e-14)
    assert validation.spherical_density_projection(1000.0, radii, density) == 0.0
    with pytest.raises(ValueError, match="strictly ordered"):
        validation.spherical_density_projection(
            0.0, np.array([0.0, 1.0, 1.0]), density)


def test_segmented_nodes_resolve_each_profile_interval(profile):
    source = model.build_source(profile, profile.geometry, "high")
    breaks = np.unique(np.r_[0.0, source.radii_pc, source.cutoff_pc])
    nodes, weights = quadrature.radial_nodes(breaks, 900, 16)
    for left, right in zip(breaks[:-1], breaks[1:], strict=True):
        selected = (nodes >= left) & (nodes <= right)
        powers = np.arange(1, 10)
        expected = (right**powers - left**powers) / powers
        actual = np.array([np.sum(weights[selected] * nodes[selected]**k) for k in range(9)])
        np.testing.assert_allclose(actual, expected, rtol=2e-13, atol=1e-10)


def test_segmented_tail_nodes_integrate_an_exponential_to_infinity():
    breaks = np.array([0.0, 1.0, 2.0])
    nodes, weights = quadrature.radial_nodes(
        breaks, 1.5, 64, outer_tail_scale=2.0)
    tail = nodes >= 2.0
    actual = np.sum(weights[tail] * np.exp(-(nodes[tail] - 2.0) / 2.0))
    assert actual == pytest.approx(2.0, rel=1e-12)
    with pytest.raises(ValueError, match="not decaying"):
        model.outer_log_slope(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 4.0]))


def test_segmented_quadrature_converges_on_reconstructed_synthetic_source(profile):
    source = model.build_source(profile, profile.geometry, "high")
    radii = np.array([600.0, 900.0, 1300.0])
    coarse = validation.cpu_v2(source, radii, 2.0, 0.1, 64, "segmented")
    fine = validation.cpu_v2(source, radii, 2.0, 0.1, 128, "segmented")
    assert validation.relative_error(coarse, fine) < 0.005


def test_segmented_quadrature_converges_on_exponential_tail(profile):
    variant = next(v for v in model.sensitivity_variants() if v.outer_exponential_tails)
    source = model.build_source(profile, profile.geometry, "high", variant=variant)
    radii = np.array([600.0, 900.0, 1300.0])
    coarse = validation.cpu_v2(source, radii, 1.0, 0.1, 64, "segmented")
    fine = validation.cpu_v2(source, radii, 1.0, 0.1, 128, "segmented")
    assert validation.relative_error(coarse, fine) < 0.005


def test_v4_uses_only_model_component_columns(profile, monkeypatch, tmp_path):
    source = model.build_source(profile, profile.geometry, "high")
    columns = np.array([[0.5, -2.0, 3.0, 4.0], [1.0, 1.0, 2.0, 2.0]])
    monkeypatch.setattr(model, "load_model_columns", lambda *_: columns)
    monkeypatch.setattr(
        validation, "cpu_v2", lambda *_: np.array([21.0, 9.0]))
    result = validation.run_v4(
        ["test"], {("primary", "test", "low"): source,
                   ("primary", "test", "high"): source},
        tmp_path, "segmented",
    )
    assert result["status"] == "reported_model_only"
    assert result["cases"][0]["max_absolute_delta_v2_kms2"] == 0
    assert "Vobs and errV are not parsed" in result["method"]


def test_v5_reports_fixed_grid_model_only_sensitivities(profile, monkeypatch, tmp_path):
    source = model.build_source(profile, profile.geometry, "high")
    variants = model.sensitivity_variants()
    sources = {
        (variant.name, "test", envelope): source
        for variant in variants for envelope in ("low", "high")
    }
    columns = np.array([[0.5, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]])
    monkeypatch.setattr(model, "load_model_columns", lambda *_: columns)
    monkeypatch.setattr(
        validation, "cpu_v2", lambda *_: np.array([1.0, 4.0]))
    baseline = {
        ("test", envelope, alpha, log_rho0): np.array([1.0, 4.0])
        for envelope in ("low", "high")
        for alpha in (0.5, 1.0, 2.0)
        for log_rho0 in (-4.0, -1.0, 2.0)
    }
    result = validation.run_v5(
        variants, ["test"], sources, baseline, tmp_path, "segmented")
    assert result["status"] == "reported_model_only"
    assert all(row["status"] == "reported_model_only" for row in result["variants"])
    assert all(row["case_count"] == 18 for row in result["variants"])
    assert result["inference_only_sensitivities"]["delta_Q_without_error_inflation"] == (
        "not_applicable_to_model_only_Vc")


def test_current_ledger_retains_failure_and_frozen_scope():
    ledger = json.loads((model.ROOT / "knowledgebase" /
                         "thermodynamic_collision_candidates.json").read_text())
    followup = ledger["functional_comparison"]["option_3_reconstruction_followup"]
    report = json.loads((model.ROOT / followup["artifact"]).read_text())
    assert followup["protocol_sha256"] == report["protocol_sha256"] == model.PROTOCOL_SHA256
    assert followup["outcome"] == report["outcome"] == "incomplete"
    assert not followup["observational_fit_performed"]
    assert not report["observed_velocities_parsed"]
    assert len(report["cases"]) == 180
    assert followup["v3_max_relative_error"] == report["gates"]["V3"]["max_relative_error"]
    assert followup["v3_max_relative_error"] > followup["v3_threshold"]
    assert followup["v3b_max_relative_error"] < followup["v3b_threshold"]
    assert report["gates"]["V1"]["status"] == "incomplete"
    assert report["gates"]["V4"]["status"] == report["gates"]["V5"]["status"] == "not_run"
    assert (model.ROOT / followup["initial_implementation_failure"]).is_file()
    assert ledger["parallel_exploration"]["stxs_feasibility_followup"]["outcome"] == (
        "closed_for_restricted_model_without_computation")
    assert (model.ROOT / "knowledgebase" / "GRAPH_MEMORY.json").read_bytes() == (
        model.ROOT / "emergent_matter_model" / "src" / "emrf" / "knowledge" /
        "graph_memory.json").read_bytes()


def test_incomplete_report_is_persistent_and_nonzero(tmp_path, monkeypatch):
    output = tmp_path / "report.json"
    monkeypatch.setattr(validation, "run", lambda *_: {
        "outcome": "incomplete", "gates": {}, "blockers": ["V3"],
        "fit_permitted": False,
    })
    assert validation.main(["--output", str(output)]) == 2
    assert json.loads(output.read_text())["fit_permitted"] is False
    with pytest.raises(SystemExit):
        validation.main(["--output", str(output)])


def test_missing_gpu_does_not_fall_back(monkeypatch):
    def missing(_):
        raise ImportError("deliberately absent")
    monkeypatch.setattr(gpu.importlib, "import_module", missing)
    with pytest.raises(RuntimeError, match="optional"):
        gpu.require_gpu()


def test_hash_failure_stops_before_reading_sources(monkeypatch):
    def fail(_):
        raise ValueError("deliberate frozen hash mismatch")
    monkeypatch.setattr(model, "verify_inputs", fail)
    monkeypatch.setattr(model, "load_profiles", lambda *_: pytest.fail("sources read"))
    report = validation.run()
    assert "hash mismatch" in report["incomplete_reason"]
    assert not report["fit_permitted"]


@pytest.mark.skipif(
    not (model.ROOT / "data" / "external" / "candidate_a" / "leroy2008" / "table7.dat").exists(),
    reason="Pinned density inputs are not downloaded",
)
def test_real_inputs_and_corrected_audit_without_velocities():
    protocol = model.verify_inputs()
    names = set(protocol["population"]["primary"]) | {"NGC7793"}
    profiles = model.load_profiles(model.ROOT, names)
    assert sum(r.hi is None for p in profiles.values() for r in p.rings) == 13
    assert sum(r.h2 is None for p in profiles.values() for r in p.rings) == 265
    assert len(profiles) == 11
    geometry = model.load_geometry(model.ROOT, set(protocol["population"]["primary"]))
    for name in protocol["population"]["primary"]:
        for envelope in ("low", "high"):
            source = model.build_source(profiles[name], geometry[name], envelope)
            assert source.sigma.shape == (3, len(profiles[name].rings))
            assert np.isfinite(source.sigma).all()


@pytest.mark.skipif(os.environ.get("EMRF_TEST_GPU") != "1",
                    reason="GPU tests require explicit EMRF_TEST_GPU=1")
def test_gpu_matches_cpu_primary_sources(profile):
    cp = gpu.require_gpu()
    radii = np.array([500, 1000, 1500.0])
    for envelope in ("low", "high"):
        source = model.build_source(profile, profile.geometry, envelope)
        for alpha in (0.5, 1.0, 2.0):
            for order in (64, 128):
                expected = validation.cpu_v2(source, radii, alpha, 0.1, order)
                actual = gpu.DeviceQuadrature(cp, order, source.scale_pc).evaluate(
                    source, radii, alpha, 0.1)
                assert validation.relative_error(actual, expected) < 1e-10
                expected_segmented = validation.cpu_v2(
                    source, radii, alpha, 0.1, order, "segmented")
                actual_segmented = gpu.DeviceSegmentedQuadrature(
                    cp, order, source.scale_pc).evaluate(source, radii, alpha, 0.1)
                assert validation.relative_error(actual_segmented, expected_segmented) < 1e-10
    tails = next(v for v in model.sensitivity_variants() if v.outer_exponential_tails)
    source = model.build_source(profile, profile.geometry, "high", variant=tails)
    expected = validation.cpu_v2(source, radii, 1.0, 0.1, 64, "segmented")
    actual = gpu.DeviceSegmentedQuadrature(cp, 64, source.scale_pc).evaluate(
        source, radii, 1.0, 0.1)
    assert validation.relative_error(actual, expected) < 1e-10
