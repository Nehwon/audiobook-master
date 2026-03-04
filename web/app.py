#!/usr/bin/env python3
"""Interface web moderne pour Audiobook Manager Pro (API + UI)."""

from __future__ import annotations

import json
import os
import queue
import re
import shutil
import threading
import time
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import rarfile
from flask import Flask, jsonify, render_template, request, send_file

from core.config import ProcessingConfig
from core.processor import AudiobookProcessor

app = Flask(__name__, template_folder="../templates")
app.config["SECRET_KEY"] = "audiobook_manager_2024"

MEDIA_DIR = Path(os.getenv("AUDIOBOOK_MEDIA_DIR", os.getenv("SOURCE_DIR", "/app/data/source")))
OUTPUT_DIR = Path(os.getenv("AUDIOBOOK_OUTPUT_DIR", os.getenv("OUTPUT_DIR", "/app/data/output")))
TEMP_DIR = Path(os.getenv("AUDIOBOOK_TEMP_DIR", os.getenv("TEMP_DIR", "/tmp/audiobooks_web")))
CONFIG_PATH = TEMP_DIR / "web_config.json"

AUDIO_EXTENSIONS = {".mp3", ".m4a", ".m4b", ".wav", ".flac", ".aac", ".ogg"}
ARCHIVE_EXTENSIONS = {".zip", ".rar"}


@dataclass
class Job:
    id: str
    folder: str
    status: str = "pending"
    progress: int = 0
    stage: str = "En attente"
    error: Optional[str] = None
    output_file: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    ended_at: Optional[float] = None


jobs_lock = threading.Lock()
job_queue: "queue.Queue[str]" = queue.Queue()
jobs: Dict[str, Job] = {}
review_bin: List[Dict] = []
worker_started = False


def _default_config() -> Dict:
    return {
        "bitrate": "128k",
        "sample_rate": 44100,
        "processing_mode": "final_m4b",
        "enable_gpu": True,
        "enable_loudnorm": True,
        "enable_compressor": True,
        "auto_extract_archives": False,
    }


def _load_config() -> Dict:
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_PATH.exists():
        try:
            return {**_default_config(), **json.loads(CONFIG_PATH.read_text(encoding="utf-8"))}
        except Exception:
            return _default_config()
    return _default_config()


