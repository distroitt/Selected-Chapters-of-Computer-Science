from __future__ import annotations

from common.decorators import task_screen
from common.input_utils import read_text


def count_uppercase_english_letters(text: str) -> int:
    count = 0
    for symbol in text:
        if "A" <= symbol <= "Z":
            count += 1
    return count


@task_screen("Task 3. Uppercase English Letters")
def run_task() -> None:
    text = read_text("Enter a line of text: ", allow_empty=True)
    count = count_uppercase_english_letters(text)
    print(f"Uppercase English letters: {count}")
