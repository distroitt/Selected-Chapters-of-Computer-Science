"""Task 2: text processing with regex.

Laboratory work #4: files, classes, serializers, regex and standard libraries.
Version: 1.1.0
Developer: Dmitry Adarov
Date: 2026-04-27
"""

from __future__ import annotations

import re
import zipfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from lab4.common.base import ResultSaverMixin, RunnableTask
from lab4.common.input_utils import ask_path_or_default, print_title

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "task2"
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs" / "task2"
DEFAULT_TEXT = DATA_DIR / "source_text.txt"

WORD_PATTERN = re.compile(r"[A-Za-zА-Яа-яЁё]+(?:-[A-Za-zА-Яа-яЁё]+)?")
SENTENCE_PATTERN = re.compile(r"[^.!?]+[.!?]+", re.MULTILINE)
EMOTICON_PATTERN = re.compile(r"(?<![:;\-\(\)\[\]])[:;]-*(?:\(+|\)+|\[+|\]+)(?![:;\-\(\)\[\]])")
ABC_PATTERN = re.compile(r"a+b{2,}c+") # a...ab...bc...c (a > 0, b > 1, c > 0)


@dataclass
class TextStatistics:
    """Store calculated text statistics."""
    sentence_count: int
    narrative_count: int
    question_count: int
    imperative_count: int
    average_sentence_word_length: float
    average_word_length: float
    emoticon_count: int


class TextSource(ABC):
    """Abstract text source."""

    @abstractmethod
    def load_text(self) -> str:
        """Return source text."""


class FileTextSource(TextSource):
    """Read text from a file."""

    def __init__(self, path: Path) -> None:
        """Store the source file path."""
        self.path = path

    @property
    def text_path(self) -> Path:
        """Return the source path."""
        return self.path

    def load_text(self) -> str:
        """Read UTF-8 text from a file."""
        return self.path.read_text(encoding="utf-8")


