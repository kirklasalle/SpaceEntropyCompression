"""Standard gravity and orbital baselines exposed through the EMRF namespace."""

from physics_baseline import (
    AU,
    C_LIGHT,
    SGR_A_DISTANCE,
    SGR_A_MASS,
    SOLAR_MASS,
    YEAR_SEC,
    G,
    integrate_orbit_1pn,
    keplerian_orbit_2d,
    kretschmann_invariant,
    schwarzschild_1pn_acceleration,
    schwarzschild_pericenter_advance_analytical,
    solve_kepler,
)

__all__ = [
    "AU",
    "C_LIGHT",
    "G",
    "SGR_A_DISTANCE",
    "SGR_A_MASS",
    "SOLAR_MASS",
    "YEAR_SEC",
    "integrate_orbit_1pn",
    "keplerian_orbit_2d",
    "kretschmann_invariant",
    "schwarzschild_1pn_acceleration",
    "schwarzschild_pericenter_advance_analytical",
    "solve_kepler",
]
