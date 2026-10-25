from typing import List, Optional, Literal
from pydantic import BaseModel, Field

Mode = Literal["safety", "crack", "valuation", "planning", "daily_assistant", "knowledge"]

class Finding(BaseModel):
    title: str
    severity: Literal["low", "medium", "high", "critical", "unknown"] = "unknown"
    description: str
    recommendation: str

class Estimate(BaseModel):
    currency: str = "INR"
    low: Optional[float] = None
    high: Optional[float] = None
    assumptions: List[str] = Field(default_factory=list)

class AnalysisResponse(BaseModel):
    mode: Mode
    summary: str
    findings: List[Finding] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    estimate: Optional[Estimate] = None
    limitations: List[str] = Field(default_factory=list)
    source: Literal["ai", "demo"] = "demo"
