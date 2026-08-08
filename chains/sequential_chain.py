from agents.research_agent import get_research_agent_response
from agents.news_agent import get_news_agent_response
from agents.pdf_agent import get_pdf_agent_response
from chains.report_chain import generate_investment_report
from models.report_schema import InvestmentReport

def run_sequential_workflow(company_name: str, provider: str = "openai", api_key: str = None) -> dict:
    """
    Module 7: Executes an automated sequential pipeline:
    1. Gather Web & Wiki Research
    2. Gather Live Financial News
    3. Query PDF RAG Index
    4. Synthesize Structured Pydantic Investment Report
    """
    # Step 1: Research
    research_res = get_research_agent_response(company_name, provider=provider, api_key=api_key)
    
    # Step 2: Live News
    news_res = get_news_agent_response(company_name, provider=provider, api_key=api_key)
    
    # Step 3: PDF Document Query
    pdf_res = get_pdf_agent_response(f"{company_name} financial metrics risks revenue", provider=provider, api_key=api_key)
    
    # Step 4: Synthesize Report
    report: InvestmentReport = generate_investment_report(
        company_name=company_name,
        research_data=research_res,
        news_data=news_res,
        pdf_data=pdf_res,
        provider=provider,
        api_key=api_key
    )
    
    return {
        "research": research_res,
        "news": news_res,
        "pdf": pdf_res,
        "report": report
    }
