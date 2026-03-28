from __future__ import annotations

from common.constants import SOURCE_TEXT
from common.decorators import task_screen


def extract_words(text: str) -> list[str]:
    words: list[str] = []
    current: list[str] = []

    for symbol in text:
        if symbol.isalpha() or symbol == "-":
            current.append(symbol)
        elif current:
            words.append("".join(current))
            current.clear()

    if current:
        words.append("".join(current))

    return words


def find_longest_word(words: list[str]) -> tuple[str, int]:
    longest_word = words[0]
    longest_index = 1

    for index, word in enumerate(words, start=1):
        if len(word) > len(longest_word):
            longest_word = word
            longest_index = index

    return longest_word, longest_index


def get_even_words(words: list[str]) -> list[str]:
    return words[1::2]


@task_screen("Task 4. Fixed Text Analysis")
def run_task() -> None:
    words = extract_words(SOURCE_TEXT)
    longest_word, longest_index = find_longest_word(words)
    even_words = get_even_words(words)

    print("Source text:")
    print(SOURCE_TEXT)
    print(f"\nNumber of words: {len(words)}")
    print(f"Longest word: {longest_word}")
    print(f"Position of the longest word: {longest_index}")
    print("Every even word:")
    for word in even_words:
        print(word)
