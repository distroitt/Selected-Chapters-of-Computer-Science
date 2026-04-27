"""Main application module.

Laboratory work #4: files, classes, serializers, regex and standard libraries.
Version: 1.0.0
Developer: Dmitry Adarov
Date: 2026-04-21
"""

from __future__ import annotations

from lab4.common.input_utils import ask_menu_choice, print_title, wait_for_enter
from lab4.tasks.task1_exports import ExportTaskApp
from lab4.tasks.task2_text import TextAnalysisApp
from lab4.tasks.task3_series import SeriesApproximationApp
from lab4.tasks.task4_geometry import GeometryTaskApp
from lab4.tasks.task5_numpy import NumPyTaskApp
from lab4.tasks.task6_pandas import PandasTaskApp


def run_application() -> None:
    """Run the interactive laboratory launcher."""
    apps = {
        "1": ExportTaskApp(),
        "2": TextAnalysisApp(),
        "3": SeriesApproximationApp(),
        "4": GeometryTaskApp(),
        "5": NumPyTaskApp(),
        "6": PandasTaskApp(),
    }

    while True:
        print_title("Лабораторная работа 4, вариант 1")
        print("1. Задание 1 - сериализация словаря в CSV и pickle")
        print("2. Задание 2 - анализ текста и регулярные выражения")
        print("3. Задание 3 - разложение функции в ряд и графики")
        print("4. Задание 4 - базовые и производные классы фигур")
        print("5. Задание 5 - NumPy и матрица")
        print("6. Задание 6 - Pandas и Titanic")
        print("0. Выход")

        choice = ask_menu_choice("Выберите пункт меню", {"0", *apps.keys()})
        if choice == "0":
            print("Работа завершена.")
            return

        apps[choice].run()
        wait_for_enter()
