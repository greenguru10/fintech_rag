"""Financial calculation endpoints."""

import uuid
from decimal import Decimal
from fastapi import APIRouter
from app.schemas.calculations import (
    EMIRequest,
    SIPRequest,
    CompoundInterestRequest,
    CAGRRequest,
    CalculationResponse,
)
from app.calculations.loan import calculate_emi
from app.calculations.investment import (
    calculate_sip,
    calculate_compound_interest,
    calculate_cagr,
    calculate_simple_interest,
)
from app.calculations.validators import parse_money, parse_rate, parse_tenure_months

router = APIRouter(prefix="/calculate", tags=["Calculations"])


@router.post("/emi", response_model=CalculationResponse)
def compute_emi(req: EMIRequest):
    principal = parse_money(req.principal, "principal")
    rate = parse_rate(req.annual_interest_rate_pct, "annual_interest_rate_pct")

    if req.tenure_months:
        months = req.tenure_months
    elif req.tenure_years:
        months = int(req.tenure_years * 12)
    else:
        months = 60  # Default 5 years

    res = calculate_emi(
        principal=principal,
        annual_rate_pct=rate,
        tenure_months=months,
        include_schedule=req.include_schedule,
        currency=req.currency,
    )

    return CalculationResponse(
        request_id=f"req_{uuid.uuid4().hex[:12]}",
        calculation_type=res["calculation_type"],
        formula_version=res["formula_version"],
        formula=res["formula"],
        inputs=res["inputs"],
        result=res["result"],
        assumptions=res["assumptions"],
        schedule=res.get("schedule"),
    )


@router.post("/sip", response_model=CalculationResponse)
def compute_sip(req: SIPRequest):
    monthly_inv = parse_money(req.monthly_investment, "monthly_investment")
    ret_rate = parse_rate(req.annual_return_pct, "annual_return_pct")
    years = Decimal(str(req.years))

    res = calculate_sip(
        monthly_investment=monthly_inv,
        annual_return_pct=ret_rate,
        years=years,
        payment_timing=req.payment_timing,
        currency=req.currency,
    )

    return CalculationResponse(
        request_id=f"req_{uuid.uuid4().hex[:12]}",
        calculation_type=res["calculation_type"],
        formula_version=res["formula_version"],
        formula=res["formula"],
        inputs=res["inputs"],
        result=res["result"],
        assumptions=res["assumptions"],
    )


@router.post("/compound-interest", response_model=CalculationResponse)
def compute_compound_interest(req: CompoundInterestRequest):
    principal = parse_money(req.principal, "principal")
    rate = parse_rate(req.annual_rate_pct, "annual_rate_pct")
    years = Decimal(str(req.years))

    res = calculate_compound_interest(
        principal=principal,
        annual_rate_pct=rate,
        years=years,
        compounds_per_year=req.compounds_per_year,
        currency=req.currency,
    )

    return CalculationResponse(
        request_id=f"req_{uuid.uuid4().hex[:12]}",
        calculation_type=res["calculation_type"],
        formula_version=res["formula_version"],
        formula=res["formula"],
        inputs=res["inputs"],
        result=res["result"],
        assumptions=res["assumptions"],
    )


@router.post("/cagr", response_model=CalculationResponse)
def compute_cagr(req: CAGRRequest):
    bv = parse_money(req.beginning_value, "beginning_value")
    ev = parse_money(req.ending_value, "ending_value")
    years = Decimal(str(req.years))

    res = calculate_cagr(
        beginning_value=bv,
        ending_value=ev,
        years=years,
    )

    return CalculationResponse(
        request_id=f"req_{uuid.uuid4().hex[:12]}",
        calculation_type=res["calculation_type"],
        formula_version=res["formula_version"],
        formula=res["formula"],
        inputs=res["inputs"],
        result=res["result"],
        assumptions=res["assumptions"],
    )
