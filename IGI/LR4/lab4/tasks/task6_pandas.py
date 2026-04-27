"""Task 6: pandas structures and Titanic analytics.

Laboratory work #4: files, classes, serializers, regex and standard libraries.
Version: 1.0.0
Developer: Dmitry Adarov
Date: 2026-04-21
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from io import StringIO
from pathlib import Path

from lab4.common.base import ResultSaverMixin, RunnableTask
from lab4.common.input_utils import ask_path_or_default, print_title
from lab4.common.optional_deps import import_pandas


DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "task6"
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs" / "task6"
DEFAULT_DATASET = DATA_DIR / "titanic_sample.csv"


class DatasetTask(ABC):
    """Abstract dataset task."""

    def __init__(self, dataset_path: Path) -> None:
        """Store dataset path."""
        self.dataset_path = dataset_path

    @abstractmethod
    def execute(self) -> str:
        """Run the task and return a text report."""


class TitanicDatasetTask(DatasetTask):
    """Solve task 6 for variant 1 using Titanic data."""

    def execute(self) -> str:
        """Create Series, inspect DataFrame and compute the required ratio."""
        pd = import_pandas()

        try:
            from IPython.display import display
        except ModuleNotFoundError:
            display = print

        gender_series = pd.Series(
            ["male", "female", "male", "female", "female"],
            index=["P1", "P2", "P3", "P4", "P5"],
            name="gender_series",
        )

        dataset = pd.read_csv(self.dataset_path)
        buffer = StringIO()
        dataset.info(buf=buffer)
        info_text = buffer.getvalue().strip()

        first_class_mean = dataset.loc[dataset["Pclass"] == 1, "Age"].mean()
        third_class_mean = dataset.loc[dataset["Pclass"] == 3, "Age"].mean()
        ratio = round(first_class_mean / third_class_mean, 2)

        report_lines = [
            "Задание 6. Pandas, вариант 1 (Titanic)",
            "",
            "Часть A. Series gender_series:",
            str(gender_series),
            "",
            "Часть B. Информация о датафрейме:",
            info_text,
            "",
            f"Средний возраст пассажиров 1 класса: {first_class_mean:.2f}",
            f"Средний возраст пассажиров 3 класса: {third_class_mean:.2f}",
            "Во сколько раз средний возраст пассажиров 1-го класса больше, "
            f"чем у пассажиров 3-го класса: {ratio:.2f}",
        ]

        display(gender_series)
        return "\n".join(report_lines)


class PandasTaskApp(RunnableTask, ResultSaverMixin):
    """Interactive wrapper for task 6."""

    title = "Задание 6"

    def run(self) -> None:
        """Execute task 6."""
        self.run_count += 1
        print_title("Задание 6. Pandas и Titanic")

        dataset_path = ask_path_or_default(
            "Введите путь к CSV-файлу Titanic или нажмите Enter для демонстрационного файла",
            DEFAULT_DATASET,
        )
        if not dataset_path.exists():
            print(f"Ошибка: файл '{dataset_path}' не найден.")
            return

        try:
            report_text = TitanicDatasetTask(dataset_path).execute()
        except ModuleNotFoundError:
            print("Pandas не найден. Установите зависимость и повторите запуск задания.")
            return

        report_path = self.save_text(OUTPUT_DIR / "pandas_report.txt", report_text)
        print(report_text)
        print(f"\nОтчёт сохранён в: {report_path}")
