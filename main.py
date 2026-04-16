"""
Chatbot bancario en consola.
Usa rich para output profesional en cámara.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.spinner import Spinner
from rich.live import Live
import time

from agent.router import run

console = Console()


def print_header():
    console.print(Panel.fit(
        "[bold green]🤖 Agente Bancario[/bold green]\n"
        "[dim]RAG + MCP + Claude[/dim]\n"
        "[dim]Escribe 'salir' para terminar[/dim]",
        border_style="green",
    ))
    console.print()


def print_question(question: str):
    console.print(f"\n[bold cyan]👤 Tú:[/bold cyan] {question}")


def print_thinking():
    return Live(
        Spinner("dots", text="[dim]Pensando...[/dim]"),
        console=console,
        refresh_per_second=10,
    )


def print_answer(answer: str):
    console.print(Panel(
        Text(answer, style="white"),
        title="[bold green]🤖 Agente[/bold green]",
        border_style="green",
        padding=(1, 2),
    ))


def main():
    print_header()

    while True:
        try:
            question = Prompt.ask("\n[bold cyan]Pregunta[/bold cyan]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Hasta luego.[/dim]")
            break

        if question.strip().lower() in ("salir", "exit", "quit"):
            console.print("\n[dim]Hasta luego.[/dim]")
            break

        if not question.strip():
            continue

        print_question(question)

        with print_thinking():
            try:
                answer = run(question)
            except Exception as e:
                answer = f"Error: {e}"

        print_answer(answer)


if __name__ == "__main__":
    main()