class BaseTextAnalyzer(ABC):
    """Abstract analyzer for text tasks."""

    def __init__(self, text: str) -> None:
        """Store the source text."""
        self.text = text

    @property
    def text(self) -> str:
        """Return the analyzed text."""
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        """Validate and store text."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Text must not be empty.")
        self._text = cleaned


class VariantOneTextAnalyzer(BaseTextAnalyzer):
    """Analyze text for the extended variant requirements."""

    def get_uppercase_english(self) -> str:
        """1. Вывести все заглавные английские буквы."""
        letters = re.findall(r"[A-Z]", self.text)
        return " ".join(letters) if letters else "Не найдены."

    def replace_abc_sequence(self) -> str:
        """2. Заменить последовательность «a…ab…bc…c» на «qqq»."""
        return ABC_PATTERN.sub("qqq", self.text)

    def count_max_length_words(self) -> int:
        """3. Определить, сколько слов имеют максимальную длину."""
        words = WORD_PATTERN.findall(self.text)
        if not words:
            return 0
        max_length = max(len(word) for word in words)
        return sum(1 for word in words if len(word) == max_length)

    def get_words_before_comma_or_dot(self) -> list[str]:
        """4. Вывести все слова, за которыми следует запятая или точка."""
        pattern = re.compile(r"([A-Za-zА-Яа-яЁё]+(?:-[A-Za-zА-Яа-яЁё]+)?)(?=[.,])")
        return pattern.findall(self.text)

    def get_longest_word_ending_in_e(self) -> str:
        """5. Найти самое длинное слово, которое заканчивается на 'е' (рус или англ)."""
        words = WORD_PATTERN.findall(self.text)
        e_words = [word for word in words if re.search(r"[eе]$", word, re.IGNORECASE)]
        if not e_words:
            return "Слова, оканчивающиеся на 'е', не найдены."
        return max(e_words, key=len)

    def calculate_statistics(self) -> TextStatistics:
        """Calculate general text statistics required by the laboratory work."""
        sentences = SENTENCE_PATTERN.findall(self.text)
        words = WORD_PATTERN.findall(self.text)

        narrative_count = sum(1 for sentence in sentences if re.search(r"\.\s*$", sentence))
        question_count = sum(1 for sentence in sentences if re.search(r"\?\s*$", sentence))
        imperative_count = sum(1 for sentence in sentences if re.search(r"!\s*$", sentence))

        if sentences:
            sentence_lengths = [
                sum(len(word) for word in WORD_PATTERN.findall(sentence))
                for sentence in sentences
            ]
            avg_sentence_word_length = sum(sentence_lengths) / len(sentence_lengths)
        else:
            avg_sentence_word_length = 0.0

        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0.0

        return TextStatistics(
            sentence_count=len(sentences),
            narrative_count=narrative_count,
            question_count=question_count,
            imperative_count=imperative_count,
            average_sentence_word_length=avg_sentence_word_length,
            average_word_length=avg_word_length,
            emoticon_count=len(EMOTICON_PATTERN.findall(self.text)),
        )


class TextReportBuilder(ResultSaverMixin):
    """Build and persist task 2 reports."""

    def __init__(self, analyzer: VariantOneTextAnalyzer) -> None:
        """Store analyzer instance."""
        self.analyzer = analyzer

    def build_report(self) -> str:
        """Create a complete report."""
        stats = self.analyzer.calculate_statistics()
        words_before_punct = self.analyzer.get_words_before_comma_or_dot()
        words_before_punct_str = ", ".join(words_before_punct) if words_before_punct else "Не найдены"

        return "\n".join(
            [
                "Задание 2. Анализ текста",
                "",
                "--- Индивидуальное задание ---",
                f"1. Все заглавные английские буквы: {self.analyzer.get_uppercase_english()}",
                f"2. Текст с заменой 'a+b{{2,}}c+' на 'qqq':\n{self.analyzer.replace_abc_sequence()}\n",
                f"3. Количество слов максимальной длины: {self.analyzer.count_max_length_words()}",
                f"4. Слова перед запятой или точкой: {words_before_punct_str}",
                f"5. Самое длинное слово, заканчивающееся на 'е': {self.analyzer.get_longest_word_ending_in_e()}",
                "",
                "--- Общая статистика ---",
                f"Количество предложений: {stats.sentence_count}",
                f"Повествовательных предложений: {stats.narrative_count}",
                f"Вопросительных предложений: {stats.question_count}",
                f"Побудительных предложений: {stats.imperative_count}",
                "Средняя длина предложения в символах "
                f"(учтены только слова): {stats.average_sentence_word_length:.2f}",
                f"Средняя длина слова: {stats.average_word_length:.2f}",
                f"Количество смайликов: {stats.emoticon_count}",
            ]
        )

    def archive_report(self, report_path: Path) -> tuple[Path, str]:
        """Archive the report and return archive info."""
        archive_path = report_path.with_suffix(".zip")
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.write(report_path, arcname=report_path.name)

        with zipfile.ZipFile(archive_path, "r") as archive:
            info = archive.getinfo(report_path.name)
            archive_info = (
                f"Архив: {archive_path}\n"
                f"Файл в архиве: {info.filename}\n"
                f"Размер исходного файла: {info.file_size} байт\n"
                f"Размер в архиве: {info.compress_size} байт"
            )
        return archive_path, archive_info


class TextAnalysisApp(RunnableTask):
    """Interactive wrapper for task 2."""

    title = "Задание 2"

    def run(self) -> None:
        """Execute task 2."""
        self.run_count += 1
        print_title("Задание 2. Анализ текста и регулярные выражения")

        text_path = ask_path_or_default(
            "Введите путь к текстовому файлу или нажмите Enter для демонстрационного примера",
            DEFAULT_TEXT,
        )
        if not text_path.exists():
            print(f"Ошибка: файл '{text_path}' не найден.")
            return

        source = FileTextSource(text_path)
        analyzer = VariantOneTextAnalyzer(source.load_text())
        builder = TextReportBuilder(analyzer)
        report_text = builder.build_report()

        report_path = builder.save_text(OUTPUT_DIR / "analysis_report.txt", report_text)
        archive_path, archive_info = builder.archive_report(report_path)

        print(report_text)
        print("\nИнформация об архиве:")
        print(archive_info)
        print(f"\nИсходный файл: {source.text_path}")
        print(f"Отчёт: {report_path}")
        print(f"ZIP-архив: {archive_path}")
