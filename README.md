# 🔬 Deep Research AI Agent

> An autonomous AI research agent built with **LangGraph** that conducts multi-step web research, synthesizes findings from multiple sources, and generates structured, citation-backed reports — mimicking how a human researcher works.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)](https://github.com/langchain-ai/langgraph)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991.svg)](https://openai.com/)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude-D97757.svg)](https://anthropic.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 🎯 What This Project Demonstrates

This isn't just "ChatGPT with a search button." It's a **stateful, graph-based agent** that demonstrates:

- ✅ **Multi-agent orchestration** with LangGraph (planner → researcher → writer → reviewer)
- ✅ **Parallel tool execution** for efficient web search
- ✅ **Structured output generation** with Pydantic schemas
- ✅ **Provider-agnostic LLM layer** (swap OpenAI ↔ Anthropic via config)
- ✅ **Production patterns**: logging, retries, error handling, config management
- ✅ **Evaluation-ready**: includes tests and example outputs

---

## 🏗️ Architecture

```
          ┌─────────────┐
          │   User      │
          │   Query     │
          └──────┬──────┘
                 │
                 ▼
        ┌────────────────┐
        │   PLANNER      │  Decomposes query into
        │   (LLM)        │  research sub-questions
        └───────┬────────┘
                │
                ▼
        ┌────────────────┐
        │   RESEARCHER   │  Parallel web searches
        │   (Tavily API) │  via Tavily
        └───────┬────────┘
                │
                ▼
        ┌────────────────┐
        │   SYNTHESIZER  │  Consolidates findings,
        │   (LLM)        │  removes duplicates
        └───────┬────────┘
                │
                ▼
        ┌────────────────┐
        │   WRITER       │  Generates structured
        │   (LLM)        │  report with citations
        └───────┬────────┘
                │
                ▼
        ┌────────────────┐
        │   REVIEWER     │  Quality check &
        │   (LLM)        │  gap analysis
        └───────┬────────┘
                │
                ▼
        ┌────────────────┐
        │ Final Report   │
        │   (Markdown)   │
        └────────────────┘
```

See [`docs/architecture.md`](docs/architecture.md) for a detailed breakdown.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **LangGraph State Machine** | Each node is an isolated, testable unit with typed state transitions |
| 🔀 **Multi-Provider Support** | Works with OpenAI GPT-4 or Anthropic Claude — toggle in `.env` |
| 🔍 **Tavily Web Search** | Purpose-built search API for LLMs (better than raw Google scraping) |
| ⚡ **Parallel Execution** | Research multiple sub-questions concurrently |
| 📝 **Structured Reports** | Markdown output with proper citations and sections |
| 🔁 **Self-Correction** | Reviewer node flags gaps and triggers re-research if needed |
| 📊 **Observability** | Built-in logging + optional LangSmith tracing |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- API keys for at least one LLM provider (OpenAI or Anthropic) and Tavily

### Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/deep-research-agent.git
cd deep-research-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys
```

### Configuration

Edit `.env`:

```env
# Choose your provider: "openai" or "anthropic"
LLM_PROVIDER=anthropic

# API Keys (only fill in what you need)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...

# Optional: LangSmith for tracing
LANGSMITH_API_KEY=
LANGSMITH_TRACING=false
```

### Run Your First Research

```bash
python -m src.main --query "What are the latest advances in fusion energy in 2025?"
```

Or use it programmatically:

```python
from src.agents.research_agent import DeepResearchAgent

agent = DeepResearchAgent(provider="anthropic")
report = agent.run("Compare Rust vs Go for backend microservices")
print(report.markdown)
```

---

## 📁 Project Structure

```
deep-research-agent/
├── src/
│   ├── agents/
│   │   └── research_agent.py      # Main LangGraph agent
│   ├── tools/
│   │   └── search_tool.py         # Tavily wrapper
│   ├── utils/
│   │   ├── config.py              # Environment & config
│   │   ├── llm_factory.py         # Provider-agnostic LLM loader
│   │   └── logger.py              # Structured logging
│   ├── schemas.py                 # Pydantic models
│   └── main.py                    # CLI entry point
├── tests/
│   ├── test_agent.py
│   └── test_tools.py
├── examples/
│   └── sample_output.md           # Example research report
├── docs/
│   ├── architecture.md
│   └── images/
├── .env.example
├── .gitignore
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=html
```

---

## 📸 Example Output

Query: *"What are the most promising approaches to AI alignment in 2025?"*

See [`examples/sample_output.md`](examples/sample_output.md) for a full generated report.

---

## 🛠️ Tech Stack

- **[LangGraph](https://github.com/langchain-ai/langgraph)** — Stateful agent orchestration
- **[LangChain](https://github.com/langchain-ai/langchain)** — LLM abstractions
- **[Tavily](https://tavily.com/)** — AI-optimized web search
- **[Pydantic](https://docs.pydantic.dev/)** — Data validation
- **[OpenAI](https://openai.com/) / [Anthropic](https://anthropic.com/)** — LLM providers

---

## 🗺️ Roadmap

- [ ] Add support for local models via Ollama
- [ ] Streamlit UI for interactive research
- [ ] PDF export of reports
- [ ] Memory across research sessions
- [ ] Multi-language support

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 License

MIT License — see [LICENSE](LICENSE).

---

## 👤 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [linkedin.com/in/yourusername](https://linkedin.com/in/yourusername)
- Portfolio: [yourportfolio.com](https://yourportfolio.com)

---

## 🙏 Acknowledgments

- Inspired by OpenAI's Deep Research feature and the Analytics Vidhya "Top 5 Agentic AI Projects" series
- Built on the shoulders of the LangChain/LangGraph community

---

⭐ **If this project helped you, please give it a star!**
