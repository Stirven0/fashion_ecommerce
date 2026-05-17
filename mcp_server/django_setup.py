import os
import sys
from pathlib import Path

import django


def setup_django():
    """Configure Django settings and initialize."""
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "config.settings.local",
    )
    os.environ.setdefault("DATABASE_URL", "sqlite:///db.sqlite3")

    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root / "fashion_store"))
    sys.path.insert(0, str(project_root))

    django.setup()
