"""Minimal subset of :mod:`rich.console` required for unit tests."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import builtins


class Console:
    """Very small console abstraction compatible with the project's usage."""

    def __init__(self, *, quiet: bool = False) -> None:
        self.quiet = quiet

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        if self.quiet:
            return
        message = sep.join(str(obj) for obj in objects)
        builtins_print(message, end=end)

    def log(self, message: str, *args: Any) -> None:
        if self.quiet:
            return
        if args:
            try:
                message = message % args
            except TypeError:
                message = " ".join([message, *map(str, args)])
        timestamp = datetime.utcnow().isoformat(timespec="seconds")
        builtins_print(f"[{timestamp}] {message}")

    def rule(self, title: str) -> None:
        if self.quiet:
            return
        builtins_print(f"---- {title} ----")


def builtins_print(*args: Any, **kwargs: Any) -> None:
    builtins.print(*args, **kwargs)
