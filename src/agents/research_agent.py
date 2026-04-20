"""Deep Research Agent built with LangGraph.

The agent is a state graph of 5 nodes:
    planner -> researcher -> synthesizer -> writer -> reviewer

The reviewer can loop back to researcher if the report has gaps.
"""

from __future__ import annotations

from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

from src.schemas import (
    AgentState,
    ResearchPlan,
    ResearchReport,
    ReviewFeedback,
    SubQuestion,
)
from src.tools.search_tool import SearchTool
from src.utils.config import config
from src.utils.llm_factory import get_llm
from src.utils.logger import get_logger

logger = get_logger(__name__)

MAX_ITERATIONS = 2  # Cap on reviewer-triggered re-research


class DeepResearchAgent:
    """Orchestrates a multi-step research workflow using LangGraph."""

    def __init__(self, provider: str | None = None):
        if provider:
            # Allow override at construction time
            import os

            os.environ["LLM_PROVIDER"] = provider

        config.validate()
        self.llm = get_llm()
        self.search_tool = SearchTool()
        self.graph = self._build_graph()

    # ------------------------------------------------------------------
    # Graph construction
    # ------------------------------------------------------------------

    def _build_graph(self):
        """Wire up the LangGraph state machine."""
        graph = StateGraph(AgentState)

        graph.add_node("planner", self._plan)
        graph.add_node("researcher", self._research)
        graph.add_node("synthesizer", self._synthesize)
        graph.add_node("writer", self._write)
        graph.add_node("reviewer", self._review)

        graph.set_entry_point("planner")
        graph.add_edge("planner", "researcher")
        graph.add_edge("researcher", "synthesizer")
        graph.add_edge("synthesizer", "writer")
        graph.add_edge("writer", "reviewer")

        # Conditional edge: reviewer decides continue or loop back
        graph.add_conditional_edges(
            "reviewer",
            self._route_after_review,
            {
                "continue": END,
                "revise": "researcher",
            },
        )

        return graph.compile()

    # ------------------------------------------------------------------
    # Node implementations
    # ------------------------------------------------------------------

    def _plan(self, state: AgentState) -> dict:
        """Decompose the query into researchable sub-questions."""
        logger.info("🧠 [PLANNER] Decomposing query into sub-questions")

        structured_llm = self.llm.with_structured_output(ResearchPlan)

        system = SystemMessage(
            content=(
                "You are a research strategist. Break the user's question into "
                f"{config.max_sub_questions} or fewer focused sub-questions that, "
                "taken together, would produce a comprehensive answer. "
                "Each sub-question should be specific enough to search the web for. "
                "Include a brief rationale for each."
            )
        )
        user = HumanMessage(content=f"Main question: {state['query']}")

        plan: ResearchPlan = structured_llm.invoke([system, user])
        logger.info(f"   ↳ Generated {len(plan.sub_questions)} sub-questions")

        return {"plan": plan, "iteration": state.get("iteration", 0)}

    def _research(self, state: AgentState) -> dict:
        """Execute web searches for each sub-question in parallel."""
        logger.info("🔍 [RESEARCHER] Executing web searches")

        plan = state["plan"]
        if plan is None:
            return {"sub_questions": []}

        # For simplicity we search sequentially. For true parallelism, wrap
        # each search call in asyncio.gather() — left as an exercise.
        enriched = []
        for sq in plan.sub_questions:
            results = self.search_tool.search(
                query=sq.question,
                max_results=config.max_search_results,
            )
            enriched.append(
                SubQuestion(
                    question=sq.question,
                    rationale=sq.rationale,
                    results=results,
                )
            )

        return {"sub_questions": enriched}

    def _synthesize(self, state: AgentState) -> dict:
        """Consolidate search results into a coherent synthesis."""
        logger.info("🧩 [SYNTHESIZER] Consolidating findings")

        context_blocks = []
        for sq in state["sub_questions"]:
            block = f"### Sub-question: {sq.question}\n\n"
            for i, r in enumerate(sq.results, start=1):
                block += f"[{i}] {r.title}\n{r.url}\n{r.content[:500]}...\n\n"
            context_blocks.append(block)

        context = "\n\n".join(context_blocks)

        system = SystemMessage(
            content=(
                "You are a research synthesizer. Given search results for multiple "
                "sub-questions, produce a coherent synthesis that identifies key "
                "themes, resolves contradictions, and highlights the most important "
                "findings. Preserve source URLs for later citation."
            )
        )
        user = HumanMessage(
            content=f"Main question: {state['query']}\n\nResearch context:\n{context}"
        )

        response = self.llm.invoke([system, user])
        return {"synthesis": response.content}

    def _write(self, state: AgentState) -> dict:
        """Generate the final markdown report with citations."""
        logger.info("✍️  [WRITER] Drafting the final report")

        # Collect all unique URLs for citation
        all_sources = []
        for sq in state["sub_questions"]:
            for r in sq.results:
                if r.url and r.url not in all_sources:
                    all_sources.append(r.url)

        citations = "\n".join(
            f"[{i + 1}] {url}" for i, url in enumerate(all_sources)
        )

        system = SystemMessage(
            content=(
                "You are a professional research writer. Using the provided "
                "synthesis and source list, produce a structured markdown report. "
                "Include the following sections:\n"
                "  1. Executive Summary (3-5 sentences)\n"
                "  2. Key Findings (bulleted, with inline [N] citations)\n"
                "  3. Detailed Analysis (prose, multiple paragraphs)\n"
                "  4. Limitations & Open Questions\n"
                "  5. Sources (numbered list of URLs)\n\n"
                "Use the numbering from the provided source list for citations."
            )
        )
        user = HumanMessage(
            content=(
                f"# Research Question\n{state['query']}\n\n"
                f"# Synthesis\n{state['synthesis']}\n\n"
                f"# Available Sources\n{citations}"
            )
        )

        response = self.llm.invoke([system, user])
        return {"draft_report": response.content}

    def _review(self, state: AgentState) -> dict:
        """Review the draft and decide if re-research is needed."""
        logger.info("🔎 [REVIEWER] Evaluating report quality")

        structured_llm = self.llm.with_structured_output(ReviewFeedback)

        system = SystemMessage(
            content=(
                "You are a critical reviewer of research reports. Evaluate the "
                "draft on completeness, accuracy, citation usage, and logical "
                "coherence. Score from 1-10. Only flag as insufficient if there "
                "are critical gaps — minor issues should still pass."
            )
        )
        user = HumanMessage(
            content=(
                f"Original question: {state['query']}\n\n"
                f"Draft report:\n{state['draft_report']}"
            )
        )

        review: ReviewFeedback = structured_llm.invoke([system, user])
        iteration = state.get("iteration", 0) + 1

        logger.info(
            f"   ↳ Quality: {review.quality_score}/10 | "
            f"Sufficient: {review.is_sufficient}"
        )

        return {"review": review, "iteration": iteration}

    # ------------------------------------------------------------------
    # Routing logic
    # ------------------------------------------------------------------

    def _route_after_review(
        self, state: AgentState
    ) -> Literal["continue", "revise"]:
        """Decide whether to end or loop back for more research."""
        review = state.get("review")
        iteration = state.get("iteration", 0)

        if review is None or review.is_sufficient or iteration >= MAX_ITERATIONS:
            return "continue"

        logger.info("   ↳ Review flagged gaps — looping back to researcher")
        return "revise"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, query: str) -> ResearchReport:
        """Execute the full research pipeline.

        Args:
            query: The user's research question.

        Returns:
            A ResearchReport with the final markdown and metadata.
        """
        logger.info(f"🚀 Starting research: {query}")

        initial_state: AgentState = {
            "query": query,
            "plan": None,
            "sub_questions": [],
            "synthesis": None,
            "draft_report": None,
            "review": None,
            "iteration": 0,
            "final_report": None,
        }

        final_state = self.graph.invoke(initial_state)

        # Collect sources
        sources = []
        for sq in final_state["sub_questions"]:
            for r in sq.results:
                if r.url and r.url not in sources:
                    sources.append(r.url)

        report = ResearchReport(
            query=query,
            markdown=final_state["draft_report"] or "",
            sources=sources,
            sub_questions=[
                sq.question for sq in final_state["sub_questions"]
            ],
            quality_score=(
                final_state["review"].quality_score
                if final_state.get("review")
                else None
            ),
        )

        logger.info("✅ Research complete")
        return report
