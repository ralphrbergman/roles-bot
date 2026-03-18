from collections.abc import Generator
from importlib import reload
from pathlib import Path
from traceback import format_exception
from types import ModuleType
from sys import modules
from typing import Any

from config import EXTENSIONS_PATH, SKIP_RELOAD

ROOT = Path()

def fmt_traceback_message(
    error: Exception,
    existing_message: str,
    limit: bool = True
) -> str:
    """
    Formats message and returns with exception in a traceback.

    Args:
        error: Exception to display.
        existing_message: Existing message to account for with traceback.
    """
    tb_lines = format_exception(type(error), error, error.__traceback__)
    tb = ''.join(tb_lines)
    max_tb_length = 1950 - len(existing_message)

    if len(tb) > max_tb_length and limit:
        tb = f'{tb[:max_tb_length]}...\n[Traceback truncated]'
    else:
        tb = tb

    message = f'{existing_message}\n```py\n{tb}```'

    return message

def get_extension_name(path: Path) -> str:
    """
    Gets import friendly name of extension path.
    """
    parts = list(path.relative_to(ROOT).parts)
    parts[-1] = path.stem

    return '.'.join(parts)

def get_partial_name(partial: str) -> str:
    """
    Gets import friendly name from a partial name.
    """
    for extension in iterate_extensions():
        if len(partial) > 1 and partial in extension:
            return extension

def iterate_extensions() -> Generator[str, Any, Any]:
    """
    Iterates over Discord.py extensions
    in the extensions directory.
    """
    for path in EXTENSIONS_PATH.rglob('*.py'):
        if path.parent.name == '__pycache__':   continue

        yield get_extension_name(path)

def recursive_reload(module: ModuleType) -> None:
    """
    Recursively reloads sub-modules and module itself for a given module.
    """
    if module.__name__ in SKIP_RELOAD:
        return

    reload(module)

    prefix = f'{module.__name__}.'

    sub_modules = [
        mod for name, mod in modules.items()
        if name.startswith(prefix) and isinstance(mod, ModuleType) and
        name not in SKIP_RELOAD
    ]

    for mod in sub_modules:
        reload(mod)
