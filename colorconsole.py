from rich.console import Console

console = Console()

# Print a styled prompt before input
user_name = console.input("[bold green]Enter your name:[/bold green] ")

console.print(f"Hello, [cyan]{user_name}[/cyan]! Welcome to the Agentic CLI 🤖")
