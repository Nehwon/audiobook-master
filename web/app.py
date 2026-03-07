#!/usr/bin/env python3
"""Interface web moderne pour Audiobook Manager Pro (API + UI)."""

from __future__ import annotations

import json
import base64
import hashlib
import hmac
import logging
import sqlite3
import os
import queue
import re
import secrets
import shutil
import subprocess
import threading
import time
import urllib.error
import urllib.request
import zipfile
from dataclasses import asdict, dataclass, field
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, List, Optional

import rarfile
from flask import Flask, jsonify, render_template, request, send_file

from core.config import ProcessingConfig
from core.runtime_paths import resolve_runtime_paths
from core.processor import AudiobookProcessor, PROCESSOR_LOG_PATH

app = Flask(__name__, template_folder="../templates")
app.config["SECRET_KEY"] = "audiobook_manager_2024"

RUNTIME_PATHS = resolve_runtime_paths(profile="web")
MEDIA_DIR = RUNTIME_PATHS.source
OUTPUT_DIR = RUNTIME_PATHS.output
TEMP_DIR = RUNTIME_PATHS.temp
LOG_DIR = RUNTIME_PATHS.log
WEB_DEBUG_LOG_PATH = LOG_DIR / "web_debug.log"
DEFAULT_CONFIG_PATH = Path(os.getenv("AUDIOBOOK_CONFIG_PATH", "/app/data/config/web_config.json"))
CONFIG_PATH = DEFAULT_CONFIG_PATH
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", os.getenv("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
APP_VERSION = os.getenv("AUDIOBOOK_MANAGER_VERSION", "v2.1.2")

AUDIO_EXTENSIONS = {".mp3", ".m4a", ".m4b", ".wav", ".flac", ".aac", ".ogg"}
ARCHIVE_EXTENSIONS = {".zip", ".rar"}
SENSITIVE_CONFIG_KEYS = ("audiobookshelf_password", "audiobookshelf_api_key")
SECRET_V1_PREFIX = "enc:v1:"


@dataclass
class Job:
    id: str
    folder: str
    status: str = "pending"
    progress: int = 0
    stage: str = "En attente"
    phase_progress: Dict[str, Dict[str, object]] = field(default_factory=dict)
    error: Optional[str] = None
    output_file: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    ended_at: Optional[float] = None


jobs_lock = threading.RLock()
packets_lock = threading.RLock()
job_queue: "queue.Queue[str]" = queue.Queue()
jobs: Dict[str, Job] = {}
upload_packets: Dict[str, Dict[str, object]] = {}
packet_schedule_jobs: Dict[str, Dict[str, object]] = {}
review_bin: List[Dict] = []
worker_started = False
MAX_JOB_EVENTS = 500
job_events: List[Dict] = []
archive_validation_cache: Dict[str, Dict[str, object]] = {}
PACKET_STATUSES = ["en_attente", "en_preparation", "pret", "planifie", "publie", "erreur"]


def _api_error(message: str, status: int = 400, code: str = "bad_request", *, details: Optional[Dict] = None):
    payload: Dict[str, object] = {
        "ok": False,
        "error": message,
        "code": code,
    }
    if details:
        payload["details"] = details
    return jsonify(payload), status


def _resolve_output_file(filename: str) -> Optional[Path]:
    root = OUTPUT_DIR.resolve()
    target = (OUTPUT_DIR / filename).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        return None
    return target


def _state_db_path() -> Path:
    return TEMP_DIR / "web_state.db"


