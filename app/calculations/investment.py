"""Investment calculation engine: SIP, Simple Interest, Compound Interest, CAGR."""

from decimal import Decimal
from typing import Dict, Any
from app.calculations.common import quantize_currency, quantize_rate
from app.core.exceptions import CalculationError


def calculate_sip(
    monthly_investment: Decimal,
    annual_return_pct: Decimal,
    years: Decimal,
    payment_timing: str = "end_of_period",  # "end_of_period" or "beginning_of_period"
    currency: str = "INR",
) -> Dict[str, Any]:
    """Calculates Systematic Investment Plan (SIP) future value.

    End of period: FV = PMT * ((1+i)^n - 1) / i
    Beginning of period: FV = PMT * ((1+i)^n - 1) / i * (1+i)
    where:
      PMT = Monthly investment
      i = Monthly rate (annual_return_pct / 1200)
      n = Total months (years * 12)
    """
    if monthly_investment <= 0:
        raise CalculationError("Monthly investment must be greater than zero.")
    if annual_return_pct <= 0:
        raise CalculationError("Assumed annual return percentage must be greater than zero.")
    if years <= 0:
        raise CalculationError("Investment duration in years must be greater than zero.")

    total_months = int(years * Decimal("12"))
    total_invested = quantize_currency(monthly_investment * Decimal(total_months))

    monthly_rate = annual_return_pct / Decimal("1200")
    growth_factor = (Decimal("1") + monthly_rate) ** total_months

    if payment_timing == "beginning_of_period":
        fv_raw = monthly_investment * (growth_factor - Decimal("1")) / monthly_rate * (Decimal("1") + monthly_rate)
    else:
        payment_timing = "end_of_period"
        fv_raw = monthly_investment * (growth_factor - Decimal("1")) / monthly_rate

    future_value = quantize_currency(fv_raw)
    estimated_gain = quantize_currency(future_value - total_invested)

    return {
        "calculation_type": "sip",
        "formula_version": "1.0.0",
        "formula": "FV = PMT × ((1+i)^n - 1) / i" + (" × (1+i)" if payment_timing == "beginning_of_period" else ""),
        "inputs": {
            "monthly_investment": str(quantize_currency(monthly_investment)),
            "annual_return_pct": str(annual_return_pct),
            "years": str(years),
            "total_months": total_months,
            "payment_timing": payment_timing,
            "currency": currency,
        },
        "result": {
            "total_invested": str(total_invested),
            "estimated_future_value": str(future_value),
            "estimated_gain": str(estimated_gain),
        },
        "assumptions": [
            "Assumed constant rate of return throughout the investment horizon.",
            "Monthly compounding frequency.",
            "Illustration only; mutual fund returns are subject to market risks and not guaranteed.",
            "Taxes and expense ratios are excluded.",
        ],
    }


def calculate_compound_interest(
    principal: Decimal,
    annual_rate_pct: Decimal,
    years: Decimal,
    compounds_per_year: int = 4,  # default quarterly for Indian fixed deposits
    currency: str = "INR",
) -> Dict[str, Any]:
    """Calculates Compound Interest (CI) and maturity amount.

    A = P * (1 + r/n)^(n*t)
    CI = A - P
    """
    if principal <= 0:
        raise CalculationError("Principal amount must be greater than zero.")
    if annual_rate_pct < 0:
        raise CalculationError("Annual rate cannot be negative.")
    if years <= 0:
        raise CalculationError("Duration in years must be greater than zero.")
    if compounds_per_year <= 0:
        raise CalculationError("Compounding frequency per year must be at least 1.")

    r = annual_rate_pct / Decimal("100")
    n = Decimal(compounds_per_year)
    t = years

    exponent = int(n * t)
    base = Decimal("1") + (r / n)
    amount_raw = principal * (base ** exponent)

    maturity_amount = quantize_currency(amount_raw)
    total_interest = quantize_currency(maturity_amount - principal)

    return {
        "calculation_type": "compound_interest",
        "formula_version": "1.0.0",
        "formula": "A = P(1 + r/n)^(n*t)",
        "inputs": {
            "principal": str(quantize_currency(principal)),
            "annual_rate_pct": str(annual_rate_pct),
            "years": str(years),
            "compounds_per_year": compounds_per_year,
            "currency": currency,
        },
        "result": {
            "principal": str(quantize_currency(principal)),
            "total_interest": str(total_interest),
            "maturity_amount": str(maturity_amount),
        },
        "assumptions": [
            f"Interest compounded {compounds_per_year} times per year.",
            "Interest rate remains fixed for the entire duration.",
            "Taxes (such as TDS) and premature withdrawal penalties are excluded.",
        ],
    }


