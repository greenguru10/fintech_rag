"""Unit tests for the financial calculation engine using Decimal precision."""

from decimal import Decimal
import pytest
from app.calculations.loan import calculate_emi
from app.calculations.investment import (
    calculate_sip,
    calculate_compound_interest,
    calculate_simple_interest,
    calculate_cagr,
)
from app.calculations.validators import parse_money, parse_rate, parse_tenure_months
from app.core.exceptions import CalculationError


def test_calculate_emi_standard():
    """EMI for ₹5,00,000 at 10% annual interest for 60 months (5 years). Expected EMI: ₹10,623.52."""
    p = Decimal("500000.00")
    r = Decimal("10.00")
    n = 60
    res = calculate_emi(p, r, n, include_schedule=True)

    assert res["result"]["monthly_emi"] == "10623.52"
    assert res["result"]["total_payment"] == "637411.20"
    assert res["result"]["total_interest"] == "137411.20"
    assert len(res["schedule"]) == 60
    # Final remaining balance should be 0.00
    assert res["schedule"][-1]["remaining_balance"] == "0.00"


def test_calculate_emi_zero_interest():
    """Zero interest loan of ₹1,20,000 for 12 months -> EMI = 10,000.00, Interest = 0.00."""
    p = Decimal("120000.00")
    r = Decimal("0.00")
    n = 12
    res = calculate_emi(p, r, n)

    assert res["result"]["monthly_emi"] == "10000.00"
    assert res["result"]["total_interest"] == "0.00"
    assert res["result"]["total_payment"] == "120000.00"


def test_calculate_sip():
    """SIP of ₹10,000/month for 10 years at 12% return."""
    res = calculate_sip(Decimal("10000.00"), Decimal("12.00"), Decimal("10"))
    assert res["result"]["total_invested"] == "1200000.00"
    # FV formula yields ~23,00,386.89
    assert res["result"]["estimated_future_value"] == "2300386.89"
    assert res["result"]["estimated_gain"] == "1100386.89"


def test_calculate_compound_interest():
    """₹1,00,000 at 8% for 5 years compounded quarterly."""
    res = calculate_compound_interest(Decimal("100000.00"), Decimal("8.00"), Decimal("5"), compounds_per_year=4)
    assert res["result"]["principal"] == "100000.00"
    assert res["result"]["maturity_amount"] == "148594.74"
    assert res["result"]["total_interest"] == "48594.74"


def test_calculate_simple_interest():
    """₹50,000 at 8% for 2 years -> SI = 8000.00."""
    res = calculate_simple_interest(Decimal("50000.00"), Decimal("8.00"), Decimal("2"))
    assert res["result"]["total_interest"] == "8000.00"
    assert res["result"]["total_amount"] == "58000.00"


def test_calculate_cagr():
    """₹1,00,000 to ₹1,50,000 in 3 years -> CAGR = 14.47%."""
    res = calculate_cagr(Decimal("100000.00"), Decimal("150000.00"), Decimal("3"))
    assert res["result"]["cagr_pct"] == "14.47%"
    assert res["result"]["absolute_gain"] == "50000.00"


def test_money_parser():
    assert parse_money("5 lakh") == Decimal("500000")
    assert parse_money("₹10,50,000") == Decimal("1050000")
    assert parse_money("1.5 crore") == Decimal("15000000")
    assert parse_money("50k") == Decimal("50000")


def test_invalid_calculations_rejected():
    with pytest.raises(CalculationError):
        calculate_emi(Decimal("-500"), Decimal("10"), 12)
    with pytest.raises(CalculationError):
        calculate_emi(Decimal("50000"), Decimal("-5"), 12)
    with pytest.raises(CalculationError):
        calculate_cagr(Decimal("-100"), Decimal("200"), Decimal("2"))