def _setup_logging() -> logging.Logger:
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("audiobook.web")
    if logger.handlers:
        return logger

    level_name = os.getenv("AUDIOBOOK_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logger.setLevel(level)

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    file_handler = RotatingFileHandler(WEB_DEBUG_LOG_PATH, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(level)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False
    return logger


logger = _setup_logging()

def _ensure_state_db() -> None:
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(_state_db_path()) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS archive_fingerprints (
                archive_name TEXT PRIMARY KEY,
                file_size INTEGER NOT NULL,
                modified REAL NOT NULL,
                md5 TEXT,
                sha256 TEXT,
                content_sig TEXT,
                updated_at REAL NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS m4b_candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_folder TEXT NOT NULL,
                output_name TEXT,
                metadata_status TEXT NOT NULL DEFAULT 'pending',
                metadata_payload TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_m4b_candidates_source_folder
            ON m4b_candidates(source_folder)
            """
        )


def _get_archive_fingerprint_from_db(archive_name: str, file_size: int, modified: float) -> Optional[Dict[str, Optional[str]]]:
    _ensure_state_db()
    with sqlite3.connect(_state_db_path()) as conn:
        row = conn.execute(
            """
            SELECT md5, sha256, content_sig
            FROM archive_fingerprints
            WHERE archive_name = ? AND file_size = ? AND modified = ?
            """,
            (archive_name, file_size, modified),
        ).fetchone()
    if not row:
        return None
    return {"md5": row[0], "sha256": row[1], "content_sig": row[2]}




def _safe_iterdir(path: Path) -> List[Path]:
    if not path.exists() or not path.is_dir():
        return []
    try:
        return list(path.iterdir())
    except Exception:  # noqa: BLE001
        return []


def _path_entries_signature(path: Path, *, allowed_suffixes: Optional[set[str]] = None) -> str:
    entries: List[str] = []
    for entry in sorted(_safe_iterdir(path), key=lambda item: item.name.lower()):
        try:
            if allowed_suffixes is not None and not entry.is_dir() and entry.suffix.lower() not in allowed_suffixes:
                continue
            stat = entry.stat()
            entry_type = "d" if entry.is_dir() else "f"
            entries.append(f"{entry.name}|{entry_type}|{int(stat.st_size)}|{int(stat.st_mtime_ns)}")
        except Exception:  # noqa: BLE001
            continue
    payload = "\n".join(entries).encode("utf-8")
    return hashlib.sha1(payload).hexdigest()


def _jobs_signature() -> str:
    with jobs_lock:
        compact_jobs = [
            {
                "id": j.id,
                "status": j.status,
                "progress": j.progress,
                "stage": j.stage,
                "error": j.error,
                "output_file": j.output_file,
            }
            for j in jobs.values()
        ]
        compact_jobs.sort(key=lambda item: str(item.get("id")))
        last_event_ts = job_events[-1]["timestamp"] if job_events else 0
        review_count = len(review_bin)
    payload = json.dumps(
        {
            "jobs": compact_jobs,
            "last_event_ts": last_event_ts,
            "review_count": review_count,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha1(payload).hexdigest()


def _compute_monitor_signatures() -> Dict[str, str]:
    return {
        "source_sig": _path_entries_signature(MEDIA_DIR),
        "output_sig": _path_entries_signature(OUTPUT_DIR, allowed_suffixes={".m4b"}),
        "jobs_sig": _jobs_signature(),
    }


def _bootstrap_upload_packets() -> None:
    with packets_lock:
        if upload_packets:
            return
        folders = sorted((entry for entry in _safe_iterdir(MEDIA_DIR) if entry.is_dir()), key=lambda p: p.name.lower())
        if not folders:
            folders = [MEDIA_DIR / "Demo - Livre 01", MEDIA_DIR / "Demo - Livre 02"]

        for index, folder in enumerate(folders):
            packet_id = hashlib.sha1(str(folder.name).encode("utf-8")).hexdigest()[:10]
            packet_files = []
            if folder.exists():
                packet_files = [
                    {
                        "name": item.name,
                        "size": item.stat().st_size,
                    }
                    for item in _safe_iterdir(folder)
                    if item.is_file() and item.suffix.lower() in AUDIO_EXTENSIONS
                ]

            upload_packets[packet_id] = {
                "id": packet_id,
                "name": folder.name,
                "status": PACKET_STATUSES[index % len(PACKET_STATUSES)],
                "progress": 0 if index % 2 == 0 else 55,
                "created_at": int(time.time()) - (index * 3600),
                "files": packet_files,
                "file_count": len(packet_files),
                "size_mb": round(sum(item["size"] for item in packet_files) / (1024 * 1024), 2),
                "metadata": {
                    "title": folder.name,
                    "author": "",
                    "series": "",
                    "volume": "",
                    "narrator": "",
                    "language": "fr",
                    "tags": "",
                    "synopsis": "",
                },
                "validation": {"ok": False, "missing": ["author", "synopsis"]},
                "changelog": {"draft": "", "edited": "", "source": "none", "updated_at": None},
            }


def _packet_payload_preview(packet: Dict[str, object]) -> Dict[str, object]:
    metadata = packet.get("metadata") if isinstance(packet.get("metadata"), dict) else {}
    return {
        "library_id": _load_config().get("audiobookshelf_library_id"),
        "files": [item.get("name") for item in packet.get("files", []) if isinstance(item, dict) and item.get("name")],
        "media": {
            "title": metadata.get("title", ""),
            "authorName": metadata.get("author", ""),
            "series": metadata.get("series", ""),
            "narratorName": metadata.get("narrator", ""),
            "language": metadata.get("language", "fr"),
            "description": metadata.get("synopsis", ""),
            "tags": [tag.strip() for tag in str(metadata.get("tags", "")).split(",") if tag.strip()],
        },
    }


def _refresh_packet_metrics(packet: Dict[str, object]) -> None:
    files = packet.get("files") if isinstance(packet.get("files"), list) else []
    packet["file_count"] = len(files)
    packet["size_mb"] = round(sum(int(item.get("size", 0)) for item in files if isinstance(item, dict)) / (1024 * 1024), 2)


def _channel_configured(config: Dict[str, object], channel: str) -> bool:
    key_map = {
        "discord": "notify_discord_webhook",
        "telegram": "notify_telegram_chat_id",
        "whatsapp": "notify_whatsapp_recipient",
        "email": "notify_email_to",
    }
    key = key_map.get(channel)
    if not key:
        return False
    return bool(str(config.get(key, "")).strip())


def _build_changelog_message(packet: Dict[str, object]) -> str:
    changelog = packet.get("changelog") if isinstance(packet.get("changelog"), dict) else {}
    message = str(changelog.get("edited") or changelog.get("draft") or "").strip()
    if message:
        return message
    metadata = packet.get("metadata") if isinstance(packet.get("metadata"), dict) else {}
    title = str(metadata.get("title") or packet.get("name") or "Publication")
    author = str(metadata.get("author") or "")
    if author:
        return f"📚 {title} — {author}\nPublication terminée."
    return f"📚 {title}\nPublication terminée."


def _deliver_changelog(packet: Dict[str, object], channels: List[str], config: Dict[str, object]) -> Dict[str, object]:
    message = _build_changelog_message(packet)
    deliveries: List[Dict[str, object]] = []
    for channel in channels:
        configured = _channel_configured(config, channel)
        deliveries.append(
            {
                "channel": channel,
                "status": "sent" if configured else "skipped",
                "reason": "ok" if configured else "channel_not_configured",
            }
        )
    return {"message": message, "deliveries": deliveries}


def _cleanup_packet_files(packet: Dict[str, object], delete_outputs: bool) -> List[str]:
    files = packet.get("files") if isinstance(packet.get("files"), list) else []
    removed_files: List[str] = []
    for item in files:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "")
        if not name:
            continue
        if delete_outputs:
            candidate = _resolve_output_file(name)
            if candidate and candidate.exists() and candidate.is_file():
                candidate.unlink(missing_ok=True)
        removed_files.append(name)

    packet["files"] = []
    _refresh_packet_metrics(packet)
    packet["cleanup"] = {
        "done": True,
        "removed_files": removed_files,
        "delete_output_files": delete_outputs,
        "at": int(time.time()),
    }
    return removed_files


def _mark_packet_published(packet: Dict[str, object], request_changelog: Optional[str] = None) -> None:
    validation = packet.get("validation") if isinstance(packet.get("validation"), dict) else {"ok": False}
    if not validation.get("ok"):
        missing = validation.get("missing", [])
        raise ValueError(f"metadata_incomplete:{','.join(str(x) for x in missing)}")

    changelog = packet.get("changelog") if isinstance(packet.get("changelog"), dict) else {}
    if isinstance(request_changelog, str) and request_changelog.strip():
        changelog["edited"] = request_changelog.strip()
        changelog["updated_at"] = int(time.time())
    packet["changelog"] = changelog
    packet["status"] = "publie"
    packet["progress"] = 100

def _save_archive_fingerprint_to_db(
    archive_name: str,
    file_size: int,
    modified: float,
    md5: Optional[str],
    sha256: Optional[str],
    content_sig: Optional[str],
) -> None:
    _ensure_state_db()
    with sqlite3.connect(_state_db_path()) as conn:
        conn.execute(
            """
            INSERT INTO archive_fingerprints
                (archive_name, file_size, modified, md5, sha256, content_sig, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(archive_name) DO UPDATE SET
                file_size = excluded.file_size,
                modified = excluded.modified,
                md5 = excluded.md5,
                sha256 = excluded.sha256,
                content_sig = excluded.content_sig,
                updated_at = excluded.updated_at
            """,
            (archive_name, file_size, modified, md5, sha256, content_sig, time.time()),
        )


def _delete_archive_fingerprint_from_db(archive_name: str) -> None:
    _ensure_state_db()
    with sqlite3.connect(_state_db_path()) as conn:
        conn.execute("DELETE FROM archive_fingerprints WHERE archive_name = ?", (archive_name,))


def _cleanup_archive_fingerprint_db(existing_archive_names: List[str]) -> None:
    _ensure_state_db()
    keep = set(existing_archive_names)
    with sqlite3.connect(_state_db_path()) as conn:
        rows = conn.execute("SELECT archive_name FROM archive_fingerprints").fetchall()
        for (name,) in rows:
            if name not in keep:
                conn.execute("DELETE FROM archive_fingerprints WHERE archive_name = ?", (name,))


def _save_m4b_candidate(source_folder: str, output_name: str) -> None:
    _ensure_state_db()
    with sqlite3.connect(_state_db_path()) as conn:
        conn.execute(
            """
            INSERT INTO m4b_candidates
                (source_folder, output_name, metadata_status, metadata_payload, created_at, updated_at)
            VALUES (?, ?, 'completed', NULL, ?, ?)
            ON CONFLICT(source_folder) DO UPDATE SET
                output_name = excluded.output_name,
                metadata_status = excluded.metadata_status,
                updated_at = excluded.updated_at
            """,
            (source_folder, output_name, time.time(), time.time()),
        )


def _get_completed_folders_with_existing_outputs() -> set[str]:
    _ensure_state_db()
    if not OUTPUT_DIR.exists():
        return set()

    existing_outputs = {file.name for file in OUTPUT_DIR.glob("*.m4b") if file.is_file()}
    if not existing_outputs:
        return set()

    placeholders = ",".join("?" for _ in existing_outputs)
    query = (
        "SELECT source_folder FROM m4b_candidates "
        "WHERE metadata_status = 'completed' AND output_name IN (" + placeholders + ")"
    )
    with sqlite3.connect(_state_db_path()) as conn:
        rows = conn.execute(query, tuple(existing_outputs)).fetchall()
    return {str(row[0]) for row in rows if row and row[0]}


_ensure_state_db()

def _default_config() -> Dict:
    return {
        "bitrate": "128k",
        "sample_rate": 44100,
        "processing_mode": "final_m4b",
        "enable_gpu": True,
        "enable_loudnorm": True,
        "enable_compressor": True,
        "auto_extract_archives": False,
        "show_live_processing_tracking": False,
        "show_backend_debug_logs": False,
        "ignored_folders": [],
        "recently_extracted_folders": [],
        "audiobookshelf_server_url": "",
        "audiobookshelf_username": "",
        "audiobookshelf_password": "",
        "audiobookshelf_api_key": "",
        "audiobookshelf_library_id": "",
        "scraping_sources": ["google_books", "audible", "babelio"],
        "cover_sources": ["existing_file", "url_download"],
        "export_plugins": ["audiobookshelf"],
        "ollama_enabled": False,
        "ollama_model": "qwen2.5:7b",
        "ollama_extract_model": "nuextract",
        "ollama_default_prompt": (
            "Tu es un agent de métadonnées audiobook. À partir du nom de dossier '{folder_name}', "
            "retourne UNIQUEMENT un JSON valide avec les clés: title, author, series, volume, confidence, "
            "search_query, source_url, notes. Commence par inférer localement depuis le nom; "
            "si un élément critique manque (ex: volume absent), alors lance une recherche web avec les MCP tools "
            "et vérifie sur des sources éditoriales fiables (éditeur, Goodreads, OpenLibrary, sites libraires). "
            "Exemple: 'T. Kingfisher - Nettle and Bone. Comment tuer un prince' => auteur=T. Kingfisher, "
            "série=Nettle and Bone, titre=Comment tuer un prince; vérifier si la série existe et trouver le numéro "
            "de volume correspondant. Si introuvable, laisser volume vide et expliquer dans notes."
        ),
        "notify_discord_webhook": "",
        "notify_telegram_bot_token": "",
        "notify_telegram_chat_id": "",
        "notify_whatsapp_recipient": "",
        "notify_email_to": "",
        "ollama_mcp_tools": json.dumps(
            [
                {
                    "name": "web_search",
                    "description": "Recherche web (Google, SearXNG, OpenLibrary, Goodreads, Audible)",
                    "input_schema": {"query": "string", "language": "string"},
                },
                {
                    "name": "fetch_page",
                    "description": "Récupère le contenu HTML/texte d'une URL cible",
                    "input_schema": {"url": "string"},
                },
                {
                    "name": "extract_metadata",
                    "description": "Extraction structurée title/author/series/narrator en JSON",
                    "input_schema": {"content": "string", "template": "json"},
                },
                {
                    "name": "mcp_web_lookup",
                    "description": "Tool MCP externe pour recherche internet quand la déduction locale est insuffisante",
                    "input_schema": {"query": "string", "need": "string"},
                },
            ],
            ensure_ascii=False,
            indent=2,
        ),
    }


def _run_ollama_command(args: List[str], timeout: int = 120) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["ollama", *args], capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError as exc:
        raise RuntimeError("Commande 'ollama' introuvable. Installez Ollama ou configurez OLLAMA_BASE_URL.") from exc


def _ollama_api_request(path: str, payload: Optional[Dict] = None, timeout: int = 120) -> Dict:
    url = f"{OLLAMA_BASE_URL}{path}"
    body = None
    headers = {}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=body, headers=headers, method="POST" if payload is not None else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="ignore")
    return json.loads(raw) if raw else {}


def _normalize_audiobookshelf_server_url(raw_url: str) -> str:
    server_url = (raw_url or "").strip().rstrip("/")
    if not server_url:
        return ""
    if not re.match(r"^https?://", server_url, flags=re.IGNORECASE):
        server_url = f"https://{server_url}"
    return server_url


def _audiobookshelf_api_request(
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    payload: Optional[Dict] = None,
    token: Optional[str] = None,
    timeout: int = 15,
) -> tuple[int, Dict[str, object], str]:
    target_url = f"{base_url}{path}"
    body = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode("utf-8")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(target_url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            parsed = json.loads(raw) if raw else {}
            return int(getattr(resp, "status", 200) or 200), parsed, raw
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace") if hasattr(exc, "read") else ""
        try:
            parsed = json.loads(raw) if raw else {}
        except Exception:
            parsed = {}
        return int(exc.code), parsed, raw


def _list_ollama_models() -> List[Dict[str, str]]:
    try:
        data = _ollama_api_request("/api/tags", timeout=20)
        models = []
        for model in data.get("models", []):
            name = model.get("name")
            if name:
                models.append({"name": name})
        if models:
            return models
    except Exception:
        pass

    try:
        result = _run_ollama_command(["list"], timeout=20)
    except Exception:
        return []

    if result.returncode != 0:
        return []

    lines = [line for line in (result.stdout or "").splitlines() if line.strip()]
    if len(lines) <= 1:
        return []

    models = []
    for line in lines[1:]:
        parts = line.split()
        if parts:
            models.append({"name": parts[0]})
    return models


def _ollama_pull_model(model: str) -> Dict:
    try:
        return _ollama_api_request("/api/pull", {"name": model, "stream": False}, timeout=600)
    except Exception:
        result = _run_ollama_command(["pull", model], timeout=600)
        if result.returncode != 0:
            raise RuntimeError((result.stderr or "Échec du pull").strip())
        return {"status": "success", "raw": (result.stdout or "").strip()}


def _ollama_delete_model(model: str) -> Dict:
    try:
        return _ollama_api_request("/api/delete", {"name": model}, timeout=120)
    except Exception:
        result = _run_ollama_command(["rm", model], timeout=120)
        if result.returncode != 0:
            raise RuntimeError((result.stderr or "Échec suppression").strip())
        return {"status": "success"}


def _extract_json_from_text(raw: str) -> Optional[Dict]:
    text = (raw or "").strip()
    if not text:
        return None

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return None

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _run_ollama_metadata_search(folder_name: str, config: Dict) -> Dict:
    model = config.get("ollama_model", "qwen2.5:7b")
    tools = config.get("ollama_mcp_tools", "[]")
    prompt_template = config.get("ollama_default_prompt", _default_config()["ollama_default_prompt"])
    base_prompt = prompt_template.replace("{folder_name}", folder_name)
    prompt = (
        f"{base_prompt}\n\n"
        "Contexte des MCP tools disponibles (JSON):\n"
        f"{tools}\n\n"
        "Réponds en JSON strict, sans markdown."
    )

    raw_output = ""
    try:
        data = _ollama_api_request(
            "/api/generate",
            {"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0}},
            timeout=90,
        )
        raw_output = data.get("response", "")
    except Exception:
        try:
            result = _run_ollama_command(["run", model, prompt], timeout=90)
        except Exception as exc:  # noqa: BLE001
            return {"folder": folder_name, "error": f"Ollama indisponible: {exc}"}

        if result.returncode != 0:
            return {"folder": folder_name, "error": (result.stderr or "Erreur Ollama").strip()}
        raw_output = result.stdout or ""

    payload = _extract_json_from_text(raw_output)
    if payload is None:
        return {
            "folder": folder_name,
            "error": "Réponse non JSON du modèle",
            "raw": raw_output.strip(),
        }

    payload["folder"] = folder_name
    return payload


def _generate_packet_changelog_draft(packet: Dict[str, object], config: Dict) -> Dict[str, object]:
    metadata = packet.get("metadata") if isinstance(packet.get("metadata"), dict) else {}
    files = packet.get("files") if isinstance(packet.get("files"), list) else []
    file_names = [str(item.get("name")) for item in files if isinstance(item, dict) and item.get("name")]

    title = str(metadata.get("title") or packet.get("name") or "Titre inconnu")
    author = str(metadata.get("author") or "Auteur inconnu")
    synopsis = str(metadata.get("synopsis") or "")
    tags = [tag.strip() for tag in str(metadata.get("tags", "")).split(",") if tag.strip()]

    prompt = (
        "Tu es un assistant qui rédige un brouillon de changelog de publication audiobook en français. "
        "Réponds avec du texte brut, concis (4 à 8 lignes), lisible et éditable humainement.\n\n"
        f"Titre: {title}\n"
        f"Auteur: {author}\n"
        f"Synopsis: {synopsis}\n"
        f"Tags: {', '.join(tags) if tags else 'aucun'}\n"
        f"Fichiers inclus: {', '.join(file_names) if file_names else 'aucun'}\n"
    )

    model = str(config.get("ollama_model") or "qwen2.5:7b")
    if bool(config.get("ollama_enabled", False)):
        try:
            data = _ollama_api_request(
                "/api/generate",
                {"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0.3}},
                timeout=90,
            )
            draft = str(data.get("response") or "").strip()
            if draft:
                return {"draft": draft, "source": "ollama"}
        except Exception as exc:  # noqa: BLE001
            logger.warning("Génération changelog via Ollama indisponible: %s", exc)

    fallback = (
        f"📚 Nouvelle publication disponible\n"
        f"Titre : {title}\n"
        f"Auteur : {author}\n"
        f"Résumé : {synopsis or 'Résumé à compléter.'}\n"
        f"Fichiers : {len(file_names)}\n"
        "#audiobook #nouveaute"
    )
    return {"draft": fallback, "source": "fallback"}


def _fix_mojibake(text: str) -> str:
    """Corrige les problèmes d'encodage les plus fréquents dans les noms."""
    fixed = text
    if "�" in fixed:
        fixed = fixed.replace("�", "e")

    if any(marker in fixed for marker in ("Ã", "Â")):
        try:
            repaired = fixed.encode("latin-1", errors="ignore").decode("utf-8", errors="ignore")
            if repaired:
                fixed = repaired
        except Exception:
            pass

    replacements = {
        "Ã©": "é",
        "Ã¨": "è",
        "Ãª": "ê",
        "Ã«": "ë",
        "Ã ": "à",
        "Ã¢": "â",
        "Ã®": "î",
        "Ã´": "ô",
        "Ã¹": "ù",
        "Å“": "œ",
    }
    for bad, good in replacements.items():
        fixed = fixed.replace(bad, good)
    return fixed


def _load_config() -> Dict:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if CONFIG_PATH.exists():
        try:
            loaded = {**_default_config(), **json.loads(CONFIG_PATH.read_text(encoding="utf-8"))}
            for key in SENSITIVE_CONFIG_KEYS:
                raw_value = loaded.get(key, "")
                loaded[key] = _decrypt_config_secret(raw_value) if isinstance(raw_value, str) else ""
            return loaded
        except Exception:
            return _default_config()
    return _default_config()


def _save_config(config: Dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    serialized = {**config}
    for key in SENSITIVE_CONFIG_KEYS:
        value = serialized.get(key, "")
        serialized[key] = _encrypt_config_secret(value) if isinstance(value, str) and value else ""
    CONFIG_PATH.write_text(json.dumps(serialized, indent=2, ensure_ascii=False), encoding="utf-8")


def _config_secret_key() -> bytes:
    secret = os.getenv("AUDIOBOOK_CONFIG_SECRET", app.config.get("SECRET_KEY", "audiobook_manager_2024"))
    if not isinstance(secret, str):
        secret = str(secret)
    return hashlib.sha256(secret.encode("utf-8")).digest()


def _stream_xor(data: bytes, key: bytes, nonce: bytes) -> bytes:
    output = bytearray()
    counter = 0
    while len(output) < len(data):
        block = hashlib.sha256(key + nonce + counter.to_bytes(4, "big")).digest()
        output.extend(block)
        counter += 1
    return bytes(d ^ output[i] for i, d in enumerate(data))


def _encrypt_config_secret(value: str) -> str:
    if not value:
        return ""
    key = _config_secret_key()
    nonce = secrets.token_bytes(16)
    plaintext = value.encode("utf-8")
    ciphertext = _stream_xor(plaintext, key, nonce)
    mac = hmac.new(key, nonce + ciphertext, hashlib.sha256).digest()
    payload = base64.urlsafe_b64encode(nonce + mac + ciphertext).decode("ascii")
    return f"{SECRET_V1_PREFIX}{payload}"


def _decrypt_config_secret(value: str) -> str:
    if not value:
        return ""
    if not value.startswith(SECRET_V1_PREFIX):
        return value

    key = _config_secret_key()
    try:
        raw = base64.urlsafe_b64decode(value[len(SECRET_V1_PREFIX):].encode("ascii"))
        if len(raw) < 48:
            return ""
        nonce = raw[:16]
        mac = raw[16:48]
        ciphertext = raw[48:]
        expected = hmac.new(key, nonce + ciphertext, hashlib.sha256).digest()
        if not hmac.compare_digest(mac, expected):
            return ""
        plaintext = _stream_xor(ciphertext, key, nonce)
        return plaintext.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def _clean_name(name: str) -> str:
    cleaned = _fix_mojibake(name).replace("+", " ")
    cleaned = re.sub(r"\[[^\]]*\]", "", cleaned)
    cleaned = re.sub(r"\.(mp3|m4a|m4b|zip|rar|flac|wav|aac|ogg)$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"(?i)\b([cdjlmnst])_", r"\1'", cleaned)
    cleaned = cleaned.replace("_", " ")
    cleaned = cleaned.replace("dOs", "d'Os")
    cleaned = re.sub(r'[<>:"/\\|?*]', "_", cleaned)
    cleaned = re.sub(r"(?i)\b(mp3|flac|audio|audiobook|128\s?kbps|320\s?kbps|x\d+|multi\s?part|download)\b", "", cleaned)
    cleaned = re.sub(r"\s*\(\d+\)$", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    return cleaned or "Dossier"


def _clean_manual_title(title: str) -> str:
    """Nettoie une saisie manuelle sans appliquer les heuristiques auto."""
    cleaned = _fix_mojibake(title).replace("+", " ")
    cleaned = re.sub(r'[<>:"/\\|?*]', "_", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    return cleaned


def _rename_from_ollama(folder: str, config: Dict) -> Optional[str]:
    """Construit un nom cible depuis les métadonnées Ollama si disponibles."""
    if not config.get("ollama_enabled", False):
        return None

    result = _run_ollama_metadata_search(folder, config)
    if not isinstance(result, dict) or result.get("error"):
        return None

    author = _clean_manual_title(str(result.get("author", "")))
    title = _clean_manual_title(str(result.get("title", "")))
    series = _clean_manual_title(str(result.get("series", "")))
    volume = str(result.get("volume", "")).strip()

    if not author or not title:
        return None

    chunks = [author, title]
    if series:
        chunks.append(series)

    vol_match = re.search(r"\d+", volume)
    if vol_match:
        chunks.append(f"Vol {int(vol_match.group(0))}")

    return " - ".join(chunks)


def _guess_author_with_ollama(title_hint: str) -> Optional[str]:
    """Essaie de deviner l'auteur via Ollama pour les cas ambigus."""
    prompt = (
        "Donne uniquement le nom de l'auteur du livre suivant, sans explication: "
        f"{title_hint}"
    )
    model = _load_config().get("ollama_model", "qwen2.5:7b")

    try:
        data = _ollama_api_request(
            "/api/generate",
            {"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0}},
            timeout=15,
        )
        output = data.get("response", "")
    except Exception:
        try:
            result = subprocess.run(
                ["ollama", "run", model, prompt],
                capture_output=True,
                text=True,
                timeout=15,
            )
        except Exception:
            return None

        if result.returncode != 0:
            return None
        output = result.stdout or ""

    answer = output.strip().splitlines()[0:1]
    if not answer:
        return None
    author = answer[0].strip(" .:-")
    if not author or len(author.split()) < 2:
        return None
    return author


def _smart_rename_local(folder: str) -> str:
    """Transforme un nom de dossier via heuristiques locales uniquement."""
    cleaned = _clean_name(folder)
    parts = [p.strip() for p in re.split(r"\s+-\s+", cleaned) if p.strip()]

    if len(parts) == 2 and re.search(r",", parts[0]):
        return f"{parts[1]} - {parts[0]}"

    if len(parts) == 2:
        author_with_volume = re.match(r"^(?P<author>.+?)\s+(?P<volume>\d+)$", parts[0])
        if author_with_volume:
            return (
                f"{author_with_volume.group('author')} - Vol {int(author_with_volume.group('volume'))}"
                f" - {parts[1]}"
            )

        vol_match = re.match(r"^(?P<title>.+?)\s+Vol\s*(?P<vol>\d+)$", parts[1], re.IGNORECASE)
        if vol_match:
            return f"{parts[0]} - {vol_match.group('title')} - Vol {int(vol_match.group('vol'))}"
        return f"{parts[0]} - {parts[1]}"

    if len(parts) >= 3:
        author = parts[0]
        book = parts[-1]

        trailing_volume = re.fullmatch(r"(?i)(?:vol(?:ume)?|tome)\s*(\d+)", parts[-1])
        if trailing_volume and len(parts) == 3:
            return f"{author} - {parts[1]} - Vol {int(trailing_volume.group(1))}"

        middle_volume = re.fullmatch(r"(?i)(?:vol(?:ume)?|tome)\s*(\d+)", parts[1])
        if middle_volume and len(parts) == 3:
            return f"{author} - {parts[2]} - Vol {int(middle_volume.group(1))}"

        series_block = " - ".join(parts[1:-1])
        series_block = re.sub(r"(?i)\b(vol(?:ume)?|tome)\s*", "", series_block)
        series_block = re.sub(r"\s*[-–]+\s*", " ", series_block).strip()
        match = re.match(r"^(?P<series>.+?)\s+(?P<volume>\d+)$", series_block)
        if match:
            series = match.group("series").strip()
            volume = int(match.group("volume"))
            return f"{author} - {series} - Vol {volume} - {book}"

        solo_volume = re.fullmatch(r"\d+", series_block)
        if solo_volume:
            return f"{author} - Vol {int(series_block)} - {book}"

        return f"{author} - {series_block} - {book}"

    return cleaned


def _smart_rename(folder: str) -> str:
    """Transforme un nom de dossier; Ollama seulement en dernier recours."""
    local_name = _smart_rename_local(folder)
    cleaned = _clean_name(folder)

    if local_name != cleaned:
        return local_name

    compact_vol = re.match(r"^(?P<title>.+?)\s+(?P<volume>\d+)$", cleaned)
    if compact_vol:
        author = _guess_author_with_ollama(compact_vol.group("title"))
        if author:
            return f"{author} - {compact_vol.group('title')} - Vol {int(compact_vol.group('volume'))}"

    ollama_name = _rename_from_ollama(folder, _load_config())
    if ollama_name:
        return ollama_name

    return local_name


def _count_audio_files(path: Path) -> int:
    return sum(1 for f in path.rglob("*") if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS)


def _folder_size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def _should_show_ignore_for_folder(file_count: int, folder_size: int, suggest_delete: bool) -> bool:
    """Affiche Ignorer pour les dossiers atypiques (non normaux)."""
    is_normal = file_count > 1 and folder_size >= 100 * 1024 * 1024 and not suggest_delete
    return not is_normal


def _normalize_media_label(value: str) -> str:
    label = value.strip().lower()
    label = re.sub(r"\.[a-z0-9]{2,4}$", "", label)
    label = re.sub(r"[^a-z0-9]+", " ", label)
    return " ".join(label.split())


def _list_media() -> Dict:
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    config = _load_config()
    ignored = set(config.get("ignored_folders", []))
    extracted_folders = {
        Path(name).name for name in config.get("recently_extracted_folders", []) if isinstance(name, str) and name.strip()
    }
    changed = False
    folders = []
    archives = []
    output_keys = {
        _normalize_media_label(file.stem)
        for file in OUTPUT_DIR.glob("*.m4b")
        if file.is_file()
    } if OUTPUT_DIR.exists() else set()
    completed_source_folders = _get_completed_folders_with_existing_outputs()

    for item in sorted(MEDIA_DIR.iterdir(), key=lambda x: x.name.lower()):
        if item.is_dir():
            if item.name in ignored:
                continue
            if item.name in completed_source_folders:
                continue
            if _normalize_media_label(item.name) in output_keys:
                continue
            file_count = sum(1 for f in item.rglob("*") if f.is_file())
            if file_count == 0:
                continue
            issues = []
            part_files = [f.name for f in item.rglob("*.part*") if f.is_file()]
            if part_files:
                issues.append("Fichier .part détecté (décompression incomplète)")
            folder_size = _folder_size(item)
            if file_count == 1:
                issues.append("Un seul fichier dans le dossier (anormal)")
            if folder_size < 30 * 1024 * 1024:
                issues.append("Taille très faible pour un audiobook")
            suggest_delete = bool(part_files) or (file_count == 1 and folder_size < 30 * 1024 * 1024)
            folders.append(
                {
                    "name": item.name,
                    "audio_count": _count_audio_files(item),
                    "size": folder_size,
                    "file_count": file_count,
                    "issues": issues,
                    "suggest_delete": suggest_delete,
                    "can_ignore": _should_show_ignore_for_folder(file_count, folder_size, suggest_delete),
                    "modified": item.stat().st_mtime,
                    "extracted_from_archive": item.name in extracted_folders,
                }
            )
            if item.name in extracted_folders:
                extracted_folders.remove(item.name)
        elif item.is_file() and item.suffix.lower() in ARCHIVE_EXTENSIONS:
            modified = item.stat().st_mtime
            validation = archive_validation_cache.get(item.name)
            if validation and validation.get("modified") != modified:
                archive_validation_cache.pop(item.name, None)
                validation = None

            archives.append(
                {
                    "name": item.name,
                    "size": item.stat().st_size,
                    "path": str(item),
                    "modified": modified,
                    "validation": {
                        "valid": validation.get("valid"),
                        "message": validation.get("message", ""),
                    } if validation else None,
                }
            )

    grouped_archives = _group_archives_for_ui(archives)
    _cleanup_archive_fingerprint_db([a.get("primary_name", "") for a in grouped_archives if a.get("primary_name")])
    _attach_archive_duplicate_hints(grouped_archives)

    if extracted_folders:
        config["recently_extracted_folders"] = sorted(
            {folder["name"] for folder in folders if folder.get("extracted_from_archive")}
        )
        changed = True

    if changed:
        _save_config(config)

    return {"base_path": str(MEDIA_DIR), "folders": folders, "archives": grouped_archives}


def _archive_group_parts(name: str) -> tuple[str, Optional[int]]:
    match = re.match(r"(?i)^(?P<base>.+)\.part(?P<num>\d+)\.rar$", name)
    if not match:
        return name, None
    base = match.group("base")
    part_num = int(match.group("num"))
    return f"{base}.rar", part_num


def _archive_members_from_name(name: str) -> List[Path]:
    normalized = Path(name).name
    group_key, _ = _archive_group_parts(normalized)
    exact_target = MEDIA_DIR / normalized

    if exact_target.exists() and exact_target.is_file() and exact_target.suffix.lower() in ARCHIVE_EXTENSIONS:
        return [exact_target]

    matches: List[Path] = []
    for item in MEDIA_DIR.iterdir():
        if not item.is_file() or item.suffix.lower() not in ARCHIVE_EXTENSIONS:
            continue
        key, _ = _archive_group_parts(item.name)
        if key == group_key:
            matches.append(item)

    return sorted(matches, key=lambda p: p.name.lower())


def _group_archives_for_ui(archives: List[Dict]) -> List[Dict]:
    grouped: Dict[str, Dict] = {}
    for archive in archives:
        archive_name = str(archive.get("name", ""))
        group_key, part_num = _archive_group_parts(archive_name)
        bucket = grouped.setdefault(
            group_key,
            {
                "group_key": group_key,
                "name": group_key,
                "size": 0,
                "members": [],
                "validation": None,
                "primary_name": None,
                "primary_path": None,
                "part_numbers": [],
                "duplicate_reasons": [],
                "duplicate_peers": [],
            },
        )
        bucket["size"] += int(archive.get("size", 0) or 0)
        bucket["members"].append(
            {
                "name": archive_name,
                "size": archive.get("size", 0),
                "path": archive.get("path"),
                "part_num": part_num,
                "validation": archive.get("validation"),
            }
        )

    result: List[Dict] = []
    for group_key in sorted(grouped.keys(), key=lambda n: n.lower()):
        bucket = grouped[group_key]
        members = sorted(bucket["members"], key=lambda m: (m.get("part_num") is None, m.get("part_num") or 0, m["name"].lower()))
        bucket["members"] = [m["name"] for m in members]
        primary = members[0]
        bucket["primary_name"] = primary["name"]
        bucket["primary_path"] = primary.get("path")
        bucket["validation"] = primary.get("validation")
        if any(m.get("part_num") is not None for m in members):
            listed = ", ".join(m["name"] for m in members)
            bucket["display_name"] = f"{primary['name']} (+{len(members)-1}): {listed}"
        else:
            bucket["display_name"] = primary["name"]
        result.append(bucket)
    return result


def _file_hash(path: Path, algorithm: str) -> Optional[str]:
    try:
        hasher = hashlib.new(algorithm)
    except ValueError:
        return None
    try:
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except OSError:
        return None


def _archive_content_signature(path: Path) -> Optional[str]:
    try:
        if path.suffix.lower() == ".zip":
            with zipfile.ZipFile(path, "r") as zf:
                members = [f"{i.filename}|{i.file_size}|{i.CRC}" for i in zf.infolist()]
        else:
            with rarfile.RarFile(path, "r") as rf:
                members = [f"{i.filename}|{getattr(i, 'file_size', 0)}|{getattr(i, 'CRC', 0)}" for i in rf.infolist()]
    except Exception:  # noqa: BLE001
        return None
    normalized = "\n".join(sorted(members)).encode("utf-8", errors="ignore")
    return hashlib.sha256(normalized).hexdigest()


def _normalized_archive_title(name: str) -> str:
    cleaned = name.lower()
    cleaned = re.sub(r"\.part\d+", "", cleaned)
    cleaned = re.sub(r"\.(zip|rar)$", "", cleaned)
    cleaned = re.sub(r"[^a-z0-9]+", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def _attach_archive_duplicate_hints(archives: List[Dict]) -> None:
    by_title: Dict[str, List[str]] = {}
    by_md5: Dict[str, List[str]] = {}
    by_sha: Dict[str, List[str]] = {}
    by_content: Dict[str, List[str]] = {}

    by_size: Dict[int, List[Dict]] = {}
    for archive in archives:
        size = int(archive.get("size", 0) or 0)
        by_size.setdefault(size, []).append(archive)

    for archive in archives:
        primary_name = archive.get("primary_name")
        primary_path_raw = archive.get("primary_path")
        if not primary_name or not primary_path_raw:
            continue
        primary_path = Path(primary_path_raw)
        if not primary_path.exists():
            continue

        stat = primary_path.stat()
        cached = _get_archive_fingerprint_from_db(primary_name, int(stat.st_size), float(stat.st_mtime))
        if cached:
            md5 = cached.get("md5")
            sha256 = cached.get("sha256")
            content_sig = cached.get("content_sig")
        else:
            candidates = by_size.get(int(archive.get("size", 0) or 0), [])
            has_same_size_peer = any(a.get("primary_name") != primary_name for a in candidates)

            # Les hashs complets sont coûteux sur de gros volumes :
            # on les calcule seulement s'il existe au moins un pair de même taille.
            md5 = _file_hash(primary_path, "md5") if has_same_size_peer else None
            sha256 = _file_hash(primary_path, "sha256") if has_same_size_peer else None
            content_sig = _archive_content_signature(primary_path) if has_same_size_peer else None
            _save_archive_fingerprint_to_db(
                primary_name,
                int(stat.st_size),
                float(stat.st_mtime),
                md5,
                sha256,
                content_sig,
            )

        title_key = _normalized_archive_title(primary_name)
        if title_key:
            by_title.setdefault(title_key, []).append(primary_name)

        if md5:
            by_md5.setdefault(md5, []).append(primary_name)

        if sha256:
            by_sha.setdefault(sha256, []).append(primary_name)

        if content_sig:
            by_content.setdefault(content_sig, []).append(primary_name)

    duplicate_sources = [
        ("titre", by_title),
        ("MD5", by_md5),
        ("SHA256", by_sha),
        ("contenu", by_content),
    ]

    for archive in archives:
        primary_name = archive.get("primary_name")
        if not primary_name:
            continue
        reasons = []
        peers_union = set()
        for label, mapping in duplicate_sources:
            for names in mapping.values():
                if primary_name in names and len(names) > 1:
                    peers = sorted(n for n in names if n != primary_name)
                    peers_union.update(peers)
                    reasons.append(f"{label}: {', '.join(peers)}")
                    break
        archive["duplicate_reasons"] = reasons
        archive["duplicate_peers"] = sorted(peers_union)


def _validate_archive(path: Path) -> Dict:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Archive introuvable: {path.name}")
    if path.suffix.lower() not in ARCHIVE_EXTENSIONS:
        raise ValueError("Archive non supportée")

    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path, "r") as zf:
            if not zf.namelist():
                return {"valid": False, "message": "Archive ZIP vide"}
            if any(info.flag_bits & 0x1 for info in zf.infolist()):
                return {"valid": False, "message": "Archive ZIP protégée par mot de passe"}
            bad_file = zf.testzip()
            if bad_file:
                return {"valid": False, "message": f"Archive ZIP corrompue (erreur sur: {bad_file})"}
        return {"valid": True, "message": "Archive ZIP valide"}

    with rarfile.RarFile(path, "r") as rf:
        if not rf.infolist():
            return {"valid": False, "message": "Archive RAR vide"}
        if rf.needs_password():
            return {"valid": False, "message": "Archive RAR protégée par mot de passe"}
        bad_file = rf.testrar()
        if bad_file:
            return {"valid": False, "message": f"Archive RAR corrompue (erreur sur: {bad_file})"}
    return {"valid": True, "message": "Archive RAR valide"}


def _mark_folder_as_recently_extracted(folder_name: str) -> None:
    config = _load_config()
    existing = {
        Path(name).name for name in config.get("recently_extracted_folders", []) if isinstance(name, str) and name.strip()
    }
    existing.add(Path(folder_name).name)
    config["recently_extracted_folders"] = sorted(existing)
    _save_config(config)


def _clear_recently_extracted_flag(folder_name: str) -> None:
    config = _load_config()
    existing = {
        Path(name).name for name in config.get("recently_extracted_folders", []) if isinstance(name, str) and name.strip()
    }
    normalized = Path(folder_name).name
    if normalized not in existing:
        return
    existing.remove(normalized)
    config["recently_extracted_folders"] = sorted(existing)
    _save_config(config)


def _extract_archive(path: Path, delete_archive: bool = True) -> Dict:
    validation = _validate_archive(path)
    if not validation["valid"]:
        raise ValueError(validation["message"])

    target_dir = MEDIA_DIR / path.stem
    if target_dir.exists():
        stamp = int(time.time())
        target_dir = MEDIA_DIR / f"{path.stem}_{stamp}"
    target_dir.mkdir(parents=True, exist_ok=True)

    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path, "r") as zf:
            zf.extractall(target_dir)
    elif path.suffix.lower() == ".rar":
        with rarfile.RarFile(path, "r") as rf:
            rf.extractall(target_dir)
    else:
        raise ValueError("Archive non supportée")

    extracted_files = [f for f in target_dir.rglob("*") if f.is_file()]
    if not extracted_files:
        shutil.rmtree(target_dir, ignore_errors=True)
        raise ValueError("Extraction invalide: aucun fichier extrait")

    if delete_archive:
        path.unlink(missing_ok=True)
        archive_validation_cache.pop(path.name, None)
        _delete_archive_fingerprint_from_db(path.name)

    _mark_folder_as_recently_extracted(target_dir.name)

    return {
        "archive": path.name,
        "folder": target_dir.name,
        "validation": validation,
        "extracted_files": len(extracted_files),
        "archive_deleted": delete_archive,
    }


def _build_processing_config() -> ProcessingConfig:
    web_config = _load_config()
    cfg = ProcessingConfig()
    cfg.audio_bitrate = web_config["bitrate"]
    cfg.sample_rate = int(web_config["sample_rate"])
    cfg.processing_mode = web_config["processing_mode"]
    cfg.enable_gpu_acceleration = bool(web_config["enable_gpu"])
    cfg.enable_loudnorm = bool(web_config["enable_loudnorm"])
    cfg.enable_compressor = bool(web_config["enable_compressor"])
    cfg.scraping_sources = list(web_config.get("scraping_sources") or cfg.scraping_sources)
    cfg.cover_sources = list(web_config.get("cover_sources") or cfg.cover_sources)
    return cfg


def _guess_output_file(folder_name: str, start_time: float) -> Optional[str]:
    if not OUTPUT_DIR.exists():
        return None
    candidates = sorted(OUTPUT_DIR.glob("*.m4b"), key=lambda p: p.stat().st_mtime, reverse=True)
    for file in candidates:
        if file.stat().st_mtime >= start_time - 2:
            return file.name
    return candidates[0].name if candidates else None


def _push_job_event(
    job_id: str,
    folder: str,
    stage: str,
    message: str,
    level: str = "info",
    details: Optional[Dict] = None,
) -> None:
    event = {
        "timestamp": time.time(),
        "job_id": job_id,
        "folder": folder,
        "stage": stage,
        "message": message,
        "level": level,
        "details": details or {},
    }
    with jobs_lock:
        job_events.append(event)
        if len(job_events) > MAX_JOB_EVENTS:
            del job_events[: len(job_events) - MAX_JOB_EVENTS]

    log_fn = logger.info
    if level == "error":
        log_fn = logger.error
    elif level == "warning":
        log_fn = logger.warning
    elif level == "debug":
        log_fn = logger.debug
    log_fn("[%s] %s - %s", job_id, stage, message)


def _worker_loop() -> None:
    while True:
        job_id = job_queue.get()
        with jobs_lock:
            job = jobs.get(job_id)
            if not job:
                continue
            job.status = "running"
            job.stage = "Préparation"
            job.progress = 5
            job.started_at = time.time()
            _push_job_event(job.id, job.folder, job.stage, "Job démarré")

        try:
            folder_path = MEDIA_DIR / job.folder
            if not folder_path.exists() or not folder_path.is_dir():
                raise FileNotFoundError(f"Dossier introuvable: {job.folder}")

            audio_files = _count_audio_files(folder_path)
            folder_size_mb = _folder_size(folder_path) / 1024 / 1024
            _push_job_event(
                job.id,
                job.folder,
                "Analyse",
                f"Dossier prêt: {audio_files} fichier(s) audio, {folder_size_mb:.1f} MB",
                "debug",
            )

            processor = AudiobookProcessor(str(MEDIA_DIR), str(OUTPUT_DIR), str(TEMP_DIR))
            processor.config = _build_processing_config()

            def _on_processor_progress(payload: Dict[str, object]) -> None:
                stage = str(payload.get("stage") or "Conversion")
                message = str(payload.get("message") or "Mise à jour conversion")
                progress_value = payload.get("progress")
                details = payload.get("details") if isinstance(payload.get("details"), dict) else {}
                event_level = str(details.get("level") or "info").lower()
                if event_level not in {"info", "warning", "error", "debug"}:
                    event_level = "info"
                with jobs_lock:
                    current_job = jobs.get(job_id)
                    if not current_job:
                        return
                    current_job.stage = stage
                    if isinstance(progress_value, (int, float)):
                        current_job.progress = max(0, min(100, int(progress_value)))

                    phase_key = details.get("phase_key") if isinstance(details, dict) else None
                    if isinstance(phase_key, str) and phase_key:
                        phase_label = details.get("phase_label") or phase_key
                        processed_raw = details.get("processed", 0)
                        total_raw = details.get("total", 0)
                        try:
                            processed = max(0, int(processed_raw))
                        except (TypeError, ValueError):
                            processed = 0
                        try:
                            total = max(0, int(total_raw))
                        except (TypeError, ValueError):
                            total = 0
                        if total and processed > total:
                            processed = total
                        current_job.phase_progress[phase_key] = {
                            "label": str(phase_label),
                            "processed": processed,
                            "total": total,
                        }

                    _push_job_event(current_job.id, current_job.folder, stage, message, event_level, details)

            processor.progress_callback = _on_processor_progress

            with jobs_lock:
                job.stage = "Conversion"
                job.progress = 30
                _push_job_event(job.id, job.folder, job.stage, "Conversion démarrée")

            success = processor.process_audiobook(folder_path)

            with jobs_lock:
                if success:
                    job.status = "completed"
                    job.stage = "Terminé"
                    job.progress = 100
                    job.phase_progress.setdefault("finalization", {"label": "Finalisation", "processed": 2, "total": 2})
                    job.output_file = _guess_output_file(job.folder, job.started_at or time.time())
                    _push_job_event(job.id, job.folder, job.stage, f"Succès. Fichier: {job.output_file or 'inconnu'}")
                else:
                    job.status = "failed"
                    job.stage = "Erreur"
                    processor_error = getattr(processor, "last_error", None)
                    job.error = str(processor_error) if processor_error else "Échec conversion"
                    job.progress = 100
                    _push_job_event(
                        job.id,
                        job.folder,
                        job.stage,
                        f"{job.error} (web: {WEB_DEBUG_LOG_PATH}, processor: {PROCESSOR_LOG_PATH}).",
                        "error",
                    )
                job.ended_at = time.time()

            if success and job.output_file:
                _save_m4b_candidate(job.folder, job.output_file)
        except Exception as exc:  # noqa: BLE001
            with jobs_lock:
                job.status = "failed"
                job.stage = "Erreur"
                job.error = str(exc)
                job.progress = 100
                job.ended_at = time.time()
                _push_job_event(job.id, job.folder, job.stage, f"Exception: {exc}", "error")
        finally:
            job_queue.task_done()


def _ensure_worker() -> None:
    global worker_started
    if worker_started:
        return
    thread = threading.Thread(target=_worker_loop, daemon=True)
    thread.start()
    worker_started = True


@app.route("/")
def index():
    return render_template("index.html", app_version=APP_VERSION)


@app.route("/integrations/audiobookshelf/packets")
def integration_packets_page():
    return render_template("packets.html")


@app.route("/api/integrations/audiobookshelf/packets")
def api_integration_packets():
    _bootstrap_upload_packets()
    requested_status = (request.args.get("status") or "").strip()
    with packets_lock:
        payload = list(upload_packets.values())
    if requested_status:
        payload = [packet for packet in payload if packet.get("status") == requested_status]
    payload.sort(key=lambda packet: str(packet.get("created_at", 0)), reverse=True)
    return jsonify({"packets": payload, "statuses": PACKET_STATUSES})


@app.route("/api/integrations/audiobookshelf/packets", methods=["POST"])
def api_integration_packets_create():
    _bootstrap_upload_packets()
    payload = request.get_json(silent=True) or {}
    output_files = payload.get("output_files")
    packet_name = str(payload.get("name") or "").strip()
    if not isinstance(output_files, list) or not output_files:
        return _api_error("Le champ 'output_files' doit contenir au moins un fichier", code="invalid_output_files")

    selected_files: List[Dict[str, object]] = []
    for name in output_files:
        if not isinstance(name, str) or not name.strip():
            continue
        output_file = _resolve_output_file(name)
        if not output_file or not output_file.exists() or not output_file.is_file():
            return _api_error(f"Fichier output introuvable: {name}", 404, code="output_file_not_found")
        selected_files.append({"name": output_file.name, "size": output_file.stat().st_size})

    if not selected_files:
        return _api_error("Aucun fichier output valide fourni", code="invalid_output_files")

    if not packet_name:
        packet_name = Path(selected_files[0]["name"]).stem

    packet_id = hashlib.sha1(f"{packet_name}:{time.time()}".encode("utf-8")).hexdigest()[:10]
    packet = {
        "id": packet_id,
        "name": packet_name,
        "status": "en_preparation",
        "progress": 0,
        "created_at": int(time.time()),
        "files": selected_files,
        "metadata": {
            "title": packet_name,
            "author": "",
            "series": "",
            "volume": "",
            "narrator": "",
            "language": "fr",
            "tags": "",
            "synopsis": "",
        },
        "validation": {"ok": False, "missing": ["author", "synopsis"]},
        "changelog": {"draft": "", "edited": "", "source": "none", "updated_at": None},
    }
    _refresh_packet_metrics(packet)

    with packets_lock:
        upload_packets[packet_id] = packet

    return jsonify({"ok": True, "packet": packet, "payload_preview": _packet_payload_preview(packet)})


@app.route("/api/integrations/audiobookshelf/packets/<packet_id>")
def api_integration_packet_detail(packet_id: str):
    _bootstrap_upload_packets()
    with packets_lock:
        packet = upload_packets.get(packet_id)
    if not packet:
        return _api_error("Paquet introuvable", 404, code="packet_not_found")
    return jsonify({"packet": packet, "payload_preview": _packet_payload_preview(packet)})


@app.route("/api/integrations/audiobookshelf/packets/<packet_id>/metadata", methods=["PUT"])
def api_integration_packet_update_metadata(packet_id: str):
    _bootstrap_upload_packets()
    payload = request.get_json(silent=True) or {}
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        return _api_error("Le champ 'metadata' doit être un objet", code="invalid_metadata")

    with packets_lock:
        packet = upload_packets.get(packet_id)
        if not packet:
            return _api_error("Paquet introuvable", 404, code="packet_not_found")

        current_metadata = packet.get("metadata") if isinstance(packet.get("metadata"), dict) else {}
        merged = {**current_metadata, **{k: str(v) for k, v in metadata.items()}}
        missing = [key for key in ("title", "author", "synopsis") if not str(merged.get(key, "")).strip()]
        packet["metadata"] = merged
        packet["validation"] = {"ok": len(missing) == 0, "missing": missing}
        if len(missing) == 0:
            packet["status"] = "pret"
    return jsonify({"ok": True, "packet": packet, "payload_preview": _packet_payload_preview(packet)})


@app.route("/api/integrations/audiobookshelf/packets/<packet_id>/changelog/draft", methods=["POST"])
def api_integration_packet_changelog_draft(packet_id: str):
    _bootstrap_upload_packets()
    config = _load_config()
    with packets_lock:
        packet = upload_packets.get(packet_id)
        if not packet:
            return _api_error("Paquet introuvable", 404, code="packet_not_found")

    result = _generate_packet_changelog_draft(packet, config)

    with packets_lock:
        packet = upload_packets.get(packet_id)
        if not packet:
            return _api_error("Paquet introuvable", 404, code="packet_not_found")
        changelog = packet.get("changelog") if isinstance(packet.get("changelog"), dict) else {}
        changelog["draft"] = str(result.get("draft") or "")
        if not changelog.get("edited"):
            changelog["edited"] = changelog["draft"]
        changelog["source"] = str(result.get("source") or "fallback")
        changelog["updated_at"] = int(time.time())
        packet["changelog"] = changelog
    return jsonify({"ok": True, "packet": packet, "draft": changelog["draft"], "source": changelog["source"]})


@app.route("/api/integrations/audiobookshelf/packets/<packet_id>/changelog", methods=["PUT"])
def api_integration_packet_changelog_update(packet_id: str):
    _bootstrap_upload_packets()
    payload = request.get_json(silent=True) or {}
    edited = payload.get("edited")
    if not isinstance(edited, str):
        return _api_error("Le champ 'edited' doit être une chaîne", code="invalid_changelog")

    with packets_lock:
        packet = upload_packets.get(packet_id)
        if not packet:
            return _api_error("Paquet introuvable", 404, code="packet_not_found")
        changelog = packet.get("changelog") if isinstance(packet.get("changelog"), dict) else {}
        changelog["edited"] = edited.strip()
        changelog["updated_at"] = int(time.time())
        packet["changelog"] = changelog

    return jsonify({"ok": True, "packet": packet})


@app.route("/api/integrations/audiobookshelf/packets/<packet_id>/submit", methods=["POST"])
def api_integration_packet_submit(packet_id: str):
    _bootstrap_upload_packets()
    payload = request.get_json(silent=True) or {}
    request_changelog = payload.get("changelog")
    with packets_lock:
        packet = upload_packets.get(packet_id)
        if not packet:
            return _api_error("Paquet introuvable", 404, code="packet_not_found")
        try:
            _mark_packet_published(packet, request_changelog if isinstance(request_changelog, str) else None)
        except ValueError:
            validation = packet.get("validation") if isinstance(packet.get("validation"), dict) else {"ok": False}
            return _api_error(
                "Métadonnées incomplètes: complétez les champs obligatoires.",
                400,
                code="metadata_incomplete",
                details={"missing": validation.get("missing", [])},
            )

    return jsonify(
        {
            "ok": True,
            "packet_id": packet_id,
            "steps": [
                {"key": "prepare", "status": "done", "label": "Préparation"},
                {"key": "upload", "status": "done", "label": "Upload"},
                {"key": "scan", "status": "done", "label": "Scan bibliothèque"},
                {"key": "confirm", "status": "done", "label": "Confirmation finale"},
            ],
            "payload_preview": _packet_payload_preview(packet),
            "changelog": packet.get("changelog", {}),
        }
    )


@app.route("/api/integrations/audiobookshelf/packets/<packet_id>/broadcast", methods=["POST"])
def api_integration_packet_broadcast(packet_id: str):
    _bootstrap_upload_packets()
    payload = request.get_json(silent=True) or {}
    channels = payload.get("channels")
    if not isinstance(channels, list) or not channels:
        channels = ["discord", "telegram", "whatsapp", "email"]
    channels = [str(channel).strip().lower() for channel in channels if str(channel).strip()]
    channels = [channel for channel in channels if channel in {"discord", "telegram", "whatsapp", "email"}]
    if not channels:
        return _api_error("Aucun canal valide fourni", code="invalid_channels")

    config = _load_config()
    with packets_lock:
        packet = upload_packets.get(packet_id)
        if not packet:
            return _api_error("Paquet introuvable", 404, code="packet_not_found")
        delivery = _deliver_changelog(packet, channels, config)

    return jsonify({"ok": True, "packet_id": packet_id, **delivery})


@app.route("/api/integrations/audiobookshelf/packets/<packet_id>/schedule", methods=["POST"])
def api_integration_packet_schedule(packet_id: str):
    _bootstrap_upload_packets()
    payload = request.get_json(silent=True) or {}
    publish_at = payload.get("publish_at")
    if isinstance(publish_at, str) and publish_at.strip().isdigit():
        publish_at = int(publish_at.strip())
    if not isinstance(publish_at, int):
        return _api_error("Le champ 'publish_at' (timestamp unix) est requis", code="invalid_publish_at")
    if publish_at <= int(time.time()):
        return _api_error("La date de publication doit être dans le futur", code="invalid_publish_at")

    channels = payload.get("channels")
    if not isinstance(channels, list) or not channels:
        channels = ["discord", "telegram", "whatsapp", "email"]
    channels = [str(channel).strip().lower() for channel in channels if str(channel).strip()]
    channels = [channel for channel in channels if channel in {"discord", "telegram", "whatsapp", "email"}]

    job_id = hashlib.sha1(f"{packet_id}:{publish_at}:{time.time()}".encode("utf-8")).hexdigest()[:12]
    with packets_lock:
        packet = upload_packets.get(packet_id)
        if not packet:
            return _api_error("Paquet introuvable", 404, code="packet_not_found")
        packet["status"] = "planifie"
        packet_schedule_jobs[job_id] = {
            "id": job_id,
            "packet_id": packet_id,
            "status": "scheduled",
            "publish_at": publish_at,
            "channels": channels,
            "cleanup_after_publish": bool(payload.get("cleanup_after_publish", False)),
            "created_at": int(time.time()),
            "completed_at": None,
            "delivery": None,
        }

    return jsonify({"ok": True, "job": packet_schedule_jobs[job_id]})


@app.route("/api/integrations/audiobookshelf/scheduler/jobs")
def api_integration_scheduler_jobs():
    _bootstrap_upload_packets()
    with packets_lock:
        jobs_payload = list(packet_schedule_jobs.values())
    jobs_payload.sort(key=lambda item: int(item.get("publish_at", 0)))
    return jsonify({"jobs": jobs_payload})


@app.route("/api/integrations/audiobookshelf/scheduler/jobs/<job_id>/run", methods=["POST"])
def api_integration_scheduler_run_job(job_id: str):
    _bootstrap_upload_packets()
    config = _load_config()
    with packets_lock:
        job = packet_schedule_jobs.get(job_id)
        if not job:
            return _api_error("Job planifié introuvable", 404, code="schedule_job_not_found")
        packet = upload_packets.get(str(job.get("packet_id")))
        if not packet:
            return _api_error("Paquet introuvable", 404, code="packet_not_found")
        try:
            _mark_packet_published(packet)
        except ValueError:
            validation = packet.get("validation") if isinstance(packet.get("validation"), dict) else {"ok": False}
            job["status"] = "failed"
            return _api_error(
                "Métadonnées incomplètes: complétez les champs obligatoires.",
                400,
                code="metadata_incomplete",
                details={"missing": validation.get("missing", [])},
            )

        delivery = _deliver_changelog(packet, list(job.get("channels") or []), config)
        job["status"] = "completed"
        job["completed_at"] = int(time.time())
        job["delivery"] = delivery

    if job.get("cleanup_after_publish"):
        with packets_lock:
            pkt = upload_packets.get(str(job.get("packet_id")))
            if pkt:
                _cleanup_packet_files(pkt, True)

    return jsonify({"ok": True, "job": job, "packet": packet})


@app.route("/api/integrations/audiobookshelf/packets/<packet_id>/cleanup", methods=["POST"])
def api_integration_packet_cleanup(packet_id: str):
    _bootstrap_upload_packets()
    payload = request.get_json(silent=True) or {}
    delete_outputs = bool(payload.get("delete_output_files", True))

    with packets_lock:
        packet = upload_packets.get(packet_id)
        if not packet:
            return _api_error("Paquet introuvable", 404, code="packet_not_found")
        removed_files = _cleanup_packet_files(packet, delete_outputs)

    return jsonify({"ok": True, "packet": packet, "removed_files": removed_files})


@app.route("/api/integrations/audiobookshelf/packets/<packet_id>/files", methods=["DELETE"])
def api_integration_packet_remove_file(packet_id: str):
    _bootstrap_upload_packets()
    payload = request.get_json(silent=True) or {}
    filename = payload.get("filename")
    if not isinstance(filename, str) or not filename.strip():
        return _api_error("Le champ 'filename' est requis", code="invalid_filename")

    with packets_lock:
        packet = upload_packets.get(packet_id)
        if not packet:
            return _api_error("Paquet introuvable", 404, code="packet_not_found")

        files = packet.get("files") if isinstance(packet.get("files"), list) else []
        updated_files = [item for item in files if not (isinstance(item, dict) and item.get("name") == filename)]
        if len(updated_files) == len(files):
            return _api_error("Fichier introuvable dans ce paquet", 404, code="packet_file_not_found")
        packet["files"] = updated_files
        _refresh_packet_metrics(packet)

    return jsonify({"ok": True, "packet": packet, "payload_preview": _packet_payload_preview(packet)})


@app.route("/api/library")
def api_library():
    media = _list_media()
    with jobs_lock:
        active_jobs = [asdict(j) for j in jobs.values() if j.status in {"pending", "running"}]

    by_folder: Dict[str, Dict] = {}
    for job in sorted(active_jobs, key=lambda j: j.get("created_at", 0), reverse=True):
        folder_name = job.get("folder")
        if isinstance(folder_name, str) and folder_name and folder_name not in by_folder:
            by_folder[folder_name] = {
                "job_id": job.get("id"),
                "status": job.get("status"),
                "progress": job.get("progress", 0),
                "stage": job.get("stage", "En attente"),
            }

    for folder in media["folders"]:
        folder["job"] = by_folder.get(folder["name"])

    return jsonify(media)


@app.route("/api/extract", methods=["POST"])
def api_extract():
    payload = request.get_json(silent=True) or {}
    names = payload.get("archives", [])

    results = []
    errors = []
    for name in names:
        archive_members = _archive_members_from_name(str(name))
        if not archive_members:
            errors.append(f"Archive introuvable: {name}")
            continue

        archive_path = archive_members[0]
        try:
            results.append(_extract_archive(archive_path, delete_archive=True))
            for member in archive_members[1:]:
                member.unlink(missing_ok=True)
                archive_validation_cache.pop(member.name, None)
                _delete_archive_fingerprint_from_db(member.name)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{name}: {exc}")

    return jsonify({"results": results, "errors": errors})


@app.route("/api/archive/validate", methods=["POST"])
def api_archive_validate():
    payload = request.get_json(silent=True) or {}
    names = payload.get("archives", [])

    results = []
    errors = []
    for name in names:
        archive_members = _archive_members_from_name(str(name))
        if not archive_members:
            errors.append(f"Archive introuvable: {name}")
            continue

        archive_path = archive_members[0]
        try:
            outcome = _validate_archive(archive_path)
            for member in archive_members:
                archive_validation_cache[member.name] = {
                    "valid": bool(outcome.get("valid")),
                    "message": str(outcome.get("message", "")),
                    "modified": member.stat().st_mtime,
                }
            results.append({"archive": archive_path.name, **outcome})
        except Exception as exc:  # noqa: BLE001
            message = str(exc)
            for member in archive_members:
                archive_validation_cache[member.name] = {
                    "valid": False,
                    "message": message,
                    "modified": member.stat().st_mtime,
                }
            results.append({"archive": archive_path.name, "valid": False, "message": message})

    return jsonify({"results": results, "errors": errors})


@app.route("/api/rename", methods=["POST"])
def api_rename():
    payload = request.get_json(silent=True) or {}
    folders = payload.get("folders", [])
    overrides = payload.get("overrides", {})
    if not isinstance(folders, list):
        return _api_error("Le champ 'folders' doit être une liste", code="invalid_folders")
    if not isinstance(overrides, dict):
        return _api_error("Le champ 'overrides' doit être un objet", code="invalid_overrides")

    renamed = []
    skipped = []

    for folder in folders:
        if not isinstance(folder, str) or not folder.strip():
            skipped.append({"folder": str(folder), "reason": "nom invalide"})
            continue
        if Path(folder).name != folder:
            skipped.append({"folder": folder, "reason": "nom de dossier invalide"})
            continue

        src = MEDIA_DIR / folder
        if not src.exists() or not src.is_dir():
            skipped.append({"folder": folder, "reason": "introuvable"})
            continue

        manual_title = overrides.get(folder)
        if manual_title is not None:
            if not isinstance(manual_title, str):
                skipped.append({"folder": folder, "reason": "titre manuel invalide"})
                continue
            new_name = _clean_manual_title(manual_title)
            if not new_name:
                skipped.append({"folder": folder, "reason": "titre manuel vide"})
                continue
        else:
            new_name = _smart_rename(folder)
        dst = MEDIA_DIR / new_name
        if new_name == folder:
            skipped.append({"folder": folder, "reason": "déjà conforme"})
            continue
        if dst.exists():
            skipped.append({"folder": folder, "reason": "destination existante"})
            continue

        try:
            src.rename(dst)
            renamed.append({"old": folder, "new": new_name})
            _clear_recently_extracted_flag(folder)
        except OSError as exc:
            skipped.append({"folder": folder, "reason": f"erreur système: {exc}"})

    return jsonify({"renamed": renamed, "skipped": skipped})


@app.route("/api/ignore", methods=["POST"])
def api_ignore_folder():
    payload = request.get_json(silent=True) or {}
    folder = payload.get("folder")
    if not isinstance(folder, str) or not folder.strip():
        return _api_error("folder invalide", code="invalid_folder")
    if Path(folder).name != folder:
        return _api_error("nom de dossier invalide", code="invalid_folder_name")

    config = _load_config()
    ignored = set(config.get("ignored_folders", []))
    ignored.add(Path(folder).name)
    config["ignored_folders"] = sorted(ignored)
    _save_config(config)
    return jsonify({"ignored_folders": config["ignored_folders"]})


@app.route("/api/archive/delete", methods=["POST"])
def api_delete_archive():
    payload = request.get_json(silent=True) or {}
    archive = (payload.get("archive") or "").strip()
    if not archive:
        return _api_error("archive requis", code="missing_archive")

    normalized = Path(archive).name
    if normalized != archive:
        return _api_error("nom d'archive invalide", code="invalid_archive_name")

    targets = _archive_members_from_name(normalized)
    if not targets:
        return _api_error("archive introuvable", status=404, code="archive_not_found")

    for target in targets:
        target.unlink(missing_ok=True)
        archive_validation_cache.pop(target.name, None)
        _delete_archive_fingerprint_from_db(target.name)
    return jsonify({"deleted": normalized})


@app.route("/api/folder/delete", methods=["POST"])
def api_delete_folder():
    payload = request.get_json(silent=True) or {}
    folder = payload.get("folder")
    if not isinstance(folder, str) or not folder.strip():
        return _api_error("folder invalide", code="invalid_folder")
    if Path(folder).name != folder:
        return _api_error("nom de dossier invalide", code="invalid_folder_name")

    target = MEDIA_DIR / folder
    if not target.exists() or not target.is_dir():
        return _api_error("dossier introuvable", status=404, code="folder_not_found")

    file_count = sum(1 for f in target.rglob("*") if f.is_file())
    folder_size = _folder_size(target)
    has_part = any(f.is_file() for f in target.rglob("*.part*"))
    suggest_delete = has_part or (file_count == 1 and folder_size < 30 * 1024 * 1024)
    if not suggest_delete:
        return _api_error("suppression autorisée uniquement pour dossier suspect", code="folder_not_suspicious")

    shutil.rmtree(target)
    return jsonify({"deleted": folder})


@app.route("/api/jobs/enqueue", methods=["POST"])
def api_enqueue_jobs():
    _ensure_worker()
    payload = request.get_json(silent=True) or {}
    folders = payload.get("folders", [])
    if not isinstance(folders, list):
        return _api_error("Le champ 'folders' doit être une liste", code="invalid_folders")

    queued = []
    skipped = []

    with jobs_lock:
        active_folders = {j.folder for j in jobs.values() if j.status in {"pending", "running"}}
        for folder in folders:
            folder_name = str(folder or "").strip()
            if not folder_name:
                skipped.append({"folder": str(folder), "reason": "nom invalide"})
                continue
            if folder_name in active_folders:
                skipped.append({"folder": folder_name, "reason": "déjà en attente/en cours"})
                continue
            jid = f"job-{int(time.time() * 1000)}-{len(jobs)}"
            job = Job(id=jid, folder=folder_name)
            jobs[jid] = job
            job_queue.put(jid)
            queued.append(asdict(job))
            active_folders.add(folder_name)

    return jsonify({"queued": queued, "skipped": skipped})


@app.route("/api/jobs")
def api_jobs():
    with jobs_lock:
        values = [asdict(j) for j in jobs.values()]

    def sort_key(entry):
        return entry["created_at"]

    pending = sorted([j for j in values if j["status"] == "pending"], key=sort_key)
    running = sorted([j for j in values if j["status"] == "running"], key=sort_key)
    done = sorted([j for j in values if j["status"] in {"completed", "failed"}], key=sort_key, reverse=True)

    return jsonify({"pending": pending, "running": running, "done": done, "review": review_bin, "events": job_events[-100:]})


@app.route("/api/logs")
def api_logs_tail():
    lines = int(request.args.get("lines", 80))
    lines = min(max(lines, 10), 300)
    log_file = WEB_DEBUG_LOG_PATH
    if not log_file.exists():
        return jsonify({"lines": [], "path": str(log_file)})

    content = log_file.read_text(encoding="utf-8", errors="ignore").splitlines()
    return jsonify({"lines": content[-lines:], "path": str(log_file)})


@app.route("/api/jobs/review", methods=["POST"])
def api_review():
    payload = request.get_json(silent=True) or {}
    job_id = payload.get("job_id")
    action = payload.get("action", "queue_delete")

    with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            return _api_error("Job introuvable", status=404, code="job_not_found")

        review_bin.append({
            "job_id": job.id,
            "folder": job.folder,
            "output_file": job.output_file,
            "action": action,
            "timestamp": time.time(),
        })

    return jsonify({"status": "ok"})


@app.route("/api/jobs/reprocess", methods=["POST"])
def api_reprocess():
    payload = request.get_json(silent=True) or {}
    folder = payload.get("folder")
    if not folder:
        return _api_error("folder requis", code="missing_folder")
    if not isinstance(folder, str) or Path(folder).name != folder:
        return _api_error("nom de dossier invalide", code="invalid_folder_name")
    target = MEDIA_DIR / folder
    if not target.exists() or not target.is_dir():
        return _api_error("dossier introuvable", status=404, code="folder_not_found")

    _ensure_worker()
    with jobs_lock:
        jid = f"job-{int(time.time() * 1000)}-{len(jobs)}"
        job = Job(id=jid, folder=folder)
        jobs[jid] = job
        job_queue.put(jid)

    return jsonify({"queued": asdict(job)})


@app.route("/api/review/clear", methods=["POST"])
def api_review_clear():
    payload = request.get_json(silent=True) or {}
    folder = payload.get("folder")
    global review_bin
    review_bin = [i for i in review_bin if i.get("folder") != folder]
    return jsonify({"status": "ok"})


@app.route("/api/config", methods=["GET", "POST"])
def api_config():
    if request.method == "GET":
        return jsonify(_load_config())

    payload = request.get_json(silent=True) or {}
    config = {**_load_config(), **payload}
    _save_config(config)

    if config.get("auto_extract_archives"):
        archives = [a["name"] for a in _list_media()["archives"]]
        for arch in archives:
            try:
                _extract_archive(MEDIA_DIR / arch)
            except Exception:
                continue

    return jsonify(config)


@app.route("/api/audiobookshelf/test-connection", methods=["POST"])
def api_test_audiobookshelf_connection():
    payload = request.get_json(silent=True) or {}
    saved_config = _load_config()

    server_url = _normalize_audiobookshelf_server_url(
        str(payload.get("audiobookshelf_server_url") or saved_config.get("audiobookshelf_server_url") or "")
    )
    username = str(payload.get("audiobookshelf_username") or saved_config.get("audiobookshelf_username") or "").strip()
    password = str(payload.get("audiobookshelf_password") or saved_config.get("audiobookshelf_password") or "")
    api_key = str(payload.get("audiobookshelf_api_key") or saved_config.get("audiobookshelf_api_key") or "").strip()

    if not server_url:
        return _api_error("URL serveur Audiobookshelf requise", code="missing_server_url")

    try:
        if api_key:
            status_code, me_payload, _ = _audiobookshelf_api_request(
                server_url,
                "/api/me",
                token=api_key,
                timeout=15,
            )
            if status_code >= 400:
                return _api_error(
                    "Échec authentification API key",
                    status=401,
                    code="audiobookshelf_auth_failed",
                    details={"status": status_code},
                )
            user_info = me_payload.get("user") if isinstance(me_payload, dict) else {}
            username_value = user_info.get("username") if isinstance(user_info, dict) else None
            return jsonify(
                {
                    "status": "ok",
                    "server_url": server_url,
                    "auth_method": "api_key",
                    "username": username_value,
                }
            )

        if not username or not password:
            return _api_error(
                "Renseignez une API key ou un couple login/mot de passe",
                code="missing_credentials",
            )

        status_code, login_payload, _ = _audiobookshelf_api_request(
            server_url,
            "/api/login",
            method="POST",
            payload={"username": username, "password": password},
            timeout=15,
        )
        if status_code >= 400:
            return _api_error(
                "Échec authentification login/mot de passe",
                status=401,
                code="audiobookshelf_auth_failed",
                details={"status": status_code},
            )

        token = ""
        if isinstance(login_payload, dict):
            token = str(login_payload.get("token") or "").strip()
            if not token:
                user_info = login_payload.get("user")
                if isinstance(user_info, dict):
                    token = str(user_info.get("token") or "").strip()

        if not token:
            return _api_error(
                "Réponse Audiobookshelf invalide (token manquant)",
                status=502,
                code="audiobookshelf_invalid_response",
            )

        return jsonify(
            {
                "status": "ok",
                "server_url": server_url,
                "auth_method": "password",
                "username": username,
            }
        )
    except urllib.error.URLError as exc:
        return _api_error(
            f"Connexion impossible au serveur Audiobookshelf: {exc}",
            status=503,
            code="audiobookshelf_unreachable",
        )
    except Exception as exc:  # noqa: BLE001
        return _api_error(str(exc), status=500, code="audiobookshelf_test_failed")


@app.route("/api/ollama/status")
def api_ollama_status():
    config = _load_config()
    models = _list_ollama_models()
    return jsonify(
        {
            "enabled": bool(config.get("ollama_enabled", False)),
            "selected_model": config.get("ollama_model"),
            "extract_model": config.get("ollama_extract_model"),
            "base_url": OLLAMA_BASE_URL,
            "models": models,
        }
    )


@app.route("/api/ollama/pull", methods=["POST"])
def api_ollama_pull_model():
    payload = request.get_json(silent=True) or {}
    model = (payload.get("model") or "").strip()
    if not model:
        return _api_error("model requis", code="missing_model")

    try:
        output = _ollama_pull_model(model)
    except Exception as exc:  # noqa: BLE001
        return _api_error(str(exc), status=503, code="ollama_unavailable")

    return jsonify({"status": "ok", "model": model, "output": output})


@app.route("/api/ollama/delete", methods=["POST"])
def api_ollama_delete_model():
    payload = request.get_json(silent=True) or {}
    model = (payload.get("model") or "").strip()
    if not model:
        return _api_error("model requis", code="missing_model")

    try:
        output = _ollama_delete_model(model)
    except Exception as exc:  # noqa: BLE001
        return _api_error(str(exc), status=500, code="ollama_delete_failed")

    return jsonify({"status": "ok", "model": model, "output": output})


@app.route("/api/ollama/search", methods=["POST"])
def api_ollama_search_metadata():
    payload = request.get_json(silent=True) or {}
    folders = payload.get("folders", [])
    if not isinstance(folders, list) or not folders:
        return _api_error("folders requis", code="missing_folders")

    config = _load_config()
    results = [_run_ollama_metadata_search(folder, config) for folder in folders if isinstance(folder, str)]
    return jsonify({"results": results})





@app.route("/api/monitor")
def api_monitor():
    previous = {
        "source_sig": request.args.get("source_sig") or "",
        "output_sig": request.args.get("output_sig") or "",
        "jobs_sig": request.args.get("jobs_sig") or "",
    }
    current = _compute_monitor_signatures()
    changes = {
        "library": previous["source_sig"] != current["source_sig"],
        "outputs": previous["output_sig"] != current["output_sig"],
        "jobs": previous["jobs_sig"] != current["jobs_sig"],
    }
    return jsonify({"changes": changes, "signatures": current})

@app.route("/api/outputs")
def api_outputs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    files = []
    for item in sorted(OUTPUT_DIR.glob("*.m4b"), key=lambda p: p.stat().st_mtime, reverse=True):
        files.append({"name": item.name, "size": item.stat().st_size, "created": item.stat().st_mtime})
    return jsonify(files)


@app.route("/api/download/<path:filename>")
def download_file(filename: str):
    file_path = _resolve_output_file(filename)
    if file_path and file_path.is_file():
        return send_file(str(file_path), as_attachment=True)
    return _api_error("Fichier non trouvé", status=404, code="file_not_found")


@app.route("/api/stream/<path:filename>")
def stream_file(filename: str):
    file_path = _resolve_output_file(filename)
    if file_path and file_path.is_file():
        return send_file(str(file_path), mimetype="audio/mp4")
    return _api_error("Fichier non trouvé", status=404, code="file_not_found")


@app.route("/health")
def health_check():
    return jsonify({"status": "healthy", "service": "audiobook-manager-web"})


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    app.run(host="0.0.0.0", port=5000)
