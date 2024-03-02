import pytest
from src.demo import validate_affordability


@pytest.mark.parametrize(
    "mortgage,income,affordability,outcome",
    [
        (10000, 1000, 4.5, True),  # covers low mortage size
        (100000, 30000, 4.5, True),  # covers standard expected outcome
        (100000, 30000, 4.0, True),  # covers lower multiplier
    ],
)
def test_afforadbility_success_standard(
    mortgage: int, income: int, affordability: float, outcome: bool
) -> None:
    check = validate_affordability(
        mortgage, income, affordability, existing_customer=False
    )
    assert check is outcome


def test_afforadbility_success_existing_customer() -> None:
    check = validate_affordability(10000, 1000, 4.5, existing_customer=True)
    assert check is True


from hypothesis import given, strategies as st, settings, example


@example(mortgage=25000, salary=0, affordability=1)
@example(mortgage=20000, salary=1, affordability=2)
@example(mortgage=100000, salary=20000, affordability=5)
@example(mortgage=19999, salary=1, affordability=2)
@given(
    st.integers(min_value=5000),
    st.integers(min_value=1),
    st.floats(min_value=1, max_value=10),
)
def test_afforadbility_success_property_test(
    mortgage: int, salary: int, affordability: float
):
    outcome = validate_affordability(
        mortgage, salary, affordability, existing_customer=False
    )
    if not salary:
        assert outcome is False
    elif mortgage < 20000:
        assert outcome is True
    else:
        assert outcome is (mortgage / salary <= affordability)
