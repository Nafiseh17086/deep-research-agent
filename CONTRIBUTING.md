# Contributing

Thanks for your interest in contributing! This project is open to PRs, issues, and ideas.

## Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/deep-research-agent.git
cd deep-research-agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
```

## Running Tests

```bash
pytest                          # All tests
pytest --cov=src                # With coverage
pytest tests/test_tools.py      # Single file
```

## Code Style

This project uses:
- **Black** for formatting
- **Ruff** for linting
- **mypy** for type checking

Run before submitting a PR:

```bash
black src/ tests/
ruff check src/ tests/
mypy src/
```

## Pull Request Process

1. Fork the repo and create a feature branch (`git checkout -b feature/your-feature`)
2. Make your changes with tests
3. Ensure all tests pass and linters are clean
4. Update docs if behavior changed
5. Open a PR with a clear description of what and why

## Ideas for Contributions

- 🔍 Add alternative search backends (SerpAPI, Brave Search)
- 🧠 Support local models via Ollama
- 🎨 Build a Streamlit or Gradio UI
- 📊 Add evaluation benchmarks
- 🌍 Multi-language prompt templates
- 📝 PDF export of reports

## Questions?

Open an issue — happy to discuss.
