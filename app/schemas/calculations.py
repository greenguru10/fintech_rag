"""Calculation API schemas."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class EMIRequest(BaseModel):
    principal: str = Field(..., description="Principal loan amount, e.g. 500000 or '5 lakh'")
    annual_interest_rate_pct: str = Field(..., description="Annual interest rate percentage, e.g. 10.5")
    tenure_months: Optional[int] = Field(None, description="Tenure in months")
    tenure_years: Optional[float] = Field(None, description="Tenure in years")
    currency: str = "INR"
    include_schedule: bool = False


class SIPRequest(BaseModel):
    monthly_investment: str = Field(..., description="Monthly investment amount, e.g. 10000")
    annual_return_pct: str = Field(..., description="Assumed annual return percentage, e.g. 12")
    years: float = Field(..., gt=0, description="Duration in years")
    payment_timing: str = Field("end_of_period", description="'end_of_period' or 'beginning_of_period'")
    currency: str = "INR"


class CompoundInterestRequest(BaseModel):
    principal: str = Field(..., description="Initial principal amount")
    annual_rate_pct: str = Field(..., description="Annual interest rate percentage")
    years: float = Field(..., gt=0, description="Duration in years")
    compounds_per_year: int = Field(4, ge=1, description="Compounding events per year (e.g. 4 for quarterly)")
    currency: str = "INR"


class CAGRRequest(BaseModel):
    beginning_value: str = Field(..., description="Initial investment value")
    ending_value: str = Field(..., description="Final investment value")
    years: float = Field(..., gt=0, description="Number of years")


class CalculationResponse(BaseModel):
    request_id: str
    calculation_type: str
    formula_version: str
    formula: str
    inputs: Dict[str, Any]
    result: Dict[str, Any]
    assumptions: List[str]
    schedule: Optional[List[Dict[str, Any]]] = None
