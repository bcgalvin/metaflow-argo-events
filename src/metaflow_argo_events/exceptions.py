import typer
from rich.console import Console
from rich.panel import Panel

console = Console(stderr=True)


class CliError(Exception):
    def __init__(self, message: str, hint: str | None = None, exit_code: int = 1) -> None:
        self.message = message
        self.hint = hint
        self.exit_code = exit_code
        super().__init__(message)


class SchemaError(CliError):
    def __init__(self, message: str, hint: str | None = None, errors: list[str] | None = None) -> None:
        self.errors = errors or []
        super().__init__(message, hint)


class ValidationError(CliError):
    def __init__(self, message: str, hint: str | None = None, errors: list[str] | None = None) -> None:
        self.errors = errors or []
        super().__init__(message, hint)


class EventError(CliError):
    pass


class OpenApiError(CliError):
    pass


class ClientError(CliError):
    pass


def handle_error(error: Exception) -> None:
    if isinstance(error, CliError):
        error_panel = Panel.fit(f"[bold red]{error.message}[/bold red]", title="Error", border_style="red")
        console.print(error_panel)

        if getattr(error, "hint", None):
            console.print(f"[yellow]Hint:[/yellow] {error.hint}")

        if hasattr(error, "errors") and error.errors:
            console.print("\n[bold red]Details:[/bold red]")
            for i, err in enumerate(error.errors, 1):
                console.print(f"  {i}. {err}")

        raise typer.Exit(code=getattr(error, "exit_code", 1))

    # Removed unnecessary 'else' here since the code will never reach this point if the previous condition is true
    console.print(f"[bold red]Unexpected error:[/bold red] {error!s}")
    console.print("[dim]For detailed error information, run with --verbose flag.[/dim]")
    raise typer.Exit(code=1)
