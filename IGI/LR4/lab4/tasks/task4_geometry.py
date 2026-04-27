"""Task 4: geometry classes and inheritance.

Laboratory work #4: files, classes, serializers, regex and standard libraries.
Version: 1.0.0
Developer: Dmitry Adarov
Date: 2026-04-21
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from lab4.common.base import ResultSaverMixin, RunnableTask
from lab4.common.input_utils import ask_float, ask_non_empty, print_title
from lab4.common.optional_deps import import_matplotlib_pyplot


OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs" / "task4"


class ColorFigure:
    """Store a figure color using a property."""

    def __init__(self, color: str) -> None:
        """Initialize the color."""
        self.color = color

    @property
    def color(self) -> str:
        """Return the figure color."""
        return self._color

    @color.setter
    def color(self, value: str) -> None:
        """Validate and store the figure color."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Color must not be empty.")
        self._color = cleaned


class GeometricFigure(ABC):
    """Abstract geometric figure."""

    figure_name = "Figure"

    def __init__(self, color: str) -> None:
        """Create the color object."""
        self.figure_color = ColorFigure(color)

    @classmethod
    def get_figure_name(cls) -> str:
        """Return the class figure name."""
        return cls.figure_name

    @abstractmethod
    def area(self) -> float:
        """Calculate the area."""

    @abstractmethod
    def vertices(self) -> list[tuple[float, float]]:
        """Return figure vertices for drawing."""


class DrawableMixin:
    """Draw a figure with matplotlib."""

    def draw(self, label: str, output_path: Path) -> Path:
        """Save the figure image to a file."""
        plt = import_matplotlib_pyplot()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        figure, axis = plt.subplots(figsize=(6, 6))
        points = self.vertices()
        xs = [point[0] for point in points] + [points[0][0]]
        ys = [point[1] for point in points] + [points[0][1]]
        axis.fill(xs, ys, color=self.figure_color.color, alpha=0.65)
        axis.plot(xs, ys, color="black", linewidth=1.5)

        centroid_x = sum(point[0] for point in points) / len(points)
        centroid_y = sum(point[1] for point in points) / len(points)
        axis.text(centroid_x, centroid_y, label, ha="center", va="center", fontsize=12)
        axis.set_aspect("equal", adjustable="box")
        axis.grid(True, linestyle="--", alpha=0.5)
        axis.set_title(self.get_figure_name())
        axis.axhline(0, color="black", linewidth=0.8)
        axis.axvline(0, color="black", linewidth=0.8)
        figure.tight_layout()
        figure.savefig(output_path, dpi=150)
        plt.close(figure)
        return output_path


class TriangleFigure(GeometricFigure, DrawableMixin):
    """Base triangle class."""

    figure_name = "Triangle"

    def __len__(self) -> int:
        """Return the number of vertices."""
        return len(self.vertices())


class IsoscelesTriangle(TriangleFigure):
    """Variant 1 figure: an isosceles triangle."""

    figure_name = "Isosceles Triangle"

    def __init__(self, base: float, height: float, color: str) -> None:
        """Initialize triangle dimensions and color."""
        super().__init__(color)
        self.base = base
        self.height = height

    @property
    def base(self) -> float:
        """Return the base length."""
        return self._base

    @base.setter
    def base(self, value: float) -> None:
        """Validate and store the base length."""
        if value <= 0:
            raise ValueError("Base must be positive.")
        self._base = value

    @property
    def height(self) -> float:
        """Return the height."""
        return self._height

    @height.setter
    def height(self, value: float) -> None:
        """Validate and store the height."""
        if value <= 0:
            raise ValueError("Height must be positive.")
        self._height = value

    def area(self) -> float:
        """Calculate the triangle area."""
        return self.base * self.height / 2

    def vertices(self) -> list[tuple[float, float]]:
        """Return triangle vertices."""
        half_base = self.base / 2
        return [(-half_base, 0.0), (half_base, 0.0), (0.0, self.height)]

    def describe(self) -> str:
        """Return the figure description using format()."""
        return "{} of color {} with base {:.2f}, height {:.2f}, area {:.2f}".format(
            self.get_figure_name(),
            self.figure_color.color,
            self.base,
            self.height,
            self.area(),
        )


class GeometryTaskApp(RunnableTask, ResultSaverMixin):
    """Interactive wrapper for task 4."""

    title = "Задание 4"

    def run(self) -> None:
        """Execute task 4."""
        self.run_count += 1
        print_title("Задание 4. Равнобедренный треугольник")

        base = ask_float("Введите основание a", 0.0)
        height = ask_float("Введите высоту h", 0.0)
        color = ask_non_empty("Введите цвет фигуры (например, skyblue)")
        label = ask_non_empty("Введите подпись фигуры")

        triangle = IsoscelesTriangle(base, height, color)
        description = triangle.describe()
        report_path = self.save_text(OUTPUT_DIR / "triangle_report.txt", description)

        try:
            image_path = triangle.draw(label, OUTPUT_DIR / "triangle.png")
        except ModuleNotFoundError:
            image_path = None

        print(description)
        print(f"Количество вершин (__len__): {len(triangle)}")
        print(f"Текстовый отчёт сохранён в: {report_path}")
        if image_path is None:
            print("Рисунок не построен: не найден matplotlib.")
        else:
            print(f"Рисунок сохранён в: {image_path}")
