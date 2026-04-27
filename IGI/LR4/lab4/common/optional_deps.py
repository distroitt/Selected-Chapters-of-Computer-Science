"""Helpers for optional third-party dependencies.

Laboratory work #4: files, classes, serializers, regex and standard libraries.
Version: 1.0.0
Developer: Dmitry Adarov
Date: 2026-04-21
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOCAL_DEPS = PROJECT_ROOT / ".deps"


def bootstrap_local_dependencies() -> None:
    """Add a local dependency directory to sys.path when it exists."""
    if LOCAL_DEPS.exists():
        sys.path.insert(0, str(LOCAL_DEPS))


def import_numpy():
    """Import NumPy after bootstrapping optional dependencies."""
    bootstrap_local_dependencies()
    import numpy as np  # type: ignore

    return np


def import_matplotlib_pyplot():
    """Import matplotlib.pyplot after bootstrapping optional dependencies."""
    bootstrap_local_dependencies()
    config_dir = PROJECT_ROOT / ".mplconfig"
    config_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(config_dir))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # type: ignore

    return plt


def import_pandas():
    """Import pandas after bootstrapping optional dependencies."""
    bootstrap_local_dependencies()
    import pandas as pd  # type: ignore

    return pd
