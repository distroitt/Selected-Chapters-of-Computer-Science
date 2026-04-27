"""Task 5: NumPy matrix operations.

Laboratory work #4: files, classes, serializers, regex and standard libraries.
Version: 1.0.0
Developer: Dmitry Adarov
Date: 2026-04-21
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from lab4.common.base import ResultSaverMixin, RunnableTask
from lab4.common.input_utils import ask_positive_int, print_title
from lab4.common.optional_deps import import_numpy


OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs" / "task5"


class MatrixTaskBase(ABC):
    """Base class for matrix tasks."""

    task_name = "Matrix task"

    def __init__(self, rows: int, columns: int, seed: int) -> None:
        """Store matrix dimensions and random seed."""
        self.rows = rows
        self.columns = columns
        self.seed = seed

    @property
    def shape(self) -> tuple[int, int]:
        """Return the matrix shape."""
        return self.rows, self.columns

    @abstractmethod
    def execute(self) -> str:
        """Run the matrix task."""


class VariantOneMatrixTask(MatrixTaskBase):
    """Variant 1 for the NumPy task."""

    task_name = "Variant 1"

    def execute(self) -> str:
        """Generate the matrix and solve the assignment."""
        np = import_numpy()
        generator = np.random.default_rng(self.seed)
        matrix = generator.integers(-20, 51, size=self.shape)

        column_sums = matrix.sum(axis=0)
        min_column_index = int(np.argmin(column_sums))
        selected_column = matrix[:, min_column_index]

        standard_median = float(np.median(selected_column))
        manual_median = self._manual_median(selected_column.tolist())

        lines = [
            "Задание 5. NumPy, вариант 1",
            f"Размер матрицы: {self.rows} x {self.columns}",
            f"Seed: {self.seed}",
            "",
            "Матрица A:",
            str(matrix),
            "",
            f"Суммы столбцов: {column_sums}",
            f"Индекс столбца с минимальной суммой: {min_column_index}",
            f"Столбец с минимальной суммой: {selected_column}",
            f"Медиана через numpy.median(): {standard_median:.2f}",
            f"Медиана по формуле: {manual_median:.2f}",
        ]
        return "\n".join(lines)

    @staticmethod
    def _manual_median(values: list[int]) -> float:
        """Calculate median without NumPy helpers."""
        ordered = sorted(values)
        middle = len(ordered) // 2
        if len(ordered) % 2 == 1:
            return float(ordered[middle])
        return (ordered[middle - 1] + ordered[middle]) / 2


class NumPyTaskApp(RunnableTask, ResultSaverMixin):
    """Interactive wrapper for task 5."""

    title = "Задание 5"

    def run(self) -> None:
        """Execute task 5."""
        self.run_count += 1
        print_title("Задание 5. NumPy и матрица")

        rows = ask_positive_int("Введите количество строк n")
        columns = ask_positive_int("Введите количество столбцов m")
        seed = ask_positive_int("Введите seed для генератора случайных чисел")

        try:
            task = VariantOneMatrixTask(rows, columns, seed)
            report_text = task.execute()
        except ModuleNotFoundError:
            print("NumPy не найден. Установите зависимость и повторите запуск задания.")
            return

        report_path = self.save_text(OUTPUT_DIR / "numpy_report.txt", report_text)
        print(report_text)
        print(f"\nОтчёт сохранён в: {report_path}")
