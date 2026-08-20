"""CID Local Media Agent — Producer GUI (tkinter/ttk).

Producer-facing Windows window built on the stable CID LMA backend.
Exposes audiovisual tasks only; runtime, model and implementation details
are hidden. Works fully local and offline.
"""

from __future__ import annotations

import os
import queue
import subprocess
import sys
import threading
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

APP_VERSION = "0.3.0-beta1"
APP_TITLE = "CID Local Media Agent"
LOCAL_HINT = "CID trabaja en modo local\nLos originales no se modifican"
RESULTS_DAVINCI_HINT = "Se genera un SRT listo para DaVinci."
DONE_SRT_HINT_COMPLETED = "Los SRT completados están listos para DaVinci."
DONE_SRT_HINT_NONE = "No se ha generado ningún SRT en esta ejecución."
MIN_ETA_AUDIO_SECONDS = 25.0
GROUPS_HIGH_CONFIDENCE = "CID ha seleccionado la mejor fuente de audio."
GROUPS_ALTERNATIVES_TITLE = "Fuentes de esta grabación"
DUPLICATE_AVOIDED_HINT = "Las fuentes relacionadas no se transcriben varias veces."

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from scripts.local_media_agent.read_only_folder_scanner import scan_read_only_folder
from scripts.local_media_agent.ffprobe_metadata_extraction import extract_metadata
from scripts.local_media_agent.audio_source_intelligence import (
    build_sync_manifest,
    group_related_media,
)
from scripts.local_media_agent.batch_transcription import (
    _default_results_dir,
    last_result_location,
    make_run_results_dir,
    remember_result_location,
    run_batch_transcription,
    select_batch_candidates,
)
from scripts.local_media_agent.cid_local_media_agent_operator import (
    _resolve_packaged_model,
)


