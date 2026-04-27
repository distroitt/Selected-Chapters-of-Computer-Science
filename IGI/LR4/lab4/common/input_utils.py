"""Input utilities.

Laboratory work #4: files, classes, serializers, regex and standard libraries.
Version: 1.0.0
Developer: Dmitry Adarov
Date: 2026-04-21
"""

from __future__ import annotations

from pathlib import Path


def print_title(title: str) -> None:
    """Print a decorated section title."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def ask_menu_choice(prompt: str, valid_choices: set[str]) -> str:
    """Ask the user for a menu choice until it becomes valid."""
    while True:
        value = input(f"{prompt}: ").strip()
        if value in valid_choices:
            return value
        print("Ошибка: введите один из допустимых пунктов меню.")


def ask_float(prompt: str, min_value: float | None = None) -> float:
    """Ask the user for a floating-point number."""
    while True:
        raw = input(f"{prompt}: ").strip().replace(",", ".")
        try:
            value = float(raw)
        except ValueError:
            print("Ошибка: нужно ввести число.")
            continue
        if min_value is not None and value <= min_value:
            print(f"Ошибка: число должно быть больше {min_value}.")
            continue
        return value


def ask_positive_int(prompt: str) -> int:
    """Ask the user for a positive integer."""
    while True:
        raw = input(f"{prompt}: ").strip()
        try:
            value = int(raw)
        except ValueError:
            print("Ошибка: нужно ввести целое число.")
            continue
        if value <= 0:
            print("Ошибка: число должно быть положительным.")
            continue
        return value


def ask_non_empty(prompt: str) -> str:
    """Ask the user for a non-empty string."""
    while True:
        value = input(f"{prompt}: ").strip()
        if value:
            return value
        print("Ошибка: пустая строка недопустима.")


def ask_path_or_default(prompt: str, default_path: Path) -> Path:
    """Ask the user for a path and use the default value when empty."""
    value = input(f"{prompt} [{default_path}]: ").strip()
    if not value:
        return default_path
    return Path(value).expanduser()


def wait_for_enter() -> None:
    """Pause the application until the user presses Enter."""
    input("\nНажмите Enter, чтобы вернуться в меню...")