def _save_config(config: Dict) -> None:
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def _clean_name(name: str) -> str:
    cleaned = name.replace("+", " ")
    cleaned = re.sub(r"(?i)\b([cdjlmnst])_", r"\1'", cleaned)
    cleaned = cleaned.replace("_", " ")
    cleaned = re.sub(r'[<>:"/\\|?*]', "_", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    return cleaned or "Dossier"


def _smart_rename(folder: str) -> str:
    """Transforme un nom de dossier en format lisible pour les audiobooks."""
    cleaned = _clean_name(folder)
    parts = [p.strip() for p in re.split(r"\s+-\s+", cleaned) if p.strip()]

    if len(parts) == 2:
        return f"{parts[0]} - {parts[1]}"

    if len(parts) >= 3:
        author = parts[0]
        book = parts[-1]
        series_block = " - ".join(parts[1:-1])
        match = re.match(r"^(?P<series>.+?)\s+(?P<volume>\d+)$", series_block)
        if match:
            series = match.group("series").strip()
            volume = int(match.group("volume"))
            return f"{author} - {series} - Vol {volume} - {book}"

        return f"{author} - {series_block} - {book}"

    return cleaned


def _count_audio_files(path: Path) -> int:
    return sum(1 for f in path.rglob("*") if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS)


def _folder_size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def _list_media() -> Dict:
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    folders = []
    archives = []

    for item in sorted(MEDIA_DIR.iterdir(), key=lambda x: x.name.lower()):
        if item.is_dir():
            folders.append(
                {
                    "name": item.name,
                    "audio_count": _count_audio_files(item),
                    "size": _folder_size(item),
                    "modified": item.stat().st_mtime,
                }
            )
        elif item.is_file() and item.suffix.lower() in ARCHIVE_EXTENSIONS:
            archives.append(
                {
                    "name": item.name,
                    "size": item.stat().st_size,
                    "modified": item.stat().st_mtime,
                }
            )

    return {"base_path": str(MEDIA_DIR), "folders": folders, "archives": archives}


def _extract_archive(path: Path, delete_archive: bool = False) -> Dict:
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

    if delete_archive:
        path.unlink(missing_ok=True)

    return {"archive": path.name, "folder": target_dir.name}


def _build_processing_config() -> ProcessingConfig:
    web_config = _load_config()
    cfg = ProcessingConfig()
    cfg.audio_bitrate = web_config["bitrate"]
    cfg.sample_rate = int(web_config["sample_rate"])
    cfg.processing_mode = web_config["processing_mode"]
    cfg.enable_gpu_acceleration = bool(web_config["enable_gpu"])
    cfg.enable_loudnorm = bool(web_config["enable_loudnorm"])
    cfg.enable_compressor = bool(web_config["enable_compressor"])
    return cfg


def _guess_output_file(folder_name: str, start_time: float) -> Optional[str]:
    if not OUTPUT_DIR.exists():
        return None
    candidates = sorted(OUTPUT_DIR.glob("*.m4b"), key=lambda p: p.stat().st_mtime, reverse=True)
    for file in candidates:
        if file.stat().st_mtime >= start_time - 2:
            return file.name
    return candidates[0].name if candidates else None


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

        try:
            folder_path = MEDIA_DIR / job.folder
            if not folder_path.exists() or not folder_path.is_dir():
                raise FileNotFoundError(f"Dossier introuvable: {job.folder}")

            processor = AudiobookProcessor(str(MEDIA_DIR), str(OUTPUT_DIR), str(TEMP_DIR))
            processor.config = _build_processing_config()

            with jobs_lock:
                job.stage = "Conversion"
                job.progress = 30

            success = processor.process_audiobook(folder_path)

            with jobs_lock:
                if success:
                    job.status = "completed"
                    job.stage = "Terminé"
                    job.progress = 100
                    job.output_file = _guess_output_file(job.folder, job.started_at or time.time())
                else:
                    job.status = "failed"
                    job.stage = "Erreur"
                    job.error = "Échec conversion"
                    job.progress = 100
                job.ended_at = time.time()
        except Exception as exc:  # noqa: BLE001
            with jobs_lock:
                job.status = "failed"
                job.stage = "Erreur"
                job.error = str(exc)
                job.progress = 100
                job.ended_at = time.time()
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
    return render_template("index.html")


@app.route("/api/library")
def api_library():
    return jsonify(_list_media())


@app.route("/api/extract", methods=["POST"])
def api_extract():
    payload = request.get_json(silent=True) or {}
    names = payload.get("archives", [])
    delete_archive = bool(payload.get("delete_archive", False))

    results = []
    errors = []
    for name in names:
        archive_path = MEDIA_DIR / name
        try:
            if archive_path.exists() and archive_path.suffix.lower() in ARCHIVE_EXTENSIONS:
                results.append(_extract_archive(archive_path, delete_archive=delete_archive))
            else:
                errors.append(f"Archive introuvable: {name}")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{name}: {exc}")

    return jsonify({"results": results, "errors": errors})


@app.route("/api/rename", methods=["POST"])
def api_rename():
    payload = request.get_json(silent=True) or {}
    folders = payload.get("folders", [])
    if not isinstance(folders, list):
        return jsonify({"error": "Le champ 'folders' doit être une liste"}), 400

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
        except OSError as exc:
            skipped.append({"folder": folder, "reason": f"erreur système: {exc}"})

    return jsonify({"renamed": renamed, "skipped": skipped})


@app.route("/api/jobs/enqueue", methods=["POST"])
def api_enqueue_jobs():
    _ensure_worker()
    payload = request.get_json(silent=True) or {}
    folders = payload.get("folders", [])
    queued = []

    with jobs_lock:
        for folder in folders:
            jid = f"job-{int(time.time() * 1000)}-{len(jobs)}"
            job = Job(id=jid, folder=folder)
            jobs[jid] = job
            job_queue.put(jid)
            queued.append(asdict(job))

    return jsonify({"queued": queued})


@app.route("/api/jobs")
def api_jobs():
    with jobs_lock:
        values = [asdict(j) for j in jobs.values()]

    def sort_key(entry):
        return entry["created_at"]

    pending = sorted([j for j in values if j["status"] == "pending"], key=sort_key)
    running = sorted([j for j in values if j["status"] == "running"], key=sort_key)
    done = sorted([j for j in values if j["status"] in {"completed", "failed"}], key=sort_key, reverse=True)

    return jsonify({"pending": pending, "running": running, "done": done, "review": review_bin})


@app.route("/api/jobs/review", methods=["POST"])
def api_review():
    payload = request.get_json(silent=True) or {}
    job_id = payload.get("job_id")
    action = payload.get("action", "queue_delete")

    with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            return jsonify({"error": "Job introuvable"}), 404

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
        return jsonify({"error": "folder requis"}), 400

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


@app.route("/api/outputs")
def api_outputs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    files = []
    for item in sorted(OUTPUT_DIR.glob("*.m4b"), key=lambda p: p.stat().st_mtime, reverse=True):
        files.append({"name": item.name, "size": item.stat().st_size, "created": item.stat().st_mtime})
    return jsonify(files)


@app.route("/api/download/<path:filename>")
def download_file(filename: str):
    file_path = OUTPUT_DIR / filename
    if file_path.exists():
        return send_file(str(file_path), as_attachment=True)
    return jsonify({"error": "Fichier non trouvé"}), 404


@app.route("/api/stream/<path:filename>")
def stream_file(filename: str):
    file_path = OUTPUT_DIR / filename
    if file_path.exists():
        return send_file(str(file_path), mimetype="audio/mp4")
    return jsonify({"error": "Fichier non trouvé"}), 404


@app.route("/health")
def health_check():
    return jsonify({"status": "healthy", "service": "audiobook-manager-web"})


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    app.run(host="0.0.0.0", port=5000)