def _format_duration(seconds: float | None) -> str:
    """Format seconds as HH:MM:SS (or MM:SS for sub-hour)."""
    if seconds is None or seconds <= 0:
        return "—"
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def _format_clock(seconds: float) -> str:
    """Format seconds as HH:MM:SS always."""
    s = max(0, int(seconds))
    h, rem = divmod(s, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _done_srt_hint(completed_count: int, srt_files_created: int) -> str:
    """Truthful done-screen hint: never claim an SRT unless one was produced."""
    if completed_count > 0 and srt_files_created > 0:
        return DONE_SRT_HINT_COMPLETED
    return DONE_SRT_HINT_NONE


def cluster_view(cluster: Any) -> dict[str, Any]:
    """Producer-facing view of one recording/session cluster.

    Exposes the internal cluster as understandable audiovisual concepts:
    counts per category, whether audio was synchronized, the selected masters
    and the sources kept as alternatives. No technical parameters are exposed.
    """
    sources = list(cluster.sources)
    audio_count = sum(1 for sig in sources if not sig.has_video)
    video_count = sum(1 for sig in sources if sig.has_video)
    masters = list(cluster.transcription_masters)
    master = Path(masters[0]).name if masters else "—"
    sync_ok = any(
        rel.get("sync", {}).get("status") == "RESOLVED"
        for rel in getattr(cluster, "relationships", [])
    )
    dispositions = getattr(cluster, "dispositions", {})
    dialogue = sum(1 for p, d in dispositions.items() if d == "DIALOGUE")
    technical = sum(1 for p, d in dispositions.items() if d == "TECHNICAL_OR_EMPTY")
    unique = sum(1 for p, d in dispositions.items() if d == "UNIQUE_CONTENT")
    uncertain = sum(1 for p, d in dispositions.items() if d == "UNCERTAIN")
    duplicates = len(list(cluster.duplicate_sources))
    return {
        "session_id": cluster.session_id,
        "title": f"Grabación {cluster.session_id}",
        "audio_count": audio_count,
        "video_count": video_count,
        "source_count": len(sources),
        "master": master,
        "master_rel": masters[0] if masters else None,
        "sync_ok": sync_ok,
        "duplicate_count": duplicates,
        "alternate_count": len(list(cluster.alternate_sources)),
        "dialogue_count": dialogue,
        "technical_count": technical,
        "unique_count": unique,
        "uncertain_count": uncertain,
    }


def _sources_for_cluster(cluster: Any, metadata: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return the metadata entries belonging to a cluster's transcription masters."""
    master_rels = set(cluster.transcription_masters)
    return [
        item for item in metadata
        if item.get("relative_path") in master_rels
    ]


def _duration_of(item: dict[str, Any]) -> float | None:
    """Return a positive duration for a metadata item, else None."""
    dur = item.get("duration_seconds")
    return float(dur) if isinstance(dur, (int, float)) and dur > 0 else None


def _weight_of(item: dict[str, Any]) -> float:
    """Weight for overall batch progress: duration, or 1.0 when unknown."""
    dur = _duration_of(item)
    return dur if dur is not None else 1.0


def _logs_dir() -> Path:
    local_appdata = os.environ.get("LOCALAPPDATA", os.environ.get("HOME", "/tmp"))
    path = Path(local_appdata) / "CID" / "LocalMediaAgent" / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_log(*lines: str) -> None:
    """Append a timestamped diagnostic line to the CID-controlled log."""
    try:
        log_file = _logs_dir() / "cid_gui.log"
        stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with log_file.open("a", encoding="utf-8") as fh:
            for line in lines:
                fh.write(f"{stamp} {line}\n")
    except Exception:
        pass


def _open_folder(path: str) -> None:
    """Open a folder using normal Windows Explorer behavior."""
    try:
        if sys.platform == "win32":
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as exc:
        _write_log(f"open_folder_error: {exc}")


def _confirm_dialog(
    parent: tk.Misc,
    title: str,
    message: str,
    buttons: tuple[str, ...],
) -> str | None:
    """Small modal dialog with explicit Spanish buttons.

    Returns the chosen button label, or None if the dialog was closed.
    """
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.transient(parent)
    dialog.grab_set()
    dialog.resizable(False, False)

    frame = ttk.Frame(dialog, padding=18)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text=message, justify="left", wraplength=360).grid(
        row=0, column=0, sticky="w", pady=(0, 14)
    )

    row_buttons = ttk.Frame(frame)
    row_buttons.grid(row=1, column=0, sticky="e")

    result: list[str | None] = [None]

    def choose(value: str) -> None:
        result[0] = value
        dialog.destroy()

    for idx, label in enumerate(buttons):
        ttk.Button(
            row_buttons,
            text=label,
            command=lambda value=label: choose(value),
        ).grid(row=0, column=idx, padx=(4, 0))

    dialog.update_idletasks()
    width = dialog.winfo_reqwidth()
    height = dialog.winfo_reqheight()
    x = parent.winfo_rootx() + max(0, (parent.winfo_width() - width) // 2)
    y = parent.winfo_rooty() + max(0, (parent.winfo_height() - height) // 2)
    dialog.geometry(f"{width}x{height}+{x}+{y}")

    parent.wait_window(dialog)
    return result[0]


class ProducerApp:
    """Main producer window with task-oriented views."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.ui_q: "queue.Queue[tuple]" = queue.Queue()
        self.cancel_event = threading.Event()
        self.worker: threading.Thread | None = None
        self.active = False
        self.close_after_done = False

        self.folder: str | None = None
        self.scan_result: dict[str, Any] = {}
        self.metadata: dict[str, Any] = {}
        self.candidates: list[dict[str, Any]] = []
        self.clusters: list[Any] = []
        self.cluster_views: list[dict[str, Any]] = []
        self.results_dir: str | None = None
        self.results_root: str = last_result_location() or str(_default_results_dir())
        self.analysis_model_path: str | None = _resolve_packaged_model()
        self._duration_map: dict[str, float | None] = {}
        self._weight_map: dict[str, float] = {}
        self._run_state: dict[str, Any] = {}
        self._last_srt_path: str | None = None
        self._last_davinci_path: str | None = None

        self.root.title(f"{APP_TITLE} {APP_VERSION}")
        self.root.geometry("780x620")
        self.root.minsize(700, 540)

        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Header.TLabel", font=("Segoe UI", 15, "bold"))
        style.configure("Sub.TLabel", foreground="#555555")
        style.configure("Count.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("CountName.TLabel", foreground="#555555")
        style.configure("Info.TLabel", foreground="#777777", justify="left")
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(14, 8))
        style.configure("LocalBox.TLabel", background="#eef6ec", foreground="#2f6b2f", padding=10)

        self.container = ttk.Frame(self.root, padding=18)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames: dict[str, ttk.Frame] = {}
        self._build_home()
        self._build_material()
        self._build_groups()
        self._build_run()
        self._build_done()

        self._show("home")

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(120, self._poll_queue)

    # ------------------------------------------------------------ frames

    def _new_frame(self, name: str) -> ttk.Frame:
        frame = ttk.Frame(self.container, padding=8)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        self.frames[name] = frame
        return frame

    def _show(self, name: str) -> None:
        self.frames[name].tkraise()

    def _build_home(self) -> None:
        frame = self._new_frame("home")
        body = ttk.Frame(frame)
        body.grid(row=0, column=0, sticky="n")

        ttk.Label(body, text=APP_TITLE, style="Header.TLabel").pack(pady=(30, 2))
        ttk.Label(body, text=f"Versión {APP_VERSION}", style="Sub.TLabel").pack(pady=(0, 22))

        local_box = ttk.Label(body, text=LOCAL_HINT, style="LocalBox.TLabel", justify="center")
        local_box.pack(pady=(0, 26))

        self.folder_label = ttk.Label(body, text="", style="Sub.TLabel", wraplength=520)
        self.folder_label.pack(pady=(0, 10))

        self.analyze_btn = ttk.Button(
            body,
            text="Seleccionar carpeta",
            style="Primary.TButton",
            command=self._pick_folder,
        )
        self.analyze_btn.pack(pady=(4, 4))

        self.analyze_hint = ttk.Label(body, text="", style="Sub.TLabel")
        self.analyze_hint.pack(pady=(8, 0))

    def _build_material(self) -> None:
        frame = self._new_frame("material")
        body = ttk.Frame(frame)
        body.grid(row=0, column=0, sticky="nsew")
        body.grid_rowconfigure(2, weight=1)
        body.grid_columnconfigure(0, weight=1)

        header = ttk.Frame(body)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(header, text="Material", style="Header.TLabel").pack(side="left")
        self.material_path_label = ttk.Label(header, text="", style="Sub.TLabel")
        self.material_path_label.pack(side="right")

        counts = ttk.Frame(body)
        counts.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        self.count_labels: dict[str, tk.StringVar] = {}
        for idx, key in enumerate(("video", "audio", "images", "other", "errors")):
            var = tk.StringVar(value="0")
            self.count_labels[key] = var
            cell = ttk.Frame(counts)
            cell.grid(row=0, column=idx, padx=(0, 22))
            ttk.Label(cell, textvariable=var, style="Count.TLabel").pack(anchor="w")
            name = {"video": "Vídeo", "audio": "Audio", "images": "Imágenes",
                    "other": "Otros", "errors": "Errores"}[key]
            ttk.Label(cell, text=name, style="CountName.TLabel").pack(anchor="w")

        list_frame = ttk.Frame(body)
        list_frame.grid(row=2, column=0, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            list_frame,
            columns=("file", "type", "duration"),
            show="headings",
            selectmode="extended",
        )
        self.tree.heading("file", text="Archivo")
        self.tree.heading("type", text="Tipo")
        self.tree.heading("duration", text="Duración")
        self.tree.column("file", width=360, anchor="w", stretch=True)
        self.tree.column("type", width=70, anchor="center", stretch=False)
        self.tree.column("duration", width=90, anchor="center", stretch=False)
        self.tree.grid(row=0, column=0, sticky="nsew")

        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scroll.set)

        selection = ttk.Frame(body)
        selection.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        self.selection_label = ttk.Label(selection, text="Archivos seleccionados: 0")
        self.selection_label.pack(side="left")

        actions = ttk.Frame(body)
        actions.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(actions, text="Seleccionar todo", command=self._select_all).pack(side="left")
        self.transcribe_btn = ttk.Button(
            actions,
            text="Transcribir archivos",
            style="Primary.TButton",
            command=self._start_transcription_click,
        )
        self.transcribe_btn.pack(side="right")
        self.material_davinci_hint = ttk.Label(
            body, text=RESULTS_DAVINCI_HINT, style="Info.TLabel"
        )
        self.material_davinci_hint.grid(row=5, column=0, sticky="w", pady=(8, 0))

        location = ttk.Frame(body)
        location.grid(row=6, column=0, sticky="ew", pady=(10, 0))
        ttk.Label(location, text="Guardar resultados en:").pack(side="left")
        self.results_root_label = ttk.Label(location, text="", style="Sub.TLabel", wraplength=430)
        self.results_root_label.pack(side="left", padx=(8, 8))
        ttk.Button(location, text="Cambiar…", command=self._choose_results_location).pack(side="left")
        self._refresh_results_root_label()

        self.tree.bind("<<TreeviewSelect>>", lambda _e: self._update_selection())

    def _build_groups(self) -> None:
        frame = self._new_frame("groups")
        body = ttk.Frame(frame)
        body.grid(row=0, column=0, sticky="nsew")
        body.grid_rowconfigure(2, weight=1)
        body.grid_columnconfigure(0, weight=1)

        header = ttk.Frame(body)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(header, text="Grabaciones", style="Header.TLabel").pack(side="left")
        self.groups_path_label = ttk.Label(header, text="", style="Sub.TLabel")
        self.groups_path_label.pack(side="right")

        self.groups_hint = ttk.Label(
            body,
            text="CID agrupa las fuentes relacionadas y selecciona la mejor para transcribir.",
            style="Info.TLabel",
            wraplength=680,
        )
        self.groups_hint.grid(row=1, column=0, sticky="w", pady=(0, 10))

        list_frame = ttk.Frame(body)
        list_frame.grid(row=2, column=0, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.groups_tree = ttk.Treeview(
            list_frame,
            columns=("title", "sources", "master"),
            show="headings",
            selectmode="browse",
        )
        self.groups_tree.heading("title", text="Grabación")
        self.groups_tree.heading("sources", text="Fuentes")
        self.groups_tree.heading("master", text="Recomendación CID")
        self.groups_tree.column("title", width=260, anchor="w", stretch=True)
        self.groups_tree.column("sources", width=120, anchor="center", stretch=False)
        self.groups_tree.column("master", width=280, anchor="w", stretch=True)
        self.groups_tree.grid(row=0, column=0, sticky="nsew")

        groups_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.groups_tree.yview)
        groups_scroll.grid(row=0, column=1, sticky="ns")
        self.groups_tree.configure(yscrollcommand=groups_scroll.set)

        actions = ttk.Frame(body)
        actions.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        self.groups_transcribe_btn = ttk.Button(
            actions,
            text="Transcribir entrevista",
            style="Primary.TButton",
            command=self._transcribe_selected_group_click,
        )
        self.groups_transcribe_btn.pack(side="left")
        self.groups_sources_btn = ttk.Button(
            actions,
            text="Ver fuentes",
            command=self._view_selected_group_sources,
        )
        self.groups_sources_btn.pack(side="left", padx=(8, 0))
        self.groups_duplicate_hint = ttk.Label(
            body, text=DUPLICATE_AVOIDED_HINT, style="Info.TLabel"
        )
        self.groups_duplicate_hint.grid(row=4, column=0, sticky="w", pady=(8, 0))

        self.groups_tree.bind("<<TreeviewSelect>>", lambda _e: self._update_groups_selection())

    def _build_run(self) -> None:
        frame = self._new_frame("run")
        body = ttk.Frame(frame)
        body.grid(row=0, column=0, sticky="n")

        self.run_title = ttk.Label(body, text="Transcribiendo…", style="Header.TLabel")
        self.run_title.pack(pady=(24, 8))

        self.run_progress_label = ttk.Label(body, text="Transcribiendo 0 de 0", style="Count.TLabel")
        self.run_progress_label.pack(pady=(0, 6))

        self.run_file_label = ttk.Label(body, text="", wraplength=560)
        self.run_file_label.pack(pady=(0, 8))

        self.file_bar = ttk.Progressbar(body, mode="determinate", maximum=100)
        self.file_bar.pack(fill="x", padx=40, pady=(0, 4))

        self.run_file_progress_label = ttk.Label(body, text="", style="Sub.TLabel")
        self.run_file_progress_label.pack(pady=(0, 2))

        self.run_processed_label = ttk.Label(body, text="Procesado: —", style="Sub.TLabel")
        self.run_processed_label.pack(pady=(0, 10))

        self.batch_bar = ttk.Progressbar(body, mode="determinate", maximum=100)
        self.batch_bar.pack(fill="x", padx=40, pady=(0, 4))

        self.run_batch_progress_label = ttk.Label(body, text="Avance total: 0 %", style="Sub.TLabel")
        self.run_batch_progress_label.pack(pady=(0, 2))

        self.run_elapsed_label = ttk.Label(
            body, text="Tiempo transcurrido: 00:00:00", style="Sub.TLabel"
        )
        self.run_elapsed_label.pack(pady=(2, 2))

        self.run_eta_label = ttk.Label(body, text="", style="Sub.TLabel")
        self.run_eta_label.pack(pady=(2, 14))

        self.cancel_btn = ttk.Button(
            body,
            text="Cancelar",
            style="Primary.TButton",
            command=self._cancel_click,
        )
        self.cancel_btn.pack()

    def _build_done(self) -> None:
        frame = self._new_frame("done")
        body = ttk.Frame(frame)
        body.grid(row=0, column=0, sticky="n")

        self.done_title = ttk.Label(body, text="", style="Header.TLabel")
        self.done_title.pack(pady=(30, 14))

        self.done_body = ttk.Frame(body)
        self.done_body.pack(pady=(0, 18))

        self.done_davinci_label = ttk.Label(body, text=RESULTS_DAVINCI_HINT, style="Info.TLabel")
        self.done_davinci_label.pack(pady=(0, 18))

        actions = ttk.Frame(body)
        actions.pack(pady=(0, 14))
        self.open_results_btn = ttk.Button(
            actions,
            text="Abrir resultados",
            style="Primary.TButton",
            command=self._open_results,
        )
        self.open_results_btn.pack(side="left", padx=(0, 6))
        self.open_srt_btn = ttk.Button(
            actions, text="Abrir SRT", state="disabled", command=self._open_srt
        )
        self.open_srt_btn.pack(side="left", padx=(6, 0))
        self.davinci_btn = ttk.Button(
            actions, text="Preparar para DaVinci", state="disabled", command=self._open_davinci
        )
        self.davinci_btn.pack(side="left", padx=(6, 0))

        self.transcribe_more_btn = ttk.Button(
            body, text="Transcribir más", command=self._transcribe_more
        )
        self.transcribe_more_btn.pack(pady=(0, 10))

        self.done_results_path = ttk.Label(body, text="", style="Info.TLabel", justify="left")
        self.done_results_path.pack()

    # ------------------------------------------------------------ helpers

    def _pick_folder(self) -> None:
        if self.active:
            return
        folder = filedialog.askdirectory(
            parent=self.root,
            title="Seleccionar carpeta de material",
        )
        if not folder:
            return
        self.folder = folder
        self.folder_label.config(text=folder)
        self.analyze_btn.config(text="Analizar material")
        self.analyze_hint.config(text="")
        self.root.after(100, self._start_analysis)

    def _refresh_results_root_label(self) -> None:
        self.results_root_label.config(text=self.results_root or "")

    def _choose_results_location(self) -> None:
        folder = filedialog.askdirectory(
            parent=self.root,
            title="Seleccionar carpeta de resultados",
            initialdir=self.results_root or None,
        )
        if not folder:
            return
        self.results_root = folder
        remember_result_location(folder)
        self._refresh_results_root_label()

    def _selected_group_index(self) -> int | None:
        selection = self.groups_tree.selection()
        if not selection:
            return None
        iid = selection[0]
        for index, view in enumerate(self.cluster_views):
            if str(index) == iid:
                return index
        return None

    def _update_groups_selection(self) -> None:
        index = self._selected_group_index()
        enabled = index is not None
        self.groups_transcribe_btn.config(state="normal" if enabled else "disabled")
        self.groups_sources_btn.config(state="normal" if enabled else "disabled")

    def _view_selected_group_sources(self) -> None:
        index = self._selected_group_index()
        if index is None or index >= len(self.clusters):
            return
        cluster = self.clusters[index]
        disp_labels = {
            "DIALOGUE": "entrevista",
            "DUPLICATE": "duplicada",
            "ALTERNATE": "alternativa",
            "TECHNICAL_OR_EMPTY": "pista auxiliar",
            "UNIQUE_CONTENT": "independiente",
            "UNCERTAIN": "sin clasificar",
        }
        rows = []
        for sig in cluster.sources:
            disp = cluster.dispositions.get(sig.relative_path, "DIALOGUE")
            if sig.relative_path in cluster.transcription_masters:
                label = "seleccionada para transcripción"
            else:
                label = disp_labels.get(disp, "alternativa")
            rows.append(f"• {sig.relative_path} ({label})")
        messagebox.showinfo(
            GROUPS_ALTERNATIVES_TITLE,
            "\n".join(rows) or "No hay fuentes en esta grabación.",
            parent=self.root,
        )

    def _transcribe_selected_group_click(self) -> None:
        if self.active or not self.folder:
            return
        index = self._selected_group_index()
        if index is None or index >= len(self.clusters):
            return
        cluster = self.clusters[index]
        master_rels = set(cluster.transcription_masters)
        selected = [
            item for item in self.metadata.get("results", [])
            if item.get("relative_path") in master_rels
        ]
        if not selected:
            messagebox.showinfo(APP_TITLE, "Esta grabación no tiene una fuente clara para transcribir.", parent=self.root)
            return
        view = cluster_view(cluster)
        category_lines = []
        if view["dialogue_count"]:
            category_lines.append(f"{view['dialogue_count']} fuentes de la entrevista")
        if view["technical_count"]:
            category_lines.append(f"{view['technical_count']} pistas auxiliares")
        if view["unique_count"]:
            category_lines.append(f"{view['unique_count']} fuente independiente" if view["unique_count"] == 1 else f"{view['unique_count']} fuentes independientes")
        if view["uncertain_count"]:
            category_lines.append(f"{view['uncertain_count']} fuente sin clasificar" if view["uncertain_count"] == 1 else f"{view['uncertain_count']} fuentes sin clasificar")
        category_text = "\n".join(f"- {line}" for line in category_lines) or "Sin categorías."
        master_label = view["master"]
        if len(cluster.transcription_masters) > 1:
            master_label = f"{len(cluster.transcription_masters)} fuentes"
        message = (
            f"{view['title']}\n"
            f"{view['source_count']} fuentes encontradas\n\n"
            f"CID ha identificado:\n{category_text}\n\n"
            f"Recomendación CID: {master_label}\n\n"
            f"¿Transcribir?"
        )
        choice = _confirm_dialog(self.root, "Transcribir entrevista", message, ("Continuar", "Cancelar"))
        if choice != "Continuar":
            return
        manifest = build_sync_manifest(cluster, media_root=self.folder)
        self._start_transcription(selected, project_name=cluster.session_id, sync_manifest=manifest)

    def _start_analysis(self) -> None:
        if not self.folder or self.active:
            return
        self.analyze_btn.config(state="disabled")
        self.analyze_hint.config(text="Analizando material…")
        self.cancel_event.clear()
        self.worker = threading.Thread(target=self._analysis_worker, daemon=True)
        self.worker.start()

    def _analysis_worker(self) -> None:
        folder = self.folder
        try:
            scan = scan_read_only_folder(folder)
            self.ui_q.put(("scan_done", scan))
            meta = extract_metadata(folder, scan)
            self.ui_q.put(("metadata_done", meta))
            candidates = select_batch_candidates(meta.get("results", []))
            self.ui_q.put(("candidates_done", candidates))
            clusters = group_related_media(
                meta.get("results", []),
                media_root=folder,
                analyze_content=True,
            )
            self.ui_q.put(("clusters_done", clusters))
        except Exception as exc:
            _write_log("analysis_error", traceback.format_exc())
            self.ui_q.put(("error", "No se pudo analizar el material.", str(exc)))

    def _on_scan_done(self, scan: dict[str, Any]) -> None:
        ext = scan.get("extension_summary", {})
        video_exts = {".mp4", ".mov", ".mxf", ".mkv", ".avi", ".mts", ".m2ts", ".webm"}
        audio_exts = {".wav", ".bwf", ".aif", ".aiff", ".mp3", ".m4a", ".aac", ".flac", ".ogg"}
        image_exts = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".dng", ".cr2", ".cr3", ".arw", ".nef", ".orf", ".raf"}
        self.count_labels["video"].set(str(sum(v for e, v in ext.items() if e in video_exts)))
        self.count_labels["audio"].set(str(sum(v for e, v in ext.items() if e in audio_exts)))
        self.count_labels["images"].set(str(sum(v for e, v in ext.items() if e in image_exts)))
        self.count_labels["other"].set(str(sum(v for e, v in ext.items() if e not in video_exts | audio_exts | image_exts)))
        self.count_labels["errors"].set(str(len(scan.get("errors", []))))

    def _on_candidates_done(self, candidates: list[dict[str, Any]]) -> None:
        self.candidates = candidates
        for item in self.tree.get_children():
            self.tree.delete(item)
        for c in candidates:
            rel = c.get("relative_path", "?")
            cat = c.get("category", "?")
            label = "Vídeo" if cat == "video" else "Audio"
            self.tree.insert(
                "", "end",
                iid=rel,
                values=(rel, label, _format_duration(c.get("duration_seconds"))),
            )
        self.material_path_label.config(text=self.folder or "")
        self.analyze_btn.config(state="normal", text="Seleccionar carpeta")
        self.analyze_hint.config(text="")
        self._show("material")
        self._update_selection()

    def _on_clusters_done(self, clusters: list[Any]) -> None:
        self.clusters = clusters or []
        self.cluster_views = [cluster_view(cluster) for cluster in self.clusters]
        for item in self.groups_tree.get_children():
            self.groups_tree.delete(item)
        for index, view in enumerate(self.cluster_views):
            parts = []
            if view["dialogue_count"]:
                parts.append(f"{view['dialogue_count']} entrevista")
            if view["unique_count"]:
                parts.append(f"{view['unique_count']} independiente")
            if view["technical_count"]:
                parts.append(f"{view['technical_count']} auxiliar")
            if view["uncertain_count"]:
                parts.append(f"{view['uncertain_count']} sin clasificar")
            sources_label = " · ".join(parts) if parts else f"{view['source_count']} fuentes"
            self.groups_tree.insert(
                "", "end",
                iid=str(index),
                values=(view["title"], sources_label, view["master"]),
            )
        self.groups_path_label.config(text=self.folder or "")
        self._update_groups_selection()
        if self.clusters:
            self._show("groups")
        else:
            self._show("material")

    def _selected_metadata(self) -> list[dict[str, Any]]:
        selected = set(self.tree.selection())
        return [
            c for c in self.candidates
            if c.get("relative_path") in selected
        ]

    def _select_all(self) -> None:
        for item in self.tree.get_children():
            self.tree.selection_add(item)
        self._update_selection()

    def _update_selection(self) -> None:
        selected = self._selected_metadata()
        count = len(selected)
        durations = [c.get("duration_seconds") for c in selected]
        total = sum(d for d in durations if isinstance(d, (int, float)))
        has_unknown = any(not isinstance(d, (int, float)) for d in durations)
        if has_unknown:
            total_str = "—"
        else:
            total_str = _format_duration(total)
        self.selection_label.config(
            text=f"Archivos seleccionados: {count}    Duración total: {total_str}"
        )
        self.transcribe_btn.config(text=f"Transcribir {count} archivos" if count else "Transcribir archivos")

    # ------------------------------------------------------------ transcription

    def _start_transcription_click(self) -> None:
        if self.active or not self.folder:
            return
        selected = self._selected_metadata()
        if not selected:
            messagebox.showinfo(APP_TITLE, "Selecciona al menos un archivo para transcribir.", parent=self.root)
            return
        count = len(selected)
        durations = [c.get("duration_seconds") for c in selected]
        total = sum(d for d in durations if isinstance(d, (int, float)))
        has_unknown = any(not isinstance(d, (int, float)) for d in durations)
        total_str = "—" if has_unknown else _format_duration(total)
        message = (
            f"Archivos seleccionados: {count}\n"
            f"Duración total: {total_str}\n\n"
            f"¿Quieres transcribir estos archivos?"
        )
        choice = _confirm_dialog(self.root, "Confirmar transcripción", message, ("Continuar", "Cancelar"))
        if choice != "Continuar":
            return
        self._start_transcription(selected)

    def _start_transcription(
        self,
        selected: list[dict[str, Any]],
        project_name: str | None = None,
        sync_manifest: dict[str, Any] | None = None,
    ) -> None:
        model_dir = self.analysis_model_path
        if not model_dir:
            messagebox.showerror(
                APP_TITLE,
                "No se encontró el modelo de transcripción local.",
                parent=self.root,
            )
            return

        run_dir = make_run_results_dir(self.results_root, project_name)
        self.results_dir = str(run_dir)

        self.cancel_event.clear()
        self.active = True
        self.cancel_btn.config(state="normal", text="Cancelar")
        self.run_eta_label.config(text="")
        self.run_file_label.config(text="")
        self.run_file_progress_label.config(text="")
        self.run_processed_label.config(text="Procesado: —")
        self.run_batch_progress_label.config(text="Avance total: 0 %")
        self.run_elapsed_label.config(text="Tiempo transcurrido: 00:00:00")
        self.file_bar["value"] = 0
        self.batch_bar["value"] = 0

        durations = {c.get("relative_path"): _duration_of(c) for c in selected}
        weights = {c.get("relative_path"): _weight_of(c) for c in selected}
        self._duration_map = durations
        self._weight_map = weights
        self._run_state = {
            "total_weight": sum(weights.values()),
            "total_audio": sum(d for d in durations.values() if d),
            "completed_weight": 0.0,
            "completed_audio": 0.0,
            "current_rel": None,
            "current_index": 0,
            "batch_total": len(selected),
            "current_dur": None,
            "current_weight": 0.0,
            "current_processed": 0.0,
            "start_monotonic": time.monotonic(),
            "last_eta_update": 0.0,
            "last_elapsed_shown": -1,
        }

        self._show("run")
        self.root.after(
            150,
            self._begin_run_worker,
            str(self.folder),
            model_dir,
            selected,
            str(run_dir),
            project_name,
            sync_manifest,
        )

    def _begin_run_worker(
        self,
        folder: str,
        model_dir: str,
        selected: list[dict[str, Any]],
        results_dir: str,
        project_name: str | None,
        sync_manifest: dict[str, Any] | None,
    ) -> None:
        self.worker = threading.Thread(
            target=self._transcription_worker,
            args=(folder, model_dir, selected, results_dir, project_name, sync_manifest),
            daemon=True,
        )
        self.worker.start()

    def _transcription_worker(
        self,
        folder: str,
        model_dir: str,
        selected: list[dict[str, Any]],
        results_dir: str,
        project_name: str | None,
        sync_manifest: dict[str, Any] | None,
    ) -> None:
        try:
            def progress(index: int, total: int, rel: str) -> None:
                self.ui_q.put(("progress", index, total, rel))

            def segment(seg: dict[str, Any]) -> None:
                self.ui_q.put(("segment", seg))

            batch = run_batch_transcription(
                folder,
                model_dir,
                metadata_results=selected,
                compute_type="int8",
                results_dir=results_dir,
                cancel_event=self.cancel_event,
                progress_callback=progress,
                segment_callback=segment,
                worker_process=True,
                grace_period_seconds=3.0,
                worker_log_dir=str(_logs_dir()),
                sync_manifest=sync_manifest,
            )
            self.ui_q.put(("batch_done", batch))
        except Exception as exc:
            _write_log("transcription_error", traceback.format_exc())
            self.ui_q.put(("error", "No se pudo transcribir este archivo.\nCID continuará con los demás archivos.", str(exc)))

    def _on_progress(self, index: int, total: int, rel: str) -> None:
        st = self._run_state
        prev = st.get("current_rel")
        if prev is not None and prev != rel:
            st["completed_weight"] += st.get("current_weight", 0.0)
            st["completed_audio"] += st.get("current_dur") or 0.0
        st["current_rel"] = rel
        st["current_index"] = index
        st["batch_total"] = total
        st["current_dur"] = self._duration_map.get(rel)
        st["current_weight"] = self._weight_map.get(rel, 1.0)
        st["current_processed"] = 0.0
        self.run_progress_label.config(text=f"Transcribiendo {index} de {total}")
        self.run_file_label.config(text=rel)
        self.run_eta_label.config(text="Calculando tiempo restante…")
        self._render_progress()

    def _on_segment(self, seg: dict[str, Any]) -> None:
        st = self._run_state
        end = seg.get("source_end_seconds")
        if not isinstance(end, (int, float)):
            end = seg.get("end_seconds", 0.0)
        try:
            end = float(end or 0.0)
        except (TypeError, ValueError):
            end = 0.0
        st["current_processed"] = max(st.get("current_processed", 0.0), end)
        self._render_progress()

    def _render_progress(self) -> None:
        st = self._run_state
        dur = st.get("current_dur")
        processed = st.get("current_processed", 0.0)

        if dur:
            frac = min(1.0, processed / dur)
            self.file_bar["value"] = frac * 100
            self.run_file_progress_label.config(text=f"{round(frac * 100)} %")
            self.run_processed_label.config(
                text=f"Procesado: {_format_duration(processed)} / {_format_duration(dur)}"
            )
            current_contrib = st.get("current_weight", 0.0) * frac
        else:
            self.file_bar["value"] = 0
            self.run_file_progress_label.config(text="Procesando…")
            self.run_processed_label.config(text="Procesado: —")
            current_contrib = 0.0

        completed_w = st.get("completed_weight", 0.0)
        total_w = st.get("total_weight", 0.0)
        batch_frac = (completed_w + current_contrib) / total_w if total_w else 0.0
        batch_frac = min(1.0, max(0.0, batch_frac))
        self.batch_bar["value"] = batch_frac * 100
        self.run_batch_progress_label.config(text=f"Avance total: {round(batch_frac * 100)} %")

        elapsed = time.monotonic() - st.get("start_monotonic", time.monotonic())
        shown = int(elapsed)
        if shown != st.get("last_elapsed_shown"):
            st["last_elapsed_shown"] = shown
            self.run_elapsed_label.config(
                text=f"Tiempo transcurrido: {_format_clock(float(shown))}"
            )

        now = time.monotonic()
        if now - st.get("last_eta_update", 0.0) >= 5.0:
            st["last_eta_update"] = now
            self._update_eta()

    def _update_eta(self) -> None:
        st = self._run_state
        processed_audio = st.get("completed_audio", 0.0) + st.get("current_processed", 0.0)
        total_audio = st.get("total_audio", 0.0)
        elapsed = time.monotonic() - st.get("start_monotonic", time.monotonic())
        if processed_audio < MIN_ETA_AUDIO_SECONDS or processed_audio <= 0:
            self.run_eta_label.config(text="Calculando tiempo restante…")
            return
        rtf = elapsed / processed_audio
        remaining = total_audio - processed_audio
        if remaining <= 0:
            self.run_eta_label.config(text="Tiempo restante estimado: menos de un minuto")
            return
        self.run_eta_label.config(
            text=f"Tiempo restante estimado: ~{_format_clock(remaining * rtf)}"
        )

    def _on_batch_done(self, batch: dict[str, Any]) -> None:
        self.active = False
        status = batch.get("status", "BATCH_COMPLETED")
        completed = batch.get("completed_count", batch.get("files_transcribed", 0))
        cancelled = batch.get("cancelled_count", 0)
        pending = batch.get("unstarted_count", 0)
        errors = batch.get("error_count", batch.get("files_errors", 0))
        srt_count = batch.get("srt_files_created", completed)
        processed = batch.get("files_transcribed", 0) + batch.get("files_no_speech", 0) + cancelled
        results_dir = batch.get("results_directory") or self.results_dir
        self.results_dir = results_dir

        for widget in self.done_body.winfo_children():
            widget.destroy()

        if status == "BATCH_CANCELLED":
            self.done_title.config(text="Transcripción detenida")
            rows = (
                (f"Completados: {completed}", f"Pendientes: {pending}"),
                (f"Cancelado: {cancelled}", f"Errores: {errors}"),
            )
            note = "Los resultados completados se han conservado."
            self.batch_bar["value"] = 100
        else:
            self.done_title.config(text="Transcripción completada")
            rows = (
                (f"Archivos procesados: {processed}", f"Subtítulos creados: {srt_count}"),
                ("", ""),
            )
            note = "Los resultados se han guardado en tu carpeta de resultados."
            self.batch_bar["value"] = 100
            self.file_bar["value"] = 100
            self.run_batch_progress_label.config(text="Avance total: 100 %")

        self.done_davinci_label.config(text=_done_srt_hint(completed, srt_count))

        for row_index, (left, right) in enumerate(rows):
            ttk.Label(self.done_body, text=left).grid(
                row=row_index, column=0, sticky="w", padx=(0, 24), pady=2
            )
            ttk.Label(self.done_body, text=right).grid(
                row=row_index, column=1, sticky="w", pady=2
            )
        ttk.Label(self.done_body, text=note, style="Sub.TLabel").grid(
            row=len(rows), column=0, columnspan=2, sticky="w", pady=(10, 0)
        )

        self._last_srt_path = self._first_result_file(batch, "srt_file")
        self._last_davinci_path = self._first_result_file(batch, "davinci_handoff_file")
        self._refresh_done_actions(results_dir)

        self._show("done")

        if self.close_after_done:
            self.root.after(200, self.root.destroy)

    def _first_result_file(self, batch: dict[str, Any], key: str) -> str | None:
        results_dir = batch.get("results_directory") or self.results_dir
        for item in batch.get("results", []):
            name = item.get(key)
            if name:
                return str(Path(results_dir) / name)
        return None

    def _refresh_done_actions(self, results_dir: str) -> None:
        self.open_results_btn.config(text="Abrir resultados")
        self.open_srt_btn.config(state="normal" if self._last_srt_path else "disabled")
        self.davinci_btn.config(state="normal" if self._last_davinci_path else "disabled")
        self.transcribe_more_btn.config(state="normal")
        self.done_results_path.config(
            text=f"Resultados guardados en:\n{results_dir}", style="Sub.TLabel"
        )

    def _open_srt(self) -> None:
        if self._last_srt_path:
            _open_folder(str(Path(self._last_srt_path).parent))
            _open_folder(self._last_srt_path)

    def _open_davinci(self) -> None:
        if self._last_davinci_path:
            _open_folder(str(Path(self._last_davinci_path).parent))
            _open_folder(self._last_davinci_path)

    def _transcribe_more(self) -> None:
        self._show("groups" if self.clusters else "material")

    def _cancel_click(self) -> None:
        if not self.active:
            return
        choice = _confirm_dialog(
            self.root,
            "Detener transcripción",
            "¿Quieres detener la transcripción?\n\nLos archivos ya completados se conservarán.",
            ("Continuar", "Detener"),
        )
        if choice == "Detener":
            self.cancel_event.set()
            self.cancel_btn.config(state="disabled", text="Deteniendo transcripción…")
            self.run_eta_label.config(text="Deteniendo transcripción…")

    def _on_close(self) -> None:
        if self.active:
            choice = _confirm_dialog(
                self.root,
                "Detener transcripción",
                "¿Quieres detener la transcripción y cerrar la ventana?\n\nLos archivos ya completados se conservarán.",
                ("Continuar", "Detener"),
            )
            if choice == "Detener":
                self.close_after_done = True
                self.cancel_event.set()
                self.cancel_btn.config(state="disabled", text="Deteniendo transcripción…")
                self.run_eta_label.config(text="Deteniendo transcripción…")
            return
        self.root.destroy()

    def _open_results(self) -> None:
        if self.results_dir:
            _open_folder(self.results_dir)

    def _on_error(self, message: str, detail: str) -> None:
        if self.active:
            self.active = False
        _write_log("gui_error", detail)
        messagebox.showerror(APP_TITLE, message, parent=self.root)
        if self.close_after_done:
            self.root.after(200, self.root.destroy)

    # ------------------------------------------------------------ event loop

    def _poll_queue(self) -> None:
        try:
            while True:
                item = self.ui_q.get_nowait()
                kind = item[0]
                if kind == "scan_done":
                    self._on_scan_done(item[1])
                elif kind == "metadata_done":
                    self.metadata = item[1]
                elif kind == "candidates_done":
                    self._on_candidates_done(item[1])
                elif kind == "clusters_done":
                    self._on_clusters_done(item[1])
                elif kind == "progress":
                    self._on_progress(*item[1:])
                elif kind == "segment":
                    self._on_segment(item[1])
                elif kind == "batch_done":
                    self._on_batch_done(item[1])
                elif kind == "error":
                    self._on_error(item[1], item[2] if len(item) > 2 else "")
        except queue.Empty:
            pass
        if not self.close_after_done or self.active:
            self.root.after(120, self._poll_queue)


def main() -> int:
    root = tk.Tk()
    ProducerApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())