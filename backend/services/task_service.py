from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.config import DB_PATH, ensure_data_dir


VALID_STATUSES = ("todo", "doing", "done")


class TaskService:
    """Local SQLite-backed Kanban task store with idea/output links."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        ensure_data_dir()
        self.db_path = str(db_path or DB_PATH)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'todo',
                    idea_path TEXT,
                    idea_title TEXT,
                    output_url TEXT,
                    output_title TEXT,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def get_tasks(self) -> Dict[str, Any]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM tasks ORDER BY updated_at DESC"
            ).fetchall()
        tasks = [self._row_to_dict(row) for row in rows]
        columns = {
            "todo": [t for t in tasks if t["status"] == "todo"],
            "doing": [t for t in tasks if t["status"] == "doing"],
            "done": [t for t in tasks if t["status"] == "done"],
        }
        return {"ok": True, "tasks": tasks, "columns": columns, "count": len(tasks)}

    def update_task_status(self, task_id: str, status: str) -> Dict[str, Any]:
        if status not in VALID_STATUSES:
            return {
                "ok": False,
                "error": "invalid_status",
                "message": f"status must be one of {VALID_STATUSES}",
            }

        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
                (status, now, task_id),
            )
            conn.commit()
            if cur.rowcount == 0:
                return {"ok": False, "error": "not_found", "message": "task not found"}
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()

        return {"ok": True, "task": self._row_to_dict(row)}

    def create_task_from_idea(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        title = str(idea.get("title") or idea.get("path") or "Untitled idea").strip()
        idea_path = str(idea.get("path") or idea.get("id") or "")
        now = datetime.now().isoformat(timespec="seconds")
        task_id = uuid.uuid4().hex

        with self._connect() as conn:
            # avoid duplicate open tasks for same idea
            existing = conn.execute(
                """
                SELECT * FROM tasks
                WHERE idea_path = ? AND status != 'done'
                ORDER BY updated_at DESC LIMIT 1
                """,
                (idea_path,),
            ).fetchone()
            if existing:
                return {
                    "ok": True,
                    "created": False,
                    "task": self._row_to_dict(existing),
                    "message": "已存在未完成任务",
                }

            conn.execute(
                """
                INSERT INTO tasks (
                    id, title, status, idea_path, idea_title,
                    output_url, output_title, notes, created_at, updated_at
                ) VALUES (?, ?, 'todo', ?, ?, NULL, NULL, ?, ?, ?)
                """,
                (
                    task_id,
                    title,
                    idea_path,
                    title,
                    str(idea.get("preview") or ""),
                    now,
                    now,
                ),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()

        return {"ok": True, "created": True, "task": self._row_to_dict(row)}

    def link_output(
        self, task_id: str, output_url: str, output_title: str = ""
    ) -> Dict[str, Any]:
        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE tasks
                SET output_url = ?, output_title = ?, updated_at = ?
                WHERE id = ?
                """,
                (output_url, output_title, now, task_id),
            )
            conn.commit()
            if cur.rowcount == 0:
                return {"ok": False, "error": "not_found", "message": "task not found"}
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
        return {"ok": True, "task": self._row_to_dict(row)}

    def create_demo_tasks_if_empty(self) -> None:
        with self._connect() as conn:
            count = conn.execute("SELECT COUNT(*) AS c FROM tasks").fetchone()["c"]
            if count:
                return
        samples: List[Dict[str, Any]] = [
            {
                "title": "解析 Obsidian Inbox 灵感",
                "status": "doing",
                "idea_path": "demo/inbox-parser.md",
                "notes": "MVP 骨架示例任务",
            },
            {
                "title": "搭建效能看板",
                "status": "todo",
                "idea_path": "demo/kanban.md",
                "notes": "Vue 3 Kanban",
            },
            {
                "title": "输出周复盘指标",
                "status": "done",
                "idea_path": "demo/weekly.md",
                "notes": "execution rate / outputs",
                "output_url": "https://github.com/example/center-collect-show",
                "output_title": "Repo",
            },
        ]
        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            for sample in samples:
                conn.execute(
                    """
                    INSERT INTO tasks (
                        id, title, status, idea_path, idea_title,
                        output_url, output_title, notes, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        uuid.uuid4().hex,
                        sample["title"],
                        sample["status"],
                        sample.get("idea_path"),
                        sample["title"],
                        sample.get("output_url"),
                        sample.get("output_title"),
                        sample.get("notes"),
                        now,
                        now,
                    ),
                )
            conn.commit()

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "title": row["title"],
            "status": row["status"],
            "idea_path": row["idea_path"],
            "idea_title": row["idea_title"],
            "output_url": row["output_url"],
            "output_title": row["output_title"],
            "notes": row["notes"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
