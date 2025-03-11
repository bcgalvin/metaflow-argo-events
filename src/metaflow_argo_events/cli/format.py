import json
from typing import Any, TypeVar

import yaml
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

console = Console()
T = TypeVar("T")


def format_success(message: str, data: T | None = None) -> None:
    console.print(f"[bold green]✓[/bold green] {message}")
    if data:
        if isinstance(data, dict):
            display_dict(data)
        elif isinstance(data, list):
            display_list(data)
        else:
            console.print(str(data))


def display_dict(data: dict[str, Any], title: str | None = None) -> None:
    table = Table(show_header=True, header_style="bold", expand=True)
    table.add_column("Key")
    table.add_column("Value")

    for key, value in data.items():
        value_str = json.dumps(value, indent=2) if isinstance(value, dict | list) else str(value)
        table.add_row(str(key), value_str)

    if title:
        console.print(f"[bold]{title}[/bold]")
    console.print(table)


def display_list(data: list[T], title: str | None = None) -> None:
    if title:
        console.print(f"[bold]{title}[/bold]")

    for i, item in enumerate(data, 1):
        if isinstance(item, dict):
            console.print(f"{i}.")
            display_dict(item)
        else:
            console.print(f"{i}. {item}")


def format_output(data: T, output_format: str = "text") -> str:
    match output_format.lower():
        case "json":
            return json.dumps(data, indent=2)
        case "yaml":
            return yaml.dump(data, sort_keys=False)
        case _:
            return json.dumps(data, indent=2) if isinstance(data, dict | list) else str(data)


def print_output(data: T, output_format: str = "text") -> None:
    formatted_output = format_output(data, output_format)
    match output_format.lower():
        case "json":
            console.print_json(formatted_output)
        case "yaml":
            console.print(formatted_output)
        case _:
            console.print(formatted_output)


def display_schema(schema: dict[str, Any]) -> None:
    console.print(f"[bold]Schema:[/bold] {schema.get('name', 'Unnamed')}")
    console.print(f"[bold]Version:[/bold] {schema.get('version', 'Unversioned')}")

    if "parameters" in schema and isinstance(schema["parameters"], list):
        console.print("\n[bold]Parameters:[/bold]")
        table = Table(show_header=True, header_style="bold", expand=True)
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Required")
        table.add_column("Default")

        for param in schema["parameters"]:
            name = param.get("name", "Unnamed")
            param_type = param.get("type", "Unknown")
            required = "Yes" if param.get("required", False) else "No"
            default = str(param.get("default", "")) if "default" in param else "-"

            table.add_row(name, param_type, required, default)

        console.print(table)


def display_markdown(text: str) -> None:
    md = Markdown(text)
    console.print(md)


def display_warning(message: str) -> None:
    console.print(f"[bold yellow]Warning:[/bold yellow] {message}")


def display_info(message: str) -> None:
    console.print(f"[bold blue]Info:[/bold blue] {message}")
