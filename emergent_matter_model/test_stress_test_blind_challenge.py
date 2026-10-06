"""Unit tests for Synthetic Adversarial Blind Challenge & Bayesian Falsification Stress Test."""

import pytest
from stress_test_blind_challenge import (
    generate_adversarial_challenges,
    evaluate_dataset_fit,
    run_synthetic_adversarial_challenge,
)


class TestBlindChallengeFalsifiability:
    def test_challenge_datasets_generation(self):
        """Must generate 1 real physical dataset and 3 adversarial challenges."""
        challenges = generate_adversarial_challenges()
        assert len(challenges) == 4
        assert challenges[0].is_physically_valid
        assert not challenges[1].is_physically_valid
        assert not challenges[2].is_physically_valid
        assert not challenges[3].is_physically_valid

    def test_real_galaxy_accepted(self):
        """EMRF must cleanly accept genuine physical galaxy data with low Chi2."""
        challenges = generate_adversarial_challenges()
        fit_real = evaluate_dataset_fit(challenges[0])
        assert fit_real["accepted"]
        assert fit_real["reduced_chi2"] < 2.0
        assert fit_real["correct_decision"]

    def test_adversarial_anti_gravity_rejected(self):
        """EMRF must decisively reject inverted anti-gravity data."""
        challenges = generate_adversarial_challenges()
        fit_inverted = evaluate_dataset_fit(challenges[1])
        assert not fit_inverted["accepted"]
        assert fit_inverted["reduced_chi2"] > 50.0
        assert fit_inverted["correct_decision"]

    def test_adversarial_heaviside_step_rejected(self):
        """EMRF must decisively reject unphysical discontinuous step data."""
        challenges = generate_adversarial_challenges()
        fit_step = evaluate_dataset_fit(challenges[2])
        assert not fit_step["accepted"]
        assert fit_step["reduced_chi2"] > 50.0
        assert fit_step["correct_decision"]

    def test_adversarial_white_noise_rejected(self):
        """EMRF must decisively reject uncorrelated white noise chaos."""
        challenges = generate_adversarial_challenges()
        fit_noise = evaluate_dataset_fit(challenges[3])
        assert not fit_noise["accepted"]
        assert fit_noise["reduced_chi2"] > 50.0
        assert fit_noise["correct_decision"]

    def test_all_selectivity_decisions_correct(self):
        """Full suite must achieve 100% decision selectivity accuracy."""
        report = run_synthetic_adversarial_challenge()
        assert report["all_decisions_correct"]
