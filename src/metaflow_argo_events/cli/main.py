import importlib.metadata

import typer
from rich.console import Console

console = Console()

app = typer.Typer(
    help="Metaflow OpenAPI utilities for Argo Events.",
    add_completion=True,
    pretty_exceptions_enable=True,
    no_args_is_help=True,
)


def get_version() -> str:
    """Get current package version."""
    try:
        return importlib.metadata.version("metaflow-argo-events")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


@app.callback()
def main(
    ctx: typer.Context,
    version: bool | None = typer.Option(
        False, "--version", "-v", help="Show version and exit.", is_flag=True
    ),
) -> None:
    """
    Metaflow OpenAPI Utilities.

    This CLI tool enables schema definition, OpenAPI generation,
    client library creation, and event publishing for Metaflow workflows.
    """
    if version:
        console.print(f"[bold]metaflow-events[/bold] version: {get_version()}")
        raise typer.Exit


if __name__ == "__main__":
    app()
