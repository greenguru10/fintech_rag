"""Validation and parsing of money, percentages, and tenures."""

import re
from decimal import Decimal, InvalidOperation
from app.core.exceptions import CalculationError


def parse_money(value: str | int | float | Decimal, field_name: str = "amount") -> Decimal:
    """Parses numeric string or Indian notation (e.g. 5 lakh, 1.5 crore, ₹50,000, 100 rs) into Decimal."""
    if isinstance(value, Decimal):
        val = value
    elif isinstance(value, (int, float)):
        val = Decimal(str(value))
    elif isinstance(value, str):
        clean = value.strip().replace("₹", "").replace(",", "").strip()
        clean = re.sub(r"(?i)\b(rs\.?|inr|rupees|bucks|salary)\b|/-", "", clean).strip()
        lower = clean.lower()
        if "lakh" in lower or "lac" in lower:
            num_part = re.sub(r"[a-zA-Z\s]", "", lower)
            try:
                val = Decimal(num_part) * Decimal("100000")
            except InvalidOperation:
                raise CalculationError(f"Invalid monetary format for '{field_name}': {value}")
        elif "crore" in lower or "cr" in lower:
            num_part = re.sub(r"[a-zA-Z\s]", "", lower)
            try:
                val = Decimal(num_part) * Decimal("10000000")
            except InvalidOperation:
                raise CalculationError(f"Invalid monetary format for '{field_name}': {value}")
        elif "k" in lower:
            num_part = re.sub(r"[a-zA-Z\s]", "", lower)
            try:
                val = Decimal(num_part) * Decimal("1000")
            except InvalidOperation:
                raise CalculationError(f"Invalid monetary format for '{field_name}': {value}")
        else:
            try:
                num_part = re.sub(r"[^\d.]", "", clean)
                val = Decimal(num_part)
            except InvalidOperation:
                raise CalculationError(f"Invalid numeric value for '{field_name}': {value}")
    else:
        raise CalculationError(f"Invalid type for '{field_name}': {type(value)}")

    if val < 0:
        raise CalculationError(f"'{field_name}' must be non-negative.")
    return val


def parse_rate(value: str | int | float | Decimal, field_name: str = "interest rate") -> Decimal:
    """Parses percentage string (e.g. 10.5%, 8.5) into Decimal."""
    if isinstance(value, Decimal):
        val = value
    elif isinstance(value, (int, float)):
        val = Decimal(str(value))
    elif isinstance(value, str):
        clean = value.strip().replace("%", "").replace("percent", "").strip()
        try:
            val = Decimal(clean)
        except InvalidOperation:
            raise CalculationError(f"Invalid percentage rate for '{field_name}': {value}")
    else:
        raise CalculationError(f"Invalid type for '{field_name}': {type(value)}")

    if val < 0:
        raise CalculationError(f"'{field_name}' cannot be negative.")
    if val > 100:
        raise CalculationError(f"'{field_name}' exceeds 100%. Please provide an annual percentage rate.")
    return val


def parse_tenure_months(tenure: str | int | float, unit: str = "years") -> int:
    """Parses tenure into total months."""
    if isinstance(tenure, str):
        lower = tenure.lower().strip()
        lower = re.sub(r"^(in|for)\s+", "", lower).strip()
        if any(y in lower for y in ["year", "yr", "yera", "yrs"]):
            num_part = re.sub(r"[a-zA-Z\s]", "", lower)
            months = int(float(num_part) * 12)
        elif any(m in lower for m in ["month", "mo", "mos"]):
            num_part = re.sub(r"[a-zA-Z\s]", "", lower)
            months = int(float(num_part))
        else:
            try:
                num_part = re.sub(r"[^\d.]", "", lower)
                val = float(num_part)
                months = int(val * 12) if unit.lower().startswith("year") else int(val)
            except (ValueError, InvalidOperation):
                raise CalculationError(f"Invalid tenure representation: {tenure}")
    elif isinstance(tenure, (int, float)):
        months = int(tenure * 12) if unit.lower().startswith("year") else int(tenure)
    else:
        raise CalculationError(f"Invalid tenure: {tenure}")

    if months <= 0:
        raise CalculationError("Tenure must be at least 1 month.")
    if months > 600:  # 50 years max
        raise CalculationError("Tenure exceeds realistic maximum of 50 years (600 months).")
    return months