def calculate_simple_interest(
    principal: Decimal,
    annual_rate_pct: Decimal,
    years: Decimal,
    currency: str = "INR",
) -> Dict[str, Any]:
    """Calculates Simple Interest: SI = (P * R * T) / 100"""
    if principal <= 0:
        raise CalculationError("Principal amount must be greater than zero.")
    if annual_rate_pct < 0:
        raise CalculationError("Rate cannot be negative.")
    if years <= 0:
        raise CalculationError("Years must be greater than zero.")

    interest_raw = (principal * annual_rate_pct * years) / Decimal("100")
    total_interest = quantize_currency(interest_raw)
    total_amount = quantize_currency(principal + total_interest)

    return {
        "calculation_type": "simple_interest",
        "formula_version": "1.0.0",
        "formula": "SI = (P × R × T) / 100",
        "inputs": {
            "principal": str(quantize_currency(principal)),
            "annual_rate_pct": str(annual_rate_pct),
            "years": str(years),
            "currency": currency,
        },
        "result": {
            "total_interest": str(total_interest),
            "total_amount": str(total_amount),
        },
        "assumptions": [
            "Interest calculated on initial principal only without compounding.",
        ],
    }


def calculate_cagr(
    beginning_value: Decimal,
    ending_value: Decimal,
    years: Decimal,
) -> Dict[str, Any]:
    """Calculates Compound Annual Growth Rate (CAGR).

    CAGR = (EndingValue / BeginningValue)^(1 / years) - 1
    """
    if beginning_value <= 0:
        raise CalculationError("Beginning value must be greater than zero.")
    if ending_value <= 0:
        raise CalculationError("Ending value must be greater than zero.")
    if years <= 0:
        raise CalculationError("Time period in years must be greater than zero.")

    ratio = float(ending_value / beginning_value)
    time_exp = 1.0 / float(years)
    cagr_float = (ratio ** time_exp) - 1.0
    cagr_pct = quantize_rate(Decimal(str(cagr_float * 100.0)))
    absolute_growth = quantize_currency(ending_value - beginning_value)
    absolute_growth_pct = quantize_rate(Decimal(str(((ending_value - beginning_value) / beginning_value) * 100)))

    return {
        "calculation_type": "cagr",
        "formula_version": "1.0.0",
        "formula": "CAGR = (EndingValue / BeginningValue)^(1/years) - 1",
        "inputs": {
            "beginning_value": str(quantize_currency(beginning_value)),
            "ending_value": str(quantize_currency(ending_value)),
            "years": str(years),
        },
        "result": {
            "cagr_pct": f"{cagr_pct}%",
            "absolute_gain": str(absolute_growth),
            "absolute_gain_pct": f"{absolute_growth_pct}%",
        },
        "assumptions": [
            "Smoothed annual rate of investment growth assuming annual compounding.",
            "Does not account for volatility or interim cash inflows/outflows.",
        ],
    }


def calculate_percentage(
    principal: Decimal,
    percentage: Decimal,
    currency: str = "INR",
) -> Dict[str, Any]:
    """Calculates percentage share of an amount.
    
    Result = (Principal * Percentage) / 100
    """
    if principal < 0:
        raise CalculationError("Amount cannot be negative.")
    if percentage < 0:
        raise CalculationError("Percentage cannot be negative.")

    val_raw = (principal * percentage) / Decimal("100")
    result_val = quantize_currency(val_raw)

    return {
        "calculation_type": "percentage",
        "formula_version": "1.0.0",
        "formula": "Value = (Amount × Percentage) / 100",
        "inputs": {
            "amount": str(quantize_currency(principal)),
            "percentage": str(percentage),
            "currency": currency,
        },
        "result": {
            "calculated_value": str(result_val),
            "original_amount": str(quantize_currency(principal)),
            "percentage_rate": f"{percentage}%",
        },
        "assumptions": [
            "Exact arithmetic percentage calculation performed via Python Decimal.",
        ],
    }

