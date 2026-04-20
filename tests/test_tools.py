"""Tests for the search tool."""

from unittest.mock import MagicMock, patch

import pytest

from src.schemas import SearchResult
from src.tools.search_tool import SearchTool


@pytest.fixture
def mock_tavily_response():
    return {
        "results": [
            {
                "title": "Fusion energy breakthrough",
                "url": "https://example.com/fusion",
                "content": "Net energy gain achieved in 2024...",
                "score": 0.95,
            },
            {
                "title": "ITER project update",
                "url": "https://example.com/iter",
                "content": "First plasma expected in 2028...",
                "score": 0.87,
            },
        ]
    }


def test_search_returns_parsed_results(mock_tavily_response):
    """Search returns list of SearchResult with correct fields."""
    with patch("src.tools.search_tool.TavilyClient") as MockClient:
        instance = MagicMock()
        instance.search.return_value = mock_tavily_response
        MockClient.return_value = instance

        tool = SearchTool(api_key="fake-key")
        results = tool.search("fusion energy 2025", max_results=2)

        assert len(results) == 2
        assert isinstance(results[0], SearchResult)
        assert results[0].title == "Fusion energy breakthrough"
        assert results[0].score == 0.95


def test_search_returns_empty_list_on_exception():
    """Search gracefully handles API failures."""
    with patch("src.tools.search_tool.TavilyClient") as MockClient:
        instance = MagicMock()
        instance.search.side_effect = Exception("API down")
        MockClient.return_value = instance

        tool = SearchTool(api_key="fake-key")
        results = tool.search("anything")

        assert results == []


def test_search_handles_missing_fields():
    """Search tolerates partial Tavily responses."""
    with patch("src.tools.search_tool.TavilyClient") as MockClient:
        instance = MagicMock()
        instance.search.return_value = {
            "results": [{"url": "https://example.com"}]  # Missing title, content
        }
        MockClient.return_value = instance

        tool = SearchTool(api_key="fake-key")
        results = tool.search("test")

        assert len(results) == 1
        assert results[0].title == "Untitled"
        assert results[0].content == ""
