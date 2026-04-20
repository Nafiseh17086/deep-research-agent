"""Configuration loading from environment variables."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    """Immutable application configuration loaded from environment."""

    # Provider
    llm_provider: str
    llm_model: str
    llm_temperature: float

    # API Keys
    openai_api_key: str
    anthropic_api_key: str
    tavily_api_key: str

    # Agent behavior
    max_sub_questions: int
    max_search_results: int

    # Observability
    langsmith_tracing: bool
    langsmith_api_key: str
    langsmith_project: str

    @classmethod
    def from_env(cls) -> "Config":
        """Load config from environment variables with sensible defaults."""
        provider = os.getenv("LLM_PROVIDER", "anthropic").lower()

        # Pick a default model if none specified
        default_models = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-haiku-4-5-20251001",
        }
        model = os.getenv("LLM_MODEL") or default_models.get(provider, "")

        return cls(
            llm_provider=provider,
            llm_model=model,
            llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
            max_sub_questions=int(os.getenv("MAX_SUB_QUESTIONS", "5")),
            max_search_results=int(os.getenv("MAX_SEARCH_RESULTS", "5")),
            langsmith_tracing=os.getenv("LANGSMITH_TRACING", "false").lower() == "true",
            langsmith_api_key=os.getenv("LANGSMITH_API_KEY", ""),
            langsmith_project=os.getenv("LANGSMITH_PROJECT", "deep-research-agent"),
        )

    def validate(self) -> None:
        """Raise ValueError if required keys are missing."""
        if self.llm_provider not in ("openai", "anthropic"):
            raise ValueError(
                f"Invalid LLM_PROVIDER: {self.llm_provider}. "
                "Must be 'openai' or 'anthropic'."
            )

        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")

        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic"
            )

        if not self.tavily_api_key:
            raise ValueError("TAVILY_API_KEY is required for web search")


# Module-level singleton
config = Config.from_env()
