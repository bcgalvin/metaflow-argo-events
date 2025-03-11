import typer
from rich.panel import Panel

from metaflow_argo_events.cli.console import get_error_console
from metaflow_argo_events.logger import get_logger

console = get_error_console()
logger = get_logger("exceptions")


class CliError(Exception):
    def __init__(self, message: str, hint: str | None = None, exit_code: int = 1) -> None:
        self.message = message
        self.hint = hint
        self.exit_code = exit_code
        logger.error(message)
        if hint:
            logger.info("Error hint: %s", hint)
        super().__init__(message)


class SchemaError(CliError):
    def __init__(self, message: str, hint: str | None = None, errors: list[str] | None = None) -> None:
        self.errors = errors or []
        full_message = f"Schema error: {message}"
        super().__init__(full_message, hint)
        if errors:
            for error in errors:
                logger.debug("Schema detail: %s", error)


class ValidationError(CliError):
    def __init__(self, message: str, hint: str | None = None, errors: list[str] | None = None) -> None:
        self.errors = errors or []
        full_message = f"Validation error: {message}"
        super().__init__(full_message, hint)

        if errors:
            for error in errors:
                logger.debug("Validation detail: %s", error)


class EventError(CliError):
    @classmethod
    def not_found(cls, event_id: str, hint: str | None = None) -> "EventError":
        return cls(f"Event not found: {event_id}", hint)


class OpenApiError(CliError):
    @classmethod
    def schema_invalid(cls, detail: str, hint: str | None = None) -> "OpenApiError":
        return cls(f"Invalid OpenAPI schema: {detail}", hint)


class ClientError(CliError):
    @classmethod
    def connection_failed(cls, service: str, detail: str, hint: str | None = None) -> "ClientError":
        return cls(f"Failed to connect to {service}: {detail}", hint)

    @classmethod
    def api_error(cls, service: str, status_code: int, detail: str, hint: str | None = None) -> "ClientError":
        return cls(f"API error from {service} (status {status_code}): {detail}", hint)


class ConfigError(CliError):
    def __init__(self, config_name: str, detail: str, hint: str | None = None) -> None:
        message = f"Configuration error ({config_name}): {detail}"
        super().__init__(message, hint)


class AccessDeniedError(CliError):
    def __init__(self, resource: str, operation: str, hint: str | None = None) -> None:
        message = f"Permission denied: Cannot {operation} {resource}"
        super().__init__(message, hint, exit_code=13)


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

    logger.exception("Unexpected error: %s", error)
    console.print(f"[bold red]Unexpected error:[/bold red] {error}")
    console.print("[dim]For detailed error information, run with --verbose flag.[/dim]")
    raise typer.Exit(code=1)
