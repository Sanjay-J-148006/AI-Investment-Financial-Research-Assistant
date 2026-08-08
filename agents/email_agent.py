from tools.gmail_tool import send_email_report
from langchain_core.prompts import ChatPromptTemplate
from utils.llm_factory import get_llm
import re

def get_email_agent_response(query: str, last_report_text: str = "", provider: str = "openai", api_key: str = None) -> str:
    """
    Email Agent that parses recipient email, composes a professional cover message, and dispatches the email.
    """
    llm = get_llm(provider=provider, api_key=api_key)
    
    # Extract email address if present
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', query)
    recipient = match.group(0) if match else "client@example.com"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an Investor Relations Director at AlphaVest Capital. "
            "Draft a concise, executive email cover letter summarizing the latest research report for a valued client. "
            "Provide a clear Subject line and Email Body."
        )),
        ("user", "User Request: {query}\n\nLatest Investment Report Content:\n{report}")
    ])
    
    email_draft = (prompt | llm).invoke({"query": query, "report": last_report_text[:1500] if last_report_text else "General Market & Company Analysis Report"}).content
    
    # Attempt to send email via tool
    tool_status = send_email_report.invoke({
        "recipient_email": recipient,
        "subject": "AlphaVest Capital — Investment Research Briefing",
        "body": email_draft
    })
    
    return f"**Email Composition Draft:**\n\n{email_draft}\n\n---\n**Dispatch Status:**\n{tool_status}"
