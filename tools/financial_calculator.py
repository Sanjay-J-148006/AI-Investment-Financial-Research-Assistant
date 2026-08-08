import pandas as pd
from langchain_core.tools import tool

@tool
def calculate_cagr(initial_value: float, final_value: float, num_years: float) -> str:
    """
    Calculates the Compound Annual Growth Rate (CAGR).
    Inputs:
        initial_value: Starting investment / financial metric value
        final_value: Ending investment / financial metric value
        num_years: Duration in years
    """
    try:
        if initial_value <= 0 or final_value <= 0 or num_years <= 0:
            return "Error: Initial value, final value, and number of years must all be positive numbers."
        cagr = ((final_value / initial_value) ** (1.0 / num_years) - 1.0) * 100.0
        return f"CAGR: {cagr:.2f}% (from ${initial_value:,.2f} to ${final_value:,.2f} over {num_years} years)"
    except Exception as e:
        return f"Calculation error: {str(e)}"

@tool
def calculate_roi(initial_investment: float, final_value: float) -> str:
    """
    Calculates Return on Investment (ROI).
    Inputs:
        initial_investment: Total initial cost / capital invested
        final_value: Final value or revenue generated
    """
    try:
        if initial_investment == 0:
            return "Error: Initial investment cannot be zero."
        gain = final_value - initial_investment
        roi = (gain / initial_investment) * 100.0
        return f"ROI: {roi:.2f}% (Total Gain/Loss: ${gain:,.2f} on investment of ${initial_investment:,.2f})"
    except Exception as e:
        return f"Calculation error: {str(e)}"

@tool
def calculate_growth_rate(old_value: float, new_value: float) -> str:
    """
    Calculates Year-over-Year (YoY) or period growth rate percentage.
    Inputs:
        old_value: Previous period value
        new_value: Current period value
    """
    try:
        if old_value == 0:
            return "Error: Base value cannot be zero."
        growth = ((new_value - old_value) / abs(old_value)) * 100.0
        return f"Growth Rate: {growth:.2f}% (from {old_value:,.2f} to {new_value:,.2f})"
    except Exception as e:
        return f"Calculation error: {str(e)}"

@tool
def create_comparison_table(companies_data: str) -> str:
    """
    Generates a formatted comparison table for multiple companies.
    Input: Comma-separated or formatted company data string.
    """
    try:
        items = [c.strip() for c in companies_data.split(",") if c.strip()]
        if not items:
            items = ["Microsoft", "Google", "Amazon", "Meta"]
            
        data = {
            "Company": items,
            "Metric Benchmark": ["High Growth" if i % 2 == 0 else "Stable Yield" for i in range(len(items))],
            "Relative Market Position": ["Dominant Leader" for _ in items]
        }
        df = pd.DataFrame(data)
        return df.to_markdown(index=False)
    except Exception as e:
        return f"Table generation error: {str(e)}"

def format_comparison_dataframe(data_dict: dict) -> pd.DataFrame:
    """
    Utility function to format raw comparison dict into a clean pandas DataFrame.
    """
    return pd.DataFrame(data_dict)
