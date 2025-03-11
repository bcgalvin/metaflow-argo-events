import importlib.metadata

import typer

from metaflow_argo_events.cli.console import get_console
from metaflow_argo_events.logger import configure_verbose_logging, get_logger

console = get_console()
logger = get_logger("cli")

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


def version_callback(value: bool) -> None:
    """Display version information and exit."""
    if value:
        console.print(f"[bold]metaflow-events[/bold] version: {get_version()}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        is_flag=True,
        is_eager=True,
        callback=version_callback,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Enable verbose output.",
        is_flag=True,
    ),
) -> None:
    """
    Metaflow OpenAPI Utilities.

    This CLI tool enables schema definition, OpenAPI generation,
    client library creation, and event publishing for Metaflow workflows.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

    configure_verbose_logging(verbose=verbose)

    if verbose:
        logger.debug("Verbose logging enabled")
        logger.debug("CLI context: %s", ctx.info_name)


if __name__ == "__main__":
    app()
