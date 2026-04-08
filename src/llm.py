import os
from langchain_core.language_models import BaseChatModel

# Ollama is listed first so it becomes the default index (0) locally.
# is_cloud() in st_app.py shifts the default to OpenAI on Streamlit Cloud.
PROVIDER_DEFAULTS = {
    "Ollama": "llama3.2",
    "OpenAI": "gpt-4o-mini",
    "Groq": "llama-3.1-8b-instant",
    "Anthropic": "claude-haiku-4-5-20251001",
    "Google": "gemini-2.0-flash",
}

# Providers that require an API key (Ollama runs locally, no key needed)
REQUIRES_API_KEY = {"OpenAI", "Groq", "Anthropic", "Google"}


def is_cloud() -> bool:
    """Return True when running on Streamlit Cloud."""
    return os.environ.get("STREAMLIT_SHARING_MODE") == "streamlit"


def get_models(provider: str, api_key: str = "") -> list[str]:
    """Fetch available chat model IDs from the provider's API.

    Args:
        provider: One of the keys in PROVIDER_DEFAULTS.
        api_key: The provider API key. Not required for Ollama.

    Returns:
        Sorted list of model ID strings.

    Raises:
        Exception: Re-raises auth or network errors so the caller can surface them.
    """
    if provider == "Ollama":
        import ollama
        return sorted(m.model for m in ollama.list().models)

    if provider == "OpenAI":
        from openai import OpenAI
        models = OpenAI(api_key=api_key).models.list()
        return sorted(m.id for m in models if "gpt" in m.id)

    if provider == "Anthropic":
        from anthropic import Anthropic
        response = Anthropic(api_key=api_key).models.list()
        return sorted(m.id for m in response.data)

    if provider == "Groq":
        from groq import Groq
        response = Groq(api_key=api_key).models.list()
        return sorted(m.id for m in response.data if m.active)

    if provider == "Google":
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        models = genai.list_models()
        return sorted(
            m.name.removeprefix("models/")
            for m in models
            if "generateContent" in m.supported_generation_methods
        )

    raise ValueError(f"Unsupported provider: {provider!r}")


def get_llm(provider: str, model: str | None = None, api_key: str = "") -> BaseChatModel:
    """Return a chat model for the given provider.

    Args:
        provider: One of the keys in PROVIDER_DEFAULTS.
        model: Optional model name override. Falls back to PROVIDER_DEFAULTS.
        api_key: API key (not required for Ollama).

    Returns:
        A LangChain BaseChatModel instance.
    """
    resolved_model = model or PROVIDER_DEFAULTS.get(provider)

    if provider == "Ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=resolved_model)

    if provider == "OpenAI":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=resolved_model, api_key=api_key)

    if provider == "Anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=resolved_model, api_key=api_key)

    if provider == "Google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model=resolved_model, google_api_key=api_key)

    if provider == "Groq":
        from langchain_groq import ChatGroq
        return ChatGroq(model=resolved_model, api_key=api_key)

    raise ValueError(f"Unsupported provider: {provider!r}. Choose from: {list(PROVIDER_DEFAULTS)}")
