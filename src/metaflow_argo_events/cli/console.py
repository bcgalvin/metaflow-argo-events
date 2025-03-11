from rich.console import Console

_console = Console()

_error_console = Console(stderr=True)


def get_console() -> Console:
    return _console


def get_error_console() -> Console:
    return _error_console
