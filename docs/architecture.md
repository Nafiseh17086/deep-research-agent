# Architecture Deep Dive

## Why LangGraph?

Traditional agent frameworks like early LangChain used a "ReAct loop" — the LLM decides each next step in free-form text, which is parsed and executed. This works but has problems:

- **No structured state** — everything lives in conversation history
- **Hard to test** — you can't isolate individual steps
- **No conditional branching** — loops are awkward
- **Poor observability** — hard to see why decisions were made

**LangGraph** treats the agent as a **state machine** (technically a directed graph). Each node is a function that reads and writes typed state. Edges can be conditional. This gives us:

- ✅ Each node is independently testable
- ✅ State is inspectable at every step
- ✅ Conditional loops are first-class (see reviewer → researcher feedback loop)
- ✅ Easy to visualize and debug

---

## State Design

The shared state (`AgentState` in `schemas.py`) is a `TypedDict` with these fields:

| Field | Type | Purpose |
|-------|------|---------|
| `query` | `str` | The user's original question |
| `plan` | `ResearchPlan` | Output of planner — sub-questions + rationale |
| `sub_questions` | `list[SubQuestion]` | Accumulated with search results |
| `synthesis` | `str` | Consolidated findings from researcher |
| `draft_report` | `str` | Writer's output (markdown) |
| `review` | `ReviewFeedback` | Reviewer's verdict |
| `iteration` | `int` | Tracks re-research loops |

The `sub_questions` field uses `Annotated[list, add]` — LangGraph's reducer pattern — so repeated writes accumulate instead of overwriting. This matters when the reviewer triggers a re-research pass.

---

## Node Responsibilities

### 1. Planner
- **Input:** raw user query
- **Output:** `ResearchPlan` with ≤5 sub-questions
- **LLM call:** uses `with_structured_output(ResearchPlan)` for reliable parsing
- **Why:** a good plan prevents shallow research. Better to spend one extra LLM call here than 10 bad searches later.

### 2. Researcher
- **Input:** plan
- **Output:** sub-questions enriched with `SearchResult` lists
- **Tool:** Tavily (LLM-optimized search API)
- **Why Tavily over Google/SerpAPI:** Tavily returns cleaned article text, not just snippets. Cheaper for LLM context.

### 3. Synthesizer
- **Input:** all search results across all sub-questions
- **Output:** prose synthesis
- **Why separate from Writer:** separation of concerns. Synthesizer finds patterns; Writer handles formatting/citations.

### 4. Writer
- **Input:** synthesis + source list
- **Output:** structured markdown with 5 sections
- **Citation strategy:** numbered `[N]` references tied to a source list at the end.

### 5. Reviewer
- **Input:** draft report
- **Output:** `ReviewFeedback` with quality score + gap list
- **Routing logic:** if `is_sufficient=False` AND `iteration < MAX_ITERATIONS`, loop back to Researcher with the missing aspects.

---

## Conditional Edges

```python
graph.add_conditional_edges(
    "reviewer",
    self._route_after_review,
    {
        "continue": END,
        "revise": "researcher",
    },
)
```

The router checks:
1. Is the review marked sufficient? → `continue`
2. Have we hit max iterations? → `continue` (prevent infinite loops)
3. Otherwise → `revise` (loop back)

---

## Extending the Agent

Want to add a new node? Three steps:

1. Add a new field to `AgentState` in `schemas.py`
2. Write the node function in `research_agent.py` (accepts state dict, returns partial update)
3. Wire it into the graph with `graph.add_node()` and `graph.add_edge()`

Common extensions:
- **Fact-checker node** between writer and reviewer
- **Memory node** that loads context from prior sessions
- **Multi-source synthesizer** that pulls from arxiv + web + internal docs

---

## Observability

Set `LANGSMITH_TRACING=true` in `.env` to get full execution traces including:
- Each LLM prompt + completion
- Tool calls and responses
- State transitions between nodes
- Latency per step

Invaluable when debugging "why did the agent say X?"
