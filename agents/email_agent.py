from tools.gmail_tool import send_email_report
from langchain_core.prompts import ChatPromptTemplate
from utils.llm_factory import get_llm
import re
import os

def get_email_agent_response(
    query: str,
    last_report_text: str = "",
    provider: str = "groq",
    api_key: str = None,
    gmail_user: str = "",
    gmail_password: str = "",
    attachment_path: str = ""
) -> str:
    """
    Email Agent that parses recipient email, composes a professional cover message, and dispatches the email.
    """
    llm = get_llm(provider=provider, api_key=api_key)
    
    # Extract email address if present in query
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', query)
    recipient = match.group(0) if match else "client@alphavest.com"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an Investor Relations Director at AlphaVest Capital. "
            "Draft a concise, executive email cover letter summarizing the latest research report for a valued client. "
            "Provide a clear Subject line and Email Body."
        )),
        ("user", "User Request: {query}\n\nLatest Investment Report Content:\n{report}")
    ])
    
    email_draft = (prompt | llm).invoke({"query": query, "report": last_report_text[:1500] if last_report_text else "General Market & Company Analysis Report"}).content
    
    # Send email via tool
    user = gmail_user or os.getenv("GMAIL_USER", "")
    pwd = gmail_password or os.getenv("GMAIL_APP_PASSWORD", "")
    
    tool_status = send_email_report.invoke({
        "recipient_email": recipient,
        "subject": "AlphaVest Capital — Investment Research Briefing",
        "body": email_draft,
        "attachment_path": attachment_path,
        "gmail_user": user,
        "gmail_password": pwd
    })
    
    return f"**📧 Email Composition Cover Letter:**\n\n{email_draft}\n\n---\n**📬 Dispatch Status:**\n{tool_status}"
