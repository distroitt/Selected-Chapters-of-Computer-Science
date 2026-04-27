"""Task 1: serializers and classes.

Laboratory work #4: files, classes, serializers, regex and standard libraries.
Version: 1.0.0
Developer: Dmitry Adarov
Date: 2026-04-21
"""

from __future__ import annotations

import csv
import pickle
from abc import ABC, abstractmethod
from pathlib import Path

from lab4.common.base import NamedEntity, ResultSaverMixin, RunnableTask
from lab4.common.input_utils import ask_non_empty, print_title


DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "task1"
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs" / "task1"


class TradeRecord(NamedEntity):
    """Represent a generic trade record."""

    category = "trade"

    def __init__(self, product_name: str, country: str, volume: int) -> None:
        """Initialize a trade record."""
        super().__init__(product_name)
        self.country = country.strip()
        self.volume = volume

    @property
    def volume(self) -> int:
        """Return the supplied volume."""
        return self._volume

    @volume.setter
    def volume(self, value: int) -> None:
        """Validate and store volume."""
        if int(value) <= 0:
            raise ValueError("Volume must be positive.")
        self._volume = int(value)

    def to_dict(self) -> dict[str, str | int]:
        """Convert the record to a dictionary."""
        return {"product": self.name, "country": self.country, "volume": self.volume}

    def summary(self) -> str:
        """Return a one-line description of the record."""
        return "{} -> {}: {} pcs".format(self.name, self.country, self.volume)

    def __len__(self) -> int:
        """Return the volume for a magic-method example."""
        return self.volume


class ExportRecord(TradeRecord):
    """Represent an export record."""

    category = "export"

    def summary(self) -> str:
        """Return an export-specific description."""
        return "Export {} to {}: {} pcs".format(self.name, self.country, self.volume)


class ImportRecord(TradeRecord):
    """Represent an import record to demonstrate polymorphism."""

    category = "import"

    def summary(self) -> str:
        """Return an import-specific description."""
        return "Import {} from {}: {} pcs".format(self.name, self.country, self.volume)


class RepositoryBase(ABC):
    """Abstract repository for export records."""

    repository_name = "base"

    def __init__(self, path: Path) -> None:
        """Store the target file path."""
        self.path = path

    @abstractmethod
    def save(self, records: list[ExportRecord]) -> Path:
        """Save records to a file."""

    @abstractmethod
    def load(self) -> list[ExportRecord]:
        """Load records from a file."""


class CsvExportRepository(RepositoryBase):
    """Store export records in CSV format."""

    repository_name = "CSV"

    def save(self, records: list[ExportRecord]) -> Path:
        """Save export records to a CSV file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["product", "country", "volume"])
            writer.writeheader()
            writer.writerows(record.to_dict() for record in records)
        return self.path

    def load(self) -> list[ExportRecord]:
        """Load export records from a CSV file."""
        with self.path.open("r", encoding="utf-8", newline="") as file:
            rows = csv.DictReader(file)
            return [
                ExportRecord(row["product"], row["country"], int(row["volume"]))
                for row in rows
            ]


class PickleExportRepository(RepositoryBase):
    """Store export records in pickle format."""

    repository_name = "pickle"

    def save(self, records: list[ExportRecord]) -> Path:
        """Save export records to a pickle file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("wb") as file:
            pickle.dump([record.to_dict() for record in records], file)
        return self.path

    def load(self) -> list[ExportRecord]:
        """Load export records from a pickle file."""
        with self.path.open("rb") as file:
            rows = pickle.load(file)
        return [ExportRecord(row["product"], row["country"], int(row["volume"])) for row in rows]


class ExportCatalogue(ResultSaverMixin):
    """Manage export records and reporting logic."""

    def __init__(self, records: list[ExportRecord]) -> None:
        """Store export records."""
        self.records = sorted(records)

    @classmethod
    def from_dictionary(cls, source_data: dict[str, list[dict[str, str | int]]]) -> "ExportCatalogue":
        """Create the catalogue from the required dictionary structure."""
        records: list[ExportRecord] = []
        for product, shipments in source_data.items():
            for shipment in shipments:
                records.append(ExportRecord(product, str(shipment["country"]), int(shipment["volume"])))
        return cls(records)

    def find_product(self, product_name: str) -> list[ExportRecord]:
        """Return all records for one product."""
        return [record for record in self.records if record.name.lower() == product_name.lower()]

    def total_volume(self, product_name: str) -> int:
        """Calculate the total export volume for a product."""
        return sum(record.volume for record in self.find_product(product_name))

    def countries_for_product(self, product_name: str) -> list[str]:
        """Return sorted unique countries for a product."""
        countries = {record.country for record in self.find_product(product_name)}
        return sorted(countries)

    def render_report(self, product_name: str) -> str:
        """Create a human-readable report."""
        selected = self.find_product(product_name)
        if not selected:
            return f"Товар '{product_name}' не найден."

        countries = ", ".join(self.countries_for_product(product_name))
        total = self.total_volume(product_name)
        lines = [
            f"Информация по товару: {product_name}",
            f"Страны-импортёры: {countries}",
            f"Общий объём экспорта: {total} шт.",
            "",
            "Отсортированные записи:",
        ]
        lines.extend(f"- {record.summary()}" for record in sorted(selected, key=lambda item: item.country.lower()))
        return "\n".join(lines)


class ExportTaskApp(RunnableTask, ResultSaverMixin):
    """Interactive wrapper for task 1."""

    title = "Задание 1"

    def run(self) -> None:
        """Execute task 1."""
        self.run_count += 1
        print_title("Задание 1. Экспортируемые товары")

        source_data = {
            "Ноутбук": [
                {"country": "Польша", "volume": 120},
                {"country": "Литва", "volume": 90},
                {"country": "Германия", "volume": 50},
            ],
            "Монитор": [
                {"country": "Латвия", "volume": 70},
                {"country": "Польша", "volume": 65},
            ],
            "Сканер": [
                {"country": "Чехия", "volume": 40},
                {"country": "Словакия", "volume": 25},
            ],
        }
        catalogue = ExportCatalogue.from_dictionary(source_data)
        product_name = ask_non_empty("Введите название товара")

        csv_repo = CsvExportRepository(OUTPUT_DIR / "exports.csv")
        pickle_repo = PickleExportRepository(OUTPUT_DIR / "exports.pkl")
        csv_repo.save(catalogue.records)
        pickle_repo.save(catalogue.records)

        csv_loaded = ExportCatalogue(csv_repo.load())
        pickle_loaded = ExportCatalogue(pickle_repo.load())

        report = [
            "Исходный словарь сохранён в два формата.",
            f"CSV-файл: {csv_repo.path}",
            f"Pickle-файл: {pickle_repo.path}",
            "",
            "Отчёт после чтения CSV:",
            csv_loaded.render_report(product_name),
            "",
            "Отчёт после чтения pickle:",
            pickle_loaded.render_report(product_name),
        ]
        report_text = "\n".join(report)
        report_path = self._save_demo_dictionary(source_data, report_text)
        print(report_text)
        print(f"\nТекстовый отчёт сохранён в: {report_path}")

    def _save_demo_dictionary(self, source_data: dict[str, list[dict[str, str | int]]], report_text: str) -> Path:
        """Save the source dictionary and final report."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        source_lines = ["Исходный словарь варианта 1:"]
        for product, shipments in source_data.items():
            source_lines.append(f"{product}: {shipments}")
        source_path = DATA_DIR / "source_dictionary.txt"
        source_path.write_text("\n".join(source_lines), encoding="utf-8")
        return self.save_text(OUTPUT_DIR / "report.txt", report_text)
