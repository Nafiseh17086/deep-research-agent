"""CLI entry point for the Deep Research Agent.

Usage:
    python -m src.main --query "Your research question here"
    python -m src.main --query "..." --output report.md
"""

from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from src.agents.research_agent import DeepResearchAgent

app = typer.Typer(help="Deep Research AI Agent — multi-step research via LangGraph")
console = Console()


@app.command()
def research(
    query: str = typer.Option(..., "--query", "-q", help="Research question"),
    output: Path = typer.Option(
        None, "--output", "-o", help="Save report to this file"
    ),
    provider: str = typer.Option(
        None, "--provider", "-p", help="Override LLM provider (openai/anthropic)"
    ),
):
    """Run a deep research query end-to-end."""
    console.print(
        Panel.fit(
            f"[bold cyan]🔬 Deep Research Agent[/bold cyan]\n\n"
            f"[white]Query:[/white] {query}",
            border_style="cyan",
        )
    )

    agent = DeepResearchAgent(provider=provider)
    report = agent.run(query)

    console.print("\n")
    console.print(Panel(Markdown(report.markdown), title="📋 Research Report"))
    console.print(
        f"\n[dim]Generated {report.generated_at.isoformat()} | "
        f"Sources: {len(report.sources)} | "
        f"Quality: {report.quality_score}/10[/dim]\n"
    )

    if output:
        output.write_text(report.markdown, encoding="utf-8")
        console.print(f"[green]💾 Saved report to {output}[/green]")


if __name__ == "__main__":
    app()
