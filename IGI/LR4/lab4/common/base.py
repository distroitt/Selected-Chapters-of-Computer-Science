"""Shared base classes.

Laboratory work #4: files, classes, serializers, regex and standard libraries.
Version: 1.0.0
Developer: Dmitry Adarov
Date: 2026-04-21
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path


class NamedEntity(ABC):
    """Provide a shared interface for named entities."""

    entity_counter = 0

    def __init__(self, name: str) -> None:
        """Store a name and update the shared counter."""
        self.name = name.strip()
        self.created_at = datetime.now()
        NamedEntity.entity_counter += 1

    def __str__(self) -> str:
        """Return a friendly string representation."""
        return "{}({})".format(self.__class__.__name__, self.name)

    def __lt__(self, other: object) -> bool:
        """Support sorting by entity name."""
        if not isinstance(other, NamedEntity):
            return NotImplemented
        return self.name.lower() < other.name.lower()

    @classmethod
    def created_entities(cls) -> int:
        """Return the number of created entities."""
        return cls.entity_counter


class ResultSaverMixin:
    """Add file saving helpers."""

    def save_text(self, path: Path, content: str) -> Path:
        """Save plain text to a UTF-8 file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path


class RunnableTask(ABC):
    """Represent an interactive task."""

    title = "Task"

    def __init__(self) -> None:
        """Initialize the task state."""
        self.run_count = 0

    @abstractmethod
    def run(self) -> None:
        """Execute the task."""

