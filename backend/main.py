from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow `python backend/main.py` from repo root
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import webview

from backend.api import Api
from backend.config import FRONTEND_DEV_URL, FRONTEND_DIST, load_config


def resolve_ui_url(dev: bool) -> str:
    if dev:
        return FRONTEND_DEV_URL
    index = FRONTEND_DIST / "index.html"
    if not index.exists():
        raise FileNotFoundError(
            "frontend/dist/index.html 不存在。请先执行: cd frontend && npm run build\n"
            "或开发模式: python backend/main.py --dev（需先 npm run dev）"
        )
    return index.as_uri()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Engineer Control Panel")
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Load Vite dev server at http://127.0.0.1:5173",
    )
    args = parser.parse_args(argv)

    config = load_config()
    window_cfg = config.get("window") or {}
    api = Api()
    url = resolve_ui_url(dev=args.dev)

    window = webview.create_window(
        title=window_cfg.get("title") or "Engineer Control Panel",
        url=url,
        js_api=api,
        width=int(window_cfg.get("width") or 1440),
        height=int(window_cfg.get("height") or 900),
        min_size=(960, 640),
    )
    webview.start(debug=args.dev)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
