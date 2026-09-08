"""Common math and currency helpers for financial calculation engine."""

from decimal import Decimal, ROUND_HALF_UP
from typing import Tuple


def quantize_currency(value: Decimal) -> Decimal:
    """Rounds to 2 decimal places using standard ROUND_HALF_UP."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def quantize_rate(value: Decimal) -> Decimal:
    """Rounds percentage to 2 decimal places."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def format_indian_currency(amount: Decimal, currency: str = "INR") -> str:
    """Formats amount with Indian numbering system (e.g. ₹10,623.52, ₹5,00,000.00)."""
    q_amount = quantize_currency(amount)
    is_negative = q_amount < 0
    abs_amount = abs(q_amount)

    str_val = f"{abs_amount:.2f}"
    int_part, dec_part = str_val.split(".")

    if len(int_part) <= 3:
        formatted_int = int_part
    else:
        last_three = int_part[-3:]
        remaining = int_part[:-3]
        groups = []
        while len(remaining) > 2:
            groups.append(remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.append(remaining)
        groups.reverse()
        formatted_int = ",".join(groups) + "," + last_three

    sign = "-" if is_negative else ""
    symbol = "₹" if currency.upper() == "INR" else f"{currency} "
    return f"{sign}{symbol}{formatted_int}.{dec_part}"
