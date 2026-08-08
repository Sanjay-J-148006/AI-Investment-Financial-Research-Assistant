from pydantic import BaseModel, Field
from typing import List

class InvestmentReport(BaseModel):
    company_name: str = Field(description="Name of the company being analyzed")
    ticker: str = Field(description="Stock ticker symbol if available, e.g. NVDA, AAPL")
    company_overview: str = Field(description="Comprehensive business overview and core mission")
    industry: str = Field(description="Industry sector and primary market domain")
    business_model: str = Field(description="Revenue generation model and core value proposition")
    latest_news: str = Field(description="Summary of recent news, earnings results, and market updates")
    strengths: List[str] = Field(description="Key competitive advantages and operational strengths")
    weaknesses: List[str] = Field(description="Operational bottlenecks, disadvantages, or weaknesses")
    financial_highlights: str = Field(description="Key financial metrics, revenue, margins, or Growth figures")
    growth_opportunities: str = Field(description="Future expansion opportunities and strategic catalysts")
    potential_risks: str = Field(description="Market, regulatory, macroeconomic, or competitive risks")
    investment_summary: str = Field(description="Final analyst recommendation and investment verdict")
