from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Optional

from .config import DATABASE_PATH


def init_db() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL,
                preset_id TEXT,
                scenario_id TEXT,
                artifact_dir TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


def save_run(
    run_id: str,
    created_at: str,
    status: str,
    preset_id: Optional[str],
    scenario_id: str,
    artifact_dir: Path,
    payload: dict[str, Any],
) -> None:
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        connection.execute(
            """
            INSERT OR REPLACE INTO runs (
                run_id,
                created_at,
                status,
                preset_id,
                scenario_id,
                artifact_dir,
                payload_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                created_at,
                status,
                preset_id,
                scenario_id,
                str(artifact_dir),
                json.dumps(payload, default=str),
            ),
        )
        connection.commit()
    finally:
        connection.close()


def load_run(run_id: str) -> Optional[dict[str, Any]]:
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        row = connection.execute(
            """
            SELECT payload_json
            FROM runs
            WHERE run_id = ?
            """,
            (run_id,),
        ).fetchone()
        if row is None:
            return None
        return json.loads(row[0])
    finally:
        connection.close()
