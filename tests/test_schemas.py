"""Tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from src.schemas import (
    ResearchPlan,
    ResearchReport,
    ReviewFeedback,
    SearchResult,
    SubQuestion,
)


def test_search_result_requires_title_url_content():
    """SearchResult validates required fields."""
    with pytest.raises(ValidationError):
        SearchResult(url="https://example.com", content="x")  # missing title


def test_review_feedback_score_bounded():
    """Quality score must be between 1 and 10."""
    with pytest.raises(ValidationError):
        ReviewFeedback(
            is_sufficient=True,
            quality_score=11,
            comments="Too high",
        )

    with pytest.raises(ValidationError):
        ReviewFeedback(
            is_sufficient=True,
            quality_score=0,
            comments="Too low",
        )


def test_research_plan_accepts_empty_sub_questions():
    """ResearchPlan can have zero sub-questions (edge case)."""
    plan = ResearchPlan(
        main_question="Test?",
        sub_questions=[],
        estimated_complexity="simple",
    )
    assert plan.sub_questions == []


def test_research_report_sets_timestamp_automatically():
    """generated_at is auto-populated."""
    report = ResearchReport(
        query="Test",
        markdown="# Report",
        sources=[],
        sub_questions=[],
    )
    assert report.generated_at is not None
