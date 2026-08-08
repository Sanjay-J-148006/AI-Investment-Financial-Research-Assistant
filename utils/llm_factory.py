import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

def get_llm(
    provider: Optional[str] = None,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.2
):
    """
    Factory function returning a LangChain LLM instance based on provider.
    Supports 'openai', 'google' (Gemini), and 'groq'.
    """
    provider = (provider or os.getenv("DEFAULT_LLM_PROVIDER", "openai")).lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OpenAI API Key is missing. Please provide it in the sidebar or .env file.")
        model = model_name or os.getenv("DEFAULT_MODEL_NAME", "gpt-4o-mini")
        return ChatOpenAI(model_name=model, openai_api_key=key, temperature=temperature)

    elif provider in ["google", "gemini"]:
        from langchain_google_genai import ChatGoogleGenerativeAI
        key = api_key or os.getenv("GOOGLE_API_KEY")
        if not key:
            raise ValueError("Google Gemini API Key is missing. Please provide it in the sidebar or .env file.")
        model = model_name or "gemini-1.5-flash"
        return ChatGoogleGenerativeAI(model=model, google_api_key=key, temperature=temperature)

    elif provider == "groq":
        from langchain_groq import ChatGroq
        key = api_key or os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError("Groq API Key is missing. Please provide it in the sidebar or .env file.")
        model = model_name or "llama-3.3-70b-versatile"
        return ChatGroq(model_name=model, groq_api_key=key, temperature=temperature)

    else:
        # Fallback to ChatOpenAI if possible or raise error
        from langchain_openai import ChatOpenAI
        key = api_key or os.getenv("OPENAI_API_KEY")
        if key:
            return ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=key, temperature=temperature)
        raise ValueError(f"Unsupported provider '{provider}' and no OpenAI API key found.")
