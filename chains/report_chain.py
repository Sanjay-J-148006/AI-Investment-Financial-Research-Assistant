from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from models.report_schema import InvestmentReport
from utils.llm_factory import get_llm

def generate_investment_report(company_name: str, research_data: str, news_data: str = "", pdf_data: str = "", provider: str = "openai", api_key: str = None) -> InvestmentReport:
    """
    Generates a structured Pydantic InvestmentReport object using LCEL chain with PydanticOutputParser.
    """
    parser = PydanticOutputParser(pydantic_object=InvestmentReport)
    llm = get_llm(provider=provider, api_key=api_key)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are the Head of Research at AlphaVest Capital. "
            "Synthesize all provided company research, news updates, and PDF document disclosures into a formal structured Investment Report. "
            "Strictly satisfy the requested output schema format.\n\n"
            "{format_instructions}"
        )),
        ("user", (
            "Target Company: {company_name}\n\n"
            "Company Research Data:\n{research_data}\n\n"
            "Recent News Data:\n{news_data}\n\n"
            "PDF RAG Document Data:\n{pdf_data}"
        ))
    ])
    
    chain = prompt | llm | parser
    
    report = chain.invoke({
        "company_name": company_name,
        "research_data": research_data[:2000] if research_data else "N/A",
        "news_data": news_data[:2000] if news_data else "N/A",
        "pdf_data": pdf_data[:2000] if pdf_data else "N/A",
        "format_instructions": parser.get_format_instructions()
    })
    
    return report
