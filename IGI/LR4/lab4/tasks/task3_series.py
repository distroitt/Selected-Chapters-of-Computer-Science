"""Task 3: series approximation and plotting.

Laboratory work #4: files, classes, serializers, regex and standard libraries.
Version: 1.0.0
Developer: Dmitry Adarov
Date: 2026-04-21
"""

from __future__ import annotations

import math
import statistics
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from lab4.common.base import ResultSaverMixin, RunnableTask
from lab4.common.input_utils import ask_float, print_title
from lab4.common.optional_deps import import_matplotlib_pyplot


OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs" / "task3"


@dataclass
class FunctionRow:
    """Store one function approximation row."""

    x: float
    terms_used: int
    series_value: float
    math_value: float
    epsilon: float


class FunctionApproximator(ABC):
    """Base class for function approximation."""

    function_name = "F(x)"

    def __init__(self, epsilon: float) -> None:
        """Store epsilon."""
        self.epsilon = epsilon

    @property
    def epsilon(self) -> float:
        """Return epsilon."""
        return self._epsilon

    @epsilon.setter
    def epsilon(self, value: float) -> None:
        """Validate and store epsilon."""
        if value <= 0:
            raise ValueError("Epsilon must be positive.")
        self._epsilon = value

    @abstractmethod
    def calculate_row(self, x_value: float) -> FunctionRow:
        """Calculate one table row."""

    @abstractmethod
    def math_function(self, x_value: float) -> float:
        """Calculate the reference function from math."""

    def __call__(self, x_value: float) -> FunctionRow:
        """Allow instances to be called as functions."""
        return self.calculate_row(x_value)


class VariantOneApproximator(FunctionApproximator):
    """Approximate ln((x + 1) / (x - 1)) for |x| > 1."""

    function_name = "ln((x + 1) / (x - 1))"

    def calculate_row(self, x_value: float) -> FunctionRow:
        """Approximate the function with the series from variant 1."""
        if abs(x_value) <= 1:
            raise ValueError("For variant 1, |x| must be greater than 1.")

        series_sum = 0.0
        terms_used = 0
        n = 0
        while True:
            term = 1 / ((2 * n + 1) * (x_value ** (2 * n + 1)))
            series_sum += term
            terms_used += 1
            if abs(term) < self.epsilon:
                break
            n += 1
            if n > 100_000:
                raise RuntimeError("Series did not converge in the allowed number of steps.")

        return FunctionRow(
            x=x_value,
            terms_used=terms_used,
            series_value=2 * series_sum,
            math_value=self.math_function(x_value),
            epsilon=self.epsilon,
        )

    def math_function(self, x_value: float) -> float:
        """Calculate the exact value using math.log."""
        return math.log((x_value + 1) / (x_value - 1))


class StatisticsMixin:
    """Provide sequence statistics."""

    def calculate_statistics(self, values: list[float]) -> dict[str, object]:
        """Calculate mean, median, mode, variance and standard deviation."""
        modes = statistics.multimode(values)
        return {
            "mean": statistics.fmean(values),
            "median": statistics.median(values),
            "mode": modes[0] if modes else None,
            "variance": statistics.pvariance(values),
            "std_dev": statistics.pstdev(values),
        }


class PlottingMixin:
    """Provide plot saving logic."""

    def save_plot(self, rows: list[FunctionRow], path: Path) -> Path:
        """Save the comparison plot to a PNG file."""
        plt = import_matplotlib_pyplot()
        xs = [row.x for row in rows]
        series_values = [row.series_value for row in rows]
        math_values = [row.math_value for row in rows]

        path.parent.mkdir(parents=True, exist_ok=True)
        figure, axis = plt.subplots(figsize=(10, 6))
        axis.plot(xs, series_values, marker="o", color="tab:blue", label="Series F(x)")
        axis.plot(xs, math_values, marker="s", color="tab:red", label="Math F(x)")
        axis.axhline(0, color="black", linewidth=0.8)
        axis.axvline(0, color="black", linewidth=0.8)
        axis.set_title("Variant 1: series approximation")
        axis.set_xlabel("x")
        axis.set_ylabel("F(x)")
        axis.legend()
        axis.grid(True, linestyle="--", alpha=0.5)
        if rows:
            first = rows[0]
            axis.annotate(
                "First point\nx={:.2f}\nF={:.4f}".format(first.x, first.series_value),
                xy=(first.x, first.series_value),
                xytext=(10, 15),
                textcoords="offset points",
            )
        figure.tight_layout()
        figure.savefig(path, dpi=150)
        plt.close(figure)
        return path


class SeriesReport(ResultSaverMixin, StatisticsMixin, PlottingMixin):
    """Build a table report for task 3."""

    def render_table(self, rows: list[FunctionRow]) -> str:
        """Render rows and statistics as text."""
        header = "{:>10} {:>10} {:>16} {:>16} {:>10}".format("x", "n", "F(x)", "Math F(x)", "eps")
        lines = [header, "-" * len(header)]
        for row in rows:
            lines.append(
                "{:>10.4f} {:>10d} {:>16.8f} {:>16.8f} {:>10.6f}".format(
                    row.x,
                    row.terms_used,
                    row.series_value,
                    row.math_value,
                    row.epsilon,
                )
            )

        values = [row.series_value for row in rows]
        stats = self.calculate_statistics(values)
        lines.extend(
            [
                "",
                "Дополнительные параметры последовательности F(x):",
                f"Среднее арифметическое: {stats['mean']:.8f}",
                f"Медиана: {stats['median']:.8f}",
                f"Мода: {stats['mode']:.8f}",
                f"Дисперсия: {stats['variance']:.8f}",
                f"СКО: {stats['std_dev']:.8f}",
            ]
        )
        return "\n".join(lines)


class SeriesApproximationApp(RunnableTask):
    """Interactive wrapper for task 3."""

    title = "Задание 3"

    def run(self) -> None:
        """Execute task 3."""
        self.run_count += 1
        print_title("Задание 3. Разложение функции в ряд")
        print("Вариант 1: ln((x + 1) / (x - 1)) = 2 * sum(1 / ((2n + 1) * x^(2n + 1))), |x| > 1")

        epsilon = ask_float("Введите точность eps", 0.0)
        start = ask_float("Введите начало диапазона x")
        end = ask_float("Введите конец диапазона x")
        step = ask_float("Введите шаг")
        if step <= 0:
            print("Ошибка: шаг должен быть больше нуля.")
            return
        if start > end:
            print("Ошибка: начало диапазона не должно быть больше конца.")
            return

        approximator = VariantOneApproximator(epsilon)
        rows: list[FunctionRow] = []
        current = start
        while current <= end + 1e-12:
            try:
                rows.append(approximator(round(current, 10)))
            except ValueError:
                pass
            current += step

        if not rows:
            print("В указанном диапазоне нет значений x, удовлетворяющих условию |x| > 1.")
            return

        report = SeriesReport()
        report_text = report.render_table(rows)
        report_path = report.save_text(OUTPUT_DIR / "series_report.txt", report_text)

        try:
            plot_path = report.save_plot(rows, OUTPUT_DIR / "series_plot.png")
        except ModuleNotFoundError:
            plot_path = None

        print(report_text)
        print(f"\nТаблица сохранена в: {report_path}")
        if plot_path is None:
            print("График не построен: не найден matplotlib.")
        else:
            print(f"График сохранён в: {plot_path}")
