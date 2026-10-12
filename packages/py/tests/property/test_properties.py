"""Property-based tests for Symnoesis math core invariants using Hypothesis."""

import math

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from scipy.special import ndtr

from symnoesis.assign import compute_dyad_window_masses
from symnoesis.config import SymnoesisConfig
from symnoesis.gray import gray_to_int, int_to_gray
from symnoesis.sq import compute_sq
from symnoesis.variables import normal_cdf


@pytest.fixture(scope="module")
def config() -> SymnoesisConfig:
    return SymnoesisConfig.load_default()


@given(st.integers(min_value=0, max_value=15))
def test_gray_code_bijection(k: int) -> None:
    """Invariant: gray_to_int(int_to_gray(k)) == k for all k in [0, 15]."""
    g = int_to_gray(k)
    assert 0 <= g <= 15
    assert gray_to_int(g) == k


@given(st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False))
def test_normal_cdf_invariants(x: float) -> None:
    """Invariant: normal_cdf(x) in [0, 1] and matches scipy.special.ndtr within 1e-9."""
    val = normal_cdf(x)
    assert 0.0 <= val <= 1.0
    expected = float(ndtr(x))
    assert abs(val - expected) < 1e-9


@given(
    st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False),
    st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False),
)
def test_normal_cdf_monotonicity(x1: float, x2: float) -> None:
    """Invariant: normal_cdf is monotonically non-decreasing."""
    if x1 <= x2:
        assert normal_cdf(x1) <= normal_cdf(x2)
    else:
        assert normal_cdf(x1) >= normal_cdf(x2)


@given(
    st.lists(
        st.floats(min_value=0.01, max_value=0.99, allow_nan=False, allow_infinity=False),
        min_size=8,
        max_size=8,
    )
)
@settings(max_examples=50)
def test_mass_conservation_invariant(probs: list[float]) -> None:
    """Invariant: Renormalized mass distribution sums to 1.0 within numerical precision."""
    cfg = SymnoesisConfig.load_default()
    var_names = ["H1", "H2", "H3", "H4", "M1", "M2", "M3", "M4"]
    p_vars = dict(zip(var_names, probs, strict=True))

    masses = compute_dyad_window_masses(p_vars, cfg)
    total_mass = sum(masses.values())
    assert math.isclose(total_mass, 1.0, rel_tol=1e-9, abs_tol=1e-12)
    assert all(0.0 <= m <= 1.0 for m in masses.values())


@given(
    st.floats(min_value=-2.0, max_value=2.0, allow_nan=False, allow_infinity=False),
    st.floats(min_value=0.0, max_value=1.5, allow_nan=False, allow_infinity=False),
    st.one_of(
        st.none(),
        st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    ),
)
def test_sq_clipping_bounds_invariant(c: float, s: float, gate: float | None) -> None:
    """Invariant: Composite SQ is strictly clipped to [-100.0, +100.0]."""
    cfg = SymnoesisConfig.load_default()
    sq, sq_raw, _ = compute_sq(c, s, gate, cfg)
    assert -100.0 <= sq <= 100.0
