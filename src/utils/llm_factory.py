"""Provider-agnostic LLM factory.

Lets us swap between OpenAI and Anthropic without touching the agent code.
"""

from langchain_core.language_models.chat_models import BaseChatModel

from src.utils.config import config


def get_llm(temperature: float | None = None) -> BaseChatModel:
    """Return a LangChain chat model based on env configuration.

    Args:
        temperature: Override the default temperature. If None, uses config.

    Returns:
        A LangChain BaseChatModel instance (either ChatOpenAI or ChatAnthropic).

    Raises:
        ValueError: If LLM_PROVIDER is not supported.
    """
    temp = temperature if temperature is not None else config.llm_temperature

    if config.llm_provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=config.llm_model,
            temperature=temp,
            api_key=config.openai_api_key,
        )

    if config.llm_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=config.llm_model,
            temperature=temp,
            api_key=config.anthropic_api_key,
            max_tokens=4096,
        )

    raise ValueError(f"Unsupported LLM provider: {config.llm_provider}")
