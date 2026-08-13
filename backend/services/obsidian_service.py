from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from backend.config import inbox_tags, load_config, resolve_vault_path


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
TAG_RE = re.compile(r"(?<!\w)#([a-zA-Z0-9_/\-]+)")
CHECKBOX_RE = re.compile(r"^[\s>*-]*\[([ xX])\]\s+(.*)$", re.MULTILINE)
OUTPUT_LINK_RE = re.compile(
    r"\[([^\]]+)\]\((https?://[^\)]+)\)|(https?://[^\s\)\]]+)",
    re.IGNORECASE,
)
OUTPUT_HINT_RE = re.compile(
    r"(demo|vercel\.app|netlify\.app|github\.com|gitlab\.com|x\.com|twitter\.com|"
    r"bilibili\.com|youtu\.?be|localhost:\d+)",
    re.IGNORECASE,
)


class ObsidianService:
    """Scan an Obsidian vault for inbox ideas, weekly metrics, and outputs."""

    def __init__(self, vault_path: Optional[str] = None) -> None:
        self._vault_override = vault_path

    def get_summary(self) -> Dict[str, Any]:
        vault = resolve_vault_path(self._vault_override)
        config = load_config()

        if vault is None:
            return {
                "ok": False,
                "error": "vault_path_not_configured",
                "message": "请在 config.json 中设置有效的 vault_path",
                "vault_path": config.get("vault_path", ""),
                "ideas": [],
                "outputs": [],
                "weekly": [],
                "stats": self._empty_stats(),
                "scanned_at": datetime.now().isoformat(timespec="seconds"),
            }

        ideas: List[Dict[str, Any]] = []
        outputs: List[Dict[str, Any]] = []
        weekly: List[Dict[str, Any]] = []
        tag_counter: Dict[str, int] = {}

        md_files = [
            p
            for p in vault.rglob("*.md")
            if ".obsidian" not in p.parts and not p.name.startswith(".")
        ]

        pattern = config.get("weekly_note_pattern") or "Weekly-*.md"
        for path in md_files:
            text = self._read_text(path)
            if text is None:
                continue

            frontmatter, body = self._split_frontmatter(text)
            tags = self._collect_tags(frontmatter, body)
            rel = str(path.relative_to(vault))

            for tag in tags:
                tag_counter[tag] = tag_counter.get(tag, 0) + 1

            idea = self._extract_idea(path, rel, frontmatter, body, tags)
            if idea:
                ideas.append(idea)

            note_outputs = self._extract_outputs(path, rel, body)
            outputs.extend(note_outputs)

            if path.match(pattern) or path.name.lower().startswith("weekly"):
                weekly.append(self._parse_weekly(path, rel, body, note_outputs))

        ideas.sort(key=lambda x: x.get("mtime", ""), reverse=True)
        outputs.sort(key=lambda x: x.get("mtime", ""), reverse=True)
        weekly.sort(key=lambda x: x.get("name", ""), reverse=True)

        completed = sum(w["completed"] for w in weekly)
        planned = sum(w["planned"] for w in weekly)
        rate = round((completed / planned) * 100, 1) if planned else 0.0

        return {
            "ok": True,
            "vault_path": str(vault),
            "ideas": ideas,
            "outputs": outputs,
            "weekly": weekly,
            "stats": {
                "ideas_count": len(ideas),
                "outputs_count": len(outputs),
                "weekly_notes": len(weekly),
                "tasks_planned": planned,
                "tasks_completed": completed,
                "execution_rate": rate,
                "tag_distribution": dict(
                    sorted(tag_counter.items(), key=lambda kv: kv[1], reverse=True)[:20]
                ),
                "files_scanned": len(md_files),
            },
            "scanned_at": datetime.now().isoformat(timespec="seconds"),
        }

    def _empty_stats(self) -> Dict[str, Any]:
        return {
            "ideas_count": 0,
            "outputs_count": 0,
            "weekly_notes": 0,
            "tasks_planned": 0,
            "tasks_completed": 0,
            "execution_rate": 0.0,
            "tag_distribution": {},
            "files_scanned": 0,
        }

    def _read_text(self, path: Path) -> Optional[str]:
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None

    def _split_frontmatter(self, text: str) -> Tuple[Dict[str, Any], str]:
        match = FRONTMATTER_RE.match(text)
        if not match:
            return {}, text
        raw = match.group(1)
        try:
            data = yaml.safe_load(raw) or {}
            if not isinstance(data, dict):
                data = {}
        except yaml.YAMLError:
            data = {}
        return data, text[match.end() :]

    def _collect_tags(self, frontmatter: Dict[str, Any], body: str) -> List[str]:
        tags: List[str] = []
        fm_tags = frontmatter.get("tags") or frontmatter.get("tag") or []
        if isinstance(fm_tags, str):
            fm_tags = [fm_tags]
        for tag in fm_tags:
            tags.append(str(tag).lstrip("#"))
        tags.extend(TAG_RE.findall(body))
        # preserve order, unique
        seen = set()
        ordered: List[str] = []
        for tag in tags:
            if tag not in seen:
                seen.add(tag)
                ordered.append(tag)
        return ordered

    def _extract_idea(
        self,
        path: Path,
        rel: str,
        frontmatter: Dict[str, Any],
        body: str,
        tags: List[str],
    ) -> Optional[Dict[str, Any]]:
        wanted = set(inbox_tags())
        matched = [
            t for t in tags if any(t == w or t.startswith(f"{w}/") for w in wanted)
        ]
        if not matched:
            return None

        title = str(frontmatter.get("title") or path.stem)
        preview = self._preview(body)
        mtime = datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")
        return {
            "id": rel,
            "title": title,
            "path": rel,
            "tags": matched,
            "all_tags": tags,
            "preview": preview,
            "mtime": mtime,
            "source": "obsidian",
        }

    def _extract_outputs(self, path: Path, rel: str, body: str) -> List[Dict[str, Any]]:
        mtime = datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")
        results: List[Dict[str, Any]] = []
        seen_urls: set[str] = set()

        for match in OUTPUT_LINK_RE.finditer(body):
            label = (match.group(1) or "").strip()
            url = (match.group(2) or match.group(3) or "").strip()
            if not url or url in seen_urls:
                continue
            if not OUTPUT_HINT_RE.search(url) and not OUTPUT_HINT_RE.search(label):
                # keep links under sections that look like outputs
                continue
            seen_urls.add(url)
            results.append(
                {
                    "id": f"{rel}:{url}",
                    "title": label or url,
                    "url": url,
                    "note_path": rel,
                    "note_title": path.stem,
                    "kind": self._classify_output(url),
                    "mtime": mtime,
                }
            )
        return results

    def _classify_output(self, url: str) -> str:
        lower = url.lower()
        if "github.com" in lower or "gitlab.com" in lower:
            return "repo"
        if "x.com" in lower or "twitter.com" in lower:
            return "tweet"
        if "vercel.app" in lower or "netlify.app" in lower or "demo" in lower or "localhost" in lower:
            return "demo"
        return "link"

    def _parse_weekly(
        self,
        path: Path,
        rel: str,
        body: str,
        note_outputs: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        checks = CHECKBOX_RE.findall(body)
        completed = sum(1 for mark, _ in checks if mark.lower() == "x")
        planned = len(checks)
        rate = round((completed / planned) * 100, 1) if planned else 0.0
        return {
            "id": rel,
            "name": path.stem,
            "path": rel,
            "planned": planned,
            "completed": completed,
            "execution_rate": rate,
            "outputs_count": len(note_outputs),
            "outputs": note_outputs,
        }

    def _preview(self, body: str, limit: int = 160) -> str:
        lines = []
        for line in body.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("!"):
                continue
            lines.append(stripped)
            if sum(len(x) for x in lines) >= limit:
                break
        text = " ".join(lines)
        return text[:limit] + ("…" if len(text) > limit else "")
