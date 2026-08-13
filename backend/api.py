from __future__ import annotations

import subprocess
import sys
import threading
from pathlib import Path
from typing import Any, Dict

from backend.config import load_config, resolve_vault_path, save_config
from backend.services.obsidian_service import ObsidianService
from backend.services.task_service import TaskService


class Api:
    """JS-facing bridge methods exposed via pywebview.api."""

    def __init__(self) -> None:
        self.obsidian = ObsidianService()
        self.tasks = TaskService()
        self.tasks.create_demo_tasks_if_empty()
        self._jobs: Dict[str, Dict[str, Any]] = {}

    def get_config(self) -> Dict[str, Any]:
        config = load_config()
        vault = resolve_vault_path()
        return {
            "ok": True,
            "config": config,
            "vault_ready": vault is not None,
            "vault_resolved": str(vault) if vault else "",
        }

    def set_vault_path(self, vault_path: str) -> Dict[str, Any]:
        config = load_config()
        config["vault_path"] = vault_path
        save_config(config)
        resolved = resolve_vault_path(vault_path)
        return {
            "ok": resolved is not None,
            "vault_path": vault_path,
            "vault_resolved": str(resolved) if resolved else "",
            "message": None if resolved else "路径不存在或不是目录",
        }

    def get_obsidian_summary(self) -> Dict[str, Any]:
        return self.obsidian.get_summary()

    def get_tasks(self) -> Dict[str, Any]:
        return self.tasks.get_tasks()

    def update_task_status(self, task_id: str, status: str) -> Dict[str, Any]:
        return self.tasks.update_task_status(task_id, status)

    def create_task_from_idea(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        return self.tasks.create_task_from_idea(idea)

    def link_task_output(
        self, task_id: str, output_url: str, output_title: str = ""
    ) -> Dict[str, Any]:
        return self.tasks.link_output(task_id, output_url, output_title)

    def trigger_automation_script(self, script_name: str) -> Dict[str, Any]:
        """Run a local Python script in a background thread (non-blocking)."""
        root = Path(__file__).resolve().parent.parent
        scripts_dir = root / "scripts"
        script_path = (scripts_dir / script_name).resolve()

        if not str(script_path).startswith(str(scripts_dir.resolve())):
            return {"ok": False, "error": "invalid_path", "message": "非法脚本路径"}
        if not script_path.exists():
            return {
                "ok": False,
                "error": "not_found",
                "message": f"脚本不存在: {script_name}",
            }

        job_id = f"{script_name}:{threading.get_ident()}:{len(self._jobs)}"
        self._jobs[job_id] = {"status": "running", "script": script_name}

        def _run() -> None:
            try:
                completed = subprocess.run(
                    [sys.executable, str(script_path)],
                    capture_output=True,
                    text=True,
                    cwd=str(root),
                    check=False,
                )
                self._jobs[job_id] = {
                    "status": "done" if completed.returncode == 0 else "failed",
                    "script": script_name,
                    "returncode": completed.returncode,
                    "stdout": completed.stdout[-4000:],
                    "stderr": completed.stderr[-4000:],
                }
            except Exception as exc:  # noqa: BLE001 — surface to UI
                self._jobs[job_id] = {
                    "status": "failed",
                    "script": script_name,
                    "error": str(exc),
                }

        threading.Thread(target=_run, daemon=True).start()
        return {"ok": True, "job_id": job_id, "status": "started"}

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        job = self._jobs.get(job_id)
        if not job:
            return {"ok": False, "error": "not_found"}
        return {"ok": True, "job": job}

    def ping(self) -> Dict[str, Any]:
        return {"ok": True, "message": "pywebview bridge ready"}
