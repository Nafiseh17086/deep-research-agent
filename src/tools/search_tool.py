"""Tavily search tool wrapper with retry logic and error handling."""

from typing import List

from tavily import TavilyClient

from src.schemas import SearchResult
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SearchTool:
    """Wrapper around Tavily's search API with defensive error handling."""

    def __init__(self, api_key: str | None = None):
        self.client = TavilyClient(api_key=api_key or config.tavily_api_key)

    def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "advanced",
    ) -> List[SearchResult]:
        """Perform a web search and return parsed results.

        Args:
            query: The search query.
            max_results: Max number of results to return.
            search_depth: 'basic' (faster) or 'advanced' (deeper).

        Returns:
            A list of SearchResult objects. Empty list on failure.
        """
        try:
            logger.info(f"🔍 Searching: {query}")
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                include_answer=False,
            )

            results = [
                SearchResult(
                    title=r.get("title", "Untitled"),
                    url=r.get("url", ""),
                    content=r.get("content", ""),
                    score=r.get("score", 0.0),
                )
                for r in response.get("results", [])
            ]

            logger.info(f"   ↳ Got {len(results)} results")
            return results

        except Exception as exc:
            logger.error(f"Search failed for '{query}': {exc}")
            return []
