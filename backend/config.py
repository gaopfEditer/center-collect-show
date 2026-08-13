from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config.json"
DATA_DIR = ROOT_DIR / "backend" / "data"
DB_PATH = DATA_DIR / "tasks.db"
FRONTEND_DIST = ROOT_DIR / "frontend" / "dist"
FRONTEND_DEV_URL = "http://127.0.0.1:5173"

DEFAULT_CONFIG: Dict[str, Any] = {
    "vault_path": "",
    "weekly_note_pattern": "Weekly-*.md",
    "inbox_tags": [
        "inbox/demand",
        "inbox/traffic",
        "inbox/tech",
        "inbox/resources",
    ],
    "window": {
        "title": "Engineer Control Panel",
        "width": 1440,
        "height": 900,
    },
}


def ensure_data_dir() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def load_config() -> Dict[str, Any]:
    ensure_data_dir()
    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)

    with CONFIG_PATH.open("r", encoding="utf-8") as fp:
        raw = json.load(fp)

    merged = dict(DEFAULT_CONFIG)
    merged.update(raw)
    if "window" in raw and isinstance(raw["window"], dict):
        window = dict(DEFAULT_CONFIG["window"])
        window.update(raw["window"])
        merged["window"] = window
    return merged


def save_config(config: Dict[str, Any]) -> None:
    with CONFIG_PATH.open("w", encoding="utf-8") as fp:
        json.dump(config, fp, ensure_ascii=False, indent=2)
        fp.write("\n")


def resolve_vault_path(raw: str | None = None) -> Path | None:
    value = (raw if raw is not None else load_config().get("vault_path", "")).strip()
    if not value:
        return None
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = (ROOT_DIR / path).resolve()
    else:
        path = path.resolve()
    return path if path.exists() and path.is_dir() else None


def inbox_tags() -> List[str]:
    tags = load_config().get("inbox_tags") or DEFAULT_CONFIG["inbox_tags"]
    return [str(t).lstrip("#") for t in tags]
