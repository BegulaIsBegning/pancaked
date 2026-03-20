#!/usr/bin/env python3
"""
LocalStore — App Store local baseada em GitHub
Versão 1.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import json
import os
import sys
import platform
import subprocess
import threading
import urllib.request
import urllib.error
import tempfile
import shutil
import zipfile
import tarfile
import time
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────
#  Configurações globais
# ─────────────────────────────────────────────

# URL do JSON hospedado no GitHub (substitua pelo seu)
CATALOG_URL = "https://raw.githubusercontent.com/SEU_USUARIO/SEU_REPO/main/data/apps.json"

# Diretório local de dados do LocalStore
DATA_DIR = Path.home() / ".localstore"
HISTORY_FILE = DATA_DIR / "installed.json"
CACHE_FILE   = DATA_DIR / "catalog_cache.json"
LOG_FILE     = DATA_DIR / "localstore.log"

DATA_DIR.mkdir(parents=True, exist_ok=True)

# Detectar OS
CURRENT_OS = {
    "Windows": "windows",
    "Linux":   "linux",
    "Darwin":  "macos"
}.get(platform.system(), "linux")

# ─────────────────────────────────────────────
#  Paleta de cores
# ─────────────────────────────────────────────
COLORS = {
    "bg":           "#0d1117",
    "surface":      "#161b22",
    "surface2":     "#21262d",
    "border":       "#30363d",
    "text":         "#e6edf3",
    "text_dim":     "#8b949e",
    "text_muted":   "#484f58",
    "accent":       "#2ea043",
    "accent_hover": "#3fb950",
    "accent2":      "#1f6feb",
    "accent2_hov":  "#388bfd",
    "warning":      "#d29922",
    "danger":       "#f85149",
    "tag_bg":       "#1f2937",
    "tag_text":     "#60a5fa",
    "installed":    "#0f2a1a",
    "installed_bdr":"#2ea043",
}

CATEGORY_COLORS = {
    "Produtividade": "#7c3aed",
    "Desenvolvimento": "#1d4ed8",
    "Design":        "#b45309",
    "Utilitários":   "#0f766e",
    "Rede":          "#0369a1",
    "Segurança":     "#b91c1c",
    "Mídia":         "#a21caf",
}


# ─────────────────────────────────────────────
#  Utilitários
# ─────────────────────────────────────────────

def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def load_history() -> dict:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_history(data: dict):
    HISTORY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def version_tuple(v: str):
    try:
        return tuple(int(x) for x in v.split("."))
    except Exception:
        return (0,)


def fetch_url(url: str, timeout=20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "LocalStore/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def download_file(url: str, dest: Path, progress_cb=None) -> Path:
    req = urllib.request.Request(url, headers={"User-Agent": "LocalStore/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        total = int(r.headers.get("Content-Length", 0))
        done = 0
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            while True:
                chunk = r.read(65536)
                if not chunk:
                    break
                f.write(chunk)
                done += len(chunk)
                if progress_cb and total:
                    progress_cb(done / total)
    return dest


# ─────────────────────────────────────────────
#  Widget: Botão estilizado
# ─────────────────────────────────────────────

class StyledButton(tk.Canvas):
    def __init__(self, parent, text, command=None, style="primary",
                 width=110, height=32, **kw):
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0, bd=0,
                         bg=COLORS["surface"], **kw)
        self.command = command
        self.text = text
        self.style = style
        self.width = width
        self.height = height
        self._hovered = False
        self._draw()
        self.bind("<Enter>",    self._on_enter)
        self.bind("<Leave>",    self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _colors(self):
        styles = {
            "primary":   (COLORS["accent"],  COLORS["accent_hover"],  "#ffffff"),
            "secondary": (COLORS["accent2"], COLORS["accent2_hov"],   "#ffffff"),
            "ghost":     (COLORS["surface2"],COLORS["border"],        COLORS["text_dim"]),
            "danger":    (COLORS["danger"],  "#ff6b6b",               "#ffffff"),
        }
        return styles.get(self.style, styles["primary"])

    def _draw(self):
        self.delete("all")
        bg, bg_h, fg = self._colors()
        color = bg_h if self._hovered else bg
        r = 6
        w, h = self.width, self.height
        # Rounded rect
        self.create_arc(0, 0, r*2, r*2, start=90, extent=90, fill=color, outline=color)
        self.create_arc(w-r*2, 0, w, r*2, start=0, extent=90, fill=color, outline=color)
        self.create_arc(w-r*2, h-r*2, w, h, start=270, extent=90, fill=color, outline=color)
        self.create_arc(0, h-r*2, r*2, h, start=180, extent=90, fill=color, outline=color)
        self.create_rectangle(r, 0, w-r, h, fill=color, outline=color)
        self.create_rectangle(0, r, w, h-r, fill=color, outline=color)
        self.create_text(w//2, h//2, text=self.text, fill=fg,
                         font=("Segoe UI", 9, "bold"))

    def _on_enter(self, e):
        self._hovered = True
        self._draw()
        self.config(cursor="hand2")

    def _on_leave(self, e):
        self._hovered = False
        self._draw()
        self.config(cursor="")

    def _on_click(self, e):
        if self.command:
            self.command()

    def config_text(self, text):
        self.text = text
        self._draw()

    def config_style(self, style):
        self.style = style
        self._draw()


# ─────────────────────────────────────────────
#  Widget: Card de aplicativo
# ─────────────────────────────────────────────

class AppCard(tk.Frame):
    def __init__(self, parent, app_data: dict, installed_info: dict,
                 on_install=None, on_update=None, on_details=None, **kw):
        super().__init__(parent, bg=COLORS["surface"],
                         relief="flat", bd=0, **kw)
        self.app = app_data
        self.installed = installed_info
        self.on_install = on_install
        self.on_update = on_update
        self.on_details = on_details

        is_installed = bool(installed_info)
        installed_ver = installed_info.get("version", "") if installed_info else ""
        has_update = (is_installed and
                      version_tuple(app_data["version"]) > version_tuple(installed_ver))

        # Borda colorida se instalado
        border_color = COLORS["installed_bdr"] if is_installed else COLORS["border"]
        outer = tk.Frame(self, bg=border_color, padx=1, pady=1)
        outer.pack(fill="both", expand=True)

        inner_bg = COLORS["installed"] if is_installed else COLORS["surface"]
        inner = tk.Frame(outer, bg=inner_bg, padx=16, pady=14)
        inner.pack(fill="both", expand=True)

        # Linha do topo: ícone + nome + categoria
        top = tk.Frame(inner, bg=inner_bg)
        top.pack(fill="x")

        tk.Label(top, text=app_data.get("icon", "📦"),
                 font=("Segoe UI Emoji", 20),
                 bg=inner_bg, fg=COLORS["text"]).pack(side="left", padx=(0, 10))

        title_frame = tk.Frame(top, bg=inner_bg)
        title_frame.pack(side="left", fill="x", expand=True)

        tk.Label(title_frame, text=app_data["name"],
                 font=("Segoe UI", 12, "bold"),
                 bg=inner_bg, fg=COLORS["text"],
                 anchor="w").pack(fill="x")

        meta_line = tk.Frame(title_frame, bg=inner_bg)
        meta_line.pack(fill="x")

        cat = app_data.get("category", "")
        cat_color = CATEGORY_COLORS.get(cat, COLORS["accent2"])
        tk.Label(meta_line, text=cat,
                 font=("Segoe UI", 8, "bold"),
                 bg=inner_bg, fg=cat_color, anchor="w").pack(side="left")

        tk.Label(meta_line, text=f"  v{app_data['version']}  ·  {app_data.get('size','?')}",
                 font=("Segoe UI", 8),
                 bg=inner_bg, fg=COLORS["text_dim"]).pack(side="left")

        if is_installed:
            badge = "  ✓ instalado" + ("  · update!" if has_update else "")
            badge_color = COLORS["warning"] if has_update else COLORS["accent"]
            tk.Label(meta_line, text=badge,
                     font=("Segoe UI", 8, "bold"),
                     bg=inner_bg, fg=badge_color).pack(side="left")

        # Descrição
        desc = tk.Label(inner, text=app_data.get("description",""),
                        font=("Segoe UI", 9),
                        bg=inner_bg, fg=COLORS["text_dim"],
                        wraplength=380, justify="left", anchor="w")
        desc.pack(fill="x", pady=(8, 0))

        # Tags
        tags_frame = tk.Frame(inner, bg=inner_bg)
        tags_frame.pack(fill="x", pady=(8, 0))
        for tag in app_data.get("tags", [])[:4]:
            tk.Label(tags_frame, text=f" {tag} ",
                     font=("Segoe UI", 7),
                     bg=COLORS["tag_bg"], fg=COLORS["tag_text"],
                     padx=2, pady=1).pack(side="left", padx=(0,4))

        # Botões
        btn_row = tk.Frame(inner, bg=inner_bg)
        btn_row.pack(fill="x", pady=(12, 0))

        dl_url = app_data.get("downloads", {}).get(CURRENT_OS, "")
        is_direct_exe = dl_url.endswith(".exe")

        if not is_installed:
            label = "⬇  Baixar" if is_direct_exe else "⬇  Instalar"
            StyledButton(btn_row, label, style="primary",
                         command=lambda: self.on_install and self.on_install(app_data),
                         width=110, height=30).pack(side="left", padx=(0, 8))
        else:
            if is_direct_exe:
                StyledButton(btn_row, "▶  Jogar", style="primary",
                             command=lambda: self.on_install and self.on_install(app_data),
                             width=100, height=30).pack(side="left", padx=(0, 8))
            if has_update:
                StyledButton(btn_row, "⬆  Atualizar", style="secondary",
                             command=lambda: self.on_update and self.on_update(app_data),
                             width=110, height=30).pack(side="left", padx=(0, 8))
            elif not is_direct_exe:
                lbl = tk.Label(btn_row, text="✓ Atualizado",
                               font=("Segoe UI", 9),
                               bg=inner_bg, fg=COLORS["accent"])
                lbl.pack(side="left", padx=(0, 8))

        StyledButton(btn_row, "ℹ  Detalhes", style="ghost",
                     command=lambda: self.on_details and self.on_details(app_data),
                     width=100, height=30).pack(side="left")


# ─────────────────────────────────────────────
#  Janela de Detalhes
# ─────────────────────────────────────────────

class DetailsWindow(tk.Toplevel):
    def __init__(self, parent, app_data: dict, installed_info: dict, on_install, on_update):
        super().__init__(parent)
        self.title(f"{app_data['name']} — Detalhes")
        self.geometry("560x520")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg"])
        self.grab_set()

        a = app_data
        is_installed = bool(installed_info)
        installed_ver = installed_info.get("version","") if installed_info else ""
        has_update = (is_installed and
                      version_tuple(a["version"]) > version_tuple(installed_ver))

        pad = tk.Frame(self, bg=COLORS["bg"], padx=24, pady=20)
        pad.pack(fill="both", expand=True)

        # Header
        h = tk.Frame(pad, bg=COLORS["bg"])
        h.pack(fill="x", pady=(0,16))
        tk.Label(h, text=a.get("icon","📦"), font=("Segoe UI Emoji",28),
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left", padx=(0,12))
        hh = tk.Frame(h, bg=COLORS["bg"])
        hh.pack(side="left", fill="x", expand=True)
        tk.Label(hh, text=a["name"], font=("Segoe UI",16,"bold"),
                 bg=COLORS["bg"], fg=COLORS["text"], anchor="w").pack(fill="x")
        tk.Label(hh, text=f"v{a['version']}  ·  {a.get('size','?')}  ·  {a.get('author','')}",
                 font=("Segoe UI",9), bg=COLORS["bg"], fg=COLORS["text_dim"], anchor="w").pack(fill="x")

        sep = tk.Frame(pad, bg=COLORS["border"], height=1)
        sep.pack(fill="x", pady=(0,14))

        tk.Label(pad, text=a.get("description",""),
                 font=("Segoe UI",10), bg=COLORS["bg"], fg=COLORS["text"],
                 wraplength=510, justify="left", anchor="w").pack(fill="x", pady=(0,14))

        # Plataformas
        tk.Label(pad, text="Plataformas disponíveis:",
                 font=("Segoe UI",9,"bold"), bg=COLORS["bg"], fg=COLORS["text_dim"],
                 anchor="w").pack(fill="x")
        dl = a.get("downloads", {})
        plat_row = tk.Frame(pad, bg=COLORS["bg"])
        plat_row.pack(fill="x", pady=(4,14))
        icons = {"windows":"🪟","linux":"🐧","macos":"🍎"}
        for p in ["windows","linux","macos"]:
            color = COLORS["accent"] if p in dl else COLORS["text_muted"]
            tk.Label(plat_row, text=f"{icons[p]} {p.capitalize()}",
                     font=("Segoe UI",9), bg=COLORS["bg"], fg=color).pack(side="left", padx=(0,16))

        # Changelog
        tk.Label(pad, text="Changelog:",
                 font=("Segoe UI",9,"bold"), bg=COLORS["bg"], fg=COLORS["text_dim"],
                 anchor="w").pack(fill="x")
        cl_frame = tk.Frame(pad, bg=COLORS["surface"], bd=0, padx=12, pady=10)
        cl_frame.pack(fill="x", pady=(4,14))
        changelog = a.get("changelog", {})
        for ver, note in list(changelog.items())[:4]:
            row = tk.Frame(cl_frame, bg=COLORS["surface"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"v{ver}", font=("Segoe UI",8,"bold"),
                     width=8, bg=COLORS["surface"], fg=COLORS["accent"], anchor="w").pack(side="left")
            tk.Label(row, text=note, font=("Segoe UI",8),
                     bg=COLORS["surface"], fg=COLORS["text_dim"], anchor="w").pack(side="left", fill="x")

        # Status instalação
        if is_installed:
            status_text = f"✓ Instalado  —  versão {installed_ver}"
            if has_update:
                status_text += f"  →  update disponível: v{a['version']}"
            tk.Label(pad, text=status_text,
                     font=("Segoe UI",9,"bold"), bg=COLORS["bg"],
                     fg=COLORS["warning"] if has_update else COLORS["accent"],
                     anchor="w").pack(fill="x", pady=(0,10))

        # Botões
        btn_row = tk.Frame(pad, bg=COLORS["bg"])
        btn_row.pack(fill="x", pady=(4,0))
        if not is_installed:
            StyledButton(btn_row, "⬇  Instalar", style="primary", width=120, height=34,
                         command=lambda: [self.destroy(), on_install(a)]).pack(side="left", padx=(0,8))
        elif has_update:
            StyledButton(btn_row, "⬆  Atualizar", style="secondary", width=120, height=34,
                         command=lambda: [self.destroy(), on_update(a)]).pack(side="left", padx=(0,8))
        StyledButton(btn_row, "Fechar", style="ghost", width=90, height=34,
                     command=self.destroy).pack(side="left")


# ─────────────────────────────────────────────
#  App principal
# ─────────────────────────────────────────────

class LocalStoreApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LocalStore")
        self.geometry("900x680")
        self.minsize(760, 540)
        self.configure(bg=COLORS["bg"])

        self.catalog: list  = []
        self.history: dict  = load_history()
        self.filtered: list = []
        self._current_tab   = "catalog"
        self._search_var    = tk.StringVar()
        self._cat_var       = tk.StringVar(value="Todas")
        self._status_var    = tk.StringVar(value="Carregando catálogo...")
        self._progress_var  = tk.DoubleVar(value=0)

        self._build_ui()
        self.after(200, self._load_catalog)

    # ── Build UI ──────────────────────────────

    def _build_ui(self):
        # Sidebar
        self._sidebar = tk.Frame(self, bg=COLORS["surface"], width=200)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)
        self._build_sidebar()

        # Main area
        main = tk.Frame(self, bg=COLORS["bg"])
        main.pack(side="left", fill="both", expand=True)

        # Topbar
        topbar = tk.Frame(main, bg=COLORS["surface"], height=56, padx=16, pady=10)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        # Search
        search_frame = tk.Frame(topbar, bg=COLORS["surface2"], padx=8, pady=4)
        search_frame.pack(side="left", fill="y")
        tk.Label(search_frame, text="🔍", bg=COLORS["surface2"],
                 fg=COLORS["text_dim"], font=("Segoe UI Emoji",11)).pack(side="left")
        search_entry = tk.Entry(search_frame, textvariable=self._search_var,
                                bg=COLORS["surface2"], fg=COLORS["text"],
                                insertbackground=COLORS["text"],
                                relief="flat", font=("Segoe UI",10), width=28,
                                bd=0, highlightthickness=0)
        search_entry.pack(side="left", padx=6)
        search_entry.insert(0, "Buscar apps...")
        search_entry.bind("<FocusIn>",  lambda e: search_entry.delete(0,"end") if search_entry.get()=="Buscar apps..." else None)
        search_entry.bind("<FocusOut>", lambda e: search_entry.insert(0,"Buscar apps...") if not search_entry.get() else None)
        self._search_var.trace_add("write", lambda *_: self._apply_filters())

        # Category filter
        cats = ["Todas","Produtividade","Desenvolvimento","Design","Utilitários","Rede","Segurança","Mídia"]
        cat_menu = ttk.Combobox(topbar, textvariable=self._cat_var,
                                values=cats, state="readonly", width=14,
                                font=("Segoe UI",9))
        cat_menu.pack(side="left", padx=12, fill="y")
        self._cat_var.trace_add("write", lambda *_: self._apply_filters())
        self._style_combobox()

        # Refresh button
        StyledButton(topbar, "↻  Atualizar", style="ghost", width=110, height=34,
                     command=self._reload_catalog).pack(side="right")

        # Content stack
        self._content = tk.Frame(main, bg=COLORS["bg"])
        self._content.pack(fill="both", expand=True, padx=16, pady=12)

        # Catalog frame (scrollable)
        self._catalog_outer = tk.Frame(self._content, bg=COLORS["bg"])
        self._history_outer  = tk.Frame(self._content, bg=COLORS["bg"])

        self._catalog_canvas  = tk.Canvas(self._catalog_outer, bg=COLORS["bg"],
                                          highlightthickness=0)
        scroll = tk.Scrollbar(self._catalog_outer, orient="vertical",
                              command=self._catalog_canvas.yview)
        self._catalog_canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self._catalog_canvas.pack(side="left", fill="both", expand=True)

        self._cards_frame = tk.Frame(self._catalog_canvas, bg=COLORS["bg"])
        self._cards_win   = self._catalog_canvas.create_window(
            (0,0), window=self._cards_frame, anchor="nw")
        self._cards_frame.bind("<Configure>", self._on_frame_resize)
        self._catalog_canvas.bind("<Configure>", self._on_canvas_resize)
        self._catalog_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # History frame
        self._build_history_panel()

        # Statusbar
        statusbar = tk.Frame(main, bg=COLORS["surface"], height=30)
        statusbar.pack(fill="x", side="bottom")
        statusbar.pack_propagate(False)
        tk.Label(statusbar, textvariable=self._status_var,
                 bg=COLORS["surface"], fg=COLORS["text_dim"],
                 font=("Segoe UI",8), anchor="w", padx=12).pack(side="left", fill="y")
        self._progress = ttk.Progressbar(statusbar, variable=self._progress_var,
                                         maximum=1.0, length=180, mode="determinate")
        self._progress.pack(side="right", padx=12, pady=7)
        self._progress.pack_forget()

        self._show_tab("catalog")

    def _build_sidebar(self):
        sb = self._sidebar

        # Logo
        logo_frame = tk.Frame(sb, bg=COLORS["surface"], pady=20)
        logo_frame.pack(fill="x")
        tk.Label(logo_frame, text="📦", font=("Segoe UI Emoji",24),
                 bg=COLORS["surface"], fg=COLORS["text"]).pack()
        tk.Label(logo_frame, text="LocalStore",
                 font=("Segoe UI",13,"bold"),
                 bg=COLORS["surface"], fg=COLORS["text"]).pack()
        tk.Label(logo_frame, text="v1.0.0",
                 font=("Segoe UI",8),
                 bg=COLORS["surface"], fg=COLORS["text_dim"]).pack()

        sep = tk.Frame(sb, bg=COLORS["border"], height=1)
        sep.pack(fill="x", padx=16, pady=4)

        # Navigation
        nav = tk.Frame(sb, bg=COLORS["surface"], padx=8, pady=8)
        nav.pack(fill="x")

        self._nav_btns = {}
        nav_items = [
            ("catalog", "🏪  Catálogo"),
            ("installed","✅  Instalados"),
            ("history",  "📋  Histórico"),
        ]
        for key, label in nav_items:
            btn = tk.Label(nav, text=label,
                           font=("Segoe UI",10),
                           bg=COLORS["surface"], fg=COLORS["text_dim"],
                           anchor="w", padx=12, pady=10, cursor="hand2")
            btn.pack(fill="x", pady=1)
            btn.bind("<Button-1>", lambda e, k=key: self._show_tab(k))
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=COLORS["surface2"]))
            btn.bind("<Leave>", lambda e, b=btn, k=key:
                     b.configure(bg=COLORS["accent"] if self._current_tab==k else COLORS["surface"]))
            self._nav_btns[key] = btn

        sep2 = tk.Frame(sb, bg=COLORS["border"], height=1)
        sep2.pack(fill="x", padx=16, pady=4)

        # Stats
        self._stats_frame = tk.Frame(sb, bg=COLORS["surface"], padx=12, pady=8)
        self._stats_frame.pack(fill="x")
        self._stats_installed = tk.Label(self._stats_frame, text="0 instalados",
                                         font=("Segoe UI",9),
                                         bg=COLORS["surface"], fg=COLORS["text_dim"],
                                         anchor="w")
        self._stats_installed.pack(fill="x")
        self._stats_available = tk.Label(self._stats_frame, text="0 disponíveis",
                                         font=("Segoe UI",9),
                                         bg=COLORS["surface"], fg=COLORS["text_dim"],
                                         anchor="w")
        self._stats_available.pack(fill="x")

        os_label = {"windows":"🪟 Windows","linux":"🐧 Linux","macos":"🍎 macOS"}
        tk.Label(sb, text=os_label.get(CURRENT_OS, CURRENT_OS),
                 font=("Segoe UI",8),
                 bg=COLORS["surface"], fg=COLORS["text_muted"],
                 anchor="w", padx=12).pack(fill="x", side="bottom", pady=8)

    def _build_history_panel(self):
        f = self._history_outer
        tk.Label(f, text="📋  Histórico de Instalações",
                 font=("Segoe UI",13,"bold"),
                 bg=COLORS["bg"], fg=COLORS["text"],
                 anchor="w").pack(fill="x", pady=(0,12))
        self._history_list = tk.Frame(f, bg=COLORS["bg"])
        self._history_list.pack(fill="both", expand=True)

    # ── Tabs ──────────────────────────────────

    def _show_tab(self, tab: str):
        self._current_tab = tab
        for key, btn in self._nav_btns.items():
            btn.configure(bg=COLORS["accent"] if key==tab else COLORS["surface"],
                          fg=COLORS["text"] if key==tab else COLORS["text_dim"])

        self._catalog_outer.pack_forget()
        self._history_outer.pack_forget()

        if tab == "catalog":
            self._catalog_outer.pack(fill="both", expand=True)
            self._apply_filters()
        elif tab == "installed":
            self._catalog_outer.pack(fill="both", expand=True)
            self._apply_filters(installed_only=True)
        elif tab == "history":
            self._history_outer.pack(fill="both", expand=True)
            self._refresh_history_panel()

    # ── Catalog loading ───────────────────────

    def _load_catalog(self):
        def worker():
            self._set_status("Buscando catálogo no GitHub...")
            try:
                data = fetch_url(CATALOG_URL)
                catalog_json = json.loads(data)
                CACHE_FILE.write_bytes(data)
                log("Catálogo baixado do GitHub com sucesso.")
            except Exception as e:
                log(f"Falha ao buscar catálogo online: {e}")
                self._set_status("Offline — usando cache local.")
                if CACHE_FILE.exists():
                    catalog_json = json.loads(CACHE_FILE.read_bytes())
                else:
                    self.after(0, lambda: messagebox.showerror(
                        "Sem conexão",
                        "Não foi possível baixar o catálogo e não há cache local.\n"
                        "Verifique sua conexão e o URL do JSON no topo do arquivo."))
                    return

            self.catalog = catalog_json.get("apps", [])
            self.after(0, self._on_catalog_loaded)

        threading.Thread(target=worker, daemon=True).start()

    def _reload_catalog(self):
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
        self._load_catalog()

    def _on_catalog_loaded(self):
        total = len(self.catalog)
        inst  = len(self.history)
        self._stats_available.configure(text=f"{total} disponíveis")
        self._stats_installed.configure(text=f"{inst} instalados")
        self._set_status(f"✓ {total} apps carregados  ·  {inst} instalados")
        self._apply_filters()

    # ── Filters / render ─────────────────────

    def _apply_filters(self, installed_only=False):
        q   = self._search_var.get().strip().lower()
        if q == "buscar apps...":
            q = ""
        cat = self._cat_var.get()

        filtered = []
        for app in self.catalog:
            if installed_only and app["id"] not in self.history:
                continue
            if cat != "Todas" and app.get("category") != cat:
                continue
            if q:
                haystack = (app["name"] + app.get("description","") +
                            " ".join(app.get("tags",[]))).lower()
                if q not in haystack:
                    continue
            filtered.append(app)

        self.filtered = filtered
        self._render_cards()

    def _render_cards(self):
        for w in self._cards_frame.winfo_children():
            w.destroy()

        if not self.filtered:
            tk.Label(self._cards_frame,
                     text="Nenhum app encontrado.",
                     font=("Segoe UI",11), bg=COLORS["bg"],
                     fg=COLORS["text_dim"]).pack(pady=40)
            return

        col, row = 0, 0
        cols = max(1, self._catalog_canvas.winfo_width() // 440)
        for app in self.filtered:
            installed_info = self.history.get(app["id"], {})
            card = AppCard(self._cards_frame, app, installed_info,
                           on_install=self._start_install,
                           on_update=self._start_install,
                           on_details=self._show_details)
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            col += 1
            if col >= cols:
                col = 0
                row += 1

        for c in range(cols):
            self._cards_frame.columnconfigure(c, weight=1)

    def _refresh_history_panel(self):
        for w in self._history_list.winfo_children():
            w.destroy()

        if not self.history:
            tk.Label(self._history_list, text="Nenhum app instalado ainda.",
                     font=("Segoe UI",10), bg=COLORS["bg"],
                     fg=COLORS["text_dim"]).pack(pady=30)
            return

        # Header
        hdr = tk.Frame(self._history_list, bg=COLORS["surface"], padx=12, pady=8)
        hdr.pack(fill="x", pady=(0,8))
        for col, w in [("App",200),("Versão",80),("OS",80),("Instalado em",160)]:
            tk.Label(hdr, text=col, width=w//8, font=("Segoe UI",9,"bold"),
                     bg=COLORS["surface"], fg=COLORS["text_dim"],
                     anchor="w").pack(side="left", padx=4)

        for app_id, info in sorted(self.history.items(),
                                    key=lambda x: x[1].get("installed_at",""),
                                    reverse=True):
            row = tk.Frame(self._history_list, bg=COLORS["surface2"],
                           padx=12, pady=10)
            row.pack(fill="x", pady=2)
            name = info.get("name", app_id)
            ver  = info.get("version","?")
            os_  = info.get("os", "?")
            date = info.get("installed_at","?")[:16].replace("T"," ")

            tk.Label(row, text=name, width=25, font=("Segoe UI",9,"bold"),
                     bg=COLORS["surface2"], fg=COLORS["text"], anchor="w").pack(side="left", padx=4)
            tk.Label(row, text=f"v{ver}", width=10, font=("Segoe UI",9),
                     bg=COLORS["surface2"], fg=COLORS["accent"], anchor="w").pack(side="left", padx=4)
            tk.Label(row, text=os_, width=10, font=("Segoe UI",9),
                     bg=COLORS["surface2"], fg=COLORS["text_dim"], anchor="w").pack(side="left", padx=4)
            tk.Label(row, text=date, width=20, font=("Segoe UI",9),
                     bg=COLORS["surface2"], fg=COLORS["text_dim"], anchor="w").pack(side="left", padx=4)
            StyledButton(row, "Remover", style="danger", width=80, height=26,
                         command=lambda aid=app_id: self._remove_app(aid)).pack(side="right")

    # ── Details ───────────────────────────────

    def _show_details(self, app_data: dict):
        installed = self.history.get(app_data["id"], {})
        DetailsWindow(self, app_data, installed,
                      on_install=self._start_install,
                      on_update=self._start_install)

    # ── Install ───────────────────────────────

    def _start_install(self, app_data: dict):
        dl = app_data.get("downloads", {})
        if CURRENT_OS not in dl:
            messagebox.showwarning("Não disponível",
                                   f"{app_data['name']} não tem download para {CURRENT_OS}.")
            return

        dl_url = dl.get(CURRENT_OS, "")
        is_direct_exe = dl_url.endswith(".exe")
        msg = (f"Baixar e abrir {app_data['name']} v{app_data['version']}?\n\nO .exe será salvo em ~/.localstore/apps/ e aberto direto."
               if is_direct_exe else
               f"Instalar {app_data['name']} v{app_data['version']}?\n\nO script de instalação será executado.")
        if not messagebox.askyesno("Confirmar", msg):
            return

        def worker():
            try:
                self._set_status(f"Baixando {app_data['name']}...")
                self._show_progress(True)

                # Criar pasta temporária para esta instalação
                tmp = Path(tempfile.mkdtemp(prefix="localstore_"))

                # Baixar pacote do app
                pkg_url = dl[CURRENT_OS]
                pkg_name = pkg_url.split("/")[-1]
                pkg_path = tmp / pkg_name

                self._set_status(f"Baixando {pkg_name}...")
                download_file(pkg_url, pkg_path,
                              progress_cb=lambda p: self._progress_var.set(p * 0.7))

                scripts = app_data.get("install_scripts", {})

                if pkg_name.endswith(".exe"):
                    # ── Modo direto: .exe sem installer ──────────────
                    # Salvar em pasta permanente dentro de ~/.localstore/apps/
                    apps_dir = DATA_DIR / "apps" / app_data["id"]
                    apps_dir.mkdir(parents=True, exist_ok=True)
                    final_exe = apps_dir / pkg_name
                    shutil.copy2(pkg_path, final_exe)
                    self._progress_var.set(0.95)
                    self._set_status(f"Abrindo {app_data['name']}...")
                    subprocess.Popen([str(final_exe)], cwd=str(apps_dir))
                    install_dir = str(apps_dir)

                else:
                    # ── Modo com extração + script ────────────────────
                    self._set_status("Extraindo arquivos...")
                    extract_dir = tmp / "extracted"
                    extract_dir.mkdir()
                    if pkg_name.endswith(".zip"):
                        with zipfile.ZipFile(pkg_path) as z:
                            z.extractall(extract_dir)
                    elif pkg_name.endswith((".tar.gz", ".tgz")):
                        with tarfile.open(pkg_path) as t:
                            t.extractall(extract_dir)

                    if CURRENT_OS in scripts:
                        self._set_status("Baixando script de instalação...")
                        script_url = scripts[CURRENT_OS]
                        script_name = script_url.split("/")[-1]
                        script_path = tmp / script_name
                        download_file(script_url, script_path,
                                      progress_cb=lambda p: self._progress_var.set(0.7 + p * 0.2))

                        self._set_status("Executando instalação...")
                        self._progress_var.set(0.9)

                        if CURRENT_OS == "windows":
                            cmd = ["cmd", "/c", str(script_path)]
                        else:
                            os.chmod(script_path, 0o755)
                            cmd = ["bash", str(script_path)]

                        result = subprocess.run(cmd, cwd=str(tmp), capture_output=True, text=True)
                        log(f"Install stdout: {result.stdout}")
                        if result.returncode != 0:
                            log(f"Install stderr: {result.stderr}")

                    install_dir = str(extract_dir)

                # Registrar no histórico
                self.history[app_data["id"]] = {
                    "name":         app_data["name"],
                    "version":      app_data["version"],
                    "os":           CURRENT_OS,
                    "installed_at": datetime.now().isoformat(),
                    "install_dir":  install_dir,
                }
                save_history(self.history)

                # Limpeza da pasta temporária
                shutil.rmtree(tmp, ignore_errors=True)

                self._progress_var.set(1.0)
                self.after(0, lambda: self._on_install_done(app_data, success=True))

            except Exception as e:
                log(f"Erro na instalação de {app_data['name']}: {e}")
                self.after(0, lambda: self._on_install_done(app_data, success=False, error=str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _on_install_done(self, app_data: dict, success: bool, error=""):
        self._show_progress(False)
        n = len(self.history)
        self._stats_installed.configure(text=f"{n} instalados")

        if success:
            self._set_status(f"✓ {app_data['name']} instalado com sucesso!")
            messagebox.showinfo("Instalado!",
                                f"✅  {app_data['name']} v{app_data['version']} instalado com sucesso!")
        else:
            self._set_status(f"Erro ao instalar {app_data['name']}")
            messagebox.showerror("Erro na instalação",
                                 f"Falha ao instalar {app_data['name']}:\n\n{error}\n\n"
                                 f"Verifique o log em: {LOG_FILE}")

        self._apply_filters(installed_only=(self._current_tab == "installed"))

    def _remove_app(self, app_id: str):
        name = self.history.get(app_id, {}).get("name", app_id)
        if messagebox.askyesno("Remover do histórico",
                               f"Remover '{name}' do histórico?\n\n"
                               f"Isso não desinstala o app do sistema."):
            del self.history[app_id]
            save_history(self.history)
            self._stats_installed.configure(text=f"{len(self.history)} instalados")
            self._refresh_history_panel()

    # ── Helpers ───────────────────────────────

    def _set_status(self, msg: str):
        self._status_var.set(msg)

    def _show_progress(self, show: bool):
        if show:
            self._progress_var.set(0)
            self._progress.pack(side="right", padx=12, pady=7)
        else:
            self._progress.pack_forget()
            self._progress_var.set(0)

    def _on_frame_resize(self, e):
        self._catalog_canvas.configure(scrollregion=self._catalog_canvas.bbox("all"))

    def _on_canvas_resize(self, e):
        self._catalog_canvas.itemconfig(self._cards_win, width=e.width)
        self._render_cards()

    def _on_mousewheel(self, e):
        delta = -1 * (e.delta // 120) if platform.system() == "Windows" else -1 * e.delta
        self._catalog_canvas.yview_scroll(delta, "units")

    def _style_combobox(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TCombobox",
                        fieldbackground=COLORS["surface2"],
                        background=COLORS["surface2"],
                        foreground=COLORS["text"],
                        selectbackground=COLORS["accent"],
                        selectforeground="#ffffff",
                        borderwidth=0)


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app = LocalStoreApp()
    app.mainloop()
