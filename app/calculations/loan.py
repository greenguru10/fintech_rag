"""Loan and EMI calculation engine using Python Decimal arithmetic."""

from decimal import Decimal
from typing import Dict, Any, List
from app.calculations.common import quantize_currency
from app.core.exceptions import CalculationError


def calculate_emi(
    principal: Decimal,
    annual_rate_pct: Decimal,
    tenure_months: int,
    include_schedule: bool = False,
    currency: str = "INR",
) -> Dict[str, Any]:
    """Calculates Equated Monthly Instalment (EMI), total interest, and total payment.

    Formula:
    EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
    where:
      P = Principal
      r = Monthly interest rate (annual_rate_pct / 1200)
      n = Tenure in months
    """
    if principal <= 0:
        raise CalculationError("Principal amount must be greater than zero.")
    if tenure_months <= 0:
        raise CalculationError("Tenure months must be greater than zero.")
    if annual_rate_pct < 0:
        raise CalculationError("Annual interest rate cannot be negative.")

    # Zero-interest loan special case
    if annual_rate_pct == Decimal("0"):
        monthly_emi = quantize_currency(principal / Decimal(tenure_months))
        total_payment = quantize_currency(monthly_emi * Decimal(tenure_months))
        total_interest = Decimal("0.00")
        schedule = []
        if include_schedule:
            balance = principal
            for month in range(1, tenure_months + 1):
                balance -= monthly_emi
                schedule.append({
                    "month": month,
                    "payment": str(monthly_emi),
                    "principal_paid": str(monthly_emi),
                    "interest_paid": "0.00",
                    "remaining_balance": str(quantize_currency(max(Decimal("0.00"), balance))),
                })
        return {
            "calculation_type": "emi",
            "formula_version": "1.0.0",
            "formula": "EMI = Principal / Tenure (Zero Interest)",
            "inputs": {
                "principal": str(quantize_currency(principal)),
                "annual_interest_rate_pct": str(annual_rate_pct),
                "tenure_months": tenure_months,
                "currency": currency,
            },
            "result": {
                "monthly_emi": str(monthly_emi),
                "total_payment": str(total_payment),
                "total_interest": str(total_interest),
            },
            "assumptions": [
                "Zero interest rate applies for entire tenure.",
                "Equal monthly payments.",
                "Processing fees, statutory taxes, and insurance are excluded.",
            ],
            "schedule": schedule if include_schedule else None,
        }

    monthly_rate = annual_rate_pct / Decimal("1200")
    factor = (Decimal("1") + monthly_rate) ** tenure_months
    emi = principal * monthly_rate * factor / (factor - Decimal("1"))
    monthly_emi = quantize_currency(emi)
    total_payment = quantize_currency(monthly_emi * Decimal(tenure_months))
    total_interest = quantize_currency(total_payment - principal)

    schedule: List[Dict[str, Any]] = []
    if include_schedule:
        balance = principal
        for month in range(1, tenure_months + 1):
            interest_month = quantize_currency(balance * monthly_rate)
            principal_month = quantize_currency(monthly_emi - interest_month)
            balance = balance - principal_month
            if month == tenure_months:
                # Adjust rounding on final installment
                balance = Decimal("0.00")
            schedule.append({
                "month": month,
                "payment": str(monthly_emi),
                "principal_paid": str(principal_month),
                "interest_paid": str(interest_month),
                "remaining_balance": str(quantize_currency(max(Decimal("0.00"), balance))),
            })

    return {
        "calculation_type": "emi",
        "formula_version": "1.0.0",
        "formula": "EMI = P × r × (1+r)^n / ((1+r)^n - 1)",
        "inputs": {
            "principal": str(quantize_currency(principal)),
            "annual_interest_rate_pct": str(annual_rate_pct),
            "tenure_months": tenure_months,
            "currency": currency,
        },
        "result": {
            "monthly_emi": str(monthly_emi),
            "total_payment": str(total_payment),
            "total_interest": str(total_interest),
        },
        "assumptions": [
            "Interest rate remains constant for the full tenure.",
            "Payments are made monthly.",
            "Processing fees, insurance, taxes, prepayments, and penalties are excluded.",
        ],
        "schedule": schedule if include_schedule else None,
    }
