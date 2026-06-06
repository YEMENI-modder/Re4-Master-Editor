"""
RE4 Master Editor v1.0.1
========================
Unified RE4 modding suite  single file.
All modules embedded.

Folder structure next to EXE:
  RE4 MASTER EDITOR/
    RE4 CODE MANAGER/
      the_codes/  the_files/  Profiles/  Modified files/
    OSD EDITOR/
    CNS EDITOR/
    SND EDITOR/
    AEV OPTION EDITOR/
    MDT COLOR EDITOR/
    ROOM INIT EDITOR/
    AVL EDITOR/
"""

import sys
import os
import re
import json
import ctypes
import struct
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.scrolledtext as scrolledtext
from tkinter import filedialog, messagebox, colorchooser

try:
    import customtkinter as ctk
    CTK_AVAILABLE = True
except ImportError:
    CTK_AVAILABLE = False
    # Fallback stubs so class definitions at module level don't crash
    class _CtkStub:
        class CTkToplevel(tk.Toplevel):
            def __init__(self, *a, **kw):
                super().__init__(*a)
        class CTkFrame(tk.Frame):
            def __init__(self, *a, **kw): super().__init__(*a, bg="#1e1e1e")
        class CTkLabel(tk.Label):
            def __init__(self, *a, **kw): super().__init__(*a)
        class CTkButton(tk.Button):
            def __init__(self, *a, **kw): super().__init__(*a)
        class CTkEntry(tk.Entry):
            def __init__(self, *a, **kw): super().__init__(*a)
        class CTkScrollableFrame(tk.Frame):
            def __init__(self, parent, *a, label_text=None, label_fg_color=None, **kw):
                bg = kw.pop("fg_color", "#1e1e1e")
                kw.pop("scrollbar_button_color", None)
                kw.pop("scrollbar_button_hover_color", None)
                super().__init__(parent, bg=bg)
                import tkinter as _tk
                if label_text:
                    _tk.Label(self, text=label_text, bg=bg, fg="#c8a035",
                              font=("Courier New", 8, "bold")).pack(anchor="w", padx=4, pady=(4,0))
                canvas = _tk.Canvas(self, bg=bg, highlightthickness=0)
                vsb    = _tk.Scrollbar(self, orient="vertical", command=canvas.yview)
                canvas.configure(yscrollcommand=vsb.set)
                vsb.pack(side="right", fill="y")
                canvas.pack(side="left", fill="both", expand=True)
                self.inner = _tk.Frame(canvas, bg=bg)
                self._win  = canvas.create_window((0, 0), window=self.inner, anchor="nw")
                self.inner.bind("<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
                canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(self._win, width=e.width))
                canvas.bind("<MouseWheel>",
                    lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
                canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
                canvas.bind("<Button-5>", lambda e: canvas.yview_scroll( 1, "units"))
                self.inner.grid_columnconfigure(0, weight=1)
                self._canvas = canvas
                self._parent_canvas = canvas
            def grid_columnconfigure(self, *a, **kw): self.inner.grid_columnconfigure(*a, **kw)
            def grid_rowconfigure(self, *a, **kw):    self.inner.grid_rowconfigure(*a, **kw)
            def winfo_children(self):                 return self.inner.winfo_children()
        class CTkTextbox(tk.Text):
            def __init__(self, *a, **kw): super().__init__(*a)
        class CTkFont:
            def __new__(cls, *a, **kw): return ("Courier New", 10)
        class ThemeManager:
            theme = {"CTkLabel": {"text_color": "#e8e8e8"}}
        @staticmethod
        def set_appearance_mode(*a): pass
        @staticmethod
        def set_default_color_theme(*a): pass
    ctk = _CtkStub()

#  hide console 
# ── Last Browse Directory (persisted) ────────────────────────────────────────
_LAST_BROWSE_DIRS: dict = {}

_BROWSE_CACHE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(sys.argv[0])),
    "RE4 MASTER EDITOR", "last_dirs.json"
)

def _load_browse_dirs():
    global _LAST_BROWSE_DIRS
    try:
        if os.path.isfile(_BROWSE_CACHE_FILE):
            with open(_BROWSE_CACHE_FILE, encoding="utf-8") as f:
                _LAST_BROWSE_DIRS = json.load(f)
    except Exception:
        _LAST_BROWSE_DIRS = {}

def _save_browse_dirs():
    try:
        os.makedirs(os.path.dirname(_BROWSE_CACHE_FILE), exist_ok=True)
        with open(_BROWSE_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_LAST_BROWSE_DIRS, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def _browse_open(title="Select File", filetypes=None, key="default",
                 initialdir=None):
    if filetypes is None:
        filetypes = [("All files", "*.*")]
    saved = _LAST_BROWSE_DIRS.get(key, "")
    # only use saved dir if it actually exists — otherwise let OS decide
    if initialdir:
        start_dir = initialdir
    elif saved and os.path.isdir(saved):
        start_dir = saved
    else:
        start_dir = None  # let OS/file manager remember its own last location
    path = filedialog.askopenfilename(
        title=title,
        filetypes=filetypes,
        **({"initialdir": start_dir} if start_dir else {}),
    )
    if path:
        _LAST_BROWSE_DIRS[key] = os.path.dirname(path)
        _save_browse_dirs()
    return path

def _browse_save(title="Save File", filetypes=None, defaultextension="",
                 key="default", initialdir=None):
    if filetypes is None:
        filetypes = [("All files", "*.*")]
    saved = _LAST_BROWSE_DIRS.get(key, "")
    if initialdir:
        start_dir = initialdir
    elif saved and os.path.isdir(saved):
        start_dir = saved
    else:
        start_dir = None
    path = filedialog.asksaveasfilename(
        title=title,
        filetypes=filetypes,
        defaultextension=defaultextension,
        **({"initialdir": start_dir} if start_dir else {}),
    )
    if path:
        _LAST_BROWSE_DIRS[key] = os.path.dirname(path)
        _save_browse_dirs()
    return path


#  root path 
if getattr(sys, "frozen", False):
    _ROOT = os.path.dirname(sys.executable)
else:
    _ROOT = os.path.dirname(os.path.abspath(__file__))

APP_VERSION = "V1.1"
GITHUB_REPO  = "YEMENI-modder/Re4-Master-Editor"
GITHUB_API   = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GITHUB_ZIP   = "RE4.Master.Editor.zip"

MASTER_DIR = os.path.join(_ROOT, "RE4 MASTER EDITOR")

#  master settings 
_MSETTINGS_FILE = os.path.join(MASTER_DIR, "master_settings.json")

def load_master_settings():
    d = {"lang": "en", "remember_exe": True, "last_exe": "", "first_run": True}
    if os.path.isfile(_MSETTINGS_FILE):
        try:
            with open(_MSETTINGS_FILE, encoding="utf-8") as f:
                d.update(json.load(f))
        except Exception:
            pass
    return d

def save_master_settings(s):
    try:
        os.makedirs(os.path.dirname(_MSETTINGS_FILE), exist_ok=True)
        with open(_MSETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

MASTER_SETTINGS = load_master_settings()
_load_browse_dirs()


# 
# SECTION 1: RE4 CODE MANAGER (embedded from main.py)
# 
# The following section contains the full RE4 Code Manager.
# BASE_DIR is overridden to point to RE4 MASTER EDITOR/RE4 CODE MANAGER/


# Override BASE_DIR for master editor context
def _get_base_dir():
    return os.path.join(MASTER_DIR, "RE4 CODE MANAGER")

"""
RE4 Code Manager
=====================
Main application entry point.
Reads code definitions from the_codes/codes_info.json
Reads hex patch data  from the_codes/codes_data.json
"""

# [merged: import sys]
# [merged: import os]
# [merged: import json]
# [merged: import ctypes]
# [merged: import tkinter as tk]
# [merged: from tkinter import filedialog, messagebox]


#  paths 
def _get_base_dir():
    """
    Get the base directory for RE4 Code Manager.
    Always resolves to RE4 MASTER EDITOR/RE4 CODE MANAGER/
    regardless of how the script is run.
    """
    # embedded in master editor → MASTER_DIR is already set globally
    if "MASTER_DIR" in globals() and MASTER_DIR:
        return os.path.join(MASTER_DIR, "RE4 CODE MANAGER")
    # running as EXE
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        if os.path.basename(exe_dir).upper() == "RE4 CODE MANAGER":
            return exe_dir
        return exe_dir
    # running as .py standalone
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR     = _get_base_dir()
CODES_DIR    = os.path.join(BASE_DIR, "the_codes")
INFO_FILE    = os.path.join(CODES_DIR, "codes_info.json")
DATA_FILE    = os.path.join(CODES_DIR, "codes_data.json")
RT_DATA_FILE = os.path.join(CODES_DIR, "codes_data_rt.json")
ORIG_FILE    = os.path.join(CODES_DIR, "bio4_original.exe")
PROFILES_DIR = os.path.join(BASE_DIR, "Profiles")
MOD_DIR      = os.path.join(BASE_DIR, "Modified files")
FILES_DIR    = os.path.join(BASE_DIR, "the_files")
LOG_FILE     = os.path.join(FILES_DIR, "patch_log.txt")

#  language 
CURRENT_LANG = MASTER_SETTINGS.get("lang", "en")  # synced from master settings

def t(ar_text, en_text):
    return en_text if CURRENT_LANG == "en" else ar_text

# Panel name translations (used in nav buttons, sidebar headers, internal labels)
_T_PANELS = {
    "en": {
        "OSD EDITOR":       "OSD EDITOR",
        "CNS EDITOR":       "CNS EDITOR",
        "AEV OPTION":       "AEV OPTION",
        "MDT COLOR":        "MDT COLOR",
        "Lock AEV\nwith Key": "Lock AEV\nwith Key",
        "Scripts":          "Scripts",
        "OSD Editor":       "OSD Editor",
        "CNS Editor":       "CNS Editor",
        "AEV OPTION EDITOR":"AEV OPTION EDITOR",
        "MDT Color Editor": "MDT Color Editor",
        "Lock AEV with Key":"Lock AEV with Key",
    },
    "ar": {
        "OSD EDITOR":       "محرر OSD",
        "CNS EDITOR":       "محرر CNS",
        "AEV OPTION":       "خيارات AEV",
        "MDT COLOR":        "ألوان MDT",
        "Lock AEV\nwith Key": "قفل AEV\nبمفتاح",
        "Scripts":          "سكربتات",
        "OSD Editor":       "محرر OSD",
        "CNS Editor":       "محرر CNS",
        "AEV OPTION EDITOR":"محرر خيارات AEV",
        "MDT Color Editor": "محرر ألوان MDT",
        "Lock AEV with Key":"قفل AEV بمفتاح",
    },
}

def tp(key):
    """Translate panel name based on CURRENT_LANG."""
    return _T_PANELS.get(CURRENT_LANG, _T_PANELS["en"]).get(key, key)


def write_log(action, code_name, exe_path="", details=""):
    """Append a formatted entry to patch_log.txt."""
    from datetime import datetime
    try:
        os.makedirs(FILES_DIR, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write("=" * 60 + "\n")
            f.write(f"Time   : {ts}\n")
            f.write(f"Action : {action}\n")
            f.write(f"Code   : {code_name}\n")
            if exe_path:
                f.write(f"EXE    : {exe_path}\n")
            if details:
                for line in details.strip().splitlines():
                    f.write(f"         {line}\n")
            f.write("\n")
    except Exception:
        pass


def build_log_details(code_id, codes_data, backup=None):
    """Build details string showing offsets and before/after bytes for log."""
    entry = codes_data.get(code_id, {})
    lines = []
    patches = []
    if "variants" in entry:
        for v in entry["variants"].values():
            patches += v.get("patches", [])
    else:
        patches = entry.get("patches", [])

    backup_code = (backup or {}).get(code_id, {})

    for p in patches:
        ptype = p.get("type", "")
        if ptype == "find_replace":
            fb = p.get("find", "")[:32] + ("..." if len(p.get("find","")) > 32 else "")
            rb = p.get("replace", "")[:32] + ("..." if len(p.get("replace","")) > 32 else "")
            lines.append(f"Type   : find_replace")
            lines.append(f"Before : {fb}")
            lines.append(f"After  : {rb}")
        elif ptype in ("offset_paste", "offset_replace"):
            off = p.get("offset", "")
            nb  = p.get("bytes", "")[:32] + ("..." if len(p.get("bytes","")) > 32 else "")
            key = off.upper().lstrip("0") or "0"
            ob  = backup_code.get(key, "")
            lines.append(f"Offset : {off}")
            if ob:
                lines.append(f"Before : {ob}")
            lines.append(f"After  : {nb}")
    return "\n".join(lines)


#  colors 
BG_MAIN    = "#0d0d0d"
BG_PANEL   = "#111111"
BG_SIDEBAR = "#0a0a0a"
BG_ROW     = "#141414"
BG_ROW_ON  = "#0d1a0d"
BG_ROW_LK  = "#0d0d0d"
BG_ROW_SEL = "#1a1a0a"
BG_HEADER  = "#0f0c00"
BG_TOPBAR  = "#0f0c00"
BG_PATHBAR = "#111111"
BG_NOTICE  = "#1a1200"
BG_STATUS  = "#0a0a0a"
BG_APPLY   = "#0a1a0a"

ACCENT     = "#e8c060"
ACCENT2    = "#ffd060"
GREEN      = "#7aff7a"
RED_SOFT   = "#ff9090"
ORANGE     = "#e8b860"
MUTED      = "#888888"
TEXT_MAIN  = "#e0d0b0"
TEXT_DIM   = "#cccccc"
TEXT_LOCK  = "#666666"
BORDER     = "#4a4a2a"
BORDER_ON  = "#3a7a3a"
BORDER_LK  = "#3a2a2a"
BORDER_SEL = "#8a8a3a"

FONT_TITLE  = ("Courier New", 13, "bold")
FONT_NORMAL = ("Courier New", 11)
FONT_SMALL  = ("Courier New", 10)
FONT_TINY   = ("Courier New", 9)
FONT_BOLD   = ("Courier New", 11, "bold")


# 
#  Arabic RTL helper
# 

def fix_ar(text):
    if not text:
        return text
    if not any("\u0600" <= c <= "\u06ff" for c in text):
        return text
    # Manual RTL: reverse word order of Arabic runs, keep EN runs in place
    tokens = re.split(r"([ \t]+)", text)
    runs = []; cur_ar = None; cur = []
    for tok in tokens:
        is_ar = bool(re.search("[\u0600-\u06ff]", tok))
        if is_ar != cur_ar:
            if cur: runs.append((cur_ar, cur))
            cur_ar = is_ar; cur = [tok]
        else:
            cur.append(tok)
    if cur: runs.append((cur_ar, cur))
    runs.reverse()
    parts = []
    for ar, toks in runs:
        chunk = "".join(toks)
        if ar:
            words = chunk.split(" "); words.reverse()
            parts.append(" ".join(words))
        else:
            parts.append(chunk)
    return "".join(parts)


# 
#  Data helpers
# 

def load_json(path):
    if not os.path.exists(path):
        messagebox.showerror("Missing File", "Cannot find:\n" + path)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def scan_exe(path, codes_info, codes_data):
    """
    Scan bio4.exe for ALL codes.
    A code is considered applied only if ALL its patches match.
    For find_replace  -> replace bytes must be present.
    For offset_paste / offset_replace -> bytes at offset must match.
    For numeric_input -> value at offset differs from default_dec.
    """
    results = {}
    try:
        with open(path, "rb") as f:
            exe_bytes = f.read()
    except Exception:
        return results

    for code in codes_info.get("codes", []):
        cid = code["id"]

        # special case: link_tweaks_exe detected by offset 7212FC != "31 2E 30 2E 36"
        if cid == "link_tweaks_exe":
            try:
                off = 0x7212FC
                chunk = exe_bytes[off:off + 5]
                results[cid] = chunk != bytes.fromhex("312E302E36")
            except Exception:
                results[cid] = False
            continue

        data = codes_data.get(cid, {})

        # ── numeric_input: applied if current value ≠ default_dec ──
        if data.get("dialog") == "numeric_input":
            offset_str = data.get("offset", "")
            byte_count = data.get("byte_count", 1)
            default    = data.get("default_dec", None)
            divide_by  = data.get("divide_by", 1)
            if offset_str and default is not None:
                try:
                    off   = int(offset_str, 16)
                    chunk = exe_bytes[off:off + byte_count]
                    val   = int.from_bytes(chunk, byteorder="little") * divide_by
                    results[cid] = (val != default)
                except Exception:
                    results[cid] = False
            else:
                results[cid] = False
            continue

        # get patches (handle variants  check first variant)
        if "variants" in data:
            first_variant = list(data["variants"].values())[0]
            patches = first_variant.get("patches", [])
        else:
            patches = data.get("patches", [])

        if not patches:
            results[cid] = False
            continue

        # check ALL patches  code is applied only if every patch matches
        # scan_bytes: alternative byte values that also count as ON (e.g. rsert_order: E2 or EB)
        scan_alts = data.get("scan_bytes", [])
        all_match = True
        for patch in patches:
            try:
                ptype = patch["type"]
                if ptype == "find_replace":
                    needle = bytes.fromhex(patch["replace"].replace(" ", ""))
                    if needle not in exe_bytes:
                        all_match = False
                        break
                elif ptype in ("offset_paste", "offset_replace"):
                    offset = int(patch["offset"], 16)
                    needle = bytes.fromhex(patch["bytes"].replace(" ", ""))
                    chunk  = exe_bytes[offset:offset + len(needle)]
                    if chunk == needle:
                        continue
                    # check scan_bytes alternatives
                    alt_match = any(
                        exe_bytes[offset:offset + len(bytes.fromhex(a.replace(" ", "")))]
                        == bytes.fromhex(a.replace(" ", ""))
                        for a in scan_alts
                    )
                    if not alt_match:
                        all_match = False
                        break
                else:
                    all_match = False
                    break
            except Exception:
                all_match = False
                break

        results[cid] = all_match

    return results


def _check_game_not_running(exe_path, parent=None):
    """Show error and return True if game is running (caller should abort)."""
    if is_game_running(exe_path):
        msg = (
            "Please close the game before saving changes.\nClose bio4.exe and try again."
            if CURRENT_LANG == "en" else
            "أغلق اللعبة قبل حفظ التعديلات.\nأغلق bio4.exe وحاول مرة ثانية."
        )
        messagebox.showerror(
            "Game is Running" if CURRENT_LANG == "en" else "اللعبة شغالة",
            msg, parent=parent
        )
        return True
    return False

def is_game_running(exe_path):
    """Check if bio4.exe is running. Uses psutil only — no subprocess/CMD."""
    if sys.platform != "win32":
        return False
    exe_name = os.path.basename(exe_path).lower()
    try:
        import psutil
        return any(p.name().lower() == exe_name
                   for p in psutil.process_iter(["name"]))
    except Exception:
        return False


def _friendly_error(e):
    msg = str(e)
    if "13" in msg or "Permission denied" in msg or "Access is denied" in msg:
        return (
            "Permission Denied -- Cannot write to EXE.\n\n"
            "Solutions:\n"
            "1. Run this tool as Administrator (right-click -> Run as administrator)\n"
            "2. Copy bio4.exe to Desktop or Documents and use that copy"
        )
    return msg


BACKUP_FILE   = os.path.join(FILES_DIR, "patch_backup.json")
SETTINGS_FILE = os.path.join(FILES_DIR, "settings.json")

#  settings 
def load_settings():
    defaults = {
        "lang":              "en",
        "silent_apply":      False,
        "last_exe":          "",
        "remember_exe":      True,
        "auto_scan_startup": False,
        "auto_scan_change":  True,
        "real_time_mode":    False,
    }
    if os.path.isfile(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, encoding="utf-8") as f:
                saved = json.load(f)
            defaults.update(saved)
        except Exception:
            pass
    return defaults

# Keys managed only in memory — never written to settings.json
_SETTINGS_VOLATILE = {"last_exe", "remember_exe", "auto_scan_startup",
                      "auto_scan_change"}

def save_settings(settings):
    try:
        os.makedirs(FILES_DIR, exist_ok=True)
        to_save = {k: v for k, v in settings.items() if k not in _SETTINGS_VOLATILE}
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(to_save, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

APP_SETTINGS = load_settings()



def load_patch_backup():
    if os.path.isfile(BACKUP_FILE):
        try:
            with open(BACKUP_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_patch_backup(backup):
    try:
        os.makedirs(FILES_DIR, exist_ok=True)
        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            json.dump(backup, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def apply_patch(exe_path, code_id, codes_data, mod_expansion=None):
    entry = codes_data.get(code_id)
    if not entry:
        return False, "No patch data for '" + code_id + "'"

    try:
        with open(exe_path, "rb") as f:
            exe = bytearray(f.read())
    except Exception as e:
        return False, _friendly_error(e)

    if "variants" in entry:
        patches = list(entry["variants"][
            "with_mod_expansion" if mod_expansion else "without_mod_expansion"
        ]["patches"])
    else:
        patches = list(entry.get("patches", []))

    all_patches = patches + entry.get("shared_patches", [])

    backup = load_patch_backup()
    code_backup = {}

    for patch in all_patches:
        try:
            ptype = patch["type"]
            if ptype == "find_replace":
                find_b    = bytes.fromhex(patch["find"].replace(" ", ""))
                replace_b = bytes.fromhex(patch["replace"].replace(" ", ""))
                idx = exe.find(find_b)
                if idx == -1:
                    return False, "Pattern not found:\n" + patch["find"][:40] + "..."
                exe[idx:idx + len(find_b)] = replace_b
            elif ptype in ("offset_paste", "offset_replace"):
                off    = int(patch["offset"], 16)
                data_b = bytes.fromhex(patch["bytes"].replace(" ", ""))
                key    = patch["offset"].upper().lstrip("0") or "0"
                code_backup[key] = exe[off:off + len(data_b)].hex().upper()
                exe[off:off + len(data_b)] = data_b
        except Exception as e:
            return False, _friendly_error(e)

    backup[code_id] = code_backup
    save_patch_backup(backup)

    try:
        with open(exe_path, "wb") as f:
            f.write(exe)
    except Exception as e:
        return False, _friendly_error(e)

    return True, "OK"


# ── Real-Time Patcher ─────────────────────────────────────────────────────────
# Uses PE section headers to convert file offsets → live RAM addresses,
# then writes bytes directly into the running process via VirtualProtect.

import ctypes as _ctypes
import ctypes.wintypes as _wt

class _IMAGE_DOS_HEADER(_ctypes.Structure):
    _fields_ = [("e_magic",  _wt.WORD), ("e_cblp",   _wt.WORD),
                ("e_cp",     _wt.WORD), ("e_crlc",   _wt.WORD),
                ("e_cparhdr",_wt.WORD), ("e_minalloc",_wt.WORD),
                ("e_maxalloc",_wt.WORD),("e_ss",      _wt.WORD),
                ("e_sp",     _wt.WORD), ("e_csum",    _wt.WORD),
                ("e_ip",     _wt.WORD), ("e_cs",      _wt.WORD),
                ("e_lfarlc", _wt.WORD), ("e_ovno",    _wt.WORD),
                ("e_res",    _wt.WORD * 4), ("e_oemid",_wt.WORD),
                ("e_oeminfo",_wt.WORD), ("e_res2",   _wt.WORD * 10),
                ("e_lfanew", _wt.LONG)]

class _IMAGE_FILE_HEADER(_ctypes.Structure):
    _fields_ = [("Machine",              _wt.WORD),
                ("NumberOfSections",     _wt.WORD),
                ("TimeDateStamp",        _wt.DWORD),
                ("PointerToSymbolTable", _wt.DWORD),
                ("NumberOfSymbols",      _wt.DWORD),
                ("SizeOfOptionalHeader", _wt.WORD),
                ("Characteristics",      _wt.WORD)]

class _IMAGE_OPTIONAL_HEADER32(_ctypes.Structure):
    _fields_ = [("Magic",_wt.WORD),("MajorLinkerVersion",_ctypes.c_ubyte),
                ("MinorLinkerVersion",_ctypes.c_ubyte),("SizeOfCode",_wt.DWORD),
                ("SizeOfInitializedData",_wt.DWORD),("SizeOfUninitializedData",_wt.DWORD),
                ("AddressOfEntryPoint",_wt.DWORD),("BaseOfCode",_wt.DWORD),
                ("BaseOfData",_wt.DWORD),("ImageBase",_wt.DWORD),
                ("SectionAlignment",_wt.DWORD),("FileAlignment",_wt.DWORD),
                ("MajorOperatingSystemVersion",_wt.WORD),("MinorOperatingSystemVersion",_wt.WORD),
                ("MajorImageVersion",_wt.WORD),("MinorImageVersion",_wt.WORD),
                ("MajorSubsystemVersion",_wt.WORD),("MinorSubsystemVersion",_wt.WORD),
                ("Win32VersionValue",_wt.DWORD),("SizeOfImage",_wt.DWORD),
                ("SizeOfHeaders",_wt.DWORD),("CheckSum",_wt.DWORD),
                ("Subsystem",_wt.WORD),("DllCharacteristics",_wt.WORD),
                ("SizeOfStackReserve",_wt.DWORD),("SizeOfStackCommit",_wt.DWORD),
                ("SizeOfHeapReserve",_wt.DWORD),("SizeOfHeapCommit",_wt.DWORD),
                ("LoaderFlags",_wt.DWORD),("NumberOfRvaAndSizes",_wt.DWORD),
                ("DataDirectory", _ctypes.c_byte * 128)]

class _IMAGE_NT_HEADERS(_ctypes.Structure):
    _fields_ = [("Signature",  _wt.DWORD),
                ("FileHeader", _IMAGE_FILE_HEADER),
                ("OptionalHeader", _IMAGE_OPTIONAL_HEADER32)]

class _IMAGE_SECTION_HEADER(_ctypes.Structure):
    _fields_ = [("Name",                 _ctypes.c_char * 8),
                ("VirtualSize",          _wt.DWORD),
                ("VirtualAddress",       _wt.DWORD),
                ("SizeOfRawData",        _wt.DWORD),
                ("PointerToRawData",     _wt.DWORD),
                ("PointerToRelocations", _wt.DWORD),
                ("PointerToLinenumbers", _wt.DWORD),
                ("NumberOfRelocations",  _wt.WORD),
                ("NumberOfLinenumbers",  _wt.WORD),
                ("Characteristics",      _wt.DWORD)]

_RT_TARGET_EXE = "bio4.exe"  # always search by this name in Task Manager

def _rt_get_running_exe_path(pid):
    """Get full disk path of the running process via QueryFullProcessImageName."""
    buf  = (_ctypes.c_char * 1024)()
    size = _wt.DWORD(1024)
    PROCESS_QUERY_LIMITED = 0x1000
    h = _ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED, False, pid)
    if not h:
        return None
    ok = _ctypes.windll.kernel32.QueryFullProcessImageNameA(h, 0, buf, _ctypes.byref(size))
    _ctypes.windll.kernel32.CloseHandle(h)
    if ok and size.value:
        return buf.value.decode("mbcs", errors="ignore")
    return None

def _rt_get_process_handle(exe_path=None):
    """
    Search Task Manager for bio4.exe by name (ignores exe_path).
    Returns (pid, handle) or (None, None).
    """
    target = _RT_TARGET_EXE.lower()
    pid = None

    # Method 1: psutil (fast)
    try:
        import psutil
        for p in psutil.process_iter(["name", "pid"]):
            if p.info["name"].lower() == target:
                pid = p.info["pid"]; break
    except ImportError:
        pass

    # Method 2: Windows CreateToolhelp32Snapshot (no psutil needed)
    if pid is None:
        TH32CS_SNAPPROCESS = 0x00000002
        class PROCESSENTRY32(_ctypes.Structure):
            _fields_ = [("dwSize",              _wt.DWORD),
                        ("cntUsage",            _wt.DWORD),
                        ("th32ProcessID",       _wt.DWORD),
                        ("th32DefaultHeapID",   _ctypes.POINTER(_ctypes.c_ulong)),
                        ("th32ModuleID",        _wt.DWORD),
                        ("cntThreads",          _wt.DWORD),
                        ("th32ParentProcessID", _wt.DWORD),
                        ("pcPriClassBase",      _ctypes.c_long),
                        ("dwFlags",             _wt.DWORD),
                        ("szExeFile",           _ctypes.c_char * 260)]
        snap = _ctypes.windll.kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if snap != _wt.HANDLE(-1).value:
            pe = PROCESSENTRY32(); pe.dwSize = _ctypes.sizeof(PROCESSENTRY32)
            try:
                if _ctypes.windll.kernel32.Process32First(snap, _ctypes.byref(pe)):
                    while True:
                        if pe.szExeFile.lower() == target.encode():
                            pid = pe.th32ProcessID; break
                        if not _ctypes.windll.kernel32.Process32Next(snap, _ctypes.byref(pe)):
                            break
            finally:
                _ctypes.windll.kernel32.CloseHandle(snap)

    if pid is None:
        return None, None
    PROCESS_ALL_ACCESS = 0x1F0FFF
    handle = _ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    return (pid, handle) if handle else (None, None)

def _rt_get_module_base(pid, exe_path):
    """Return base address of the loaded module in the remote process."""
    exe_name = os.path.basename(exe_path).lower().encode()
    TH32CS_SNAPMODULE = 0x00000008
    class MODULEENTRY32(_ctypes.Structure):
        _fields_ = [("dwSize",         _wt.DWORD),
                    ("th32ModuleID",   _wt.DWORD),
                    ("th32ProcessID",  _wt.DWORD),
                    ("GlblcntUsage",   _wt.DWORD),
                    ("ProccntUsage",   _wt.DWORD),
                    ("modBaseAddr",    _ctypes.POINTER(_ctypes.c_byte)),
                    ("modBaseSize",    _wt.DWORD),
                    ("hModule",        _wt.HMODULE),
                    ("szModule",       _ctypes.c_char * 256),
                    ("szExePath",      _ctypes.c_char * 260)]
    snap = _ctypes.windll.kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, pid)
    if snap == _wt.HANDLE(-1).value:
        return None
    me = MODULEENTRY32(); me.dwSize = _ctypes.sizeof(MODULEENTRY32)
    try:
        if _ctypes.windll.kernel32.Module32First(snap, _ctypes.byref(me)):
            while True:
                if me.szModule.lower() == exe_name:
                    base = _ctypes.cast(me.modBaseAddr, _ctypes.c_void_p).value
                    _ctypes.windll.kernel32.CloseHandle(snap)
                    return base
                if not _ctypes.windll.kernel32.Module32Next(snap, _ctypes.byref(me)):
                    break
    finally:
        _ctypes.windll.kernel32.CloseHandle(snap)
    return None

def _rt_file_offset_to_ram(handle, base, file_offset):
    """Convert HxD file offset to live RAM address via PE section headers."""
    dos = _IMAGE_DOS_HEADER()
    bytes_read = _ctypes.c_size_t(0)
    _ctypes.windll.kernel32.ReadProcessMemory(
        handle, _ctypes.c_void_p(base),
        _ctypes.byref(dos), _ctypes.sizeof(dos), _ctypes.byref(bytes_read))
    nt_addr = base + dos.e_lfanew
    nt = _IMAGE_NT_HEADERS()
    _ctypes.windll.kernel32.ReadProcessMemory(
        handle, _ctypes.c_void_p(nt_addr),
        _ctypes.byref(nt), _ctypes.sizeof(nt), _ctypes.byref(bytes_read))
    sec_addr = nt_addr + _ctypes.sizeof(_IMAGE_NT_HEADERS)
    sec_size = _ctypes.sizeof(_IMAGE_SECTION_HEADER)
    for i in range(nt.FileHeader.NumberOfSections):
        sec = _IMAGE_SECTION_HEADER()
        _ctypes.windll.kernel32.ReadProcessMemory(
            handle, _ctypes.c_void_p(sec_addr + i * sec_size),
            _ctypes.byref(sec), sec_size, _ctypes.byref(bytes_read))
        raw_start = sec.PointerToRawData
        raw_end   = raw_start + sec.SizeOfRawData
        if raw_start <= file_offset < raw_end:
            return base + sec.VirtualAddress + (file_offset - raw_start)
    return None

def _rt_patch_memory(handle, address, patch_bytes):
    """VirtualProtect → write → restore protection."""
    PAGE_EXECUTE_READWRITE = 0x40
    size = len(patch_bytes)
    old_prot = _wt.DWORD(0)
    _ctypes.windll.kernel32.VirtualProtectEx(
        handle, _ctypes.c_void_p(address), size,
        PAGE_EXECUTE_READWRITE, _ctypes.byref(old_prot))
    buf = (_ctypes.c_char * size)(*patch_bytes)
    written = _ctypes.c_size_t(0)
    ok = _ctypes.windll.kernel32.WriteProcessMemory(
        handle, _ctypes.c_void_p(address), buf, size, _ctypes.byref(written))
    _ctypes.windll.kernel32.VirtualProtectEx(
        handle, _ctypes.c_void_p(address), size,
        old_prot.value, _ctypes.byref(old_prot))
    return ok and written.value == size

def _rt_read_memory(handle, address, size):
    """Read bytes from live RAM."""
    buf = (_ctypes.c_char * size)()
    read = _ctypes.c_size_t(0)
    _ctypes.windll.kernel32.ReadProcessMemory(
        handle, _ctypes.c_void_p(address), buf, size, _ctypes.byref(read))
    return bytes(buf)

def rt_apply_patch(exe_path, code_id, codes_data):
    """
    Apply patch directly to running process memory.
    Returns (True, saved_originals_dict) or (False, error_str).
    saved_originals_dict: {hex_offset_str: original_bytes_hex}
    """
    pid, handle = _rt_get_process_handle()
    if not pid:
        return False, (
            "bio4.exe not found in Task Manager.\n\n"
            "Make sure the game is running before applying RT patches."
        )
    base = _rt_get_module_base(pid, exe_path)
    if not base:
        _ctypes.windll.kernel32.CloseHandle(handle)
        return False, (
            "Could not read module base address.\n\n"
            "Possible cause: insufficient permissions (try running as Administrator)."
        )

    entry = codes_data.get(code_id, {})
    if "variants" in entry:
        patches = list(entry["variants"].get(
            "without_mod_expansion", entry["variants"].get(
            list(entry["variants"].keys())[0], {})).get("patches", []))
    else:
        patches = list(entry.get("patches", []))
    patches += entry.get("shared_patches", [])

    originals   = {}
    skipped_fr  = []

    try:
        for patch in patches:
            ptype = patch.get("type")
            if ptype in ("offset_paste", "offset_replace"):
                file_off = int(patch["offset"], 16)
                data_b   = bytes.fromhex(patch["bytes"].replace(" ", ""))
                ram_addr = _rt_file_offset_to_ram(handle, base, file_off)
                if not ram_addr:
                    _ctypes.windll.kernel32.CloseHandle(handle)
                    return False, (
                        f"Offset 0x{file_off:08X} is not mapped in any PE section.\n\n"
                        f"The file offset may not belong to a loaded section (.text / .data / .rdata)."
                    )
                # Save original bytes directly from RAM
                orig = _rt_read_memory(handle, ram_addr, len(data_b))
                originals[patch["offset"].upper()] = orig.hex().upper()
                if not _rt_patch_memory(handle, ram_addr, data_b):
                    err_code = _ctypes.windll.kernel32.GetLastError()
                    _ctypes.windll.kernel32.CloseHandle(handle)
                    return False, (
                        f"WriteProcessMemory failed at RAM 0x{ram_addr:08X}\n"
                        f"(file offset 0x{file_off:08X})\n\n"
                        f"Windows error code: {err_code}\n"
                        f"Try running the editor as Administrator."
                    )
            elif ptype == "find_replace":
                skipped_fr.append(patch.get("find", "")[:16])
    except Exception as e:
        _ctypes.windll.kernel32.CloseHandle(handle)
        return False, f"Exception during RT patch:\n{e}"

    _ctypes.windll.kernel32.CloseHandle(handle)

    if not originals and skipped_fr:
        return False, (
            "This code contains find_replace / change_to patches\n"
            "which are not supported in Real-Time mode.\n\n"
            "Switch to Normal Editor Mode to apply this code."
        )

    return True, originals

def rt_revert_patch(exe_path, originals_dict):
    """
    Restore original bytes from originals_dict into running process.
    originals_dict: {hex_offset_str: original_bytes_hex}
    Returns (True, "") or (False, error_str).
    """
    if not originals_dict:
        return True, ""
    pid, handle = _rt_get_process_handle()
    if not pid:
        return False, "bio4.exe not found in Task Manager."
    base = _rt_get_module_base(pid, exe_path)
    if not base:
        _ctypes.windll.kernel32.CloseHandle(handle)
        return False, "Could not read module base address."
    try:
        for off_str, orig_hex in originals_dict.items():
            file_off = int(off_str.lstrip("0") or "0", 16)
            orig_b   = bytes.fromhex(orig_hex)
            ram_addr = _rt_file_offset_to_ram(handle, base, file_off)
            if ram_addr:
                _rt_patch_memory(handle, ram_addr, orig_b)
    except Exception as e:
        _ctypes.windll.kernel32.CloseHandle(handle)
        return False, str(e)
    _ctypes.windll.kernel32.CloseHandle(handle)
    return True, ""

# ── end Real-Time Patcher ──────────────────────────────────────────────────────


def revert_patch(exe_path, orig_path, code_id, codes_data, mod_expansion=None):
    """
    Revert using (priority):
    1. find_replace  -> swap replace->find
    2. offset_*      -> bio4_original.exe (most reliable  true original)
    3. offset_*      -> patch_backup.json fallback (stored at apply time)
    4. offset_replace -> skip if neither available
    5. offset_paste   -> fail if neither available
    Returns (success, message, skipped)
    """
    # special case: link_tweaks_exe uses direct r+b writes  revert from backup
    if code_id == "link_tweaks_exe":
        backup      = load_patch_backup()
        code_backup = backup.get(code_id, {})
        if not code_backup:
            return False, "No backup found for Link Tweaks. Cannot revert.", 0
        try:
            # restore EXE offset 7212FC
            if "7212FC" in code_backup:
                with open(exe_path, "r+b") as f:
                    f.seek(0x7212FC)
                    f.write(bytes.fromhex(code_backup["7212FC"]))
            # restore DLL offset 894054 if backed up
            # (dll path unknown here  skip silently)
            return True, "OK", 0
        except Exception as e:
            return False, str(e), 0

    entry = codes_data.get(code_id)
    if not entry:
        return False, "No patch data for '" + code_id + "'", 0

    try:
        with open(exe_path, "rb") as f:
            exe = bytearray(f.read())
    except Exception as e:
        return False, _friendly_error(e), 0

    orig = None
    if os.path.isfile(orig_path):
        try:
            with open(orig_path, "rb") as f:
                orig = f.read()
        except Exception:
            pass

    backup     = load_patch_backup()
    code_backup = backup.get(code_id, {})

    if "variants" in entry:
        patches = list(entry["variants"][
            "with_mod_expansion" if mod_expansion else "without_mod_expansion"
        ]["patches"])
    else:
        patches = list(entry.get("patches", []))

    skipped = 0
    for patch in patches:
        ptype = patch.get("type", "")
        try:
            if ptype == "find_replace":
                find_b    = bytes.fromhex(patch["find"].replace(" ", ""))
                replace_b = bytes.fromhex(patch["replace"].replace(" ", ""))
                idx = exe.find(replace_b)
                if idx == -1:
                    skipped += 1
                    continue
                exe[idx:idx + len(replace_b)] = find_b

            elif ptype in ("offset_paste", "offset_replace"):
                off    = int(patch["offset"], 16)
                length = len(bytes.fromhex(patch["bytes"].replace(" ", "")))
                key    = patch["offset"].upper().lstrip("0") or "0"

                # 1. bio4_original.exe  الأولوية القصوى (نسخة أصلية مضمونة)
                if orig is not None:
                    chunk = orig[off:off + length]
                    if len(chunk) == length:
                        exe[off:off + length] = chunk
                        continue

                # 2. patch_backup.json  fallback (بايتات مخزّنة وقت التطبيق)
                if key in code_backup:
                    chunk = bytes.fromhex(code_backup[key])
                    if len(chunk) == length:
                        exe[off:off + length] = chunk
                        continue

                # 3. لا يوجد مصدر
                if ptype == "offset_paste":
                    return False, (
                        "Cannot revert at " + patch["offset"] + ".\n"
                        "Place bio4_original.exe in the_codes/ folder."
                    ), skipped
                else:
                    skipped += 1

        except Exception as e:
            return False, str(e), skipped

    try:
        with open(exe_path, "wb") as f:
            f.write(exe)
    except Exception as e:
        return False, _friendly_error(e), skipped

    if code_id in backup:
        del backup[code_id]
        save_patch_backup(backup)

    return True, "OK", skipped


# 
#  Helpers
# 

def make_label(parent, text="", fg=TEXT_MAIN, bg=BG_MAIN,
               font=FONT_SMALL, **kw):
    return tk.Label(parent, text=text, fg=fg, bg=bg, font=font, **kw)


def make_button(parent, text, command, fg=ACCENT, bg="#2a2a1a",
                active_bg="#3a3a2a", font=FONT_SMALL, width=10, **kw):
    return tk.Button(
        parent, text=text, command=command,
        fg=fg, bg=bg,
        activeforeground=fg, activebackground=active_bg,
        font=font, width=width,
        relief="flat", bd=0, cursor="hand2",
        highlightthickness=1, highlightbackground=BORDER,
        **kw
    )


# 
#  ITEM_LIST  — flat list of (hex_str, name) for item pickers in AOE / OSD
#  Built from the same item_hex_ids data used by OSD / AOE editors.
# 
_ITEM_HEX_IDS_RAW = {
    "0x00": "Magnum Ammo",
    "0x01": "Hand Grenade",
    "0x02": "Incendiary Grenade",
    "0x03": "Matilda",
    "0x04": "Handgun Ammo",
    "0x05": "First Aid Spray",
    "0x06": "Green Herb",
    "0x07": "Rifle Ammo",
    "0x08": "Chicken Egg",
    "0x09": "Brown Chicken Egg",
    "0x0A": "Gold Chicken Egg",
    "0x0B": "AAA",
    "0x0C": "Plaga Sample",
    "0x0D": "Krauser's Knife",
    "0x0E": "Flash Grenade",
    "0x0F": "Salazar Family Insignia",
    "0x10": "Bowgun",
    "0x11": "Bowgun Bolts",
    "0x12": "Green Herb x2",
    "0x13": "Green Herb x3",
    "0x14": "Mixed Herbs (G+R)",
    "0x15": "Mixed Herbs (G+R+Y)",
    "0x16": "Mixed Herbs (G+Y)",
    "0x17": "Rocket Launcher (Special)",
    "0x18": "Shotgun Shells",
    "0x19": "Red Herb",
    "0x1A": "Handcannon Ammo",
    "0x1B": "Hourglass w/ Gold Decor",
    "0x1C": "Yellow Herb",
    "0x1D": "Stone Tablet",
    "0x1E": "Lion Ornament",
    "0x1F": "Goat Ornament",
    "0x20": "TMP Ammo",
    "0x21": "Punisher",
    "0x22": "Punisher w/ Silencer",
    "0x23": "Handgun",
    "0x24": "Handgun w/ Silencer",
    "0x25": "Red9",
    "0x26": "Red9 w/ Stock",
    "0x27": "Blacktail",
    "0x28": "Blacktail w/ Silencer",
    "0x29": "Broken Butterfly",
    "0x2A": "Killer7",
    "0x2B": "Killer7 w/ Silencer",
    "0x2C": "Shotgun",
    "0x2D": "Striker",
    "0x2E": "Rifle",
    "0x2F": "Rifle (Semi-Auto)",
    "0x30": "TMP",
    "0x31": "Activation Key (Blue)",
    "0x32": "TMP w/ Stock",
    "0x33": "Activation Key (Red)",
    "0x34": "Chicago Typewriter (Infinite)",
    "0x35": "Rocket Launcher",
    "0x36": "Mine Thrower",
    "0x37": "Handcannon",
    "0x38": "Combat Knife",
    "0x39": "Serpent Ornament",
    "0x3A": "Moonstone (Right Half)",
    "0x3B": "Insignia Key",
    "0x3C": "Round Insignia",
    "0x3D": "False Eye",
    "0x3E": "Custom TMP",
    "0x3F": "Silencer (Handgun)",
    "0x40": "Silencer (???)",
    "0x41": "P.R.L. 412",
    "0x42": "Stock (Red9)",
    "0x43": "Stock (TMP)",
    "0x44": "Scope (Rifle)",
    "0x45": "Scope (Semi-Auto Rifle)",
    "0x46": "Mine-Darts",
    "0x47": "Shotgun (Ada)",
    "0x48": "Capture Luis Sera",
    "0x49": "Target Practice",
    "0x4A": "Luis' Memo",
    "0x4B": "Castellan Memo",
    "0x4C": "Female Intruder",
    "0x4D": "Butler's Memo",
    "0x4E": "Sample Retrieved",
    "0x4F": "Ritual Preparation",
    "0x50": "Luis' Memo 2",
    "0x51": "Rifle (Semi-Auto) w/ Infrared Scope",
    "0x52": "Krauser's Bow",
    "0x53": "Chicago Typewriter (Regular)",
    "0x54": "Treasure Map (Castle)",
    "0x55": "Treasure Map (Island)",
    "0x56": "Velvet Blue",
    "0x57": "Spinel",
    "0x58": "Pearl Pendant",
    "0x59": "Brass Pocket Watch",
    "0x5A": "Elegant Headdress",
    "0x5B": "Antique Pipe",
    "0x5C": "Gold Bangle w/ Pearls",
    "0x5D": "Amber Ring",
    "0x5E": "Beerstein",
    "0x5F": "Green Catseye",
    "0x60": "Red Catseye",
    "0x61": "Yellow Catseye",
    "0x62": "Beerstein w/ (G)",
    "0x63": "Beerstein w/ (R)",
    "0x64": "Beerstein w/ (Y)",
    "0x65": "Beerstein w/ (G,R)",
    "0x66": "Beerstein w/ (G,Y)",
    "0x67": "Beerstein w/ (R,Y)",
    "0x68": "Beerstein w/ (G,R,Y)",
    "0x69": "Moonstone (Left Half)",
    "0x6A": "Chicago Typewriter Ammo",
    "0x6B": "Rifle + Scope",
    "0x6C": "Rifle (Semi-Auto) w/ Scope",
    "0x6D": "Infinite Launcher",
    "0x6E": "King's Grail",
    "0x6F": "Queen's Grail",
    "0x70": "Staff of Royalty",
    "0x71": "Gold Bars",
    "0x72": "Arrows",
    "0x73": "Bonus Time",
    "0x74": "Emergency Lock Card Key",
    "0x75": "Bonus Points",
    "0x76": "Green Catseye (2)",
    "0x77": "Ruby",
    "0x78": "Treasure Box (S)",
    "0x79": "Treasure Box (L)",
    "0x7A": "Blue Moonstone",
    "0x7B": "Key to the Mine",
    "0x7C": "Attache Case S",
    "0x7D": "Attache Case M",
    "0x7E": "Attache Case L",
    "0x7F": "Attache Case XL",
    "0x80": "Golden Sword",
    "0x81": "Iron Key",
    "0x82": "Stone of Sacrifice",
    "0x83": "Storage Room Card Key",
    "0x84": "Freezer Card Key",
    "0x85": "Piece of the Holy Beast, Panther",
    "0x86": "Piece of the Holy Beast, Serpent",
    "0x87": "Piece of the Holy Beast, Eagle",
    "0x88": "Jet-Ski Key",
    "0x89": "Dirty Pearl Pendant",
    "0x8A": "Dirty Brass Pocket Watch",
    "0x8B": "Old Key",
    "0x8C": "Camp Key",
    "0x8D": "Dynamite",
    "0x8E": "Lift Activation Key",
    "0x8F": "Gold Bangle",
    "0x90": "Elegant Perfume Bottle",
    "0x91": "Mirror w/ Pearls & Rubies",
    "0x92": "Waste Disposal Card Key",
    "0x93": "Elegant Chessboard",
    "0x94": "Riot Gun",
    "0x95": "Black Bass",
    "0x96": "Hourglass w/ Gold Decor (2)",
    "0x97": "Black Bass (L)",
    "0x98": "Illuminados Pendant",
    "0x99": "Rifle w/ Infrared Scope",
    "0x9A": "Crown",
    "0x9B": "Crown Jewel",
    "0x9C": "Royal Insignia",
    "0x9D": "Crown with Jewels",
    "0x9E": "Crown with an Insignia",
    "0x9F": "Salazar Family Crown",
    "0xA0": "Rifle Ammo (Infrared)",
    "0xA1": "Emerald",
    "0xA2": "Bottle Caps",
    "0xA3": "Gallery Key",
    "0xA4": "Emblem (Right Half)",
    "0xA5": "Emblem (Left Half)",
    "0xA6": "Hexagonal Emblem",
    "0xA7": "Castle Gate Key",
    "0xA8": "Mixed Herbs (R+Y)",
    "0xA9": "Treasure Map (Village)",
    "0xAA": "Scope (Mine-Thrower)",
    "0xAB": "Mine-Thrower + Scope",
    "0xAC": "Playing Manual 1",
    "0xAD": "Info on Ashley",
    "0xAE": "Playing Manual 2",
    "0xAF": "Alert Order",
    "0xB0": "About the Blue Medallions",
    "0xB1": "Chief's Note",
    "0xB2": "Closure of the Church",
    "0xB3": "Anonymous Letter",
    "0xB4": "Playing Manual 3",
    "0xB5": "Sera and the 3rd Party",
    "0xB6": "Two Routes",
    "0xB7": "Village's Last Defense",
    "0xB8": "Butterfly Lamp",
    "0xB9": "Green Eye",
    "0xBA": "Red Eye",
    "0xBB": "Blue Eye",
    "0xBC": "Butterfly Lamp w/ (G)",
    "0xBD": "Butterfly Lamp w/ (R)",
    "0xBE": "Butterfly Lamp w/ (B)",
    "0xBF": "Butterfly Lamp w/ (G,R)",
    "0xC0": "Butterfly Lamp w/ (G,B)",
    "0xC1": "Butterfly Lamp w/ (R,B)",
    "0xC2": "Butterfly Lamp w/ (R,G,B)",
    "0xC3": "Prison Key",
    "0xC4": "Platinum Sword",
    "0xC5": "Infrared Scope",
    "0xC6": "Elegant Mask",
    "0xC7": "Green Gem",
    "0xC8": "Red Gem",
    "0xC9": "Purple Gem",
    "0xCA": "Elegant Mask w/ (G)",
    "0xCB": "Elegant Mask w/ (R)",
    "0xCC": "Elegant Mask w/ (P)",
    "0xCD": "Elegant Mask w/ (G,R)",
    "0xCE": "Elegant Mask w/ (G,P)",
    "0xCF": "Elegant Mask w/ (R,P)",
    "0xD0": "Elegant Mask w/ (R,G,P)",
    "0xD1": "Golden Lynx",
    "0xD2": "Green Stone of Judgement",
    "0xD3": "Red Stone of Faith",
    "0xD4": "Blue Stone of Treason",
    "0xD5": "Golden Lynx w/ (G)",
    "0xD6": "Golden Lynx w/ (R)",
    "0xD7": "Golden Lynx w/ (B)",
    "0xD8": "Golden Lynx w/ (G,R)",
    "0xD9": "Golden Lynx w/ (G,B)",
    "0xDA": "Golden Lynx w/ (R,B)",
    "0xDB": "Golden Lynx w/ (G,R,B)",
    "0xDC": "Leon w/ Rocket Launcher",
    "0xDD": "Leon w/ Shotgun",
    "0xDE": "Leon w/ Handgun",
    "0xDF": "Ashley Graham",
    "0xE0": "Luis Sera",
    "0xE1": "Don Jose",
    "0xE2": "Don Diego",
    "0xE3": "Don Esteban",
    "0xE4": "Don Manuel",
    "0xE5": "Dr. Salvador",
    "0xE6": "Merchant",
    "0xE7": "Zealot w/ Scythe",
    "0xE8": "Zealot w/ Shield",
    "0xE9": "Zealot w/ Bowgun",
    "0xEA": "Leader Zealot",
    "0xEB": "Soldier w/ Dynamite",
    "0xEC": "Soldier w/ Stun-Rod",
    "0xED": "Soldier w/ Hammer",
    "0xEE": "Isabel",
    "0xEF": "Maria",
    "0xF0": "Ada Wong",
    "0xF1": "Bella Sisters",
    "0xF2": "Don Pedro",
    "0xF3": "J.J.",
    "0xF4": "Letter from Ada",
    "0xF5": "Luis' Memo 3",
    "0xF6": "Paper Airplane",
    "0xF7": "Our Plan",
    "0xF8": "Luis' Memo 4",
    "0xF9": "Krauser's Note",
    "0xFA": "Luis' Memo 5",
    "0xFB": "Our Mission",
    "0xFC": "AAA (FC)",
    "0xFD": "AAA (FD)",
    "0xFE": "Tactical Vest",
    "0xFF": "AAA (FF)",
}
ITEM_LIST = sorted(
    [(k, v) for k, v in _ITEM_HEX_IDS_RAW.items()],
    key=lambda x: int(x[0], 16)
)

def _get_item_list_categorized():
    """Return ITEM_LIST grouped by hex range for use in ItemSelector."""
    cats = {}
    ranges = [
        ("0x00-0x0F: Ammo & Herbs",     range(0x00, 0x10)),
        ("0x10-0x1F: Ammo & Items",     range(0x10, 0x20)),
        ("0x20-0x2F: Handguns",         range(0x20, 0x30)),
        ("0x30-0x3F: Rifles & Others",  range(0x30, 0x40)),
        ("0x40-0x4F: Attachments",      range(0x40, 0x50)),
        ("0x50-0x5F: Treasure",         range(0x50, 0x60)),
        ("0x60-0x6F: Gems & Stones",    range(0x60, 0x70)),
        ("0x70-0x7F: Keys & Cases",     range(0x70, 0x80)),
        ("0x80-0x8F: Stage Keys",       range(0x80, 0x90)),
        ("0x90-0x9F: Stage Keys 2",     range(0x90, 0xA0)),
        ("0xA0-0xAF: Maps & Docs",      range(0xA0, 0xB0)),
        ("0xB0-0xBF: Letters & Lamps",  range(0xB0, 0xC0)),
        ("0xC0-0xCF: Masks & Gems",     range(0xC0, 0xD0)),
        ("0xD0-0xDF: Lynx & Characters",range(0xD0, 0xE0)),
        ("0xE0-0xEF: NPCs",             range(0xE0, 0xF0)),
        ("0xF0-0xFF: Misc",             range(0xF0, 0x100)),
    ]
    for cat_name, rng in ranges:
        items = [nm for hx, nm in ITEM_LIST if int(hx,16) in rng]
        if items:
            cats[cat_name] = items
    return {"categories": cats}


# 
#  CodeRow
# 

class CodeRow(tk.Frame):
    def __init__(self, parent, code, app, **kw):
        super().__init__(parent, bg=BG_ROW,
                         highlightthickness=1,
                         highlightbackground=BORDER, **kw)
        self.code      = code
        self.app       = app
        self._expanded = False
        self.selected  = False
        self._build()

    def _get_name(self):
        if CURRENT_LANG == "en":
            return self.code.get("name_en", self.code["name"])
        return self.code["name"]

    def _get_desc(self):
        if CURRENT_LANG == "en":
            return self.code.get("desc_en", self.code.get("desc", ""))
        return fix_ar(self.code.get("desc", ""))

    def _get_notes(self):
        if CURRENT_LANG == "en":
            return self.code.get("notes_en", [])
        return self.code.get("notes", [])

    def _build(self):
        top = tk.Frame(self, bg=BG_ROW)
        top.pack(fill="x", padx=6, pady=4)

        is_numeric  = self.code.get("dialog") == "numeric_input"
        is_num_tog  = self.code.get("dialog") == "numeric_with_toggle"
        is_dropdown = self.code.get("dialog") in (
            "dropdown", "punisher_pierce", "luis_cabin",
            "link_tweaks", "memory_alloc"
        )
        # punisher_pierce uses Change button but NOT inline numeric
        if self.code.get("dialog") == "punisher_pierce":
            is_numeric = False

        #  checkbox (queue for Apply Selected) 
        self.sel_var = tk.IntVar(value=0)
        self.sel_chk = tk.Checkbutton(
            top, variable=self.sel_var,
            bg=BG_ROW, activebackground=BG_ROW,
            fg=ACCENT, selectcolor="#1a1a1a",
            relief="flat", bd=0,
            command=self._on_select
        )
        if not is_numeric and not is_dropdown and not is_num_tog:
            self.sel_chk.pack(side="left", padx=(0, 2))

        #  ON/OFF toggle OR Change button 
        if is_dropdown:
            self.toggle_btn = tk.Button(
                top, text="Change", width=7, font=FONT_TINY,
                fg=ACCENT2, bg="#1a1a2a",
                activeforeground=ACCENT2, activebackground="#22223a",
                relief="flat", bd=0,
                highlightthickness=1, highlightbackground="#445",
                cursor="hand2",
                command=self._on_toggle
            )
            self.toggle_btn.pack(side="left", padx=(0, 6))
        elif is_num_tog or is_numeric:
            self.toggle_btn = tk.Button(top, text="", width=0)  # hidden placeholder
        else:
            self.toggle_btn = tk.Button(
                top, text="OFF", width=5, font=FONT_TINY,
                fg="#bbbbbb", bg="#1a1a1a",
                activeforeground="#bbbbbb", activebackground="#222",
                relief="flat", bd=0,
                highlightthickness=1, highlightbackground="#888",
                cursor="hand2",
                command=self._on_toggle
            )
            self.toggle_btn.pack(side="left", padx=(0, 6))

        #  status badge [L] / blank 
        self.status_var = tk.StringVar(value="")
        self.status_lbl = tk.Label(
            top, textvariable=self.status_var,
            font=FONT_SMALL, fg="#c85a2a", bg=BG_ROW, width=3,
            anchor="center"
        )
        if not is_numeric and not is_num_tog:
            self.status_lbl.pack(side="left", padx=(0, 4))

        #  name + desc 
        info_frame = tk.Frame(top, bg=BG_ROW)
        info_frame.pack(side="left", fill="x", expand=True)

        self.name_lbl = tk.Label(
            info_frame, text=self._get_name(),
            font=FONT_NORMAL, fg="#f0e0c0", bg=BG_ROW,
            anchor="w", justify="left"
        )
        self.name_lbl.pack(anchor="w")

        self.desc_lbl = tk.Label(
            info_frame, text=self._get_desc(),
            font=FONT_TINY, fg="#cccccc", bg=BG_ROW,
            anchor="w", justify="left", wraplength=400
        )
        self.desc_lbl.pack(anchor="w")

        notes = self._get_notes()

        #  inline numeric input (replaces ON/OFF for numeric_input codes) 
        if is_numeric:
            num_frame = tk.Frame(top, bg=BG_ROW)
            num_frame.pack(side="right", padx=(4, 0))

            entry_data = self.app.codes_data.get(self.code["id"], {})
            default    = entry_data.get("default_dec", 0)
            current = getattr(self.app, "_numeric_current", {}).get(self.code["id"], None)
            init_val = current if current is not None else default

            self._num_var = tk.StringVar(value=str(init_val))

            num_entry = tk.Entry(
                num_frame, textvariable=self._num_var,
                font=FONT_SMALL, fg=ACCENT2, bg="#1a1a1a",
                insertbackground=ACCENT2,
                relief="flat", bd=0,
                highlightthickness=1, highlightbackground=BORDER,
                width=7, justify="center"
            )
            num_entry.pack(side="left", ipady=3, padx=(0, 4))
            self.app._add_paste_menu(num_entry)

            tk.Button(
                num_frame, text="Apply",
                font=FONT_TINY, fg=GREEN, bg="#1a2a0a",
                activeforeground=GREEN, activebackground="#2a4a1a",
                relief="flat", bd=0, cursor="hand2",
                highlightthickness=1, highlightbackground="#2a5a2a",
                command=self._on_numeric_apply
            ).pack(side="left", padx=(0, 2), ipady=2, ipadx=4)

        #  numeric_with_toggle: ON/OFF + field + Apply 
        elif is_num_tog:
            entry_data = self.app.codes_data.get(self.code["id"], {})
            default    = entry_data.get("default_dec", 0)
            current    = getattr(self.app, "_numeric_current", {}).get(self.code["id"], None)
            init_val   = current if current is not None else default
            is_applied = self.app.applied.get(self.code["id"], False)

            self._num_var = tk.StringVar(value=str(init_val))

            # ON/OFF toggle
            self.toggle_btn = tk.Button(
                top, text="ON" if is_applied else "OFF", width=5, font=FONT_TINY,
                fg=GREEN if is_applied else "#bbbbbb",
                bg="#2a5a2a" if is_applied else "#1a1a1a",
                activeforeground=GREEN, activebackground="#2a4a1a",
                relief="flat", bd=0,
                highlightthickness=1,
                highlightbackground=GREEN if is_applied else "#888",
                cursor="hand2",
                command=self._on_toggle
            )
            self.toggle_btn.pack(side="left", padx=(0, 6))

            # field + Apply on right
            num_frame = tk.Frame(top, bg=BG_ROW)
            num_frame.pack(side="right", padx=(4, 0))

            num_entry = tk.Entry(
                num_frame, textvariable=self._num_var,
                font=FONT_SMALL, fg=ACCENT2 if is_applied else MUTED,
                bg="#1a1a1a", insertbackground=ACCENT2,
                relief="flat", bd=0,
                highlightthickness=1, highlightbackground=BORDER,
                width=7, justify="center",
                state="normal" if is_applied else "disabled"
            )
            num_entry.pack(side="left", ipady=3, padx=(0, 4))
            self.app._add_paste_menu(num_entry)
            self._num_entry_ref = num_entry  # save ref for refresh

            tk.Button(
                num_frame, text="Apply",
                font=FONT_TINY, fg=GREEN, bg="#1a2a0a",
                activeforeground=GREEN, activebackground="#2a4a1a",
                relief="flat", bd=0, cursor="hand2",
                highlightthickness=1, highlightbackground="#2a5a2a",
                command=self._on_numeric_apply
            ).pack(side="left", padx=(0, 2), ipady=2, ipadx=4)

        #  expand arrow (only if notes) 
        if notes:
            self.arrow_btn = tk.Button(
                top, text="\u25bc", width=3, font=FONT_SMALL,
                fg=ACCENT, bg=BG_ROW,
                activeforeground=ACCENT2, activebackground=BG_ROW,
                relief="flat", bd=0, cursor="hand2",
                command=self._toggle_notes
            )
            self.arrow_btn.pack(side="right", padx=4)

        #  Permanent Activation checkbox (RT mode only) 
        self.perm_var = tk.BooleanVar(value=False)
        self.perm_chk = tk.Checkbutton(
            top,
            text=t("تفعيل دائم", "Permanent"),
            variable=self.perm_var,
            font=("Courier New", 7),
            fg="#c8a035", bg=BG_ROW,
            activeforeground="#c8a035", activebackground=BG_ROW,
            selectcolor="#1a1400",
            relief="flat", bd=0, cursor="hand2",
            highlightthickness=0,
        )
        if APP_SETTINGS.get("real_time_mode", False):
            self.perm_chk.pack(side="left", padx=(2, 0))

        #  notes frame 
        self.notes_frame = tk.Frame(self, bg="#0d0d00")
        for note in notes:
            txt = note if CURRENT_LANG == "en" else fix_ar(note)
            tk.Label(
                self.notes_frame, text=txt,
                font=FONT_TINY, fg="#ffcc66", bg="#0d0d00",
                anchor="w", justify="left"
            ).pack(anchor="w", padx=8, pady=1)

    def _on_numeric_apply(self):
        """Called when Apply button is pressed on an inline numeric input code."""
        code_id = self.code["id"]

        # check if any active code has this code in its mutex list
        for other_id, conflicts in self.app.OFFSET_MUTEX.items():
            if code_id in conflicts and self.app.applied.get(other_id, False):
                other_name = self.app.code_by_id.get(other_id, {}).get(
                    "name_en" if CURRENT_LANG == "en" else "name", other_id)
                messagebox.showwarning(
                    "Code Locked" if CURRENT_LANG == "en" else "الكود مقفل",
                    ("This code is disabled while '" + other_name + "' is ON.\n"
                     "Turn it OFF first.")
                    if CURRENT_LANG == "en" else
                    ("هذا الكود مقفل لأن '" + other_name + "' شغال.\n"
                     "أطفيه أول.")
                )
                return

        if not self.app._is_unlocked(code_id):
            missing = self.app._get_missing_requires(code_id)
            if missing:
                msg = ("You need to enable the following codes first:\n\n"
                       if CURRENT_LANG == "en" else
                       "لازم تشغل الأكواد التالية أول:\n\n")
                for dep_id, dep_name, sec_label in missing:
                    msg += "  - " + dep_name + "\n"
                    msg += ("    (Found in: " + sec_label + ")\n"
                            if CURRENT_LANG == "en" else
                            "    (تجده في قسم: " + sec_label + ")\n")
                messagebox.showwarning(
                    "Code Locked" if CURRENT_LANG == "en" else "الكود مقفل", msg)
            return
        # for numeric_with_toggle: only apply value if code is ON
        if self.code.get("dialog") == "numeric_with_toggle":
            if not self.app.applied.get(code_id, False):
                messagebox.showwarning(
                    "Code is OFF" if CURRENT_LANG == "en" else "الكود طافي",
                    "Turn ON the code first before setting a value."
                    if CURRENT_LANG == "en" else
                    "شغّل الكود أولاً قبل ما تحدد القيمة."
                )
                return
        offset     = entry_data.get("offset", "")
        byte_count = entry_data.get("byte_count", 1)
        divide_by  = entry_data.get("divide_by", 1)
        try:
            dec_val = int(self._num_var.get().strip())
            if dec_val < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number.")
            return
        actual_val = dec_val // divide_by if divide_by > 1 else dec_val
        hex_bytes  = actual_val.to_bytes(byte_count, byteorder="little").hex().upper()

        # apply any prerequisite patches (e.g. ON patch for random_ptas)
        patches = entry_data.get("patches", [])
        if patches:
            ok, msg = apply_patch(exe, code_id, self.app.codes_data)
            if not ok:
                messagebox.showerror("Error", msg)
                return

        try:
            with open(exe, "r+b") as f:
                off = int(offset, 16)
                f.seek(off)
                orig = f.read(byte_count)
                backup = load_patch_backup()
                backup.setdefault(code_id, {})[offset.upper().lstrip("0") or "0"] = orig.hex().upper()
                save_patch_backup(backup)
                f.seek(off)
                f.write(bytes.fromhex(hex_bytes))
        except Exception as ex:
            messagebox.showerror("Error", str(ex))
            return
        self.app.applied[code_id] = True
        name = self.code.get("name_en" if CURRENT_LANG == "en" else "name", code_id)
        write_log("APPLIED", name + " = " + str(dec_val), exe)
        if not APP_SETTINGS.get("silent_apply", False):
            messagebox.showinfo("[+] Applied", name + "\nValue: " + str(dec_val))
        self.app._after_state_change()

    def _toggle_notes(self):
        self._expanded = not self._expanded
        if self._expanded:
            self.notes_frame.pack(fill="x")
            self.arrow_btn.configure(text="\u25b2")
        else:
            self.notes_frame.pack_forget()
            self.arrow_btn.configure(text="\u25bc")

    def _on_toggle(self):
        self.app.handle_toggle(self.code["id"])

    def _on_select(self):
        if self.sel_var.get() == 1 and not self.app._is_unlocked(self.code["id"]):
            self.sel_var.set(0)
            self.app.handle_toggle(self.code["id"])
            return
        self.selected = bool(self.sel_var.get())
        # sync with global selection
        if self.selected:
            self.app._global_selected.add(self.code["id"])
        else:
            self.app._global_selected.discard(self.code["id"])
        self.app.on_row_select_change()

    def refresh(self, applied, locked, detected):
        if detected and not applied:
            applied = True

        is_numeric  = self.code.get("dialog") == "numeric_input"
        is_dropdown = self.code.get("dialog") in (
            "dropdown", "punisher_pierce", "luis_cabin",
            "link_tweaks", "memory_alloc"
        )
        # punisher_pierce uses Change button but NOT inline numeric
        if self.code.get("dialog") == "punisher_pierce":
            is_numeric = False

        # for numeric codes: check if any active code blocks this one
        mutex_locked = False
        if is_numeric:
            for other_id, conflicts in self.app.OFFSET_MUTEX.items():
                if self.code["id"] in conflicts and self.app.applied.get(other_id, False):
                    mutex_locked = True
                    break

        has_arrow = hasattr(self, "arrow_btn")
        has_num   = hasattr(self, "_num_var")

        #  dropdown (Change button) 
        if is_dropdown:
            if applied:
                bg = BG_ROW_ON
                self.configure(bg=bg, highlightbackground=BORDER_ON)
                self.toggle_btn.configure(
                    text="Change", fg=GREEN, bg="#2a5a2a",
                    highlightbackground=GREEN, state="normal"
                )
                self.name_lbl.configure(fg="#e8e0c0", bg=bg, font=FONT_BOLD)
                self.desc_lbl.configure(bg=bg)
            else:
                bg = BG_ROW
                self.configure(bg=bg, highlightbackground=BORDER)
                self.toggle_btn.configure(
                    text="Change", fg=ACCENT2, bg="#1a1a2a",
                    highlightbackground="#445", state="normal"
                )
                self.name_lbl.configure(fg=TEXT_MAIN, bg=bg, font=FONT_NORMAL)
                self.desc_lbl.configure(bg=bg)
            self.status_lbl.configure(bg=bg)
            if has_arrow:
                self.arrow_btn.configure(bg=bg, activebackground=bg)
            return

        is_num_tog  = self.code.get("dialog") == "numeric_with_toggle"

        # update numeric field state
        if has_num and not is_num_tog:
            if mutex_locked:
                self.configure(bg=BG_ROW_LK, highlightbackground=BORDER_LK)
                self.name_lbl.configure(fg=TEXT_LOCK, bg=BG_ROW_LK)
                self.desc_lbl.configure(bg=BG_ROW_LK)
                if has_arrow:
                    self.arrow_btn.configure(bg=BG_ROW_LK, activebackground=BG_ROW_LK)
            else:
                bg = BG_ROW
                self.configure(bg=bg, highlightbackground=BORDER)
                self.name_lbl.configure(fg="#f0e0c0", bg=bg, font=FONT_NORMAL)
                self.desc_lbl.configure(bg=bg)
                if has_arrow:
                    self.arrow_btn.configure(bg=bg, activebackground=bg)
            return

        # numeric_with_toggle: update ON/OFF button + field enable state
        if has_num and is_num_tog:
            bg = BG_ROW_ON if applied else BG_ROW
            self.configure(bg=bg, highlightbackground=BORDER_ON if applied else BORDER)
            self.toggle_btn.configure(
                text="ON" if applied else "OFF",
                fg=GREEN if applied else "#bbbbbb",
                bg="#2a5a2a" if applied else "#1a1a1a",
                highlightbackground=GREEN if applied else "#555"
            )
            self.name_lbl.configure(fg="#e8e0c0" if applied else TEXT_MAIN,
                                    bg=bg, font=FONT_BOLD if applied else FONT_NORMAL)
            self.desc_lbl.configure(bg=bg)
            if has_arrow:
                self.arrow_btn.configure(bg=bg, activebackground=bg)
            if hasattr(self, "_num_entry_ref"):
                self._num_entry_ref.configure(
                    state="normal" if applied else "disabled",
                    fg=ACCENT2 if applied else MUTED
                )
            return

        # checkbox: disabled if locked or already applied
        if locked or applied:
            self.sel_chk.configure(state="disabled")
            self.sel_var.set(0)
            self.selected = False
        else:
            self.sel_chk.configure(state="normal")

        if locked and applied:
            bg = "#0d1a0a"
            self.configure(bg=bg, highlightbackground="#1a4a1a")
            self.toggle_btn.configure(
                text="ON", fg="#3a9a3a", bg="#1a2a1a",
                highlightbackground="#2a5a2a", state="normal"
            )
            self.status_var.set("[L]")
            self.status_lbl.configure(fg="#c85a2a", bg=bg)
            self.name_lbl.configure(fg="#a0c0a0", bg=bg, font=FONT_BOLD)
            self.desc_lbl.configure(bg=bg)
            self.sel_chk.configure(bg=bg, activebackground=bg)
            if has_arrow:
                self.arrow_btn.configure(bg=bg, activebackground=bg)

        elif locked:
            bg = BG_ROW_LK
            self.configure(bg=bg, highlightbackground=BORDER_LK)
            self.toggle_btn.configure(
                text="OFF", fg=TEXT_LOCK, bg="#1a1a1a",
                highlightbackground="#333", state="normal"
            )
            self.status_var.set("[L]")
            self.status_lbl.configure(fg="#c85a2a", bg=bg)
            self.name_lbl.configure(fg=TEXT_LOCK, bg=bg, font=FONT_NORMAL)
            self.desc_lbl.configure(bg=bg)
            self.sel_chk.configure(bg=bg, activebackground=bg)
            if has_arrow:
                self.arrow_btn.configure(bg=bg, activebackground=bg)
            self.notes_frame.configure(bg="#0d0d00")

        elif applied:
            bg = BG_ROW_ON
            self.configure(bg=bg, highlightbackground=BORDER_ON)
            self.toggle_btn.configure(
                text="ON", fg=GREEN, bg="#2a5a2a",
                highlightbackground=GREEN, state="normal"
            )
            self.status_var.set("")
            self.status_lbl.configure(fg=MUTED, bg=bg)
            self.name_lbl.configure(fg="#e8e0c0", bg=bg, font=FONT_BOLD)
            self.desc_lbl.configure(bg=bg)
            self.sel_chk.configure(bg=bg, activebackground=bg)
            if has_arrow:
                self.arrow_btn.configure(bg=bg, activebackground=bg)

        else:
            bg = BG_ROW_SEL if self.selected else BG_ROW
            border = BORDER_SEL if self.selected else BORDER
            self.configure(bg=bg, highlightbackground=border)
            self.toggle_btn.configure(
                text="OFF", fg=MUTED, bg="#1a1a1a",
                highlightbackground="#444", state="normal"
            )
            self.status_var.set("")
            self.status_lbl.configure(fg=MUTED, bg=bg)
            self.name_lbl.configure(fg=TEXT_MAIN, bg=bg, font=FONT_NORMAL)
            self.desc_lbl.configure(bg=bg)
            self.sel_chk.configure(bg=bg, activebackground=bg)
            if has_arrow:
                self.arrow_btn.configure(bg=bg, activebackground=bg)


# 
#  SidebarItem
# 

class SidebarItem(tk.Frame):
    def __init__(self, parent, section, app, **kw):
        super().__init__(parent, bg=BG_SIDEBAR, **kw)
        self.section = section
        self.app     = app

        self.indicator = tk.Frame(self, bg=BG_SIDEBAR, width=3)
        self.indicator.pack(side="left", fill="y")

        label = section.get("label_en", section["label"]) if CURRENT_LANG == "en" else section["label"]
        self.btn = tk.Button(
            self, text=label,
            font=FONT_SMALL, fg="#cccccc", bg=BG_SIDEBAR,
            activeforeground=ACCENT2, activebackground="#1a1200",
            anchor="w", relief="flat", bd=0, cursor="hand2",
            command=lambda: app.select_section(section["id"])
        )
        self.btn.pack(side="left", fill="x", expand=True, ipady=6)

    def set_active(self, active):
        if active:
            self.btn.configure(fg=ACCENT2, bg="#1a1200",
                               activebackground="#1a1200")
            self.indicator.configure(bg=ACCENT)
        else:
            self.btn.configure(fg="#cccccc", bg=BG_SIDEBAR,
                               activebackground="#1a1200")
            self.indicator.configure(bg=BG_SIDEBAR)


# 
#  Main App
# 

class RE4PatcherApp(tk.Frame):
    """
    RE4 Code Manager.
    Can run embedded inside RE4MasterEditor (master != None)
    or standalone (master == None, creates its own Tk root).
    """

    def __init__(self, master=None, embedded=False, shared_exe_var=None):
        global CURRENT_LANG
        CURRENT_LANG = MASTER_SETTINGS.get("lang", APP_SETTINGS.get("lang", "en"))

        if embedded and master is not None:
            # embedded mode  runs as Frame inside master
            super().__init__(master, bg=BG_MAIN)
            self.exe_path = shared_exe_var if shared_exe_var else tk.StringVar()
            self._embedded = True
        else:
            # standalone mode  create a Tk root
            self._root = tk.Tk()
            self._root.title("RE4 Code Manager")
            self._root.geometry("1000x680")
            self._root.minsize(820, 560)
            self._root.configure(bg=BG_MAIN)
            super().__init__(self._root, bg=BG_MAIN)
            self.pack(fill="both", expand=True)
            self.exe_path = tk.StringVar()
            self._embedded = False

        self.scanned          = False
        self.detected         = {}
        self.applied          = {}
        self._rt_originals    = {}  # RT mode: {code_id: {offset: orig_hex}}
        self.active_section   = None
        self._global_selected = set()

        self.codes_info = load_json(INFO_FILE)
        _data_file = RT_DATA_FILE if APP_SETTINGS.get("real_time_mode", False) and os.path.isfile(RT_DATA_FILE) else DATA_FILE
        self.codes_data = load_json(_data_file)

        # spawn_enemies: scan must recognise both Mr.Curious (50) and Leo Lima (4F) at 002B5848
        if "spawn_enemies" in self.codes_data:
            se = self.codes_data["spawn_enemies"]
            # Build the two full-patch byte strings and add as scan_bytes alternatives
            _base = "B9 01 00 00 00 83 7D CC 00 74 1C 52 56 8B 75 CC 8B 56"
            _tail = "83 FA 00 74 03 89 55 E0 8B 56 54 83 FA 00 74 02 8B C2 5E 5A E9 49 FD FF FF"
            se["scan_bytes"] = [
                f"{_base} 50 {_tail}",   # Mr.Curious
                f"{_base} 4F {_tail}",   # Leo Lima
            ]
            # Ensure patches list has the canonical offset_paste entry for scan
            if not se.get("patches"):
                se["patches"] = [{
                    "type": "offset_paste",
                    "offset": "002B5848",
                    "bytes": f"{_base} 50 {_tail}",
                }]

        self.sections_list    = self.codes_info["sections"]
        self.all_codes        = self.codes_info["codes"]
        self.code_by_id       = {c["id"]: c for c in self.all_codes}
        self.codes_by_section = {}
        for c in self.all_codes:
            self.codes_by_section.setdefault(c["section"], []).append(c)

        self._build_ui()
        self.select_section(self.sections_list[0]["id"])
        self.status_total_var.set(
            ("Total codes: " if CURRENT_LANG == "en" else "إجمالي الأكواد: ")
            + str(len(self.all_codes))
        )

        if not embedded:
            if APP_SETTINGS.get("remember_exe", True):
                last = APP_SETTINGS.get("last_exe", "")
                if last and os.path.isfile(last):
                    self.exe_path.set(last)
                    if APP_SETTINGS.get("auto_scan_startup", False):
                        self._root.after(300, self._scan)

        self._first_scan_done = False
        self.exe_path.trace_add("write", self._on_exe_path_change)

    def mainloop(self):
        """Run standalone."""
        if not self._embedded:
            self._root.mainloop()

    #  UI 

    def _build_ui(self):
        # top bar
        topbar = tk.Frame(self, bg=BG_TOPBAR)
        topbar.pack(fill="x")
        make_label(topbar, "RE4 Code Manager",
                   fg=ACCENT2, bg=BG_TOPBAR, font=FONT_TITLE
                   ).pack(side="left", padx=14, pady=6)
        make_button(topbar, t("الإعدادات","Settings"), self._open_settings,
                    fg=ACCENT, bg=BG_TOPBAR, active_bg="#1a1200",
                    font=FONT_TINY, width=8
                    ).pack(side="right", padx=4)

        rt_on = APP_SETTINGS.get("real_time_mode", False)
        self._mode_indicator = tk.Label(
            topbar,
            text="⚡ RT" if rt_on else "📄 Normal",
            fg="#ff9060" if rt_on else "#555555",
            bg=BG_TOPBAR,
            font=("Courier New", 8, "bold"),
            cursor="hand2"
        )
        self._mode_indicator.pack(side="right", padx=(0, 6))
        self._mode_indicator.bind("<Button-1>", lambda e: self._open_settings())

        # exe path row (hidden when embedded  master provides exe path)
        path_bar = tk.Frame(self, bg=BG_PATHBAR)
        self.path_bar = path_bar
        if not self._embedded:
            path_bar.pack(fill="x")
        else:
            # embedded: show compact scan-only bar
            scan_bar = tk.Frame(self, bg="#0e0e0e")
            scan_bar.pack(fill="x")

            self.scan_btn = make_button(
                scan_bar, t("فحص EXE","Scan EXE"), self._scan,
                fg=GREEN, bg="#1a2a0a", active_bg="#2a4a1a", width=9
            )
            self.scan_btn.pack(side="left", padx=10, pady=6)

            self.scan_status_var = tk.StringVar(value="")
            make_label(scan_bar, fg=GREEN, bg="#0e0e0e", font=FONT_TINY,
                       textvariable=self.scan_status_var
                       ).pack(side="left", padx=8)
        make_label(path_bar, "Game Executable (bio4.exe):",
                   fg=TEXT_DIM, bg=BG_PATHBAR
                   ).pack(side="left", padx=(12, 6), pady=5)
        self.path_entry = tk.Entry(
            path_bar, textvariable=self.exe_path,
            font=FONT_SMALL, fg="#7cfc7c", bg="#0d1a0d",
            insertbackground="#7cfc7c",
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground="#2a5a2a",
            width=48
        )
        self.path_entry.pack(side="left", pady=5, ipady=3)
        self._add_paste_menu(self.path_entry)

        # notice bar
        self.notice = tk.Frame(self, bg=BG_NOTICE)
        make_label(
            self.notice,
            fix_ar("[!] حط مسار bio4.exe واضغط Scan عشان تشوف وتفعل الاكواد")
            if CURRENT_LANG == "ar" else
            "[!] Select bio4.exe path and press Scan EXE to view and apply codes",
            fg=ACCENT, bg=BG_NOTICE
        ).pack(side="left", padx=10, pady=4)
        self.notice.pack(fill="x")

        # main body
        body = tk.Frame(self, bg=BG_MAIN)
        body.pack(fill="both", expand=True)

        # sidebar
        sidebar_outer = tk.Frame(body, bg=BG_SIDEBAR, width=210)
        sidebar_outer.pack(side="left", fill="y")
        sidebar_outer.pack_propagate(False)

        sb_canvas = tk.Canvas(sidebar_outer, bg=BG_SIDEBAR,
                              highlightthickness=0, width=210)
        sb_scroll = tk.Scrollbar(sidebar_outer, orient="vertical",
                                 command=sb_canvas.yview)
        sb_canvas.configure(yscrollcommand=sb_scroll.set)
        sb_scroll.pack(side="right", fill="y")
        sb_canvas.pack(side="left", fill="both", expand=True)

        self.sidebar_inner = tk.Frame(sb_canvas, bg=BG_SIDEBAR)
        sb_canvas.create_window((0, 0), window=self.sidebar_inner, anchor="nw")
        self.sidebar_inner.bind(
            "<Configure>",
            lambda e: sb_canvas.configure(
                scrollregion=sb_canvas.bbox("all"))
        )

        self.sidebar_items = {}
        for sec in self.sections_list:
            item = SidebarItem(self.sidebar_inner, sec, self)
            item.pack(fill="x")
            self.sidebar_items[sec["id"]] = item

        # right panel
        right = tk.Frame(body, bg=BG_PANEL)
        right.pack(side="left", fill="both", expand=True)

        # section header
        sec_header = tk.Frame(right, bg=BG_HEADER)
        sec_header.pack(fill="x")
        self.section_title_var = tk.StringVar(value="")
        make_label(sec_header, fg=ACCENT2, bg=BG_HEADER,
                   font=("Courier New", 14, "bold"),
                   textvariable=self.section_title_var
                   ).pack(side="left", padx=14, pady=6)
        self.section_count_var = tk.StringVar(value="")
        make_label(sec_header, fg=MUTED, bg=BG_HEADER, font=FONT_TINY,
                   textvariable=self.section_count_var
                   ).pack(side="left", pady=6)

        # search bar
        search_bar = tk.Frame(right, bg=BG_PATHBAR)
        search_bar.pack(fill="x", padx=10, pady=(6, 0))
        make_label(search_bar, text=t("بحث:","Search:"), fg=TEXT_DIM, bg=BG_PATHBAR,
                   font=FONT_TINY).pack(side="left", padx=(0, 6))
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_bar, textvariable=self.search_var,
            font=FONT_SMALL, fg=ACCENT2, bg="#1a1a1a",
            insertbackground=ACCENT2,
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground=BORDER,
            width=30
        )
        self.search_entry.pack(side="left", ipady=3)
        self.search_var.trace_add("write", lambda *_: self._on_search())
        make_button(search_bar, "X", self._clear_search,
                    fg=MUTED, bg="#1a1a1a", active_bg="#2a2a2a",
                    font=FONT_TINY, width=2
                    ).pack(side="left", padx=4)

        # search results frame (hidden by default)  with scrollable canvas
        self.search_results_outer = tk.Frame(right, bg="#0d0d1a",
                                             highlightthickness=1,
                                             highlightbackground="#2a2a5a")
        self.search_results_canvas = tk.Canvas(self.search_results_outer,
                                               bg="#0d0d1a", highlightthickness=0,
                                               height=180)
        sr_scroll = tk.Scrollbar(self.search_results_outer, orient="vertical",
                                 command=self.search_results_canvas.yview)
        self.search_results_canvas.configure(yscrollcommand=sr_scroll.set)
        sr_scroll.pack(side="right", fill="y")
        self.search_results_canvas.pack(side="left", fill="both", expand=True)

        self.search_results_frame = tk.Frame(self.search_results_canvas, bg="#0d0d1a")
        self._sr_win = self.search_results_canvas.create_window(
            (0, 0), window=self.search_results_frame, anchor="nw"
        )
        self.search_results_frame.bind(
            "<Configure>",
            lambda e: self.search_results_canvas.configure(
                scrollregion=self.search_results_canvas.bbox("all"))
        )

        codes_outer = tk.Frame(right, bg=BG_PANEL)
        codes_outer.pack(fill="both", expand=True, padx=10, pady=(8, 0))

        self.codes_canvas = tk.Canvas(codes_outer, bg=BG_PANEL,
                                      highlightthickness=0)
        codes_scroll = tk.Scrollbar(codes_outer, orient="vertical",
                                    command=self.codes_canvas.yview)
        self.codes_canvas.configure(yscrollcommand=codes_scroll.set)
        codes_scroll.pack(side="right", fill="y")
        self.codes_canvas.pack(side="left", fill="both", expand=True)

        self.codes_inner = tk.Frame(self.codes_canvas, bg=BG_PANEL)
        self._codes_win = self.codes_canvas.create_window(
            (0, 0), window=self.codes_inner, anchor="nw"
        )
        self.codes_inner.bind(
            "<Configure>",
            lambda e: self.codes_canvas.configure(
                scrollregion=self.codes_canvas.bbox("all"))
        )
        self.codes_canvas.bind(
            "<Configure>",
            lambda e: self.codes_canvas.itemconfig(
                self._codes_win, width=e.width)
        )

        # smart mousewheel: scroll whichever pane the cursor is over
        def _on_mousewheel(e):
            x, y = e.x_root, e.y_root
            try:
                sr = self.search_results_canvas
                if self.search_results_outer.winfo_ismapped():
                    sx, sy = sr.winfo_rootx(), sr.winfo_rooty()
                    if sx <= x <= sx + sr.winfo_width() and sy <= y <= sy + sr.winfo_height():
                        sr.yview_scroll(int(-1 * (e.delta / 120)), "units")
                        return
            except Exception:
                pass
            self.codes_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        self.bind_all("<MouseWheel>", _on_mousewheel)

        # Apply Selected bar
        apply_bar = tk.Frame(right, bg=BG_APPLY,
                             highlightthickness=1,
                             highlightbackground="#2a4a2a")
        apply_bar.pack(fill="x", padx=10, pady=6)

        self.selected_count_var = tk.StringVar(value="0 selected")
        make_label(apply_bar, fg=MUTED, bg=BG_APPLY, font=FONT_TINY,
                   textvariable=self.selected_count_var
                   ).pack(side="left", padx=10, pady=6)

        make_button(apply_bar, t("اختيار الكل","Select All"), self._select_all,
                    fg=ACCENT, bg="#2a2a0a", active_bg="#3a3a1a", width=10
                    ).pack(side="left", padx=4, pady=4)
        make_button(apply_bar, t("مسح","Clear"), self._clear_selection,
                    fg=MUTED, bg="#1a1a1a", active_bg="#2a2a2a", width=8
                    ).pack(side="left", padx=4, pady=4)
        self.apply_btn = make_button(
            apply_bar, t("تطبيق المحدد","Apply Selected"), self._apply_selected,
            fg=GREEN, bg="#1a3a1a", active_bg="#2a5a2a", width=14
        )
        self.apply_btn.pack(side="right", padx=10, pady=4)

        # status bar
        statusbar = tk.Frame(self, bg=BG_STATUS, height=24)
        statusbar.pack(fill="x")
        statusbar.pack_propagate(False)

        self.status_applied_var  = tk.StringVar(value="Applied: 0" if CURRENT_LANG == "en" else "مفعّل: 0")
        self.status_detected_var = tk.StringVar(value="Detected: 0" if CURRENT_LANG == "en" else "مكتشف: 0")
        self.status_exe_var      = tk.StringVar(value="")
        self.status_total_var    = tk.StringVar(value="Total codes: 0" if CURRENT_LANG == "en" else "إجمالي الأكواد: 0")

        make_label(statusbar, fg=MUTED, bg=BG_STATUS, font=FONT_TINY,
                   textvariable=self.status_applied_var
                   ).pack(side="left", padx=12)
        make_label(statusbar, fg=MUTED, bg=BG_STATUS, font=FONT_TINY,
                   textvariable=self.status_detected_var
                   ).pack(side="left", padx=8)
        make_label(statusbar, fg=GREEN, bg=BG_STATUS, font=FONT_TINY,
                   textvariable=self.status_exe_var
                   ).pack(side="left", padx=8)
        make_label(statusbar, fg=MUTED, bg=BG_STATUS, font=FONT_TINY,
                   textvariable=self.status_total_var
                   ).pack(side="right", padx=12)

        self.code_rows = {}

    #  logic 

    #  Best Settings preset 
    BEST_SETTINGS = [
        "pointer_edit",
        "sanity_check",
        "aev_type6",
        "aev_fse",
        "aev_ese",
        "aev_auto_door",
        "aev_cam",
        "aev_checkpoint",
        "aev_chain",
        "aev_osd",
        "aev_auto_type5",
        "aev_option",
        "aev_ita",
        "aev_ear",
        "aev_timer",
        "etm_lever",
        "spawn_enemies",
        "em_ita_preload",
        "rsert_order",
        "loot_no_disappear",
        "u3_esl",
        "regen_esl",
        "merchant_init",
        "em_incompat_fix",
        "fix_r100_crash",
        "fix_r101_disappear",
        "grey_screen_fix",
    ]

    def _apply_best_settings(self):
        exe = self.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("Error", "Please select a valid bio4.exe first.")
            return
        if not self.scanned:
            messagebox.showerror("Error", "Please Scan the EXE first.")
            return

        # Build queue in exact order, skip already applied
        queue = [cid for cid in self.BEST_SETTINGS
                 if not self.applied.get(cid, False)]

        if not queue:
            messagebox.showinfo("Best Settings", "All recommended codes are already applied.")
            return

        names = "\n".join("  - " + self.code_by_id.get(c, {}).get("name", c)
                          for c in queue)
        if not messagebox.askyesno("Best Settings",
                                   "Apply the following codes in order?\n\n" + names):
            return

        # Apply one by one in exact order to respect dependencies
        success, failed = [], []
        for cid in queue:
            ok, msg = apply_patch(exe, cid, self.codes_data)
            if ok:
                self.applied[cid] = True
                success.append(cid)
            else:
                failed.append((cid, msg))
                # stop on first failure  later codes may depend on this one
                break

        summary = "Applied " + str(len(success)) + " code(s) successfully."
        if failed:
            summary += "\n\nStopped at:\n"
            for cid, err in failed:
                summary += "- " + self.code_by_id.get(cid, {}).get("name", cid)
                summary += "\n  " + err + "\n"
            messagebox.showwarning("Done with errors", summary)
        else:
            messagebox.showinfo("[+] Done", summary)

        self._after_state_change()

    def _open_settings(self):
        global CURRENT_LANG
        dlg = tk.Toplevel(self)
        dlg.title(t("الإعدادات","Settings"))
        dlg.geometry("340x560")
        dlg.resizable(False, True)
        dlg.configure(bg="#111")
        dlg.grab_set()

        # ── Header ──
        make_label(dlg,
                   "Code Manager Settings" if CURRENT_LANG == "en" else "إعدادات Code Manager",
                   fg=ACCENT2, bg="#111", font=FONT_SMALL
                   ).pack(pady=(12, 4))
        tk.Frame(dlg, bg="#444", height=1).pack(fill="x", padx=16, pady=(0, 6))

        # ── Scrollable content ──
        outer = tk.Frame(dlg, bg="#111")
        outer.pack(fill="both", expand=True, padx=4)
        canvas = tk.Canvas(outer, bg="#111", highlightthickness=0)
        sb = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg="#111")
        cwin = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(cwin, width=e.width))
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        def section_header(text_en, text_ar, color=ACCENT2):
            fr = tk.Frame(inner, bg="#111")
            fr.pack(fill="x", padx=12, pady=(10, 2))
            tk.Label(fr,
                     text=((text_en if CURRENT_LANG == "en" else text_ar)),
                     fg=color, bg="#111", font=("Courier New", 8, "bold"),
                     anchor="w").pack(side="left")
            tk.Frame(inner, bg="#222", height=1).pack(fill="x", padx=12, pady=(0, 4))

        def make_toggle(label_en, label_ar, key):
            var = tk.BooleanVar(value=APP_SETTINGS.get(key, True))
            row = tk.Frame(inner, bg="#111")
            row.pack(fill="x", padx=20, pady=2)
            tk.Checkbutton(
                row, text=label_en if CURRENT_LANG == "en" else label_ar,
                variable=var, font=FONT_TINY,
                fg=TEXT_MAIN, bg="#111",
                activebackground="#111", selectcolor="#1a1a1a",
                relief="flat",
                command=lambda k=key, v=var: (
                    APP_SETTINGS.update({k: v.get()}),
                    save_settings(APP_SETTINGS)
                )
            ).pack(side="left")

        # ══ Section 1: Behavior ══
        section_header("Behavior", "السلوك العام")

        make_toggle("Silent Apply (no confirmation popup)",
                    "تطبيق صامت (بدون رسالة تأكيد)",
                    "silent_apply")

        # ══ Section 2: Editing Mode ══
        section_header("Editing Mode", "وضع التعديل", color="#e07070")

        rt_on = APP_SETTINGS.get("real_time_mode", False)

        def _switch_to_rt():
            warn = (
                "⚠  Real-Time Editing Mode\n\n"
                "Writes bytes directly into the running game process.\n"
                "DANGEROUS — may cause crashes or memory corruption.\n\n"
                "Only offset_paste / offset_replace patches are supported.\n"
                "find_replace patches are skipped silently.\n\n"
                "You will need to re-do Scan after switching.\n\n"
                "Are you sure?"
            ) if CURRENT_LANG == "en" else (
                "⚠  وضع التعديل الفوري\n\n"
                "يكتب مباشرة في ذاكرة اللعبة وهي شغالة.\n"
                "خطير — ممكن يسبب كراشات أو تلف في الذاكرة.\n\n"
                "يدعم فقط offset_paste / offset_replace.\n"
                "باتشات find_replace تُتجاهل.\n\n"
                "ستحتاج إعادة Scan بعد التبديل.\n\n"
                "هل أنت متأكد؟"
            )
            if not messagebox.askyesno(
                "Enable Real-Time Mode?" if CURRENT_LANG == "en" else "تفعيل وضع التعديل الفوري؟",
                warn, icon="warning"
            ):
                return
            APP_SETTINGS["real_time_mode"] = True
            save_settings(APP_SETTINGS)
            dlg.destroy()
            APP_SETTINGS.update(load_settings())
            self._reload_ui()

        def _switch_to_normal():
            APP_SETTINGS["real_time_mode"] = False
            save_settings(APP_SETTINGS)
            dlg.destroy()
            APP_SETTINGS.update(load_settings())
            self._reload_ui()

        if rt_on:
            rt_label = "Normal Editor Mode" if CURRENT_LANG == "en" else "وضع المحرر العادي"
            rt_desc  = ("Currently in Real-Time mode. Click to return to normal."
                        ) if CURRENT_LANG == "en" else (
                        "أنت في وضع التعديل الفوري. اضغط للرجوع للعادي.")
            rt_color = "#ff9060"
            rt_cmd   = _switch_to_normal
        else:
            rt_label = "Real-Time Editing Mode" if CURRENT_LANG == "en" else "وضع التعديل الفوري"
            rt_desc  = ("Apply codes to the running game without restarting."
                        ) if CURRENT_LANG == "en" else (
                        "فعّل الأكواد على اللعبة وهي شغالة.")
            rt_color = "#e07070"
            rt_cmd   = _switch_to_rt

        tk.Label(inner, text=rt_desc, fg="#555", bg="#111",
                 font=("Courier New", 7), justify="left").pack(anchor="w", padx=20)
        make_button(inner, rt_label, rt_cmd,
                    fg=rt_color, bg="#1a0a0a", active_bg="#2a1010", width=26
                    ).pack(pady=(2, 4))

        # ══ Section 3: Profiles ══
        section_header("Profiles", "الملفات الشخصية", color=ACCENT2)

        prof_row = tk.Frame(inner, bg="#111")
        prof_row.pack(pady=2)
        make_button(prof_row, "New Profile", lambda: [dlg.destroy(), self._new_profile()],
                    fg=ACCENT, bg="#2a2a0a", active_bg="#3a3a1a", width=12
                    ).pack(side="left", padx=6)
        make_button(prof_row, "Load Profile", lambda: [dlg.destroy(), self._load_profile()],
                    fg=GREEN, bg="#1a2a0a", active_bg="#2a4a1a", width=12
                    ).pack(side="left", padx=6)

        # ══ Section 4: Custom Codes ══
        section_header("Custom Codes", "أكواد مخصصة", color=ACCENT2)

        make_button(inner, "Add New Code", lambda: [dlg.destroy(), self._add_new_code()],
                    fg=ACCENT2, bg="#1a1a2a", active_bg="#2a2a3a", width=14
                    ).pack(pady=(0, 4))

        # ══ Section 5: EXE Analysis ══
        section_header("EXE Analysis", "تحليل EXE", color=ACCENT)

        cmp_row = tk.Frame(inner, bg="#111")
        cmp_row.pack(pady=2)
        make_button(cmp_row, "Compare Two EXEs",
                    lambda: [dlg.destroy(), self._compare_two_exes()],
                    fg=ACCENT, bg="#2a2a0a", active_bg="#3a3a1a", width=16
                    ).pack(side="left", padx=4)
        make_button(cmp_row, "Compare with Original",
                    lambda: [dlg.destroy(), self._compare_with_original()],
                    fg="#60c8ff", bg="#0a1a2a", active_bg="#1a2a3a", width=18
                    ).pack(side="left", padx=4)

        # ══ Section 6: Log ══
        section_header("Log", "السجل", color=ACCENT2)

        make_button(inner,
                    "View Log" if CURRENT_LANG == "en" else "عرض السجل",
                    lambda: [dlg.destroy(), self._view_log()],
                    fg=ACCENT2, bg="#1a2a0a", active_bg="#2a4a1a", width=14
                    ).pack(pady=(0, 4))

        # ══ Section 7: Restore EXE ══
        section_header("Restore", "استعادة EXE", color="#e8c060")

        make_button(inner,
                    "Restore from bio4_original.exe" if CURRENT_LANG == "en" else "استعادة من bio4_original.exe",
                    lambda: [dlg.destroy(), self._restore_original_exe()],
                    fg="#e8c060", bg="#1a1500", active_bg="#2a2000", width=26
                    ).pack(pady=(0, 4))

        # ══ Section 8: Reset ══
        section_header("Danger Zone", "منطقة الخطر", color="#ff6060")

        make_button(inner,
                    "Reset All Codes" if CURRENT_LANG == "en" else "إعادة تعيين كل الأكواد",
                    lambda: [dlg.destroy(), self._reset_all_codes()],
                    fg="#ff6060", bg="#2a0a0a", active_bg="#3a1010", width=16
                    ).pack(pady=(0, 12))

    #  EXE Comparison 

    def _show_report(self, title, report):
        """Show report in a scrollable window and offer to save."""
        dlg = tk.Toplevel(self)
        dlg.title(title)
        dlg.geometry("700x500")
        dlg.configure(bg="#111")

        txt_frame = tk.Frame(dlg, bg="#111")
        txt_frame.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        txt = tk.Text(txt_frame, font=("Courier New", 9),
                      fg="#c8c8c8", bg="#0d0d0d",
                      relief="flat", bd=0,
                      highlightthickness=1, highlightbackground=BORDER,
                      wrap="none")
        sc_y = tk.Scrollbar(txt_frame, orient="vertical", command=txt.yview)
        sc_x = tk.Scrollbar(dlg, orient="horizontal", command=txt.xview)
        txt.configure(yscrollcommand=sc_y.set, xscrollcommand=sc_x.set)
        sc_y.pack(side="right", fill="y")
        txt.pack(side="left", fill="both", expand=True)
        sc_x.pack(fill="x", padx=10, pady=(0, 4))

        txt.insert("1.0", report)
        txt.configure(state="disabled")

        btn_row = tk.Frame(dlg, bg="#111")
        btn_row.pack(pady=6)

        def save_report():
            from tkinter import filedialog as fd
            path = fd.asksaveasfilename(
                title="Save Report",
                defaultextension=".txt",
                filetypes=[("Text file", "*.txt"), ("All files", "*.*")]
            )
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(report)
                messagebox.showinfo("Saved", "Report saved:\n" + path)

        make_button(btn_row, "Save Report", save_report,
                    fg=ACCENT, bg="#2a2a1a", active_bg="#3a3a2a", width=12
                    ).pack(side="left", padx=8)
        make_button(btn_row, "Close", dlg.destroy,
                    fg=MUTED, bg="#1a1a1a", active_bg="#2a2a2a", width=8
                    ).pack(side="left", padx=4)

    def _scan_codes_in_file(self, path):
        """Run scan_exe on a given path and return {code_id: bool}."""
        return scan_exe(path, self.codes_info, self.codes_data)

    def _build_codes_report(self, results_a, results_b, label_a, label_b):
        """Compare two scan results and build a readable report."""
        lines = []
        lines.append("=" * 60)
        lines.append("  " + label_a + "  vs  " + label_b)
        lines.append("=" * 60)

        only_a, only_b, both_on, both_off = [], [], [], []

        all_ids = sorted(set(list(results_a.keys()) + list(results_b.keys())))
        for cid in all_ids:
            a = results_a.get(cid, False)
            b = results_b.get(cid, False)
            code = self.code_by_id.get(cid, {})
            name = code.get("name_en" if CURRENT_LANG == "en" else "name", cid)
            if a and not b:
                only_a.append(name)
            elif b and not a:
                only_b.append(name)
            elif a and b:
                both_on.append(name)
            else:
                both_off.append(name)

        if only_a:
            lines.append("\n[ON in " + label_a + " only]  (" + str(len(only_a)) + " codes)")
            for n in only_a:
                lines.append("  + " + n)

        if only_b:
            lines.append("\n[ON in " + label_b + " only]  (" + str(len(only_b)) + " codes)")
            for n in only_b:
                lines.append("  + " + n)

        if both_on:
            lines.append("\n[ON in both]  (" + str(len(both_on)) + " codes)")
            for n in both_on:
                lines.append("  = " + n)

        lines.append("\n[OFF in both]  (" + str(len(both_off)) + " codes)")
        for n in both_off:
            lines.append("  - " + n)

        lines.append("\n" + "=" * 60)
        lines.append(
            "Total codes: " + str(len(all_ids)) +
            "  |  " + label_a + " applied: " + str(sum(results_a.values())) +
            "  |  " + label_b + " applied: " + str(sum(results_b.values()))
        )
        return "\n".join(lines)

    def _compare_two_exes(self):
        dlg = tk.Toplevel(self)
        dlg.title("Compare Two EXEs")
        dlg.geometry("480x200")
        dlg.resizable(False, False)
        dlg.configure(bg="#111")
        dlg.grab_set()

        def pick(var):
            path = _browse_open(
                title="Select EXE",
                filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
                key="exe"
            )
            if path:
                var.set(path)

        var_a = tk.StringVar(value=self.exe_path.get())
        var_b = tk.StringVar()

        for label, var in [("EXE  A:", var_a), ("EXE  B:", var_b)]:
            row = tk.Frame(dlg, bg="#111")
            row.pack(fill="x", padx=16, pady=6)
            make_label(row, label, fg=TEXT_DIM, bg="#111",
                       font=FONT_SMALL, width=7).pack(side="left")
            tk.Entry(row, textvariable=var, font=FONT_SMALL,
                     fg=ACCENT2, bg="#1a1a1a", insertbackground=ACCENT2,
                     relief="flat", bd=0,
                     highlightthickness=1, highlightbackground=BORDER,
                     width=36).pack(side="left", ipady=2)
            make_button(row, "...", lambda v=var: pick(v),
                        fg=ACCENT, bg="#2a2a1a", active_bg="#3a3a2a",
                        font=FONT_TINY, width=3
                        ).pack(side="left", padx=4)

        def run():
            a, b = var_a.get().strip(), var_b.get().strip()
            if not a or not os.path.isfile(a):
                messagebox.showerror("Error", "Invalid EXE A path."); return
            if not b or not os.path.isfile(b):
                messagebox.showerror("Error", "Invalid EXE B path."); return
            dlg.destroy()
            res_a = self._scan_codes_in_file(a)
            res_b = self._scan_codes_in_file(b)
            report = self._build_codes_report(
                res_a, res_b,
                os.path.basename(a),
                os.path.basename(b)
            )
            self._show_report(
                "Compare: " + os.path.basename(a) + " vs " + os.path.basename(b),
                report
            )

        make_button(dlg, "Compare", run,
                    fg=GREEN, bg="#1a2a0a", active_bg="#2a4a1a", width=12
                    ).pack(pady=12)

    def _compare_with_original(self):
        exe = self.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("Error",
                "Please select a valid bio4.exe first."
                if CURRENT_LANG == "en" else
                "حط مسار bio4.exe أول.")
            return
        if not os.path.isfile(ORIG_FILE):
            messagebox.showerror("Error",
                "bio4_original.exe not found in the_codes/ folder."
                if CURRENT_LANG == "en" else
                "ما لقيت bio4_original.exe في مجلد the_codes/.")
            return
        res_orig = self._scan_codes_in_file(ORIG_FILE)
        res_exe  = self._scan_codes_in_file(exe)
        report = self._build_codes_report(
            res_orig, res_exe,
            "bio4_original.exe",
            os.path.basename(exe)
        )
        self._show_report(
            "Compare: Original vs " + os.path.basename(exe),
            report
        )

    def _view_log(self):
        """Show the patch log in a scrollable window."""
        if not os.path.isfile(LOG_FILE):
            messagebox.showinfo(
                "Log" if CURRENT_LANG == "en" else "السجل",
                "No log file found yet." if CURRENT_LANG == "en" else "ما في سجل بعد."
            )
            return
        with open(LOG_FILE, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        self._show_report("patch_log.txt", content)

    def _restore_original_exe(self):
        """Replace current bio4.exe with bio4_original.exe."""
        exe = self.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("Error",
                "Please select bio4.exe first." if CURRENT_LANG == "en"
                else "حط مسار bio4.exe أول.")
            return
        if not os.path.isfile(ORIG_FILE):
            messagebox.showerror("Error",
                "bio4_original.exe not found in the_codes folder."
                if CURRENT_LANG == "en"
                else "bio4_original.exe مو موجود في مجلد the_codes.")
            return
        confirmed = messagebox.askyesno(
            "Are you sure?" if CURRENT_LANG == "en" else "هل أنت متأكد؟",
            ("This will replace your current bio4.exe with bio4_original.exe.\n"
             "All applied codes will be reverted.\nContinue?")
            if CURRENT_LANG == "en" else
            ("هذا سيستبدل bio4.exe الحالي بالملف الأصلي.\n"
             "كل الأكواد المطبقة ستُحذف.\nتكمل؟")
        )
        if not confirmed:
            return
        import shutil
        try:
            shutil.copy2(ORIG_FILE, exe)
            self.applied  = {}
            self.detected = {}
            self.scanned  = False
            self._after_state_change()
            messagebox.showinfo("[+] Done",
                "bio4.exe has been restored to original."
                if CURRENT_LANG == "en"
                else "تم استعادة bio4.exe إلى النسخة الأصلية.")
            write_log("RESTORED", "bio4.exe restored from bio4_original.exe", exe)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _reset_all_codes(self):
        confirm_msg = (
            "Are you sure you want to revert ALL applied codes?\n\n"
            "This will restore all patched bytes in bio4.exe.\n"
            "Make sure bio4_original.exe is in the_codes/ folder."
            if CURRENT_LANG == "en" else
            "هل أنت متأكد أنك تبي تشيل كل الأكواد؟\n\n"
            "هذا يرجع كل البايتات المعدلة في bio4.exe.\n"
            "تأكد أن bio4_original.exe موجود في مجلد the_codes/."
        )
        if not messagebox.askyesno(
            "Reset All" if CURRENT_LANG == "en" else "إعادة تعيين",
            confirm_msg
        ):
            return

        exe = self.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("Error", "Please select a valid bio4.exe first.")
            return

        applied_ids = [cid for cid, v in self.applied.items() if v]
        if not applied_ids:
            messagebox.showinfo(
                "Reset All" if CURRENT_LANG == "en" else "إعادة تعيين",
                "No codes are currently applied." if CURRENT_LANG == "en"
                else "ما في أكواد مفعّلة حالياً."
            )
            return

        success, failed = [], []
        for cid in applied_ids:
            ok, msg, _ = revert_patch(exe, ORIG_FILE, cid, self.codes_data)
            if ok:
                self.applied[cid] = False
                self.detected[cid] = False
                write_log("REVERTED (reset all)", self.code_by_id.get(cid, {}).get("name", cid), exe)
                success.append(cid)
            else:
                failed.append((cid, msg))

        summary = (
            "Reverted " + str(len(success)) + " code(s)."
            if CURRENT_LANG == "en" else
            "تم إزالة " + str(len(success)) + " كود."
        )
        if failed:
            summary += "\n\nFailed:\n"
            for cid, err in failed:
                summary += "- " + self.code_by_id.get(cid, {}).get("name", cid) + "\n"
            messagebox.showwarning("Done with errors", summary)
        else:
            messagebox.showinfo("[+] Done", summary)

        self._after_state_change()

    def _reload_ui(self):
        """Rebuild entire UI with new language."""
        # Save state
        exe = self.exe_path.get()
        sec = self.active_section

        # Destroy all children
        for w in self.winfo_children():
            w.destroy()

        # Reset widget refs
        self.code_rows = {}
        self.sidebar_items = {}

        # Rebuild
        self._build_ui()

        # Restore state
        self.exe_path.set(exe)
        if self.scanned:
            n_det   = sum(1 for v in self.detected.values() if v)
            n_app   = sum(1 for v in self.applied.values() if v)
            total   = len(self.all_codes)
            orig_status = ("  |  [orig: OK]" if CURRENT_LANG == "en" else "  |  [الأصلي: OK]") if os.path.isfile(ORIG_FILE) \
                else ("  |  [orig: missing]" if CURRENT_LANG == "en" else "  |  [الأصلي: مفقود]")
            scan_msg = (
                f"Scanned  {n_det} detected  |  {n_app} applied  |  {total} total"
                if CURRENT_LANG == "en" else
                f"تم المسح  {n_det} مكتشف  |  {n_app} مطبق  |  {total} إجمالي"
            ) + orig_status
            self.scan_status_var.set(scan_msg)
            # update embedded scan bar label
            if hasattr(self, "_scan_status"):
                self._scan_status.set(
                    f"{n_det} detected  |  {n_app} applied  |  {total} total"
                    if CURRENT_LANG == "en" else
                    f"{n_det} مكتشف  |  {n_app} مطبق  |  {total} إجمالي"
                )
            self.notice.pack_forget()
            self._update_statusbar()

        if sec:
            self.select_section(sec)
        else:
            self.select_section(self.sections_list[0]["id"])

    def _on_exe_path_change(self, *_):
        """Auto-scan when exe path changes after first manual scan."""
        # auto_scan_change disabled if auto_scan_startup is on
        if APP_SETTINGS.get("auto_scan_startup", False):
            return
        if not APP_SETTINGS.get("auto_scan_change", True):
            return
        if not self._first_scan_done:
            return
        path = self.exe_path.get().strip()
        if path and os.path.isfile(path) and path.lower().endswith(".exe"):
            self.after(300, self._scan)

    def _add_paste_menu(self, entry):
        """Add right-click Paste context menu to an Entry widget."""
        menu = tk.Menu(entry, tearoff=0, bg="#1a1a1a", fg=TEXT_MAIN,
                       activebackground="#2a2a2a", activeforeground=ACCENT2,
                       font=FONT_TINY, relief="flat", bd=0)
        menu.add_command(label="Paste", command=lambda: (
            entry.event_generate("<<Paste>>")
        ))
        menu.add_command(label="Copy", command=lambda: (
            entry.event_generate("<<Copy>>")
        ))
        menu.add_command(label="Cut", command=lambda: (
            entry.event_generate("<<Cut>>")
        ))
        menu.add_separator()
        menu.add_command(label="Select All", command=lambda: (
            entry.select_range(0, "end")
        ))
        entry.bind("<Button-3>", lambda e: menu.tk_popup(e.x_root, e.y_root))

    def _on_drop(self, event):
        pass  # placeholder  DND removed

    def _browse(self):
        path = _browse_open(
            title="Select bio4.exe",
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
            key="exe"
        )
        if path:
            self.exe_path.set(path)
            self._make_backup(path)

    def _make_backup(self, exe_path):
        """Create BIO4_BACKUP.EXE next to bio4.exe if not already exists."""
        import shutil
        backup = os.path.join(os.path.dirname(exe_path), "BIO4_BACKUP.EXE")
        if not os.path.isfile(backup):
            try:
                shutil.copy2(exe_path, backup)
                messagebox.showinfo(
                    "Backup Created",
                    "Backup created successfully:\n" + backup
                )
            except Exception as e:
                messagebox.showwarning(
                    "Backup Failed",
                    "Could not create backup:\n" + str(e)
                )
        # also check path entry manual edits on scan

    def _scan(self):
        path = self.exe_path.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showerror("Error", "Please select a valid bio4.exe file.")
            return

        # make backup if not exists
        self._make_backup(path)

        self.scan_btn.configure(text="Scanning..." if CURRENT_LANG == "en" else "جاري المسح...", state="disabled")
        self.update_idletasks()

        # reset state completely  fresh scan
        self.applied  = {}
        self.detected = {}

        self.detected = scan_exe(path, self.codes_info, self.codes_data)
        for cid, found in self.detected.items():
            if found:
                self.applied[cid] = True

        self.scanned = True
        self._first_scan_done = True

        # read current numeric values from EXE for numeric_input codes
        self._numeric_current = {}
        try:
            with open(path, "rb") as f:
                exe_bytes = f.read()
            for code in self.all_codes:
                if code.get("dialog") == "numeric_input":
                    cid        = code["id"]
                    entry      = self.codes_data.get(cid, {})
                    offset     = entry.get("offset", "")
                    byte_count = entry.get("byte_count", 1)
                    divide_by  = entry.get("divide_by", 1)
                    if offset:
                        off = int(offset, 16)
                        chunk = exe_bytes[off:off + byte_count]
                        if len(chunk) == byte_count:
                            val = int.from_bytes(chunk, byteorder="little")
                            # multiply back for display (reverse of divide_by)
                            self._numeric_current[cid] = val * divide_by
        except Exception:
            pass

        # save last exe path
        if APP_SETTINGS.get("remember_exe", True):
            APP_SETTINGS["last_exe"] = path
            save_settings(APP_SETTINGS)
        n_det = sum(1 for v in self.detected.values() if v)
        self.scan_btn.configure(text="Re-Scan" if CURRENT_LANG == "en" else "إعادة المسح", state="normal")
        orig_status = ("  |  [orig: OK]" if CURRENT_LANG == "en" else "  |  [الأصلي: OK]") if os.path.isfile(ORIG_FILE) \
            else ("  |  [orig: missing - revert disabled]" if CURRENT_LANG == "en" else "  |  [الأصلي: مفقود - الإرجاع معطل]")
        n_app   = sum(1 for v in self.applied.values() if v)
        total   = len(self.all_codes)
        scan_msg = (
            f"Scanned  {n_det} detected  |  {n_app} applied  |  {total} total"
            if CURRENT_LANG == "en" else
            f"تم المسح  {n_det} مكتشف  |  {n_app} مطبق  |  {total} إجمالي"
        ) + orig_status
        self.scan_status_var.set(scan_msg)
        if hasattr(self, "_scan_status"):
            self._scan_status.set(
                f"{n_det} detected  |  {n_app} applied  |  {total} total"
                if CURRENT_LANG == "en" else
                f"{n_det} مكتشف  |  {n_app} مطبق  |  {total} إجمالي"
            )
        self.notice.pack_forget()
        self._after_state_change()
        # update master locked panels after scan
        master = getattr(self, '_master_app_ref', None)
        if master:
            master._check_locked_panels()


    def select_section(self, section_id, preserve_scroll=None):
        for sid, item in self.sidebar_items.items():
            item.set_active(sid == section_id)
        self.active_section = section_id

        sec = next((s for s in self.sections_list if s["id"] == section_id), None)
        if sec:
            self.section_title_var.set(sec["label"])

        for w in self.codes_inner.winfo_children():
            w.destroy()
        self.code_rows.clear()

        codes = self.codes_by_section.get(section_id, [])
        self.section_count_var.set("  " + str(len(codes)) + " codes")

        if not codes:
            make_label(self.codes_inner,
                       "-- No codes in this section yet --",
                       fg=MUTED, bg=BG_PANEL, font=FONT_SMALL
                       ).pack(pady=24)
            self._update_apply_bar()
            return

        for code in codes:
            row = CodeRow(self.codes_inner, code, self)
            row.pack(fill="x", pady=2)
            self.code_rows[code["id"]] = row
            self._refresh_row(code["id"])
            # restore global selection
            if code["id"] in self._global_selected:
                row.sel_var.set(1)
                row.selected = True

        # restore scroll or go to top
        if preserve_scroll is not None:
            self.codes_canvas.after(10, lambda: self.codes_canvas.yview_moveto(preserve_scroll))
        else:
            self.codes_canvas.yview_moveto(0)
        self._update_apply_bar()

    def _is_unlocked(self, code_id):
        if not self.scanned:
            return False
        code = self.code_by_id.get(code_id, {})
        for dep in code.get("requires", []):
            if not (self.applied.get(dep) or self.detected.get(dep)):
                return False
        return True

    def _get_missing_requires(self, code_id):
        """Return list of (dep_id, dep_name, section_label) for unmet requires."""
        code = self.code_by_id.get(code_id, {})
        missing = []
        sec_map = {s["id"]: s for s in self.sections_list}
        for dep in code.get("requires", []):
            if not (self.applied.get(dep) or self.detected.get(dep)):
                dep_code = self.code_by_id.get(dep, {})
                dep_name = dep_code.get("name_en" if CURRENT_LANG == "en" else "name", dep)
                dep_sec  = dep_code.get("section", "")
                sec_obj  = sec_map.get(dep_sec, {})
                sec_label = sec_obj.get("label_en" if CURRENT_LANG == "en" else "label", dep_sec)
                missing.append((dep, dep_name, sec_label))
        return missing

    def _get_dependents(self, code_id):
        """Return all applied codes that directly or transitively require code_id."""
        dependents = []
        for code in self.all_codes:
            cid = code["id"]
            if cid == code_id:
                continue
            if not self.applied.get(cid, False):
                continue
            # check if code_id is in transitive requires
            if code_id in self._transitive_requires(cid):
                dependents.append(cid)
        return dependents

    def _transitive_requires(self, cid, visited=None):
        if visited is None:
            visited = set()
        if cid in visited:
            return set()
        visited.add(cid)
        direct = set(self.code_by_id.get(cid, {}).get("requires", []))
        result = set(direct)
        for dep in direct:
            result |= self._transitive_requires(dep, visited)
        return result

    def handle_toggle(self, code_id):
        if not self.scanned:
            messagebox.showinfo(
                "Scan Required" if CURRENT_LANG == "en" else "لازم تسوي Scan",
                "Please select bio4.exe and press Scan EXE first."
                if CURRENT_LANG == "en" else
                "حط مسار bio4.exe واضغط Scan EXE أول."
            )
            return

        if not self._is_unlocked(code_id):
            missing = self._get_missing_requires(code_id)
            if missing:
                msg = ("You need to enable the following codes first:\n\n"
                       if CURRENT_LANG == "en" else
                       "لازم تشغل الأكواد التالية أول:\n\n")
                for dep_id, dep_name, sec_label in missing:
                    msg += "  - " + dep_name + "\n"
                    msg += ("    (Found in: " + sec_label + ")\n"
                            if CURRENT_LANG == "en" else
                            "    (تجده في قسم: " + sec_label + ")\n")
                messagebox.showwarning(
                    "Code Locked" if CURRENT_LANG == "en" else "الكود مقفل",
                    msg
                )
            return
        code = self.code_by_id.get(code_id, {})

        if self.applied.get(code_id, False):
            # revert
            exe = self.exe_path.get().strip()
            if not exe or not os.path.isfile(exe):
                messagebox.showerror("Error", "EXE path is invalid.")
                return

            # ── Real-Time revert ──
            if APP_SETTINGS.get("real_time_mode", False):
                originals = self._rt_originals.get(code_id, {})
                ok2, err = rt_revert_patch(exe, originals)
                if ok2:
                    self.applied[code_id] = False
                    self.detected[code_id] = False
                    self._rt_originals.pop(code_id, None)
                    write_log("RT-REVERTED", self.code_by_id.get(code_id, {}).get("name", code_id), exe)
                    self._after_state_change()
                else:
                    messagebox.showerror("RT Revert Error", err)
                return

            if is_game_running(exe):
                messagebox.showerror(
                    "Game is Running" if CURRENT_LANG == "en" else "اللعبة شغالة",
                    "Please close the game before reverting codes."
                    if CURRENT_LANG == "en" else
                    "طفي اللعبة أول عشان تقدر تشيل الكود."
                )
                return

            # check if code has offset patches requiring original
            data = self.codes_data.get(code_id, {})
            if "variants" in data:
                all_patches = []
                for v in data["variants"].values():
                    all_patches += v.get("patches", [])
            else:
                all_patches = data.get("patches", [])

            needs_orig = any(p["type"] == "offset_paste"
                             for p in all_patches)

            if needs_orig and not os.path.isfile(ORIG_FILE):
                messagebox.showerror(
                    "Cannot Revert",
                    "This code has offset-based patches.\n"
                    "To revert it, place the original bio4.exe in:\n\n"
                    "the_codes/bio4_original.exe"
                )
                return

            ok, msg, skipped = revert_patch(exe, ORIG_FILE, code_id, self.codes_data)
            if ok:
                self.applied[code_id] = False
                self.detected[code_id] = False
                backup_snap = load_patch_backup()
                write_log("REVERTED", self.code_by_id.get(code_id, {}).get("name", code_id), exe,
                           build_log_details(code_id, self.codes_data, backup_snap))

                # cascade: revert all applied codes that depend on this one
                dependents = self._get_dependents(code_id)
                if dependents:
                    dep_names = "\n".join(
                        "  - " + self.code_by_id.get(d, {}).get(
                            "name_en" if CURRENT_LANG == "en" else "name", d)
                        for d in dependents
                    )
                    title = "Cascade Revert" if CURRENT_LANG == "en" else "إيقاف الأكواد التابعة"
                    msg_cascade = (
                        "The following codes depend on this one.\n"
                        "Turn them OFF too?\n\n" + dep_names
                    ) if CURRENT_LANG == "en" else (
                        "الأكواد التالية تعتمد على هذا الكود.\n"
                        "تطفيها كذلك؟\n\n" + dep_names
                    )
                    if messagebox.askyesno(title, msg_cascade):
                        for dep in dependents:
                            ok2, _, _ = revert_patch(exe, ORIG_FILE, dep, self.codes_data)
                            if ok2:
                                self.applied[dep] = False
                                self.detected[dep] = False
                                write_log("REVERTED (cascade)",
                                          self.code_by_id.get(dep, {}).get("name", dep), exe)
                    # If No: leave dependents as applied=True in EXE
                    # _is_unlocked returns False so they show locked [L]
                    # but their toggle shows ON  user must re-enable base code first

                if skipped > 0:
                    messagebox.showinfo(
                        "Reverted",
                        "Code reverted.\n(" + str(skipped) + " patch(es) were already at original state)"
                    )
                self._after_state_change()
            else:
                messagebox.showerror("Revert Failed", msg)
            return

        if code.get("dialog") == "mod_expansion":
            self._dialog_mod_expansion(code_id)
            return
        if code.get("dialog") == "bgm_files":
            self._dialog_bgm_files(code_id)
            return
        if code.get("dialog") == "link_tweaks":
            self._dialog_link_tweaks(code_id)
            return
        if code.get("dialog") == "numeric_input":
            # numeric codes use inline Apply button, not toggle
            return
        if code.get("dialog") == "memory_alloc":
            self._dialog_memory_alloc(code_id)
            return
        if code.get("dialog") == "random_ptas":
            self._dialog_random_ptas(code_id)
            return
        if code.get("dialog") == "dropdown":
            row = self.code_rows.get(code_id)
            perm = row.perm_var.get() if row and hasattr(row, "perm_var") else False
            self._dialog_dropdown(code_id, perm_activate=perm)
            return
        if code.get("dialog") == "r11c_cabin":
            self._dialog_r11c_cabin(code_id)
            return
        if code.get("dialog") == "luis_cabin":
            self._dialog_luis_cabin(code_id)
            return
        if code.get("dialog") == "drawn_enemies_cam":
            self._dialog_drawn_enemies_cam(code_id)
            return
        if code.get("dialog") == "custom_ces":
            self._dialog_custom_ces(code_id)
            return
        if code_id == "spawn_enemies":
            self._dialog_spawn_enemies_variant(code_id)
            return
        self._do_apply(code_id)

    #  Numeric Input Dialog 

    def _dialog_numeric_input(self, code_id):
        """Generic dialog for codes with a single numeric (decimal) input."""
        exe = self.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("Error", "Please select a valid bio4.exe first.")
            return

        entry_data = self.codes_data.get(code_id, {})
        code_info  = self.code_by_id.get(code_id, {})
        offset     = entry_data.get("offset", "")
        byte_count = entry_data.get("byte_count", 1)
        default    = entry_data.get("default_dec", 0)
        divide_by  = entry_data.get("divide_by", 1)
        name       = code_info.get("name_en" if CURRENT_LANG == "en" else "name", code_id)

        dlg = tk.Toplevel(self)
        dlg.title(name)
        dlg.geometry("320x180")
        dlg.resizable(False, False)
        dlg.configure(bg="#111")
        dlg.grab_set()

        make_label(dlg, name, fg=ACCENT2, bg="#111", font=FONT_NORMAL).pack(pady=(16, 4))
        make_label(dlg,
                   "Enter value (decimal):" if CURRENT_LANG == "en" else "أدخل القيمة (decimal):",
                   fg=TEXT_DIM, bg="#111", font=FONT_TINY).pack()

        val_var = tk.StringVar(value=str(default))
        e = tk.Entry(dlg, textvariable=val_var, font=FONT_NORMAL,
                     fg=ACCENT2, bg="#1a1a1a", insertbackground=ACCENT2,
                     relief="flat", bd=0, highlightthickness=1,
                     highlightbackground=BORDER, width=12, justify="center")
        e.pack(pady=8, ipady=4)
        self._add_paste_menu(e)

        def do_apply():
            try:
                dec_val = int(val_var.get().strip())
                if dec_val < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid positive number.")
                return

            # validate against byte_count max
            max_val = (1 << (byte_count * 8)) - 1
            if dec_val > max_val:
                messagebox.showerror(
                    "Error",
                    f"Value too large. Max for {byte_count} byte(s) = {max_val}."
                    if CURRENT_LANG == "en" else
                    f"القيمة كبيرة جداً. الحد الأقصى لـ {byte_count} بايت = {max_val}."
                )
                return

            # check for prefix_template (e.g. random_ptas: BE XX 00 00 00 E9...)
            template = entry_data.get("prefix_template", "")
            divide_by = entry_data.get("divide_by", 1)
            actual_val = dec_val // divide_by if divide_by > 1 else dec_val
            if template:
                xx = format(actual_val, "02X")
                hex_bytes = template.replace("{XX}", xx)
                write_len = len(hex_bytes) // 2
            else:
                hex_bytes = actual_val.to_bytes(byte_count, byteorder="little").hex().upper()
                write_len = byte_count

            if APP_SETTINGS.get("real_time_mode", False):
                # RT mode: write directly to RAM
                pid, handle = _rt_get_process_handle()
                if not pid:
                    messagebox.showerror("RT Error",
                        "bio4.exe not found in Task Manager." if CURRENT_LANG == "en"
                        else "bio4.exe غير موجود في Task Manager.")
                    return
                base = _rt_get_module_base(pid, exe)
                if not base:
                    _ctypes.windll.kernel32.CloseHandle(handle)
                    messagebox.showerror("RT Error", "Could not read module base.")
                    return
                file_off = int(offset, 16)
                ram_addr = _rt_file_offset_to_ram(handle, base, file_off)
                if not ram_addr:
                    _ctypes.windll.kernel32.CloseHandle(handle)
                    messagebox.showerror("RT Error", f"Offset 0x{file_off:X} not mapped.")
                    return
                patch_b = bytes.fromhex(hex_bytes)
                ok = _rt_patch_memory(handle, ram_addr, patch_b)
                _ctypes.windll.kernel32.CloseHandle(handle)
                if not ok:
                    messagebox.showerror("RT Error", "WriteProcessMemory failed.")
                    return
                # Permanent Activation: write to running EXE on disk
                row = self.code_rows.get(code_id)
                if row and getattr(row, "perm_var", None) and row.perm_var.get():
                    _perm_pid, _perm_h = _rt_get_process_handle()
                    _perm_path = _rt_get_running_exe_path(_perm_pid) if _perm_pid else None
                    if _perm_h: _ctypes.windll.kernel32.CloseHandle(_perm_h)
                    perm_target = _perm_path if _perm_path and os.path.isfile(_perm_path) else exe
                    try:
                        with open(perm_target, "r+b") as f:
                            f.seek(int(offset, 16)); f.write(bytes.fromhex(hex_bytes))
                    except Exception: pass
            else:
                try:
                    with open(exe, "r+b") as f:
                        off = int(offset, 16)
                        f.seek(off)
                        orig = f.read(write_len)
                        backup = load_patch_backup()
                        backup.setdefault(code_id, {})[offset.upper().lstrip("0") or "0"] = orig.hex().upper()
                        save_patch_backup(backup)
                        f.seek(off)
                        f.write(bytes.fromhex(hex_bytes))
                except Exception as ex:
                    messagebox.showerror("Error", str(ex))
                    return

            row = self.code_rows.get(code_id)
            perm_on = row and getattr(row, "perm_var", None) and row.perm_var.get()
            self.applied[code_id] = True
            write_log("APPLIED", name + " = " + str(dec_val), exe)
            dlg.destroy()
            if not APP_SETTINGS.get("silent_apply", False):
                perm_note = "\n⚡ + Permanent" if perm_on else ""
                messagebox.showinfo("[+] Applied", name + perm_note + "\nValue: " + str(dec_val))
            self._after_state_change()

        make_button(dlg, "Apply" if CURRENT_LANG == "en" else "تطبيق",
                    do_apply, fg=GREEN, bg="#1a2a0a", active_bg="#2a4a1a", width=10
                    ).pack(pady=8)

    #  Dropdown Dialog 

    def _dialog_dropdown(self, code_id, perm_activate=False):
        """Dialog for codes with a fixed list of options (e.g. scope color)."""
        exe = self.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("Error", "Please select a valid bio4.exe first.")
            return

        entry_data = self.codes_data.get(code_id, {})
        code_info  = self.code_by_id.get(code_id, {})
        offset     = entry_data.get("offset", "")
        options    = entry_data.get("options", [])
        name       = code_info.get("name_en" if CURRENT_LANG == "en" else "name", code_id)

        dlg = tk.Toplevel(self)
        dlg.title(name)
        dlg.geometry("320x200")
        dlg.resizable(False, False)
        dlg.configure(bg="#111")
        dlg.grab_set()

        make_label(dlg, name, fg=ACCENT2, bg="#111", font=FONT_NORMAL).pack(pady=(16, 8))

        sel_var = tk.StringVar()
        labels = [o.get("label_ar" if CURRENT_LANG == "ar" else "label", o["label"]) for o in options]
        sel_var.set(labels[0])

        for lbl in labels:
            tk.Radiobutton(dlg, text=lbl, variable=sel_var, value=lbl,
                           font=FONT_SMALL, fg=TEXT_MAIN, bg="#111",
                           activebackground="#111", selectcolor="#1a1a1a",
                           relief="flat").pack(anchor="w", padx=30, pady=2)

        def do_apply():
            idx = labels.index(sel_var.get())
            hex_bytes = options[idx]["bytes"]
            patch_b   = bytes.fromhex(hex_bytes)

            if APP_SETTINGS.get("real_time_mode", False):
                pid, handle = _rt_get_process_handle()
                if not pid:
                    messagebox.showerror("RT Error",
                        "bio4.exe not found." if CURRENT_LANG == "en" else "bio4.exe غير موجود.")
                    return
                base = _rt_get_module_base(pid, exe)
                if not base:
                    _ctypes.windll.kernel32.CloseHandle(handle)
                    messagebox.showerror("RT Error", "Could not read module base.")
                    return
                file_off = int(offset, 16)
                ram_addr = _rt_file_offset_to_ram(handle, base, file_off)
                if not ram_addr:
                    _ctypes.windll.kernel32.CloseHandle(handle)
                    messagebox.showerror("RT Error", f"Offset 0x{file_off:X} not mapped.")
                    return
                ok = _rt_patch_memory(handle, ram_addr, patch_b)
                _ctypes.windll.kernel32.CloseHandle(handle)
                if not ok:
                    messagebox.showerror("RT Error", "WriteProcessMemory failed.")
                    return
                # Permanent Activation: write to running EXE on disk
                if perm_activate:
                    _perm_pid, _perm_h = _rt_get_process_handle()
                    _perm_path = _rt_get_running_exe_path(_perm_pid) if _perm_pid else None
                    if _perm_h: _ctypes.windll.kernel32.CloseHandle(_perm_h)
                    perm_target = _perm_path if _perm_path and os.path.isfile(_perm_path) else exe
                    try:
                        with open(perm_target, "r+b") as f:
                            f.seek(int(offset, 16)); f.write(patch_b)
                    except Exception: pass
            else:
                try:
                    with open(exe, "r+b") as f:
                        off = int(offset, 16)
                        f.seek(off)
                        orig = f.read(len(patch_b))
                        backup = load_patch_backup()
                        backup.setdefault(code_id, {})[offset.upper().lstrip("0") or "0"] = orig.hex().upper()
                        save_patch_backup(backup)
                        f.seek(off)
                        f.write(patch_b)
                except Exception as ex:
                    messagebox.showerror("Error", str(ex))
                    return

            self.applied[code_id] = True
            write_log("APPLIED", name + " = " + sel_var.get(), exe)
            dlg.destroy()
            if not APP_SETTINGS.get("silent_apply", False):
                perm_note = "\n⚡ + Permanent" if perm_activate else ""
                messagebox.showinfo("[+] Applied", name + perm_note + "\n" + sel_var.get())
            self._after_state_change()

        make_button(dlg, "Apply" if CURRENT_LANG == "en" else "تطبيق",
                    do_apply, fg=GREEN, bg="#1a2a0a", active_bg="#2a4a1a", width=10
                    ).pack(pady=10)

    #  r11c Cabin Dialog 

    def _dialog_r11c_cabin(self, code_id):
        exe = self.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("Error", "Please select a valid bio4.exe first.")
            return

        dlg = tk.Toplevel(self)
        dlg.title("r11c Cabin Settings")
        dlg.geometry("340x260")
        dlg.resizable(False, False)
        dlg.configure(bg="#111")
        dlg.grab_set()

        make_label(dlg, "r11c Cabin Settings", fg=ACCENT2, bg="#111", font=FONT_NORMAL).pack(pady=(12, 8))

        fields = [
            ("Time Limit (Normal):", "4B44C5", 2, 120),
            ("Time Limit (Easy):",   "4B44D5", 2, 180),
            ("Enemy Count (Normal):", "4B44CC", 1, 15),
            ("Enemy Count (Easy):",   "4B44DC", 1, 10),
        ]
        vars_ = []
        for label, offset, bcount, default in fields:
            row = tk.Frame(dlg, bg="#111")
            row.pack(fill="x", padx=20, pady=3)
            make_label(row, label, fg=TEXT_DIM, bg="#111", font=FONT_TINY, width=22, anchor="w").pack(side="left")
            v = tk.StringVar(value=str(default))
            tk.Entry(row, textvariable=v, font=FONT_SMALL, fg=ACCENT2, bg="#1a1a1a",
                     insertbackground=ACCENT2, relief="flat", bd=0,
                     highlightthickness=1, highlightbackground=BORDER, width=8
                     ).pack(side="left", ipady=2)
            vars_.append((v, offset, bcount))

        def do_apply():
            try:
                with open(exe, "r+b") as f:
                    backup = load_patch_backup()
                    for v, offset, bcount in vars_:
                        dec_val = int(v.get().strip())
                        hex_bytes = dec_val.to_bytes(bcount, byteorder="little")
                        off = int(offset, 16)
                        f.seek(off)
                        orig = f.read(bcount)
                        backup.setdefault(code_id, {})[offset.upper().lstrip("0") or "0"] = orig.hex().upper()
                        f.seek(off)
                        f.write(hex_bytes)
                    save_patch_backup(backup)
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
                return
            self.applied[code_id] = True
            write_log("APPLIED", "r11c Cabin Settings", exe)
            dlg.destroy()
            if not APP_SETTINGS.get("silent_apply", False):
                messagebox.showinfo("[+] Applied", "r11c Cabin settings applied.")
            self._after_state_change()

        make_button(dlg, "Apply" if CURRENT_LANG == "en" else "تطبيق",
                    do_apply, fg=GREEN, bg="#1a2a0a", active_bg="#2a4a1a", width=10
                    ).pack(pady=10)

    #  Luis Cabin Dialog 

    def _dialog_luis_cabin(self, code_id):
        exe = self.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("Error", "Please select a valid bio4.exe first.")
            return

        dlg = tk.Toplevel(self)
        dlg.title("Luis Cabin Settings")
        dlg.geometry("340x260")
        dlg.resizable(False, False)
        dlg.configure(bg="#111")
        dlg.grab_set()

        make_label(dlg, "Luis Cabin Settings", fg=ACCENT2, bg="#111", font=FONT_NORMAL).pack(pady=(12, 8))

        fields = [
            ("Time Limit (Normal):",  "4B44C5", 2, 60),
            ("Time Limit (Easy):",    "4B44D5", 2, 90),
            ("Kill Count (Normal):",  "4B44CC", 1, 10),
            ("Kill Count (Easy):",    "4B44DC", 1, 8),
        ]
        vars_ = []
        for label, offset, bcount, default in fields:
            row = tk.Frame(dlg, bg="#111")
            row.pack(fill="x", padx=20, pady=3)
            make_label(row, label, fg=TEXT_DIM, bg="#111", font=FONT_TINY, width=22, anchor="w").pack(side="left")
            v = tk.StringVar(value=str(default))
            tk.Entry(row, textvariable=v, font=FONT_SMALL, fg=ACCENT2, bg="#1a1a1a",
                     insertbackground=ACCENT2, relief="flat", bd=0,
                     highlightthickness=1, highlightbackground=BORDER, width=8
                     ).pack(side="left", ipady=2)
            vars_.append((v, offset, bcount))

        def do_apply():
            try:
                with open(exe, "r+b") as f:
                    backup = load_patch_backup()
                    for v, offset, bcount in vars_:
                        dec_val = int(v.get().strip())
                        hex_bytes = dec_val.to_bytes(bcount, byteorder="little")
                        off = int(offset, 16)
                        f.seek(off)
                        orig = f.read(bcount)
                        backup.setdefault(code_id, {})[offset.upper().lstrip("0") or "0"] = orig.hex().upper()
                        f.seek(off)
                        f.write(hex_bytes)
                    save_patch_backup(backup)
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
                return
            self.applied[code_id] = True
            write_log("APPLIED", "Luis Cabin Settings", exe)
            dlg.destroy()
            if not APP_SETTINGS.get("silent_apply", False):
                messagebox.showinfo("[+] Applied", "Luis Cabin settings applied.")
            self._after_state_change()

        make_button(dlg, "Apply" if CURRENT_LANG == "en" else "تطبيق",
                    do_apply, fg=GREEN, bg="#1a2a0a", active_bg="#2a4a1a", width=10
                    ).pack(pady=10)

    #  Drawn Enemies During Camera Events Dialog 

    def _dialog_drawn_enemies_cam(self, code_id):
        """Select up to 4 rooms where enemies are drawn during camera events."""
        exe = self.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("Error", "Please select a valid bio4.exe first.")
            return

        dlg = tk.Toplevel(self)
        dlg.title("Drawn Enemies During Camera Events")
        dlg.geometry("360x280")
        dlg.resizable(False, False)
        dlg.configure(bg="#111")
        dlg.grab_set()

        make_label(dlg, "Drawn Enemies During Camera Events",
                   fg=ACCENT2, bg="#111", font=FONT_NORMAL).pack(pady=(14, 4))
        make_label(dlg,
                   "Enter up to 4 room IDs (e.g. 325, 31c, 21a, 30b)"
                   if CURRENT_LANG == "en" else
                   "أدخل حتى 4 غرف (مثال: 325، 31c، 21a، 30b)",
                   fg=MUTED, bg="#111", font=FONT_TINY).pack()

        vars_ = []
        for i in range(1, 5):
            row = tk.Frame(dlg, bg="#111")
            row.pack(fill="x", padx=30, pady=4)
            make_label(row, "Room " + str(i) + ":",
                       fg=TEXT_DIM, bg="#111", font=FONT_SMALL, width=8).pack(side="left")
            v = tk.StringVar()
            e = tk.Entry(row, textvariable=v, font=FONT_SMALL,
                         fg=ACCENT2, bg="#1a1a1a", insertbackground=ACCENT2,
                         relief="flat", bd=0,
                         highlightthickness=1, highlightbackground=BORDER, width=10)
            e.pack(side="left", ipady=2)
            self._add_paste_menu(e)
            vars_.append(v)

        def room_to_bytes(room_str):
            """Convert room ID like '325' or '30b' to 2-byte little-endian."""
            r = room_str.strip().lower().lstrip("r")
            if len(r) < 3:
                raise ValueError("Invalid room ID: " + room_str)
            last_two = r[-2:]   # e.g. '25'
            first    = r[:-2]   # e.g. '3'
            b0 = int(last_two, 16)
            b1 = int(first, 16)
            return bytes([b0, b1])

        def do_apply():
            rooms = [v.get().strip() for v in vars_ if v.get().strip()]
            if not rooms:
                messagebox.showerror("Error", "Enter at least one room ID.")
                return
            if len(rooms) > 4:
                messagebox.showerror("Error", "Maximum 4 rooms.")
                return

            # build the paste bytes  4 room slots, unused = FF FF
            room_bytes_list = []
            for r in rooms:
                try:
                    room_bytes_list.append(room_to_bytes(r))
                except Exception:
                    messagebox.showerror("Error", "Invalid room ID: " + r +
                                         "\nFormat: 3-digit hex e.g. 325, 30b, 21a")
                    return
            while len(room_bytes_list) < 4:
                room_bytes_list.append(b'\xff\xff')

            # build the offset_paste bytes with room IDs embedded
            # format: 53 8B 98 AC 4F 00 00 66 81 FB [R1] 74 1F 66 81 FB [R2] 74 18 66 81 FB [R3] 74 11 66 81 FB [R4] 74 0A 81 88 20 50 00 00 00 00 00 10 5B E9 F9 FE FF FF
            r = room_bytes_list
            paste_bytes = (
                bytes.fromhex("53 8B 98 AC 4F 00 00".replace(" ","")) +
                bytes.fromhex("66 81 FB".replace(" ","")) + r[0] +
                bytes.fromhex("74 1F 66 81 FB".replace(" ","")) + r[1] +
                bytes.fromhex("74 18 66 81 FB".replace(" ","")) + r[2] +
                bytes.fromhex("74 11 66 81 FB".replace(" ","")) + r[3] +
                bytes.fromhex("74 0A 81 88 20 50 00 00 00 00 00 10 5B E9 F9 FE FF FF".replace(" ",""))
            )

            # apply find_replace patch first
            try:
                with open(exe, "rb") as f:
                    exe_data = bytearray(f.read())

                find_b    = bytes.fromhex("81882050000000000010 8B153C5F".replace(" ",""))
                replace_b = bytes.fromhex("E9D9000000 9090909090 8B153C5F".replace(" ",""))
                idx = exe_data.find(find_b)
                if idx != -1:
                    exe_data[idx:idx+len(find_b)] = replace_b

                # write paste at 002BDBE8
                off = 0x2BDBE8
                exe_data[off:off+len(paste_bytes)] = paste_bytes

                backup = load_patch_backup()
                backup[code_id] = {"applied": True}
                save_patch_backup(backup)

                with open(exe, "wb") as f:
                    f.write(exe_data)
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
                return

            self.applied[code_id] = True
            write_log("APPLIED", "Drawn Enemies Cam - rooms: " + ", ".join(rooms), exe)
            dlg.destroy()
            if not APP_SETTINGS.get("silent_apply", False):
                messagebox.showinfo("[+] Applied",
                    "Drawn Enemies During Camera Events\nRooms: " + ", ".join("r" + r for r in rooms))
            self._after_state_change()

        make_button(dlg, "Apply" if CURRENT_LANG == "en" else "تطبيق",
                    do_apply, fg=GREEN, bg="#1a2a0a", active_bg="#2a4a1a", width=10
                    ).pack(pady=12)

    #  Custom Chapter Ending Screens Dialog 

    def _dialog_custom_ces(self, code_id):
        """Set room pairs for Custom Chapter Ending Screens."""
        exe = self.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("Error", "Please select a valid bio4.exe first.")
            return

        dlg = tk.Toplevel(self)
        dlg.title("Custom Chapter Ending Screens")
        dlg.geometry("460x420")
        dlg.resizable(False, True)
        dlg.configure(bg="#111")
        dlg.grab_set()

        make_label(dlg, "Custom Chapter Ending Screens",
                   fg=ACCENT2, bg="#111", font=FONT_NORMAL).pack(pady=(14, 4))
        make_label(dlg,
                   "Enter room pairs: Last Entered  Destination (up to 5 pairs)\n"
                   "Format: 3-digit hex e.g. 220, 20a, 10c\n"
                   "Leave blank to skip a subchapter (uses FF FF FF FF)"
                   if CURRENT_LANG == "en" else
                   "أدخل أزواج الغرف: آخر غرفة دخلتها  الوجهة (حتى 5 أزواج)\n"
                   "الصيغة: 3 أرقام hex مثال: 220، 20a، 10c\n"
                   "اتركها فارغة لتخطي فصل (يستخدم FF FF FF FF)",
                   fg=MUTED, bg="#111", font=FONT_TINY, justify="left").pack(padx=16, anchor="w")

        # headers
        hdr = tk.Frame(dlg, bg="#111")
        hdr.pack(fill="x", padx=20, pady=(8, 2))
        make_label(hdr, "#", fg=ACCENT, bg="#111", font=FONT_TINY, width=3).pack(side="left")
        make_label(hdr, "Last Entered Room" if CURRENT_LANG == "en" else "آخر غرفة",
                   fg=ACCENT, bg="#111", font=FONT_TINY, width=20).pack(side="left")
        make_label(hdr, "Destination Room" if CURRENT_LANG == "en" else "الوجهة",
                   fg=ACCENT, bg="#111", font=FONT_TINY, width=18).pack(side="left")

        pair_vars = []
        for i in range(1, 6):
            row = tk.Frame(dlg, bg="#111")
            row.pack(fill="x", padx=20, pady=3)
            make_label(row, str(i), fg=MUTED, bg="#111", font=FONT_TINY, width=3).pack(side="left")
            v_from = tk.StringVar()
            v_to   = tk.StringVar()
            for v in [v_from, v_to]:
                e = tk.Entry(row, textvariable=v, font=FONT_SMALL,
                             fg=ACCENT2, bg="#1a1a1a", insertbackground=ACCENT2,
                             relief="flat", bd=0,
                             highlightthickness=1, highlightbackground=BORDER, width=14)
                e.pack(side="left", ipady=2, padx=4)
                self._add_paste_menu(e)
            pair_vars.append((v_from, v_to))

        def room_to_bytes(room_str):
            r = room_str.strip().lower().lstrip("r")
            if len(r) < 3:
                raise ValueError("Invalid: " + room_str)
            b0 = int(r[-2:], 16)
            b1 = int(r[:-2], 16)
            return bytes([b0, b1])

        def do_apply():
            # build 10-byte pairs (5 pairs  4 bytes each + FF padding per subchapter)
            pair_bytes = b""
            valid_pairs = 0
            for v_from, v_to in pair_vars:
                f_str = v_from.get().strip()
                t_str = v_to.get().strip()
                if not f_str and not t_str:
                    pair_bytes += b"\xff\xff\xff\xff"
                    continue
                if not f_str or not t_str:
                    messagebox.showerror("Error",
                        "Each pair needs both rooms, or leave both empty.")
                    return
                try:
                    pair_bytes += room_to_bytes(f_str) + room_to_bytes(t_str)
                    valid_pairs += 1
                except Exception as ex:
                    messagebox.showerror("Error", str(ex))
                    return

            if valid_pairs == 0:
                messagebox.showerror("Error", "Enter at least one room pair.")
                return

            # apply base patches first via apply_patch
            ok, msg = apply_patch(exe, code_id, self.codes_data)
            if not ok:
                messagebox.showerror("Error", "Failed:\n" + msg)
                return

            # write room pairs at 00702578 (formerly 002C2D50)
            try:
                with open(exe, "r+b") as f:
                    f.seek(0x702578)
                    f.write(pair_bytes)
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
                return

            self.applied[code_id] = True
            write_log("APPLIED", "Custom CES - " + str(valid_pairs) + " pairs", exe)
            dlg.destroy()
            if not APP_SETTINGS.get("silent_apply", False):
                messagebox.showinfo("[+] Applied",
                    "Custom Chapter Ending Screens applied.\n" + str(valid_pairs) + " pair(s) set.")
            self._after_state_change()

        make_button(dlg, "Apply" if CURRENT_LANG == "en" else "تطبيق",
                    do_apply, fg=GREEN, bg="#1a2a0a", active_bg="#2a4a1a", width=10
                    ).pack(pady=10)

    #  Spawn Enemies Variant Dialog 

    def _dialog_spawn_enemies_variant(self, code_id):
        exe = self.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("Error", "Please select a valid bio4.exe first.")
            return

        _BG   = "#0b0b0b"
        _GOLD = "#c8a035"

        dlg = tk.Toplevel(self)
        dlg.title(t("تثبيت SPAWN ENEMY FROM ITA", "Install SPAWN ENEMY FROM ITA"))
        dlg.geometry("420x280")
        dlg.resizable(False, False)
        dlg.configure(bg=_BG)
        dlg.grab_set()
        dlg.transient(self)

        make_label(dlg,
                   t("اختر النسخة:", "Choose a version:"),
                   fg=_GOLD, bg=_BG, font=FONT_NORMAL).pack(pady=(16, 6))

        # Variant descriptions
        variants = [
            {
                "id":    "mr_curious",
                "label": "Mr.Curious Code",
                "desc_ar": "لا يُفعّل وحوش Crash Game  ·  (المنصوح به)",
                "desc_en": "Does not enable Crash Game monsters  ·  (Recommended)",
                "bytes_offset": "002B5848",
                "bytes": "B9 01 00 00 00 83 7D CC 00 74 1C 52 56 8B 75 CC 8B 56 50 83 FA 00 74 03 89 55 E0 8B 56 54 83 FA 00 74 02 8B C2 5E 5A E9 49 FD FF FF",
            },
            {
                "id":    "leo_lima",
                "label": "Leo Lima Code",
                "desc_ar": "يُفعّل وحوش Crash Game",
                "desc_en": "Enables Crash Game monsters",
                "bytes_offset": "002B5848",
                "bytes": "B9 01 00 00 00 83 7D CC 00 74 1C 52 56 8B 75 CC 8B 56 4F 83 FA 00 74 03 89 55 E0 8B 56 54 83 FA 00 74 02 8B C2 5E 5A E9 49 FD FF FF",
            },
        ]

        sel_var = tk.StringVar(value="mr_curious")

        for v in variants:
            row = tk.Frame(dlg, bg=_BG)
            row.pack(fill="x", padx=24, pady=4)
            tk.Radiobutton(
                row, text=v["label"],
                variable=sel_var, value=v["id"],
                fg=_GOLD if v["id"] == "mr_curious" else "#aaa",
                bg=_BG, activebackground=_BG, selectcolor="#111",
                font=("Courier New", 10, "bold"), relief="flat"
            ).pack(anchor="w")
            tk.Label(
                row,
                text=t(v["desc_ar"], v["desc_en"]),
                fg="#555", bg=_BG,
                font=("Courier New", 8)
            ).pack(anchor="w", padx=20)

        tk.Frame(dlg, bg="#222", height=1).pack(fill="x", padx=20, pady=10)

        def do_apply():
            chosen = next(v for v in variants if v["id"] == sel_var.get())
            # Apply base patches first (all except the offset_paste at 002B5848)
            base_entry = self.codes_data.get(code_id, {})
            patched_entry = {
                "patches": [
                    p for p in base_entry.get("patches", [])
                    if not (p.get("type") == "offset_paste"
                            and p.get("offset", "").upper() == "002B5848")
                ]
            }
            # Add chosen variant patch
            patched_entry["patches"].append({
                "type":   "offset_paste",
                "offset": chosen["bytes_offset"],
                "bytes":  chosen["bytes"],
            })

            # Temporarily inject patched entry
            self.codes_data["_spawn_enemies_tmp"] = patched_entry
            ok, msg = apply_patch(exe, "_spawn_enemies_tmp", self.codes_data)
            del self.codes_data["_spawn_enemies_tmp"]

            if not ok:
                messagebox.showerror("Error", msg)
                return

            self.applied[code_id] = True
            write_log("APPLIED", f"Spawn Enemies - {chosen['label']}", exe)
            dlg.destroy()
            if not APP_SETTINGS.get("silent_apply", False):
                messagebox.showinfo("[+] Applied",
                    t(f"تم تطبيق SPAWN ENEMY FROM ITA\nالنسخة: {chosen['label']}",
                      f"Spawn Enemy From ITA applied.\nVersion: {chosen['label']}"))
            self._after_state_change()

        btn_row = tk.Frame(dlg, bg=_BG)
        btn_row.pack(pady=4)
        make_button(btn_row, t("تطبيق", "Apply"), do_apply,
                    fg=GREEN, bg="#1a2a0a", active_bg="#2a4a1a", width=10
                    ).pack(side="left", padx=8)
        make_button(btn_row, t("إلغاء", "Cancel"), dlg.destroy,
                    fg="#888", bg="#1a1a1a", active_bg="#222", width=8
                    ).pack(side="left", padx=8)

    #  Memory Allocation Dialog 

    def _dialog_memory_alloc(self, code_id):
        exe = self.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("Error", "Please select a valid bio4.exe first.")
            return

        entry    = self.codes_data.get(code_id, {})
        options  = entry.get("options", [])
        off_exe  = entry.get("offsets_exe", [])
        off_dll  = entry.get("offsets_dll", [])

        # Step 1  ask about Tweaks DLL
        use_dll = messagebox.askyesno(
            "Tweaks DLL",
            "Are you using the Tweaks DLL (dinput8.dll)?\n\nYes = write to DLL\nNo = write to EXE"
            if CURRENT_LANG == "en" else
            "هل تستخدم Tweaks DLL (dinput8.dll)?\n\nنعم = يكتب في DLL\nلا = يكتب في EXE"
        )

        dll_path = ""
        if use_dll:
            dll_path = _browse_open(
                title="Select dinput8.dll" if CURRENT_LANG == "en" else "اختر dinput8.dll",
                filetypes=[("DLL file", "*.dll"), ("All files", "*.*")],
                key="dll"
            )
            if not dll_path:
                return

        # Step 2  show options dialog
        dlg = tk.Toplevel(self)
        dlg.title("Memory Allocation (MEM2)")
        dlg.geometry("300x160")
        dlg.resizable(False, False)
        dlg.configure(bg="#111")
        dlg.grab_set()

        make_label(dlg, "Memory Allocation (MEM2)",
                   fg=ACCENT2, bg="#111", font=FONT_NORMAL).pack(pady=(14, 4))
        make_label(dlg,
                   ("Writing to: DLL  " + os.path.basename(dll_path)) if use_dll
                   else "Writing to: EXE",
                   fg=MUTED, bg="#111", font=FONT_TINY).pack(pady=(0, 10))

        labels  = [o.get("label_ar" if CURRENT_LANG == "ar" else "label") for o in options]
        sel_var = tk.StringVar(value=labels[0])

        # combobox  fits all 17 options without scrolling issues
        import tkinter.ttk as ttk
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Dark.TCombobox",
                         fieldbackground="#1a1a1a", background="#1a1a1a",
                         foreground=ACCENT2, selectbackground="#2a2a2a",
                         selectforeground=ACCENT2)
        combo = ttk.Combobox(dlg, textvariable=sel_var,
                             values=labels, state="readonly",
                             font=FONT_SMALL, width=16,
                             style="Dark.TCombobox")
        combo.pack(pady=(0, 14))

        def do_apply():
            idx        = labels.index(sel_var.get())
            hex_bytes  = bytes.fromhex(options[idx]["bytes_le"])
            target     = dll_path if use_dll else exe
            offsets    = off_dll  if use_dll else off_exe
            try:
                with open(target, "r+b") as f:
                    backup = load_patch_backup()
                    for off_str in offsets:
                        off = int(off_str, 16)
                        f.seek(off)
                        orig = f.read(4)
                        backup.setdefault(code_id, {})[off_str.upper().lstrip("0") or "0"] = orig.hex().upper()
                        f.seek(off)
                        f.write(hex_bytes)
                    save_patch_backup(backup)
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
                return
            self.applied[code_id] = True
            write_log("APPLIED", "Memory Allocation = " + sel_var.get() +
                      (" (DLL)" if use_dll else " (EXE)"), exe)
            dlg.destroy()
            if not APP_SETTINGS.get("silent_apply", False):
                messagebox.showinfo("[+] Applied",
                    "Memory Allocation: " + sel_var.get() +
                    ("\nDLL: " + os.path.basename(dll_path) if use_dll else "\nEXE"))
            self._after_state_change()

        make_button(dlg, "Apply" if CURRENT_LANG == "en" else "تطبيق",
                    do_apply, fg=GREEN, bg="#1a2a0a", active_bg="#2a4a1a", width=10
                    ).pack()

    #  Random Ptas Dialog (ON/OFF + numeric) 

    def _dialog_random_ptas(self, code_id):
        """ON/OFF toggle + numeric field for random ptas amount."""
        exe = self.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("Error", "Please select a valid bio4.exe first.")
            return

        entry     = self.codes_data.get(code_id, {})
        code_info = self.code_by_id.get(code_id, {})
        name      = code_info.get("name_en" if CURRENT_LANG == "en" else "name", code_id)
        is_on     = self.applied.get(code_id, False)
        val_off   = entry.get("value_offset", "1B87FD")
        divide_by = entry.get("divide_by", 10)
        on_patch  = entry.get("on_patch", {})

        dlg = tk.Toplevel(self)
        dlg.title(name)
        dlg.geometry("300x175")
        dlg.resizable(False, False)
        dlg.configure(bg="#111")
        dlg.grab_set()

        make_label(dlg, name, fg=ACCENT2, bg="#111", font=FONT_NORMAL).pack(pady=(14, 10))

        # ON/OFF row
        row1 = tk.Frame(dlg, bg="#111")
        row1.pack(fill="x", padx=24, pady=4)
        make_label(row1,
                   "Enable random drops:" if CURRENT_LANG == "en" else "تفعيل الإسقاط العشوائي:",
                   fg=TEXT_DIM, bg="#111", font=FONT_SMALL, anchor="w"
                   ).pack(side="left", expand=True, fill="x")

        state_var = tk.BooleanVar(value=is_on)
        state_btn = tk.Button(row1, text="ON" if is_on else "OFF",
                              width=5, font=FONT_TINY,
                              fg=GREEN if is_on else "#bbbbbb",
                              bg="#2a5a2a" if is_on else "#1a1a1a",
                              relief="flat", bd=0,
                              highlightthickness=1,
                              highlightbackground=GREEN if is_on else "#888",
                              cursor="hand2")
        state_btn.pack(side="right")

        # Amount row
        row2 = tk.Frame(dlg, bg="#111")
        row2.pack(fill="x", padx=24, pady=4)
        make_label(row2,
                   "Amount (ptas):" if CURRENT_LANG == "en" else "الكمية (ptas):",
                   fg=TEXT_DIM, bg="#111", font=FONT_SMALL, anchor="w"
                   ).pack(side="left", expand=True, fill="x")

        # read current value
        try:
            with open(exe, "rb") as f:
                f.seek(int(val_off, 16))
                cur_raw = int.from_bytes(f.read(1), "little") * divide_by
        except Exception:
            cur_raw = entry.get("default_dec", 100)

        amt_var = tk.StringVar(value=str(cur_raw))
        amt_entry = tk.Entry(row2, textvariable=amt_var, font=FONT_NORMAL,
                             fg=ACCENT2 if is_on else MUTED,
                             bg="#1a1a1a", insertbackground=ACCENT2,
                             relief="flat", bd=0,
                             highlightthickness=1, highlightbackground=BORDER,
                             width=6, justify="center",
                             state="normal" if is_on else "disabled")
        amt_entry.pack(side="right", ipady=3)

        def toggle_state():
            nonlocal is_on
            is_on = not is_on
            state_var.set(is_on)
            state_btn.configure(
                text="ON" if is_on else "OFF",
                fg=GREEN if is_on else "#bbbbbb",
                bg="#2a5a2a" if is_on else "#1a1a1a",
                highlightbackground=GREEN if is_on else "#888"
            )
            amt_entry.configure(
                state="normal" if is_on else "disabled",
                fg=ACCENT2 if is_on else MUTED
            )

        state_btn.configure(command=toggle_state)

        def do_apply():
            # ON patch
            if is_on:
                on_bytes = bytes.fromhex(on_patch["bytes"].replace(" ", ""))
                off_on   = int(on_patch["offset"], 16)
                try:
                    with open(exe, "r+b") as f:
                        backup = load_patch_backup()
                        f.seek(off_on)
                        orig = f.read(len(on_bytes))
                        backup.setdefault(code_id, {})["ON"] = orig.hex().upper()
                        f.seek(off_on)
                        f.write(on_bytes)
                        # write amount
                        try:
                            amt = int(amt_var.get().strip()) // divide_by
                        except Exception:
                            amt = 10
                        val_off_int = int(val_off, 16)
                        f.seek(val_off_int)
                        f.write(bytes([amt]))
                        save_patch_backup(backup)
                except Exception as ex:
                    messagebox.showerror("Error", str(ex)); return
                self.applied[code_id] = True
            else:
                # revert
                ok, msg, _ = revert_patch(exe, ORIG_FILE, code_id, self.codes_data)
                if not ok:
                    messagebox.showerror("Error", msg); return
                self.applied[code_id] = False

            write_log("APPLIED" if is_on else "REVERTED", name, exe)
            dlg.destroy()
            if not APP_SETTINGS.get("silent_apply", False):
                messagebox.showinfo("[+] " + ("Applied" if is_on else "Reverted"), name)
            self._after_state_change()

        make_button(dlg, "Apply" if CURRENT_LANG == "en" else "تطبيق",
                    do_apply, fg=GREEN, bg="#1a2a0a", active_bg="#2a4a1a", width=10
                    ).pack(pady=10)

    def _dialog_punisher_pierce(self, code_id):
        exe = self.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("Error", "Please select a valid bio4.exe first.")
            return

        entry_data = self.codes_data.get(code_id, {})
        fields     = entry_data.get("fields", [])
        code_info  = self.code_by_id.get(code_id, {})
        name       = code_info.get("name_en" if CURRENT_LANG == "en" else "name", code_id)

        dlg = tk.Toplevel(self)
        dlg.title(name)
        dlg.geometry("280x195")
        dlg.resizable(False, False)
        dlg.configure(bg="#111")
        dlg.grab_set()

        make_label(dlg, name, fg=ACCENT2, bg="#111", font=FONT_NORMAL).pack(pady=(14, 8))

        field_vars = []
        for field in fields:
            lbl     = field.get("label_en" if CURRENT_LANG == "en" else "label_ar", "")
            default = field.get("default_dec", 0)
            try:
                with open(exe, "rb") as f:
                    f.seek(int(field["offset"], 16) + 1)
                    current = int.from_bytes(f.read(field["byte_count"] - 1), "little")
            except Exception:
                current = default

            row = tk.Frame(dlg, bg="#111")
            row.pack(fill="x", padx=24, pady=4)
            make_label(row, lbl, fg=TEXT_DIM, bg="#111",
                       font=FONT_TINY, anchor="w").pack(side="left", expand=True, fill="x")
            var = tk.StringVar(value=str(current))
            tk.Entry(row, textvariable=var, font=FONT_NORMAL,
                     fg=ACCENT2, bg="#1a1a1a", insertbackground=ACCENT2,
                     relief="flat", bd=0,
                     highlightthickness=1, highlightbackground=BORDER,
                     width=5, justify="center").pack(side="right", ipady=3)
            field_vars.append((var, field))

        def do_apply():
            try:
                backup = load_patch_backup()
                with open(exe, "r+b") as fh:
                    for var, field in field_vars:
                        val = int(var.get().strip())
                        if val < 0: raise ValueError
                        hb  = bytes([0xB8]) + val.to_bytes(field["byte_count"] - 1, "little")
                        off = int(field["offset"], 16)
                        fh.seek(off); orig = fh.read(field["byte_count"])
                        backup.setdefault(code_id, {})[field["offset"].upper().lstrip("0") or "0"] = orig.hex().upper()
                        fh.seek(off); fh.write(hb)
                save_patch_backup(backup)
            except Exception as ex:
                messagebox.showerror("Error", str(ex)); return
            self.applied[code_id] = True
            write_log("APPLIED", name, exe)
            dlg.destroy()
            if not APP_SETTINGS.get("silent_apply", False):
                messagebox.showinfo("[+] Applied", name)
            self._after_state_change()

        make_button(dlg, "Apply" if CURRENT_LANG == "en" else "تطبيق",
                    do_apply, fg=GREEN, bg="#1a2a0a", active_bg="#2a4a1a", width=10
                    ).pack(pady=10)

    def _dialog_link_tweaks(self, code_id):
        """Dialog for link tweaks with EXE code."""
        # check if already applied (scan detects via offset 7212FC)
        # detect: bytes at 7212FC != 31 2E 30 2E 36 means ON
        exe = self.exe_path.get().strip()

        dlg = tk.Toplevel(self)
        dlg.title("Link Tweaks with EXE" if CURRENT_LANG == "en" else "ربط التويكس مع EXE")
        dlg.geometry("420x300")
        dlg.resizable(False, False)
        dlg.configure(bg="#111")
        dlg.grab_set()

        make_label(dlg,
                   "Link Tweaks with EXE" if CURRENT_LANG == "en" else "ربط التويكس مع EXE",
                   fg=ACCENT2, bg="#111", font=FONT_NORMAL
                   ).pack(pady=(16, 4))
        make_label(dlg,
                   "Enter a 5-character keyword (e.g. 3MKOO)"
                   if CURRENT_LANG == "en" else
                   "أدخل كلمة من 5 أحرف (مثال: 3MKOO)",
                   fg=MUTED, bg="#111", font=FONT_TINY
                   ).pack(pady=(0, 10))

        fields_frame = tk.Frame(dlg, bg="#111")
        fields_frame.pack(fill="x", padx=20)

        def add_row(label_text, default="", browse=False, is_dll=False):
            row = tk.Frame(fields_frame, bg="#111")
            row.pack(fill="x", pady=3)
            make_label(row, label_text, fg=TEXT_DIM, bg="#111",
                       font=FONT_TINY, width=20, anchor="w"
                       ).pack(side="left")
            var = tk.StringVar(value=default)
            e = tk.Entry(row, textvariable=var,
                         font=FONT_SMALL, fg=ACCENT2, bg="#1a1a1a",
                         insertbackground=ACCENT2, relief="flat", bd=0,
                         highlightthickness=1, highlightbackground=BORDER,
                         width=22)
            e.pack(side="left", ipady=2)
            self._add_paste_menu(e)
            if browse:
                def pick(v=var, dll=is_dll):
                    ft = [("DLL file", "*.dll"), ("All files", "*.*")] if dll \
                         else [("Executable", "*.exe"), ("All files", "*.*")]
                    p = _browse_open(
                        title="Select File",
                        filetypes=ft,
                        key="exe" if "exe" in str(ft).lower() else "misc"
                    )
                    if p:
                        v.set(p)
                make_button(row, "...", pick,
                            fg=ACCENT, bg="#2a2a1a", active_bg="#3a3a2a",
                            font=FONT_TINY, width=3
                            ).pack(side="left", padx=4)
            return var

        exe_var  = add_row("EXE path:", exe, browse=True, is_dll=False)
        word_var = add_row("Keyword (5 chars):", "")
        dll_var  = add_row("DLL path:", "", browse=True, is_dll=True)

        # word length validation
        def on_word_change(*_):
            w = word_var.get()
            if len(w) > 5:
                word_var.set(w[:5])

        word_var.trace_add("write", on_word_change)

        def do_apply():
            exe_path = exe_var.get().strip()
            word     = word_var.get().strip()
            dll_path = dll_var.get().strip()

            if not exe_path or not os.path.isfile(exe_path):
                messagebox.showerror("Error", "Invalid EXE path.")
                return
            if len(word) != 5:
                messagebox.showerror("Error",
                    "Keyword must be exactly 5 characters."
                    if CURRENT_LANG == "en" else
                    "الكلمة لازم تكون 5 أحرف بالضبط.")
                return

            # convert word to hex bytes
            word_bytes = word.encode("ascii").hex().upper()
            word_spaced = " ".join(word_bytes[i:i+2] for i in range(0, len(word_bytes), 2))

            # build patches
            patches = [
                {"type": "offset_replace", "offset": "7212FC", "bytes": word_spaced},
            ]
            if dll_path and os.path.isfile(dll_path):
                patches.append({"type": "offset_replace", "offset": "894054",
                                 "bytes": word_spaced})

            # apply directly
            try:
                with open(exe_path, "rb") as f:
                    exe_data = bytearray(f.read())
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return

            backup = load_patch_backup()
            code_backup = {}
            for p in patches:
                target = exe_path if p["offset"] == "7212FC" else dll_path
                try:
                    with open(target, "r+b") as f:
                        off = int(p["offset"], 16)
                        data_b = bytes.fromhex(p["bytes"].replace(" ", ""))
                        f.seek(off)
                        orig_b = f.read(len(data_b))
                        code_backup[p["offset"]] = orig_b.hex().upper()
                        f.seek(off)
                        f.write(data_b)
                except Exception as e:
                    messagebox.showerror("Error", "Failed at offset " + p["offset"] + ":\n" + str(e))
                    return

            backup[code_id] = code_backup
            save_patch_backup(backup)
            self.applied[code_id] = True
            write_log("APPLIED", "Link Tweaks with EXE -- keyword: " + word, exe_path)
            dlg.destroy()
            messagebox.showinfo("[+] Applied",
                                "Tweaks linked with keyword: " + word
                                if CURRENT_LANG == "en" else
                                "تم ربط التويكس بالكلمة: " + word)
            self._after_state_change()

        make_button(dlg, "Apply" if CURRENT_LANG == "en" else "تطبيق",
                    do_apply, fg=GREEN, bg="#1a2a0a", active_bg="#2a4a1a", width=12
                    ).pack(pady=14)

    def _dialog_bgm_files(self, code_id):
        #  Step 1: ask how many files 
        dlg1 = tk.Toplevel(self)
        dlg1.title("Additional BGM Files")
        dlg1.geometry("340x160")
        dlg1.resizable(False, False)
        dlg1.configure(bg="#111")
        dlg1.grab_set()

        make_label(dlg1, "How many BGM files to add? (max 8)",
                   fg=ACCENT2, bg="#111", font=FONT_NORMAL
                   ).pack(pady=(18, 6))
        make_label(dlg1, "Each file = one XWB + one XSB pair",
                   fg=MUTED, bg="#111", font=FONT_TINY
                   ).pack()

        count_var = tk.IntVar(value=1)
        spin_frame = tk.Frame(dlg1, bg="#111")
        spin_frame.pack(pady=10)
        tk.Spinbox(
            spin_frame, from_=1, to=8,
            textvariable=count_var, width=5,
            font=FONT_NORMAL, fg=ACCENT2, bg="#1a1a1a",
            buttonbackground="#2a2a2a",
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground=BORDER
        ).pack(side="left", ipady=4)

        def next_step():
            n = count_var.get()
            dlg1.destroy()
            self._dialog_bgm_names(code_id, n)

        btn_row = tk.Frame(dlg1, bg="#111")
        btn_row.pack(pady=4)
        make_button(btn_row, "Next >>", next_step,
                    fg=GREEN, bg="#1a2a0a", active_bg="#2a4a1a", width=10
                    ).pack(side="left", padx=8)
        make_button(btn_row, "Cancel", dlg1.destroy,
                    fg=MUTED, bg="#1a1a1a", active_bg="#2a2a2a", width=8
                    ).pack(side="left", padx=4)

    def _dialog_bgm_names(self, code_id, count):
        MAX_NAME = 20   # BIO4\snd\ = 10 chars, name+ext  22 chars, total  32
        ENTRY_SIZE = 32 # bytes per entry (matches game expectation)
        BASE_PATH = "BIO4\\snd\\"

        dlg2 = tk.Toplevel(self)
        dlg2.title("BGM File Names")
        dlg2.geometry("420x" + str(80 + count * 56))
        dlg2.resizable(False, True)
        dlg2.configure(bg="#111")
        dlg2.grab_set()

        make_label(dlg2, "Enter file names (without path or extension):",
                   fg=ACCENT2, bg="#111", font=FONT_SMALL
                   ).pack(pady=(14, 4), padx=16, anchor="w")
        make_label(dlg2, "Example: 1234567   ->  BIO4\\snd\\1234567.xwb / .xsb",
                   fg=MUTED, bg="#111", font=FONT_TINY
                   ).pack(padx=16, anchor="w")

        entries = []
        for i in range(count):
            row = tk.Frame(dlg2, bg="#111")
            row.pack(fill="x", padx=16, pady=4)
            make_label(row, "File " + str(i + 1) + ":",
                       fg=TEXT_DIM, bg="#111", font=FONT_TINY, width=7
                       ).pack(side="left")
            var = tk.StringVar()
            tk.Entry(
                row, textvariable=var,
                font=FONT_SMALL, fg=ACCENT2, bg="#1a1a1a",
                insertbackground=ACCENT2,
                relief="flat", bd=0,
                highlightthickness=1, highlightbackground=BORDER,
                width=24
            ).pack(side="left", ipady=3)
            entries.append(var)

        def do_apply():
            # validate
            names = [v.get().strip() for v in entries]
            for i, name in enumerate(names):
                if not name:
                    messagebox.showerror("Error", "File " + str(i+1) + " name is empty.")
                    return
                full = BASE_PATH + name + ".xwb"
                if len(full) > ENTRY_SIZE - 1:   # -1 for null terminator
                    messagebox.showerror("Error",
                        "File " + str(i+1) + " name too long.\n"
                        "Max " + str(ENTRY_SIZE - 1 - len(BASE_PATH) - 4) + " characters.")
                    return

            # build the 32-byte entries: XWB then XSB for each file, packed together
            # layout: [xwb_entry_32][xsb_entry_32] per file, sequential
            payload = bytearray()
            for name in names:
                xwb = (BASE_PATH + name + ".xwb").encode("ascii")
                xsb = (BASE_PATH + name + ".xsb").encode("ascii")
                # pad each to ENTRY_SIZE bytes with nulls
                xwb_entry = xwb + b'\x00' * (ENTRY_SIZE - len(xwb))
                xsb_entry = xsb + b'\x00' * (ENTRY_SIZE - len(xsb))
                payload += xwb_entry + xsb_entry

            # patch the additional_bgm code normally first (the JMP patches)
            # then write the string table at 0x0078C200
            dlg2.destroy()

            exe = self.exe_path.get().strip()
            if not exe or not os.path.isfile(exe):
                messagebox.showerror("Error", "EXE path is invalid.")
                return

            # apply the code patches (JMP hooks) first
            ok, msg = apply_patch(exe, code_id, self.codes_data)
            if not ok:
                messagebox.showerror("Error", "Failed applying BGM patches:\n" + msg)
                return

            # now write the string table
            STRING_TABLE_OFFSET = 0x0078C200
            try:
                with open(exe, "r+b") as f:
                    f.seek(STRING_TABLE_OFFSET)
                    # clear the area first (8 files max * 2 entries * 32 bytes)
                    f.write(b'\x00' * (8 * 2 * ENTRY_SIZE))
                    f.seek(STRING_TABLE_OFFSET)
                    f.write(bytes(payload))
            except Exception as e:
                messagebox.showerror("Error", "Failed writing string table:\n" + str(e))
                return

            self.applied[code_id] = True
            self._refresh_all()
            self._update_statusbar()
            self._update_apply_bar()

            summary = "BGM files written:\n"
            for name in names:
                summary += "  " + BASE_PATH + name + ".xwb/.xsb\n"
            messagebox.showinfo("[+] Done", summary)

        btn_row = tk.Frame(dlg2, bg="#111")
        btn_row.pack(pady=8)
        make_button(btn_row, "Apply", do_apply,
                    fg=GREEN, bg="#1a2a0a", active_bg="#2a4a1a", width=10
                    ).pack(side="left", padx=8)
        make_button(btn_row, "Cancel", dlg2.destroy,
                    fg=MUTED, bg="#1a1a1a", active_bg="#2a2a2a", width=8
                    ).pack(side="left", padx=4)

    def _dialog_mod_expansion(self, code_id):
        dlg = tk.Toplevel(self)
        dlg.title("Enemy Spawn Persistence")
        dlg.geometry("380x180")
        dlg.resizable(False, False)
        dlg.configure(bg="#111")
        dlg.grab_set()

        make_label(dlg, (fix_ar("هل انت مفعل EnableModExpansion؟") if CURRENT_LANG == "ar" else "Is EnableModExpansion active?"),
                   fg=ACCENT2, bg="#111", font=FONT_NORMAL
                   ).pack(pady=(20, 6))
        make_label(dlg, (fix_ar("سيؤثر هاذا على الكود اللي راح ينحط في EXE") if CURRENT_LANG == "ar" else "This affects the code written to EXE"),
                   fg=MUTED, bg="#111", font=FONT_TINY
                   ).pack()

        btn_frame = tk.Frame(dlg, bg="#111")
        btn_frame.pack(pady=20)

        make_button(btn_frame, "[Y] Yes",
                    lambda: [dlg.destroy(),
                             self._do_apply(code_id, mod_expansion=True)],
                    fg=GREEN, bg="#1a2a0a", active_bg="#2a4a1a", width=9
                    ).pack(side="left", padx=8)
        make_button(btn_frame, "[N] No",
                    lambda: [dlg.destroy(),
                             self._do_apply(code_id, mod_expansion=False)],
                    fg=RED_SOFT, bg="#2a0a0a", active_bg="#4a1a1a", width=9
                    ).pack(side="left", padx=8)
        make_button(btn_frame, "Cancel", dlg.destroy,
                    fg=MUTED, bg="#1a1a1a", active_bg="#2a2a2a", width=9
                    ).pack(side="left", padx=8)

    def _do_apply(self, code_id, mod_expansion=None):
        exe = self.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("Error", "EXE path is invalid.")
            return

        # ── Real-Time mode ──
        if APP_SETTINGS.get("real_time_mode", False):
            self._handle_dll_mutex(code_id)
            ok, result = rt_apply_patch(exe, code_id, self.codes_data)
            if ok:
                self.applied[code_id] = True
                self._rt_originals[code_id] = result

                # Permanent Activation: write to the running EXE on disk
                row = self.code_rows.get(code_id)
                if row and getattr(row, "perm_var", None) and row.perm_var.get():
                    running_exe = _rt_get_running_exe_path(pid)
                    perm_target = running_exe if running_exe and os.path.isfile(running_exe) else exe
                    ok2, msg2 = apply_patch(perm_target, code_id, self.codes_data, mod_expansion)
                    if ok2:
                        backup  = load_patch_backup()
                        details = build_log_details(code_id, self.codes_data, backup)
                        write_log("PERM-APPLIED", self.code_by_id[code_id]["name"], perm_target, details)

                write_log("RT-APPLIED", self.code_by_id[code_id]["name"], exe)
                if not APP_SETTINGS.get("silent_apply", False):
                    perm_note = ("\n⚡ + Permanent (written to file)"
                                 if row and getattr(row, "perm_var", None) and row.perm_var.get()
                                 else "")
                    messagebox.showinfo("[+] RT Applied",
                        "Code applied in real-time:" + perm_note + "\n" + self.code_by_id[code_id]["name"])
                self._after_state_change()
            else:
                messagebox.showerror("RT Error", "Real-Time patch failed:\n" + result)
            return

        # ── Normal mode ──
        if is_game_running(exe):
            messagebox.showerror(
                "Game is Running" if CURRENT_LANG == "en" else "اللعبة شغالة",
                "Please close the game before applying codes.\nClose bio4.exe and try again."
                if CURRENT_LANG == "en" else
                "طفي اللعبة أول عشان تقدر تفعل الكود.\nأغلق bio4.exe وحاول مرة ثانية."
            )
            return
        self._handle_dll_mutex(code_id)
        ok, msg = apply_patch(exe, code_id, self.codes_data, mod_expansion)
        if ok:
            self.applied[code_id] = True
            backup  = load_patch_backup()
            details = build_log_details(code_id, self.codes_data, backup)
            write_log("APPLIED", self.code_by_id[code_id]["name"], exe, details)
            if not APP_SETTINGS.get("silent_apply", False):
                messagebox.showinfo(
                    "[+] Applied",
                    "Code applied:\n" + self.code_by_id[code_id]["name"]
                )
            self._after_state_change()
        else:
            messagebox.showerror("Error", "Failed:\n" + msg)

    #  Apply Selected 

    def on_row_select_change(self):
        self._update_apply_bar()

    def _update_apply_bar(self):
        n = len(self._global_selected)
        self.selected_count_var.set(str(n) + " selected")

    def _select_all(self):
        for cid, row in self.code_rows.items():
            if self._is_unlocked(cid) and not self.applied.get(cid, False):
                row.sel_var.set(1)
                row.selected = True
                self._global_selected.add(cid)
        self._refresh_all()
        self._update_apply_bar()

    def _clear_selection(self):
        for row in self.code_rows.values():
            row.sel_var.set(0)
            row.selected = False
        self._global_selected.clear()
        self._refresh_all()
        self._update_apply_bar()

    def _apply_selected(self):
        exe = self.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("Error", "Please select a valid bio4.exe first.")
            return

        queue = [cid for cid in self._global_selected
                 if not self.applied.get(cid, False)]

        if not queue:
            messagebox.showinfo("Info", "No codes selected.")
            return

        needs_dialog = [c for c in queue
                        if self.code_by_id.get(c, {}).get("dialog") == "mod_expansion"]
        if needs_dialog:
            self._dialog_mod_expansion_batch(queue)
        else:
            self._run_apply_queue(queue, mod_expansion=None)

    def _dialog_mod_expansion_batch(self, full_queue):
        dlg = tk.Toplevel(self)
        dlg.title("Enemy Spawn Persistence")
        dlg.geometry("380x180")
        dlg.resizable(False, False)
        dlg.configure(bg="#111")
        dlg.grab_set()

        make_label(dlg, (fix_ar("هل انت مفعل EnableModExpansion؟") if CURRENT_LANG == "ar" else "Is EnableModExpansion active?"),
                   fg=ACCENT2, bg="#111", font=FONT_NORMAL
                   ).pack(pady=(20, 6))
        make_label(dlg, (fix_ar("سيؤثر هاذا على الكود اللي راح ينحط في EXE") if CURRENT_LANG == "ar" else "This affects the code written to EXE"),
                   fg=MUTED, bg="#111", font=FONT_TINY
                   ).pack()

        btn_frame = tk.Frame(dlg, bg="#111")
        btn_frame.pack(pady=20)

        make_button(btn_frame, "[Y] Yes",
                    lambda: [dlg.destroy(),
                             self._run_apply_queue(full_queue, mod_expansion=True)],
                    fg=GREEN, bg="#1a2a0a", active_bg="#2a4a1a", width=9
                    ).pack(side="left", padx=8)
        make_button(btn_frame, "[N] No",
                    lambda: [dlg.destroy(),
                             self._run_apply_queue(full_queue, mod_expansion=False)],
                    fg=RED_SOFT, bg="#2a0a0a", active_bg="#4a1a1a", width=9
                    ).pack(side="left", padx=8)
        make_button(btn_frame, "Cancel", dlg.destroy,
                    fg=MUTED, bg="#1a1a1a", active_bg="#2a2a2a", width=9
                    ).pack(side="left", padx=8)

    def _run_apply_queue(self, queue, mod_expansion=None):
        exe = self.exe_path.get().strip()
        success, failed = [], []

        for code_id in queue:
            self._handle_dll_mutex(code_id)
            me = mod_expansion if self.code_by_id.get(
                code_id, {}).get("dialog") == "mod_expansion" else None
            ok, msg = apply_patch(exe, code_id, self.codes_data, me)
            if ok:
                self.applied[code_id] = True
                details = build_log_details(code_id, self.codes_data, load_patch_backup())
                write_log("APPLIED", self.code_by_id.get(code_id, {}).get("name", code_id), exe, details)
                success.append(code_id)
            else:
                failed.append((code_id, msg))

        summary = "Applied " + str(len(success)) + " code(s) successfully."
        if failed:
            summary += "\n\nFailed:\n"
            for cid, err in failed:
                summary += "- " + self.code_by_id[cid]["name"] + "\n  " + err + "\n"
            messagebox.showwarning("Done with errors", summary)
        else:
            messagebox.showinfo("[+] Done", summary)

        # clear all selections after apply
        self._global_selected.clear()
        self._after_state_change()

    #  refresh 

    def _refresh_row(self, code_id):
        row = self.code_rows.get(code_id)
        if not row:
            return
        row.refresh(
            applied  = self.applied.get(code_id, False),
            locked   = not self._is_unlocked(code_id),
            detected = self.detected.get(code_id, False)
        )

    def _refresh_all(self):
        """Refresh all visible rows in current section."""
        for cid in list(self.code_rows.keys()):
            self._refresh_row(cid)

    def _after_state_change(self):
        scroll_pos = self.codes_canvas.yview()[0]
        self._refresh_all()
        if self.active_section:
            self.select_section(self.active_section, preserve_scroll=scroll_pos)
        self._update_statusbar()
        self._update_apply_bar()

    #  mutual exclusion: codes sharing same offsets 
    # Format: code_id -> list of conflicting code_ids
    OFFSET_MUTEX = {
        # DLL apply codes share offset 156
        "apply_dll_qingsheng": ["apply_dll_raz0r"],
        "apply_dll_raz0r":     ["apply_dll_qingsheng"],
        # missing sound fixes share same patches - mutually exclusive
        "sound_fix":       ["sound_fix_raz0r"],
        "sound_fix_raz0r": ["sound_fix"],
        # bodies disappear/no-disappear share same offsets
        "bodies_disappear":    ["bodies_no_disappear"],
        "bodies_no_disappear": ["bodies_disappear"],
        # verdugo versions share same find pattern + offset C2440
        "verdugo_no_teleport":       ["verdugo_no_teleport_raz0r"],
        "verdugo_no_teleport_raz0r": ["verdugo_no_teleport"],
        # saw: killable vs survive chainsaw share offset 3E4E3
        "saw_killable":     ["survive_chainsaw"],
        "survive_chainsaw": ["saw_killable"],
        # u3: esl vs form1 share offset 1034CA
        "u3_esl":        ["u3_form1_kill"],
        "u3_form1_kill": ["u3_esl"],
        # u3: form1 vs die_in_place share offset FE9C2
        "u3_form1_kill":  ["u3_die_in_place"],
        "u3_die_in_place": ["u3_form1_kill"],
        # xwb sideload vs em_xwb_xsb share offset 575487
        "xwb_sideload_r": ["em_xwb_xsb"],
        "em_xwb_xsb":     ["xwb_sideload_r"],
        # cns_x4 disables max_em_count when enabled, but not vice versa
        "cns_x4": ["max_em_count"],
    }

    def _handle_dll_mutex(self, code_id):
        """Revert all conflicting codes before applying code_id."""
        conflicts = self.OFFSET_MUTEX.get(code_id, [])
        exe = self.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            return
        for other in conflicts:
            if self.applied.get(other, False):
                ok, _, _ = revert_patch(exe, ORIG_FILE, other, self.codes_data)
                if ok:
                    self.applied[other] = False
                    self.detected[other] = False

    def _dialog_mod_expansion_batch_profile(self, queue, exe):
        """Called when profile queue contains enemy_persistence."""
        dlg = tk.Toplevel(self)
        dlg.title("Enemy Spawn Persistence")
        dlg.geometry("380x190")
        dlg.resizable(False, False)
        dlg.configure(bg="#111")
        dlg.grab_set()

        make_label(dlg,
                   "Is EnableModExpansion active?" if CURRENT_LANG == "en"
                   else (fix_ar("هل انت مفعل EnableModExpansion؟") if CURRENT_LANG == "ar" else "Is EnableModExpansion active?"),
                   fg=ACCENT2, bg="#111", font=FONT_NORMAL
                   ).pack(pady=(20, 6))
        make_label(dlg,
                   "This affects the enemy_persistence code in the profile."
                   if CURRENT_LANG == "en"
                   else (fix_ar("سيؤثر هاذا على كود enemy_persistence في البروفايل") if CURRENT_LANG == "ar" else "This affects enemy_persistence in the profile"),
                   fg=MUTED, bg="#111", font=FONT_TINY
                   ).pack()

        btn_frame = tk.Frame(dlg, bg="#111")
        btn_frame.pack(pady=20)

        def run(mod_exp):
            dlg.destroy()
            success, failed = [], []
            for cid in queue:
                self._handle_dll_mutex(cid)
                me = mod_exp if self.code_by_id.get(cid, {}).get("dialog") == "mod_expansion" else None
                ok, msg = apply_patch(exe, cid, self.codes_data, me)
                if ok:
                    self.applied[cid] = True
                    write_log("APPLIED (profile)", self.code_by_id.get(cid, {}).get("name", cid), exe)
                    success.append(cid)
                else:
                    failed.append((cid, msg))
                    break
            summary = "Applied " + str(len(success)) + " code(s)."
            if failed:
                summary += "\n\nStopped at:\n"
                for cid, err in failed:
                    summary += "- " + self.code_by_id.get(cid, {}).get("name", cid) + "\n  " + err + "\n"
                messagebox.showwarning("Done with errors", summary)
            else:
                messagebox.showinfo("[+] Done", summary)
            self._after_state_change()

        make_button(btn_frame, "[Y] Yes", lambda: run(True),
                    fg=GREEN, bg="#1a2a0a", active_bg="#2a4a1a", width=9
                    ).pack(side="left", padx=8)
        make_button(btn_frame, "[N] No", lambda: run(False),
                    fg=RED_SOFT, bg="#2a0a0a", active_bg="#4a1a1a", width=9
                    ).pack(side="left", padx=8)
        make_button(btn_frame, "Cancel", dlg.destroy,
                    fg=MUTED, bg="#1a1a1a", active_bg="#2a2a2a", width=9
                    ).pack(side="left", padx=8)

    def _update_statusbar(self):
        n_applied  = sum(1 for v in self.applied.values() if v)
        n_detected = sum(1 for v in self.detected.values() if v)
        n_total    = len(self.all_codes)
        self.status_applied_var.set(
            ("Applied: " if CURRENT_LANG == "en" else "مفعّل: ") + str(n_applied))
        self.status_detected_var.set(
            ("Detected: " if CURRENT_LANG == "en" else "مكتشف: ") + str(n_detected))
        self.status_exe_var.set(
            ("[OK] EXE Loaded" if CURRENT_LANG == "en" else "[OK] EXE محمّل")
            if self.scanned else "")
        self.status_total_var.set(
            ("Total codes: " if CURRENT_LANG == "en" else "إجمالي الأكواد: ") + str(n_total))

    #  Search 

    def _on_search(self):
        query = self.search_var.get().strip().lower()
        # clear old results
        for w in self.search_results_frame.winfo_children():
            w.destroy()

        if not query:
            self.search_results_outer.pack_forget()
            return

        # find matching codes
        matches = []
        for code in self.all_codes:
            name    = code.get("name_en" if CURRENT_LANG == "en" else "name", "")
            desc    = code.get("desc_en" if CURRENT_LANG == "en" else "desc", "")
            if query in name.lower() or query in desc.lower():
                matches.append(code)

        if not matches:
            make_label(self.search_results_frame,
                       text="No results found" if CURRENT_LANG == "en" else "ما في نتائج",
                       fg=MUTED, bg="#0d0d1a", font=FONT_TINY
                       ).pack(padx=8, pady=4)
        else:
            for code in matches[:12]:  # max 12 results
                sec = next((s for s in self.sections_list if s["id"] == code["section"]), None)
                sec_label = sec.get("label_en" if CURRENT_LANG == "en" else "label", "") if sec else ""
                name = code.get("name_en" if CURRENT_LANG == "en" else "name", code["name"])

                row = tk.Frame(self.search_results_frame, bg="#0d0d1a",
                               cursor="hand2")
                row.pack(fill="x", padx=4, pady=1)

                make_label(row, text=name,
                           fg=ACCENT2, bg="#0d0d1a", font=FONT_TINY
                           ).pack(side="left", padx=6, pady=2)
                make_label(row, text="[" + sec_label + "]",
                           fg=MUTED, bg="#0d0d1a", font=FONT_TINY
                           ).pack(side="left")

                # click -> go to section and highlight
                def _goto(c=code):
                    self._clear_search()
                    self.select_section(c["section"])
                    # scroll to the row
                    self.after(100, lambda: self._scroll_to_code(c["id"]))

                row.bind("<Button-1>", lambda e, c=code: _goto(c))
                for child in row.winfo_children():
                    child.bind("<Button-1>", lambda e, c=code: _goto(c))

        self.search_results_outer.pack(fill="x", padx=10, pady=(0, 4))

    def _scroll_to_code(self, code_id):
        row = self.code_rows.get(code_id)
        if not row:
            return
        self.codes_canvas.update_idletasks()
        row.update_idletasks()
        # get row y position relative to codes_inner
        y = row.winfo_y()
        total = self.codes_inner.winfo_height()
        if total > 0:
            frac = y / total
            self.codes_canvas.yview_moveto(frac)

    def _clear_search(self):
        self.search_var.set("")
        self.search_results_outer.pack_forget()
        for w in self.search_results_frame.winfo_children():
            w.destroy()

    #  Profiles 

    def _new_profile(self):
        dlg = tk.Toplevel(self)
        dlg.title("New Profile")
        dlg.geometry("500x520")
        dlg.resizable(False, True)
        dlg.configure(bg="#111")
        dlg.grab_set()

        make_label(dlg, "Profile Name:",
                   fg=ACCENT2, bg="#111", font=FONT_NORMAL
                   ).pack(pady=(16, 4), padx=16, anchor="w")
        name_var = tk.StringVar()
        tk.Entry(dlg, textvariable=name_var,
                 font=FONT_SMALL, fg=ACCENT2, bg="#1a1a1a",
                 insertbackground=ACCENT2, relief="flat", bd=0,
                 highlightthickness=1, highlightbackground=BORDER,
                 width=40
                 ).pack(padx=16, ipady=3, anchor="w")

        make_label(dlg, "Select codes to include:",
                   fg=TEXT_DIM, bg="#111", font=FONT_SMALL
                   ).pack(pady=(12, 4), padx=16, anchor="w")

        # scrollable checklist
        list_outer = tk.Frame(dlg, bg="#111")
        list_outer.pack(fill="both", expand=True, padx=16)
        list_canvas = tk.Canvas(list_outer, bg="#1a1a1a",
                                highlightthickness=1,
                                highlightbackground=BORDER, height=300)
        list_scroll = tk.Scrollbar(list_outer, orient="vertical",
                                   command=list_canvas.yview)
        list_canvas.configure(yscrollcommand=list_scroll.set)
        list_scroll.pack(side="right", fill="y")
        list_canvas.pack(side="left", fill="both", expand=True)

        list_inner = tk.Frame(list_canvas, bg="#1a1a1a")
        list_canvas.create_window((0, 0), window=list_inner, anchor="nw")
        list_inner.bind("<Configure>",
                        lambda e: list_canvas.configure(
                            scrollregion=list_canvas.bbox("all")))

        chk_vars = {}
        for code in self.all_codes:
            var = tk.IntVar(value=0)
            name = code.get("name_en" if CURRENT_LANG == "en" else "name", code["name"])
            tk.Checkbutton(
                list_inner, text=name, variable=var,
                font=FONT_TINY, fg=TEXT_MAIN, bg="#1a1a1a",
                activebackground="#1a1a1a", selectcolor="#2a2a2a",
                anchor="w", relief="flat"
            ).pack(fill="x", padx=6, pady=1)
            chk_vars[code["id"]] = var

        def save_profile():
            pname = name_var.get().strip()
            if not pname:
                messagebox.showerror("Error", "Please enter a profile name.")
                return
            selected = [cid for cid, v in chk_vars.items() if v.get()]
            if not selected:
                messagebox.showerror("Error", "Select at least one code.")
                return
            os.makedirs(PROFILES_DIR, exist_ok=True)
            path = os.path.join(PROFILES_DIR, pname + ".json")
            profile = {
                "name": pname,
                "description": "",
                "codes": selected
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(profile, f, ensure_ascii=False, indent=2)
            dlg.destroy()
            messagebox.showinfo("[+] Saved",
                                "Profile saved:\n" + path)

        make_button(dlg, "Save Profile", save_profile,
                    fg=GREEN, bg="#1a2a0a", active_bg="#2a4a1a", width=14
                    ).pack(pady=10)

    def _load_profile(self):
        os.makedirs(PROFILES_DIR, exist_ok=True)
        files = [f for f in os.listdir(PROFILES_DIR) if f.endswith(".json")]
        if not files:
            messagebox.showinfo("Profiles",
                                "No profiles found in:\n" + PROFILES_DIR)
            return

        dlg = tk.Toplevel(self)
        dlg.title("Load Profile")
        dlg.geometry("360x300")
        dlg.resizable(False, True)
        dlg.configure(bg="#111")
        dlg.grab_set()

        make_label(dlg, "Select a profile:",
                   fg=ACCENT2, bg="#111", font=FONT_NORMAL
                   ).pack(pady=(16, 8))

        listbox = tk.Listbox(
            dlg, font=FONT_SMALL,
            fg=TEXT_MAIN, bg="#1a1a1a",
            selectbackground="#2a3a1a", selectforeground=GREEN,
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground=BORDER,
            height=10
        )
        for f in files:
            listbox.insert("end", f.replace(".json", ""))
        listbox.pack(fill="both", expand=True, padx=16, pady=4)

        def do_load():
            sel = listbox.curselection()
            if not sel:
                messagebox.showerror("Error", "Select a profile first.")
                return
            fname = files[sel[0]]
            path = os.path.join(PROFILES_DIR, fname)
            try:
                with open(path, encoding="utf-8") as f:
                    profile = json.load(f)
            except Exception as e:
                messagebox.showerror("Error", "Failed to load profile:\n" + str(e))
                return

            dlg.destroy()

            exe = self.exe_path.get().strip()
            if not exe or not os.path.isfile(exe):
                messagebox.showerror("Error", "Please select a valid bio4.exe first.")
                return
            if not self.scanned:
                messagebox.showerror("Error", "Please Scan the EXE first.")
                return

            queue = [cid for cid in profile.get("codes", [])
                     if cid in self.code_by_id and not self.applied.get(cid, False)]
            if not queue:
                messagebox.showinfo("Profile", "All codes in this profile are already applied.")
                return

            names = "\n".join("  - " + self.code_by_id.get(c, {}).get("name", c)
                              for c in queue)
            if not messagebox.askyesno("Load Profile",
                                       "Apply codes from profile '" +
                                       profile.get("name", fname) + "'?\n\n" + names):
                return

            # check if queue has enemy_persistence (needs mod_expansion dialog)
            needs_dialog = [c for c in queue
                            if self.code_by_id.get(c, {}).get("dialog") == "mod_expansion"]
            if needs_dialog:
                self._dialog_mod_expansion_batch_profile(queue, exe)
                return

            # apply in order, stop on failure
            success, failed = [], []
            for cid in queue:
                self._handle_dll_mutex(cid)
                ok, msg = apply_patch(exe, cid, self.codes_data)
                if ok:
                    self.applied[cid] = True
                    write_log("APPLIED (profile)", self.code_by_id.get(cid, {}).get("name", cid), exe)
                    success.append(cid)
                else:
                    failed.append((cid, msg))
                    break

            summary = "Applied " + str(len(success)) + " code(s)."
            if failed:
                summary += "\n\nStopped at:\n"
                for cid, err in failed:
                    summary += "- " + self.code_by_id.get(cid, {}).get("name", cid) + "\n  " + err + "\n"
                messagebox.showwarning("Done with errors", summary)
            else:
                messagebox.showinfo("[+] Done", summary)

            self._after_state_change()

        btn_row = tk.Frame(dlg, bg="#111")
        btn_row.pack(pady=8)
        make_button(btn_row, "Load", do_load,
                    fg=GREEN, bg="#1a2a0a", active_bg="#2a4a1a", width=10
                    ).pack(side="left", padx=8)
        make_button(btn_row, "Cancel", dlg.destroy,
                    fg=MUTED, bg="#1a1a1a", active_bg="#2a2a2a", width=8
                    ).pack(side="left", padx=4)

    #  Add New Code 

    def _add_new_code(self):
        dlg = tk.Toplevel(self)
        dlg.title("Add New Code")
        dlg.geometry("480x560")
        dlg.resizable(False, True)
        dlg.configure(bg="#111")
        dlg.grab_set()

        fields = {}

        def add_field(label, key, height=1):
            make_label(dlg, label, fg=TEXT_DIM, bg="#111", font=FONT_SMALL
                       ).pack(pady=(10, 2), padx=16, anchor="w")
            if height == 1:
                var = tk.StringVar()
                tk.Entry(dlg, textvariable=var,
                         font=FONT_SMALL, fg=ACCENT2, bg="#1a1a1a",
                         insertbackground=ACCENT2, relief="flat", bd=0,
                         highlightthickness=1, highlightbackground=BORDER,
                         width=52
                         ).pack(padx=16, ipady=3, anchor="w")
                fields[key] = var
            else:
                t = tk.Text(dlg, font=FONT_SMALL, fg=ACCENT2, bg="#1a1a1a",
                            insertbackground=ACCENT2, relief="flat", bd=0,
                            highlightthickness=1, highlightbackground=BORDER,
                            width=52, height=height)
                t.pack(padx=16, anchor="w")
                fields[key] = t

        # Section dropdown
        make_label(dlg, "Section:", fg=TEXT_DIM, bg="#111", font=FONT_SMALL
                   ).pack(pady=(16, 2), padx=16, anchor="w")
        sec_var = tk.StringVar()
        sec_names = [s.get("label_en" if CURRENT_LANG == "en" else "label", s["id"])
                     for s in self.sections_list]
        sec_ids   = [s["id"] for s in self.sections_list]
        sec_menu = tk.OptionMenu(dlg, sec_var, *sec_names)
        sec_menu.configure(font=FONT_SMALL, fg=TEXT_MAIN, bg="#1a1a1a",
                           activebackground="#2a2a2a", relief="flat",
                           highlightthickness=1, highlightbackground=BORDER)
        sec_menu.pack(padx=16, anchor="w")
        sec_var.set(sec_names[0])

        add_field("Code Name:", "name")
        add_field("Description:", "desc")

        # Requires
        make_label(dlg, "Requires another code? (leave blank if none):",
                   fg=TEXT_DIM, bg="#111", font=FONT_SMALL
                   ).pack(pady=(10, 2), padx=16, anchor="w")
        req_var = tk.StringVar()
        req_names = ["(none)"] + [c.get("name_en" if CURRENT_LANG == "en" else "name", c["id"])
                                   for c in self.all_codes]
        req_ids   = [None]    + [c["id"] for c in self.all_codes]
        req_menu = tk.OptionMenu(dlg, req_var, *req_names)
        req_menu.configure(font=FONT_SMALL, fg=TEXT_MAIN, bg="#1a1a1a",
                           activebackground="#2a2a2a", relief="flat",
                           highlightthickness=1, highlightbackground=BORDER)
        req_menu.pack(padx=16, anchor="w")
        req_var.set(req_names[0])

        add_field("Code (offset - bytes, e.g.  4DE390 - C3):", "code", height=4)

        def parse_code_text(text):
            """
            Parse code text in any of these formats:

            Format 1 - offset/paste:
                Find: 002B8417
                Paste:
                E8 68 8D D4 FF

            Format 2 - find/replace (Change To):
                83 C4 08 81 60 54
                Change To:
                A3 00 0E 2E 10 83

            Format 3 - simple offset:
                4DE390 - C3
                4DE391 to C3
            """
            patches = []
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            i = 0
            while i < len(lines):
                line = lines[i]
                line_up = line.upper()

                # Format 1: Find: OFFSET  /  Paste: / BYTES
                if line_up.startswith("FIND:") or line_up.startswith("FIND :"):
                    offset = line.split(":", 1)[1].strip()
                    # next non-empty line should be Paste: or bytes
                    i += 1
                    # skip "Paste:" line
                    if i < len(lines) and lines[i].upper().startswith("PASTE"):
                        i += 1
                    # collect bytes (may span multiple lines until next keyword)
                    byte_parts = []
                    while i < len(lines):
                        nxt = lines[i]
                        nxt_up = nxt.upper()
                        if (nxt_up.startswith("FIND") or
                            nxt_up.startswith("CHANGE") or
                            ("-" in nxt and len(nxt.split("-")[0].strip()) <= 8)):
                            break
                        byte_parts.append(nxt)
                        i += 1
                    byt = " ".join(" ".join(byte_parts).split())
                    if offset and byt:
                        patches.append({
                            "type": "offset_paste",
                            "offset": offset,
                            "bytes": byt
                        })
                    continue

                # Format 2: FIND_BYTES / Change To: / REPLACE_BYTES
                # detect if next non-empty line contains "Change To"
                if i + 1 < len(lines) and "CHANGE TO" in lines[i+1].upper():
                    find_bytes = line
                    i += 2  # skip "Change To:" line
                    # collect replace bytes
                    rep_parts = []
                    while i < len(lines):
                        nxt = lines[i]
                        nxt_up = nxt.upper()
                        if (nxt_up.startswith("FIND") or
                            "CHANGE TO" in nxt_up or
                            ("-" in nxt and len(nxt.split("-")[0].strip()) <= 8)):
                            break
                        rep_parts.append(nxt)
                        i += 1
                    rep_bytes = " ".join(" ".join(rep_parts).split())
                    if find_bytes and rep_bytes:
                        patches.append({
                            "type": "find_replace",
                            "find": find_bytes,
                            "replace": rep_bytes
                        })
                    continue

                # Format 3: OFFSET - BYTES  or  OFFSET to BYTES
                sep = None
                if " - " in line:
                    sep = " - "
                elif " to " in line.lower():
                    sep = line.lower().index(" to ")
                    sep = line[sep:sep+4]  # preserve original case

                if sep:
                    parts = line.split(sep, 1)
                    if len(parts) == 2:
                        offset = parts[0].strip()
                        byt    = parts[1].strip()
                        if offset and byt:
                            patches.append({
                                "type": "offset_replace",
                                "offset": offset,
                                "bytes": byt
                            })
                    i += 1
                    continue

                # skip unrecognized lines
                i += 1

            return patches

        def save_new_code():
            name = fields["name"].get().strip()
            desc = fields["desc"].get().strip()
            code_text = fields["code"].get("1.0", "end").strip()
            sec_label = sec_var.get()
            sec_id = sec_ids[sec_names.index(sec_label)]
            req_label = req_var.get()
            req_id = req_ids[req_names.index(req_label)] if req_label != "(none)" else None

            if not name:
                messagebox.showerror("Error", "Code name is required.")
                return
            if not code_text:
                messagebox.showerror("Error", "Code bytes are required.")
                return

            patches = parse_code_text(code_text)
            if not patches:
                messagebox.showerror("Error",
                    "Could not parse the code.\n\n"
                    "Supported formats:\n"
                    "  Find: OFFSET\n  Paste:\n  BYTES\n\n"
                    "  FIND_BYTES\n  Change To:\n  REPLACE_BYTES\n\n"
                    "  OFFSET - BYTES\n  OFFSET to BYTES")
                return

            # generate id from name
            import re
            cid = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
            if cid in self.code_by_id:
                cid = cid + "_custom"

            # add to codes_info
            new_info = {
                "id": cid,
                "section": sec_id,
                "name": name,
                "name_en": name,
                "desc": desc,
                "desc_en": desc,
                "notes": [],
                "notes_en": [],
                "requires": [req_id] if req_id else [],
                "detectable": True
            }
            self.codes_info["codes"].append(new_info)
            self.code_by_id[cid] = new_info
            self.codes_by_section.setdefault(sec_id, []).append(new_info)
            self.all_codes = self.codes_info["codes"]

            # add to codes_data
            self.codes_data[cid] = {"patches": patches}

            # save both files
            try:
                with open(INFO_FILE, "w", encoding="utf-8") as f:
                    json.dump(self.codes_info, f, ensure_ascii=False, indent=2)
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(self.codes_data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                messagebox.showerror("Error", "Failed to save:\n" + str(e))
                return

            dlg.destroy()
            messagebox.showinfo("[+] Added",
                                "Code added successfully:\n" + name +
                                "\nIn section: " + sec_label)
            self._after_state_change()

        make_button(dlg, "Add Code", save_new_code,
                    fg=GREEN, bg="#1a2a0a", active_bg="#2a4a1a", width=12
                    ).pack(pady=12)



# 
# SECTION 2: MDT COLOR EDITOR
# 

# ═════════════════════════════════════════════════════════════════════════════
# MDT COLOR EDITOR
# ═════════════════════════════════════════════════════════════════════════════

MDT_COLOR_OFFSET = 0x8129C0
MDT_COLOR_COUNT  = 12
MDT_DEFAULT_BYTES = bytes.fromhex(
    "F0CFD9E5FF0EDDE8FF03A1FFFFFCA74CFFFF4339FFF5DE0CFF"
    "707070FF73DF52FF123F4DFFE80770FFD217FCFF3030D0FF"
)


def read_mdt_colors(exe_path):
    colors = []
    try:
        with open(exe_path, "rb") as f:
            f.seek(MDT_COLOR_OFFSET)
            raw = f.read(MDT_COLOR_COUNT * 4)
        for i in range(MDT_COLOR_COUNT):
            a, b, g, r = raw[i*4], raw[i*4+1], raw[i*4+2], raw[i*4+3]
            colors.append((r, g, b, a))
    except Exception:
        colors = [(200,200,200,255)] * MDT_COLOR_COUNT
    return colors


def write_mdt_colors(exe_path, colors):
    with open(exe_path, "r+b") as f:
        f.seek(MDT_COLOR_OFFSET)
        for r, g, b, a in colors:
            f.write(bytes([a, b, g, r]))


# ─── MDT Speech Color Panel ──────────────────────────────────────────────────

class SpeechColorPanel(tk.Frame):
    """MDT Speech Color Change — load txt, display with color tags, click to recolor."""

    def __init__(self, parent, master_app, **kw):
        super().__init__(parent, bg="#0b0b0b", **kw)
        self.master_app  = master_app
        self._txt_path   = tk.StringVar()
        self._entries    = []
        self._color_only = tk.BooleanVar(value=False)
        self._char_mode  = tk.BooleanVar(value=False)
        self._hover_range = None
        self._build()

    def _scan_exe_colors(self):
        """Read MDT colors from exe and update text tags."""
        exe = self.master_app.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            return
        try:
            colors = read_mdt_colors(exe)
            for i in range(MDT_COLOR_COUNT):
                r, g, b, _ = colors[i]
                hex_col = f"#{r:02x}{g:02x}{b:02x}"
                self._text.tag_configure(f"col{i}", foreground=hex_col)
        except Exception:
            pass

    def activate(self):
        pass  # built eagerly in __init__

    def _build(self):
        top = tk.Frame(self, bg="#111")
        top.pack(fill="x", padx=12, pady=8)
        tk.Label(top, text=t("ملف Txt:","TXT File:"), fg="#999", bg="#111",
                 font=("Courier New", 9)).pack(side="left")
        tk.Entry(top, textvariable=self._txt_path,
                 font=("Courier New", 9), fg="#7cfc7c", bg="#0d1a0d",
                 insertbackground="#7cfc7c", relief="flat", bd=0,
                 highlightthickness=1, highlightbackground="#2a5a2a",
                 width=40).pack(side="left", ipady=3, padx=6)
        tk.Button(top, text=t("تصفح","Browse"), font=("Courier New", 8),
                  fg="#c8a035", bg="#1a1500", activeforeground="#c8a035",
                  activebackground="#2a2000", relief="flat", bd=0,
                  cursor="hand2", highlightthickness=1, highlightbackground="#c8a035",
                  command=self._browse, padx=8, pady=2).pack(side="left")
        tk.Button(top, text=t("تحميل","Load"), font=("Courier New", 8),
                  fg="#7cfc7c", bg="#1a2a0a", activeforeground="#7cfc7c",
                  activebackground="#2a4a1a", relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#7cfc7c",
                  padx=8, pady=2, command=self._load).pack(side="left", padx=4)
        tk.Frame(self, bg="#222").pack(fill="x")
        save_row = tk.Frame(self, bg="#0b0b0b")
        save_row.pack(fill="x", padx=8, pady=(4,0))
        tk.Button(save_row, text=t("حفظ الملف","Save File"),
                  font=("Courier New", 8), fg="#c8a035", bg="#1a1500",
                  activeforeground="#c8a035", activebackground="#2a2000",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#c8a035",
                  command=self._save_txt, padx=8, pady=2
                  ).pack(side="right")
        tk.Frame(self, bg="#222", height=1).pack(fill="x")
        opt_row = tk.Frame(self, bg="#0b0b0b")
        opt_row.pack(fill="x", padx=12, pady=(0, 4))
        tk.Checkbutton(opt_row, text=t("تلوين هذه الكلمة فقط", "Color this word only"),
                       variable=self._color_only,
                       fg="#cccccc", bg="#0b0b0b", activebackground="#0b0b0b",
                       selectcolor="#1a1a1a", font=("Courier New", 8),
                       relief="flat").pack(side="left")
        tk.Checkbutton(opt_row, text=t("اختيار كل حرف", "Select each character"),
                       variable=self._char_mode,
                       fg="#cccccc", bg="#0b0b0b", activebackground="#0b0b0b",
                       selectcolor="#1a1a1a", font=("Courier New", 8),
                       relief="flat").pack(side="left", padx=14)

        tk.Frame(self, bg="#222", height=1).pack(fill="x")

        body = tk.Frame(self, bg="#0b0b0b")
        body.pack(fill="both", expand=True, padx=8, pady=8)

        self._text = tk.Text(
            body, font=("Courier New", 10),
            fg="#e8e8e8", bg="#080808",
            insertbackground="#7cfc7c",
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground="#222",
            wrap="word", cursor="arrow", state="disabled"
        )
        sb = tk.Scrollbar(body, command=self._text.yview)
        self._text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._text.pack(fill="both", expand=True)

        self._text.tag_configure("hover",   background="#2a2000")
        self._text.tag_configure("newpage", foreground="#c8a035", font=("Courier New", 8))
        self._text.tag_configure("noclick", foreground="#c8a035")

        self._text.bind("<Motion>",   self._on_hover)
        self._text.bind("<Button-1>", self._on_click)
        self._text.bind("<Leave>",    lambda e: self._clear_hover())

    def _browse(self):
        p = _browse_open(title="Select MDT .txt file", filetypes=[("Text files", "*.txt"), ("All files", "*.*")], key="mdt_txt")
        if p:
            self._txt_path.set(p)
            self._load()



    def _save_txt(self):
        path = self._txt_path.get().strip()
        if not path:
            messagebox.showerror("Error", "No file loaded."); return
        if not self._raw:
            messagebox.showerror("Error", "Nothing to save."); return
        try:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(self._raw)
            messagebox.showinfo("[+] Saved", f"Saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _load(self):
        path = self._txt_path.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showerror("Error", "Select a valid .txt file first.")
            return
        try:
            raw_bytes = open(path, "rb").read()
            # strip UTF-16 BOM and decode if needed
            if raw_bytes[:2] in (b'\xff\xfe', b'\xfe\xff'):
                raw = raw_bytes.decode("utf-16", errors="ignore")
            elif raw_bytes[:3] == b'\xef\xbb\xbf':
                raw = raw_bytes[3:].decode("utf-8", errors="ignore")
            else:
                raw = raw_bytes.decode("utf-8", errors="ignore")
            raw = raw.replace("\r\n", "\n").replace("\r", "\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        self._raw = raw
        self._render(raw)

    def _render(self, raw):
        exe = self.master_app.exe_path.get().strip()
        if exe and os.path.isfile(exe):
            colors = read_mdt_colors(exe)
        else:
            colors = [(200,200,200,255)] * MDT_COLOR_COUNT

        for i in range(MDT_COLOR_COUNT):
            r, g, b, _ = colors[i]
            hex_col = f"#{r:02x}{g:02x}{b:02x}"
            self._text.tag_configure(f"col{i}", foreground=hex_col)

        import re as _re
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")

        # _raw_char_map[text_widget_char_index] = raw_string_index
        # Only maps chars that are actual text content (not tokens/separators)
        self._raw_char_map = {}  # int(text_char_offset_0based) -> int(raw_offset)

        token_re = _re.compile(r"\{0x[0-9A-Fa-f]+\}", _re.IGNORECASE)
        tokens   = list(token_re.finditer(raw))
        pos = 0; i = 0; current_col_tag = None
        text_char_count = 0  # running count of chars inserted into text widget

        while i <= len(tokens):
            m       = tokens[i] if i < len(tokens) else None
            end_pos = m.start() if m else len(raw)
            if end_pos > pos:
                chunk = raw[pos:end_pos]
                tags  = (current_col_tag, "hover_word") if current_col_tag else ("hover_word",)
                self._text.insert("end", chunk, tags)
                # map each char of chunk to its raw position
                for ci, raw_offset in enumerate(range(pos, end_pos)):
                    self._raw_char_map[text_char_count + ci] = raw_offset
                text_char_count += len(chunk)
            if m is None:
                break
            code = m.group(0).upper().replace(" ", "")[1:-1]
            if code == "0X0000":
                pass
            elif code == "0X0100":
                sep = "\n" + chr(0x2500)*36 + "\n"
                self._text.insert("end", sep, ("newpage",))
                text_char_count += len(sep)
                current_col_tag = None
            elif code == "0X0300":
                self._text.insert("end", "\n")
                text_char_count += 1
            elif code == "0X0400":
                np = " [New Page] "
                self._text.insert("end", np, ("newpage",))
                text_char_count += len(np)
            elif code == "0X0600":
                if i + 1 < len(tokens):
                    nxt = tokens[i + 1]
                    nv  = nxt.group(0).upper().replace(" ", "")[1:-1]
                    try:
                        raw_val = int(nv, 16)
                        idx_col = (raw_val >> 8) & 0xFF
                        current_col_tag = f"col{min(idx_col, MDT_COLOR_COUNT-1)}"
                    except Exception:
                        current_col_tag = None
                    pos = nxt.end(); i += 2; continue
                else:
                    pos = m.end(); i += 1; continue
            pos = m.end(); i += 1

        self._text.configure(state="disabled")

    def _text_idx_to_raw(self, text_idx):
        """Convert tk text index (line.col) to raw string offset."""
        # get 0-based char offset from text widget start
        char_offset = int(self._text.count("1.0", text_idx, "chars")[0])
        return self._raw_char_map.get(char_offset, None)

    def _on_hover(self, event):
        self._clear_hover()
        idx = self._text.index(f"@{event.x},{event.y}")
        tags_here = self._text.tag_names(idx)
        if "newpage" in tags_here or "noclick" in tags_here:
            return
        # skip if inside a token (no raw mapping)
        if self._text_idx_to_raw(idx) is None:
            return
        if self._char_mode.get():
            ch = self._text.get(idx)
            if ch and not ch.isspace():
                self._text.tag_add("hover", idx, f"{idx}+1c")
                self._hover_range = (idx, f"{idx}+1c")
        else:
            start = self._text.index(f"{idx} wordstart")
            end   = self._text.index(f"{idx} wordend")
            word  = self._text.get(start, end).strip()
            if word and not word.startswith("{") and word not in ("[New Page]",):
                self._text.tag_add("hover", start, end)
                self._hover_range = (start, end)

    def _clear_hover(self):
        self._text.tag_remove("hover", "1.0", "end")
        self._hover_range = None

    def _on_click(self, event):
        idx = self._text.index(f"@{event.x},{event.y}")
        tags_here = self._text.tag_names(idx)
        if "newpage" in tags_here or "noclick" in tags_here:
            return
        # skip if no raw mapping (inside a separator or token area)
        if self._text_idx_to_raw(idx) is None:
            return
        if self._char_mode.get():
            ch = self._text.get(idx)
            if not ch or ch.isspace():
                return
            word  = ch
            start = idx
            end   = f"{idx}+1c"
        else:
            start = self._text.index(f"{idx} wordstart")
            end   = self._text.index(f"{idx} wordend")
            word  = self._text.get(start, end).strip()
            if not word or word.startswith("{") or word in ("[New", "Page]"):
                return
            # verify start has raw mapping
            if self._text_idx_to_raw(start) is None:
                return
        exe = self.master_app.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("Error", "Select bio4.exe first.")
            return
        colors = read_mdt_colors(exe)
        self._show_color_picker(word, start, end, colors)

    def _show_color_picker(self, word, start, end, colors):
        exe = self.master_app.exe_path.get().strip()
        txt_path = self._txt_path.get().strip()

        dlg = tk.Toplevel(self)
        dlg.title(f"Color: {word[:20]}")
        dlg.geometry("420x320")
        dlg.resizable(False, False)
        dlg.configure(bg="#111")
        dlg.grab_set()

        tk.Label(dlg, text=f'{t("اختر لون لـ","Choose color for:")}  {word[:30]}',
                 fg="#c8a035", bg="#111",
                 font=("Courier New", 10, "bold")).pack(pady=(14, 8))

        swatches_frame = tk.Frame(dlg, bg="#111")
        swatches_frame.pack(pady=4)

        for i in range(MDT_COLOR_COUNT):
            r, g, b, _ = colors[i]
            hex_col = f"#{r:02x}{g:02x}{b:02x}"

            def make_apply(idx=i):
                def do():
                    r2, g2, b2, _ = colors[idx]
                    hex_c = f"#{r2:02x}{g2:02x}{b2:02x}"
                    code_str = "{0x0600}" + "{" + f"0x{idx:02X}00" + "}"
                    suffix   = "{0x0600}{0x0000}" if self._color_only.get() else ""
                    self._apply_color_to_txt(txt_path, start, end, code_str, suffix)
                    dlg.destroy()
                return do

            btn = tk.Button(swatches_frame, bg=hex_col, width=3, height=1,
                            relief="solid", bd=1, cursor="hand2",
                            command=make_apply())
            btn.grid(row=i//6, column=i%6, padx=3, pady=3)

        tk.Button(dlg, text=t("إغلاق","Close"),
                  font=("Courier New", 9), fg="#888", bg="#1a1a1a",
                  relief="flat", bd=0, cursor="hand2",
                  command=dlg.destroy, padx=10, pady=4).pack(pady=12)

    def _apply_color_to_txt(self, txt_path, start, end, code_str, suffix=""):
        try:
            raw_bytes = open(txt_path, "rb").read()
            if raw_bytes[:2] in (b'\xff\xfe', b'\xfe\xff'):
                raw = raw_bytes.decode("utf-16", errors="ignore")
            elif raw_bytes[:3] == b'\xef\xbb\xbf':
                raw = raw_bytes[3:].decode("utf-8", errors="ignore")
            else:
                raw = raw_bytes.decode("utf-8", errors="ignore")
            raw = raw.replace("\r\n", "\n").replace("\r", "\n")

            word = self._text.get(start, end).strip()
            if not word:
                return

            # Use raw position map for exact location
            raw_start = self._text_idx_to_raw(start)
            raw_end   = self._text_idx_to_raw(end) if not end.endswith("+1c") else None

            if raw_start is not None:
                # verify word matches at this raw position
                if raw.find(word, raw_start) == raw_start:
                    pos      = raw_start
                    word_end = pos + len(word)
                    raw = raw[:pos] + code_str + raw[pos:word_end] + suffix + raw[word_end:]
                    with open(txt_path, "w", encoding="utf-8", newline="\n") as f:
                        f.write(raw)
                    self._raw = raw
                    self._render(raw)
                    messagebox.showinfo("[+] Applied", f"Color applied to '{word[:20]}'")
                    return

            # fallback: first occurrence
            import re as _re
            matches = list(_re.finditer(_re.escape(word), raw))
            if not matches:
                messagebox.showwarning("Not found", f"'{word[:20]}' not found in file.")
                return
            pos = matches[0].start()
            word_end = pos + len(word)
            raw = raw[:pos] + code_str + raw[pos:word_end] + suffix + raw[word_end:]
            with open(txt_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(raw)
            self._raw = raw
            self._render(raw)
            messagebox.showinfo("[+] Applied", f"Color applied to '{word[:20]}'")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            messagebox.showerror("Error", str(e))


# ─── MDT Custom Color Panel ──────────────────────────────────────────────────

class CustomColorPanel(tk.Frame):
    """MDT Custom Color — edit the 12 game speech colors in the EXE."""

    def __init__(self, parent, master_app, **kw):
        super().__init__(parent, bg="#0b0b0b", **kw)
        self.master_app = master_app
        self._swatches  = []
        self._colors    = [(200,200,200,255)] * MDT_COLOR_COUNT
        self._build()

    def activate(self):
        # auto-reload swatches when exe is loaded
        exe = self.master_app.exe_path.get().strip()
        if exe and os.path.isfile(exe):
            self._reload()

    def _build(self):
        top = tk.Frame(self, bg="#111")
        top.pack(fill="x", padx=12, pady=8)
        tk.Label(top, text="Custom Speech Colors",
                 fg="#c8a035", bg="#111",
                 font=("Courier New", 10, "bold")).pack(side="left")
        tk.Button(top, text=t("أعادة تحميل من EXE", "Reload from EXE"),
                  font=("Courier New", 8), fg="#7cfc7c", bg="#1a2a0a",
                  activeforeground="#7cfc7c", activebackground="#2a4a1a",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#7cfc7c",
                  command=self._reload, padx=8, pady=2).pack(side="right")
        tk.Button(top, text=t("أعادة تعيين الألوان","Reset Colors"),
                  font=("Courier New", 8), fg="#ff6060", bg="#2a0a0a",
                  activeforeground="#ff6060", activebackground="#3a1010",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#ff6060",
                  command=self._reset_colors, padx=8, pady=2
                  ).pack(side="right", padx=4)

        tk.Frame(self, bg="#222", height=1).pack(fill="x")

        grid = tk.Frame(self, bg="#0b0b0b")
        grid.pack(padx=20, pady=20)

        for i in range(MDT_COLOR_COUNT):
            row, col = divmod(i, 4)
            frame = tk.Frame(grid, bg="#0b0b0b")
            frame.grid(row=row, column=col, padx=12, pady=8)
            tk.Label(frame, text=f"{i+1}",
                     fg="#888", bg="#0b0b0b",
                     font=("Courier New", 8)).pack(pady=(0,3))
            swatch = tk.Button(frame, width=6, height=2,
                                bg="#888888", relief="solid", bd=2,
                                cursor="hand2",
                                command=lambda idx=i: self._pick_color(idx))
            swatch.pack()
            self._swatches.append(swatch)

    def _reload(self):
        exe = self.master_app.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("Error", "Select bio4.exe first.")
            return
        self._colors = read_mdt_colors(exe)
        for i, (r, g, b, _) in enumerate(self._colors):
            self._swatches[i].configure(bg=f"#{r:02x}{g:02x}{b:02x}")

    def _reset_colors(self):
        exe = self.master_app.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("Error", "Select bio4.exe first.")
            return
        if _check_game_not_running(exe):
            return
        try:
            with open(exe, "r+b") as f:
                f.seek(MDT_COLOR_OFFSET)
                f.write(MDT_DEFAULT_BYTES)
            self._reload()
            messagebox.showinfo("[+] Reset", "Colors reset to default.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _pick_color(self, idx):
        exe = self.master_app.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("Error", "Select bio4.exe first.")
            return
        r, g, b, a = self._colors[idx]
        init_col = f"#{r:02x}{g:02x}{b:02x}"
        result   = colorchooser.askcolor(color=init_col,
                                          title=f"Color {idx+1}")
        if result and result[0]:
            nr, ng, nb = int(result[0][0]), int(result[0][1]), int(result[0][2])
            self._colors[idx] = (nr, ng, nb, a)
            hex_col = f"#{nr:02x}{ng:02x}{nb:02x}"
            self._swatches[idx].configure(bg=hex_col)
            if _check_game_not_running(exe):
                return
            try:
                with open(exe, "r+b") as f:
                    f.seek(MDT_COLOR_OFFSET + idx * 4)
                    f.write(bytes([a, nb, ng, nr]))
                messagebox.showinfo("[+] Applied", f"Color {idx+1} saved.")
            except Exception as e:
                messagebox.showerror("Error", str(e))


# ─── MDT Color Panel (container) ─────────────────────────────────────────────

class MDTColorPanel(tk.Frame):
    """MDT Color Editor  tab container for Speech Color + Custom Color."""

    def __init__(self, parent, master_app, **kw):
        super().__init__(parent, bg="#0b0b0b", **kw)
        self.master_app = master_app
        self._built     = False

    def activate(self):
        if not self._built:
            self._built = True  # set BEFORE _build to prevent re-entry
            self._build()

    def _build(self):
        # tab bar
        tab_bar = tk.Frame(self, bg="#0e0e0e")
        tab_bar.pack(fill="x")
        tk.Frame(self, bg="#c8a035", height=1).pack(fill="x")

        self._tabs   = {}
        self._panels = {}

        for tid, lbl in [("speech", t("تغيير لون الكلام", "Speech Color Change")), ("custom", t("تخصيص الألوان", "Custom Color"))]:
            btn = tk.Button(tab_bar, text=lbl,
                            font=("Courier New", 9, "bold"),
                            fg="#7a7a7a", bg="#0e0e0e",
                            activeforeground="#c8a035",
                            activebackground="#16110a",
                            relief="flat", bd=0, cursor="hand2",
                            padx=16, pady=7,
                            command=lambda t=tid: self._switch_tab(t))
            btn.pack(side="left")
            self._tabs[tid] = btn

        tk.Frame(self, bg="#111", height=1).pack(fill="x")

        self._content = tk.Frame(self, bg="#0b0b0b")
        self._content.pack(fill="both", expand=True)

        self._panels["speech"] = SpeechColorPanel(self._content, self.master_app)
        self._panels["custom"] = CustomColorPanel(self._content, self.master_app)

        for p in self._panels.values():
            p.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._switch_tab("speech")

    def _switch_tab(self, tab_id):
        if tab_id not in self._panels:
            return
        for tid, p in self._panels.items():
            try: p.lower()
            except Exception: pass
            btn = self._tabs.get(tid)
            if btn:
                btn.configure(fg="#7a7a7a", bg="#0e0e0e", highlightthickness=0)
        self._panels[tab_id].lift()
        btn = self._tabs.get(tab_id)
        if btn:
            btn.configure(fg="#c8a035", bg="#16110a",
                           highlightthickness=1, highlightbackground="#c8a035")


# ── CNS Editor ─────────────────────────────────────────────────────────────────

# (offset, size_bytes, label, var_name, default_dec)
CNS_FIELDS = [
    (0x7F9A44, 4, "ENEMY NUM",    "enemy_limit",        60),
    (0x7F9A48, 4, "OBJ NUM",      "object_limit",      200),
    (0x7F9A4C, 4, "ESP NUM",      "effect_limit",     1024),
    (0x7F9A50, 4, "ESPGEN NUM",   "effect_spawn_limit", 256),
    (0x7F9A54, 4, "CTRL NUM",     "control_limit",       10),
    (0x7F9A58, 4, "LIGHT NUM",    "light_limit",        100),
    (0x7F9A5C, 4, "PARTS NUM",    "bones_limit",       1300),
    (0x7F9A60, 4, "MODEL INFO",   "model_info_limit",   300),
    (0x7F9A64, 4, "PRIM NUM",     "primitive_limit",  655360),
    (0x7F9A68, 4, "EVT NUM",      "event_limit",         10),
    (0x7F9A6C, 4, "SAT NUM",      "SAT_limit",           30),
    (0x7F9A70, 4, "EAT NUM",      "EAT_limit",           30),
]


class CNSEditorPanel(tk.Frame):
    """CNS Editor - edit game memory/limits in bio4.exe."""

    def __init__(self, parent, master_app, **kw):
        super().__init__(parent, bg="#0b0b0b", **kw)
        self.master_app = master_app
        self._vars      = {}
        self._built     = False

    def activate(self):
        if not self._built:
            self._build()
            self._built = True
        self._reload()

    def _build(self):
        hdr = tk.Frame(self, bg="#0e0e0e")
        hdr.pack(fill="x")
        tk.Label(hdr, text="CNS EDITOR",
                 fg="#e07b54", bg="#0e0e0e",
                 font=("Courier New", 13, "bold")).pack(side="left", padx=16, pady=8)
        tk.Label(hdr, text=t("تعديل حدود اللعبة في bio4.exe", "edit game limits in bio4.exe"),
                 fg="#888", bg="#0e0e0e",
                 font=("Courier New", 8)).pack(side="left")
        tk.Frame(self, bg="#e07b54", height=1).pack(fill="x")

        bar = tk.Frame(self, bg="#0b0b0b")
        bar.pack(fill="x", padx=16, pady=8)
        tk.Button(bar, text=t("أعادة تحميل من EXE","Reload from EXE"),
                  font=("Courier New", 8), fg="#7cfc7c", bg="#1a2a0a",
                  activeforeground="#7cfc7c", activebackground="#2a4a1a",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#7cfc7c",
                  padx=10, pady=3, command=self._reload).pack(side="left")
        tk.Button(bar, text=t("حفظ الكل", "Save All"),
                  font=("Courier New", 8), fg="#e07b54", bg="#2a1a0a",
                  activeforeground="#e07b54", activebackground="#3a2a0a",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#e07b54",
                  padx=10, pady=3, command=self._save_all).pack(side="left", padx=8)
        tk.Button(bar, text=t("إعادة الافتراضي", "Reset Defaults"),
                  font=("Courier New", 8), fg="#888", bg="#1a1a1a",
                  activeforeground="#aaa", activebackground="#222",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#666",
                  padx=10, pady=3, command=self._reset_all).pack(side="left")

        tk.Frame(self, bg="#1a1a1a", height=1).pack(fill="x", pady=(4, 0))

        outer = tk.Frame(self, bg="#0b0b0b")
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg="#0b0b0b", highlightthickness=0)
        sb = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        inner = tk.Frame(canvas, bg="#0b0b0b")
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.bind("<MouseWheel>",
                    lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        # column headers
        hdr2 = tk.Frame(inner, bg="#111")
        hdr2.pack(fill="x", padx=12, pady=(10, 2))
        for text, w in [(t("أوفست","Offset"), 10), (t("التسمية","Label"), 14), (t("اسم المتغير","Var Name"), 18),
                        (t("القيمة","Value"), 14), (t("الافتراضي","Default"), 12)]:
            tk.Label(hdr2, text=text, fg="#888", bg="#111",
                     font=("Courier New", 8),
                     width=w, anchor="w").pack(side="left", padx=4)
        tk.Frame(inner, bg="#222", height=1).pack(fill="x", padx=12)

        for offset, size, label, varname, default in CNS_FIELDS:
            var = tk.StringVar(value=str(default))
            self._vars[offset] = var

            row = tk.Frame(inner, bg="#0b0b0b")
            row.pack(fill="x", padx=12, pady=1)
            row.bind("<Enter>", lambda e, r=row: r.configure(bg="#111"))
            row.bind("<Leave>", lambda e, r=row: r.configure(bg="#0b0b0b"))

            tk.Label(row, text=f"0x{offset:07X}",
                     fg="#666", bg="#0b0b0b",
                     font=("Courier New", 8), width=10, anchor="w").pack(side="left", padx=4)
            tk.Label(row, text=label,
                     fg="#e07b54", bg="#0b0b0b",
                     font=("Courier New", 9, "bold"), width=14, anchor="w").pack(side="left", padx=4)
            tk.Label(row, text=varname,
                     fg="#6a6a6a", bg="#0b0b0b",
                     font=("Courier New", 8), width=18, anchor="w").pack(side="left", padx=4)

            ent = tk.Entry(row, textvariable=var,
                           font=("Courier New", 9),
                           fg="#7cfc7c", bg="#0d1a0d",
                           insertbackground="#7cfc7c",
                           relief="flat", bd=0,
                           highlightthickness=1, highlightbackground="#2a5a2a",
                           width=14, justify="center")
            ent.pack(side="left", padx=4, ipady=3)

            tk.Label(row, text=str(default),
                     fg="#2a3a2a", bg="#0b0b0b",
                     font=("Courier New", 8), width=12, anchor="w").pack(side="left", padx=4)


            tk.Button(row, text=t("تطبيق","Apply"),
                      font=("Courier New", 7), fg="#7cfc7c", bg="#1a2a0a",
                      activeforeground="#7cfc7c", activebackground="#2a4a1a",
                      relief="flat", bd=0, cursor="hand2", padx=6, pady=1,
                      command=lambda o=offset, s=size, v=var: self._apply_one(o, s, v)
                      ).pack(side="right", padx=4)

    def _get_exe(self):
        p = self.master_app.exe_path.get().strip()
        if not p or not os.path.isfile(p):
            messagebox.showerror("Error", "Select bio4.exe first.")
            return None
        return p

    def _reload(self):
        exe = self._get_exe()
        if not exe:
            return
        try:
            with open(exe, "rb") as f:
                for offset, size, *_ in CNS_FIELDS:
                    f.seek(offset)
                    data = f.read(size)
                    if len(data) != size:
                        raise ValueError(f"Short read at 0x{offset:07X}")
                    self._vars[offset].set(str(int.from_bytes(data, "little")))
        except Exception as e:
            messagebox.showerror("Read Error", str(e))

    def _apply_one(self, offset, size, var):
        exe = self._get_exe()
        if not exe:
            return
        if _check_game_not_running(exe):
            return
        try:
            val = int(var.get())
            max_val = (1 << (size * 8)) - 1
            if val < 0 or val > max_val:
                messagebox.showerror("Error", f"Value must be 0 - {max_val}")
                return
            with open(exe, "r+b") as f:
                f.seek(offset)
                f.write(val.to_bytes(size, "little"))
            messagebox.showinfo("[+] Applied", f"0x{offset:07X} = {val}")
        except ValueError:
            messagebox.showerror("Error", "Enter a valid decimal number.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _save_all(self):
        exe = self._get_exe()
        if not exe:
            return
        if _check_game_not_running(exe):
            return
        if not messagebox.askyesno("Save All", "Write all CNS values to bio4.exe?"):
            return
        errors = []
        try:
            with open(exe, "r+b") as f:
                for offset, size, label, varname, default in CNS_FIELDS:
                    try:
                        val = int(self._vars[offset].get())
                        max_val = (1 << (size * 8)) - 1
                        if val < 0 or val > max_val:
                            errors.append(f"{label}: out of range (0-{max_val})")
                            continue
                        f.seek(offset)
                        f.write(val.to_bytes(size, "little"))
                    except Exception as e2:
                        errors.append(f"{label}: {e2}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        if errors:
            messagebox.showwarning("Partial Save", "\n".join(errors))
        else:
            messagebox.showinfo("[+] Saved", "All CNS values written to EXE.")

    def _reset_all(self):
        if not messagebox.askyesno("Reset", "Reset all values to defaults?"):
            return
        for offset, _, _, _, default in CNS_FIELDS:
            self._vars[offset].set(str(default))


class LockedPanel(tk.Frame):
    """Panel shown when a module requires a code to be enabled."""

    def __init__(self, parent, tool_label, required_code_id,
                 required_code_name, master_app, unlocked_panel=None, **kw):
        super().__init__(parent, bg="#0b0b0b", **kw)
        self.master_app          = master_app
        self.required_code_id    = required_code_id
        self.required_code_name  = required_code_name
        self.tool_label          = tool_label
        self._unlocked_panel     = unlocked_panel  # real panel to show when unlocked
        self._unlocked_by_quick  = False
        self._build()

    def activate(self):
        self._check_lock()
        if self._is_unlocked_now() and self._unlocked_panel:
            self._unlocked_panel.lift()
            self._unlocked_panel.activate()

    def _is_unlocked_now(self):
        cm             = getattr(self.master_app, "_cm_app", None)
        quick_unlocked = getattr(self, "_unlocked_by_quick", False)
        scan_unlocked  = (cm and (
            cm.applied.get(self.required_code_id, False) or
            cm.detected.get(self.required_code_id, False)
        ))
        return quick_unlocked or scan_unlocked

    def _check_lock(self):
        """Re-check if required code is applied  via quick detect or full scan."""
        is_unlocked = self._is_unlocked_now()
        if is_unlocked:
            self._lbl_lock.configure(
                text="Code is enabled  module is ready.",
                fg="#7cfc7c"
            )
            if self._unlocked_panel:
                self._unlocked_panel.lift()
                self._unlocked_panel.activate()
        else:
            self._lbl_lock.configure(
                text=f"This module requires [{self.required_code_name}]\nto be enabled in RE4 CODE MANAGER.",
                fg="#e05050"
            )

    def _build(self):
        f = tk.Frame(self, bg="#0b0b0b")
        f.place(relx=0.5, rely=0.42, anchor="center")

        tk.Label(f, text="[LOCKED]", fg="#c8a035", bg="#0b0b0b",
                 font=("Courier New", 24)).pack(pady=(0, 10))
        tk.Label(f, text=self.tool_label, fg="#c8a035", bg="#0b0b0b",
                 font=("Courier New", 14, "bold")).pack(pady=(0, 12))

        self._lbl_lock = tk.Label(f, text="",
                                   fg="#e05050", bg="#0b0b0b",
                                   font=("Courier New", 10),
                                   justify="center")
        self._lbl_lock.pack(pady=(0, 16))

        tk.Label(f,
                 text="Go to RE4 CODE MANAGER  enable the required code  return here.",
                 fg="#888", bg="#0b0b0b",
                 font=("Courier New", 8),
                 justify="center").pack()

        self._check_lock()


class ComingSoonPanel(tk.Frame):
    def __init__(self, parent, tool_label, **kw):
        super().__init__(parent, bg="#0b0b0b", **kw)
        self.tool_label = tool_label
        self._build()

    def activate(self): pass

    def _build(self):
        f = tk.Frame(self, bg="#0b0b0b")
        f.place(relx=0.5, rely=0.42, anchor="center")
        tk.Label(f, text=self.tool_label, fg="#c8a035", bg="#0b0b0b",
                 font=("Courier New", 14, "bold")).pack(pady=(0, 14))
        tk.Label(f, text="[ COMING SOON ]", fg="#7a7a7a", bg="#0b0b0b",
                 font=("Courier New", 13, "bold")).pack()
        tk.Label(f, text="This module is under development.",
                 fg="#666", bg="#0b0b0b", font=("Courier New", 9)).pack(pady=(10, 0))


class WelcomePanel(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg="#080808", **kw)
        self._build()

    def activate(self): pass

    def _build(self):
        f = tk.Frame(self, bg="#080808")
        f.place(relx=0.5, rely=0.45, anchor="center")

        # Big title
        tk.Label(f, text="RE4",
                 fg="#c8a035", bg="#080808",
                 font=("Courier New", 52, "bold")).pack()
        tk.Label(f, text="MASTER EDITOR",
                 fg="#dddddd", bg="#080808",
                 font=("Courier New", 18, "bold")).pack()

        tk.Frame(f, bg="#c8a035", height=1, width=340).pack(pady=(10, 16))

        # Tools grid
        tools_frame = tk.Frame(f, bg="#080808")
        tools_frame.pack(pady=(0, 20))

        tools_info = [
            ("CODE MANAGER",  "#5b9bd5", t("تطبيق وفحص أكواد EXE","Apply & scan EXE codes")),
            ("OSD EDITOR",    "#c8a035", t("تعديل مشغلات OSD","Edit OSD item triggers")),
            ("CNS EDITOR",    "#e07b54", t("ضبط حدود اللعبة","Tune game limits")),
            ("AEV OPTION",    "#c8a035", t("تعديل خيارات AEV","Edit AEV speech options")),
            ("MDT COLOR",     "#d46fc8", t("تخصيص ألوان الكلام","Customize speech colors")),
            ("ROOM INIT",     "#7ec8a0", t("نسخ بيانات تهيئة الغرفة","Clone room init data")),
            ("LOCK AEV\nWITH KEY", "#e07b54", t("محرر AVL وملف events","AVL editor & events.cfg")),
            ("WEAPONS",       "#e05555", t("تعديل الأسلحة والعناصر","Edit weapons & items")),
            ("SCRIPTS",       "#5bc8c8", t("أدوات ومساعدات","Tools & utilities")),
        ]

        for i, (name, color, desc) in enumerate(tools_info):
            col = i % 4
            row = i // 4
            cell = tk.Frame(tools_frame, bg="#0e0e0e",
                            highlightthickness=1, highlightbackground="#1e1e1e")
            cell.grid(row=row, column=col, padx=6, pady=5, ipadx=8, ipady=6, sticky="ew")
            tk.Label(cell, text=name, fg=color, bg="#0e0e0e",
                     font=("Courier New", 8, "bold")).pack()
            tk.Label(cell, text=desc, fg="#666666", bg="#0e0e0e",
                     font=("Courier New", 7)).pack()

        tk.Label(f, text=t("اختر قسماً من الشريط الجانبي  ►","Select a module from the sidebar  ►"),
                 fg="#404040", bg="#080808",
                 font=("Courier New", 9)).pack()


class CodeManagerPanel(tk.Frame):
    """
    Embeds RE4PatcherApp inside the master editor.
    The exe_path is shared from master.
    No browse/path bar shown  master handles it.
    Settings shows code-manager-specific options only.
    """

    def __init__(self, parent, master_app, **kw):
        super().__init__(parent, bg="#0b0b0b", **kw)
        self.master_app = master_app
        self._app       = None
        self._built     = False

    def activate(self):
        if not self._built:
            self._build()
            self._built = True

    def get_app(self):
        return self._app

    def _build(self):
        # Override paths to point inside MASTER_DIR
        global BASE_DIR, CODES_DIR, INFO_FILE, DATA_FILE, ORIG_FILE
        global PROFILES_DIR, MOD_DIR, FILES_DIR, LOG_FILE
        global BACKUP_FILE, SETTINGS_FILE

        BASE_DIR     = os.path.join(MASTER_DIR, "RE4 CODE MANAGER")
        CODES_DIR    = os.path.join(BASE_DIR, "the_codes")
        INFO_FILE    = os.path.join(CODES_DIR, "codes_info.json")
        DATA_FILE    = os.path.join(CODES_DIR, "codes_data.json")
        ORIG_FILE    = os.path.join(CODES_DIR, "bio4_original.exe")
        PROFILES_DIR = os.path.join(BASE_DIR, "Profiles")
        MOD_DIR      = os.path.join(BASE_DIR, "Modified files")
        FILES_DIR    = os.path.join(BASE_DIR, "the_files")
        LOG_FILE     = os.path.join(FILES_DIR, "patch_log.txt")
        BACKUP_FILE  = os.path.join(FILES_DIR, "patch_backup.json")
        SETTINGS_FILE = os.path.join(FILES_DIR, "settings.json")

        # reload settings
        global APP_SETTINGS
        APP_SETTINGS = load_settings()

        # check data files exist
        if not os.path.isfile(INFO_FILE) or not os.path.isfile(DATA_FILE):
            self._show_missing()
            return

        try:
            app = RE4PatcherApp(
                master=self,
                embedded=True,
                shared_exe_var=self.master_app.exe_path
            )
            app.pack(fill="both", expand=True)
            self._app = app
            self.master_app._cm_app = app
            app._master_app_ref = self.master_app
            self.master_app.after(500, self.master_app._check_locked_panels)
        except Exception as e:
            import traceback
            err = traceback.format_exc()
            tk.Label(self,
                     text="Error loading Code Manager:\n" + str(e),
                     fg="#e05050", bg="#0b0b0b",
                     font=("Courier New", 8),
                     wraplength=600, justify="left").pack(pady=20, padx=20)
            print(err)

    def _show_missing(self):
        f = tk.Frame(self, bg="#0b0b0b")
        f.place(relx=0.5, rely=0.42, anchor="center")
        tk.Label(f, text="RE4 CODE MANAGER data not found.",
                 fg="#e05050", bg="#0b0b0b",
                 font=("Courier New", 10)).pack(pady=8)
        tk.Label(f,
                 text=f"Expected:\n{CODES_DIR}",
                 fg="#888", bg="#0b0b0b",
                 font=("Courier New", 8)).pack()


# 
# SECTION 6: MASTER EDITOR MAIN APP
# 

# 
# AEV OPTION EDITOR
# 

class AEVOptionPanel(tk.Frame):
    """
    AEV Option Editor  load TXT, display text, click word  set AEV option.
    Color: red = AEV will hide after press, green = AEV stays visible.
    Format written: {0x0700}{0xFFXX} or {0x0700}{0xFEXX}
    """

    def __init__(self, parent, master_app, **kw):
        super().__init__(parent, bg="#0b0b0b", **kw)
        self.master_app = master_app
        self._txt_path  = tk.StringVar()
        self._build()

    def activate(self): pass

    def _build(self):
        hdr = tk.Frame(self, bg="#0e0e0e")
        hdr.pack(fill="x")
        tk.Label(hdr, text="AEV OPTION EDITOR",
                 fg="#c8a035", bg="#0e0e0e",
                 font=("Courier New", 13, "bold")).pack(side="left", padx=16, pady=8)
        tk.Label(hdr, text=t("تعديل ملفات خيارات AEV", "edit AEV speech option files"),
                 fg="#666666", bg="#0e0e0e",
                 font=("Courier New", 8)).pack(side="left", pady=8)
        tk.Frame(self, bg="#c8a035", height=1).pack(fill="x")

        # file row
        toolbar = tk.Frame(self, bg="#0b0b0b")
        toolbar.pack(fill="x", padx=8, pady=(6, 0))
        self._txt_path = tk.StringVar()
        tk.Label(toolbar, text=t("ملف TXT:", "TXT File:"), fg="#888888", bg="#0b0b0b",
                 font=("Courier New", 9)).pack(side="left")
        tk.Entry(toolbar, textvariable=self._txt_path,
                 font=("Courier New", 9), fg="#7cfc7c", bg="#0d1a0d",
                 insertbackground="#7cfc7c", relief="flat", bd=0,
                 highlightthickness=1, highlightbackground="#2a5a2a",
                 width=36).pack(side="left", ipady=3, padx=6)
        tk.Button(toolbar, text=t("تصفح", "Browse"),
                  font=("Courier New", 8), fg="#c8a035", bg="#1a1500",
                  activeforeground="#c8a035", activebackground="#2a2000",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#c8a035",
                  command=self._browse, padx=8, pady=2).pack(side="left")
        tk.Button(toolbar, text=t("تحميل", "Load"),
                  font=("Courier New", 8), fg="#7cfc7c", bg="#1a2a0a",
                  activeforeground="#7cfc7c", activebackground="#2a4a1a",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#7cfc7c",
                  command=self._load, padx=8, pady=2).pack(side="left", padx=4)
        tk.Frame(self, bg="#222").pack(fill="x")  # separator after toolbar
        save_row = tk.Frame(self, bg="#0b0b0b")
        save_row.pack(fill="x", padx=8, pady=(4,0))
        tk.Button(save_row, text=t("حفظ الملف", "Save File"),
                  font=("Courier New", 8), fg="#c8a035", bg="#1a1500",
                  activeforeground="#c8a035", activebackground="#2a2000",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#c8a035",
                  command=self._save, padx=8, pady=2
                  ).pack(side="right")
        tk.Frame(self, bg="#222", height=1).pack(fill="x")

        # options row
        opt = tk.Frame(self, bg="#0b0b0b")
        opt.pack(fill="x", padx=8, pady=(2, 2))
        self._char_mode = tk.BooleanVar(value=False)
        tk.Checkbutton(opt, text=t("اختيار كل حرف", "Select each character"),
                       variable=self._char_mode,
                       command=self._on_char_mode_change,
                       fg="#cccccc", bg="#0b0b0b",
                       activebackground="#0b0b0b", selectcolor="#1a1a1a",
                       font=("Courier New", 8), relief="flat").pack(side="left")

        tk.Frame(self, bg="#1a1a1a", height=1).pack(fill="x")

        # text display
        body = tk.Frame(self, bg="#0b0b0b")
        body.pack(fill="both", expand=True, padx=8, pady=8)

        self._text = tk.Text(
            body, font=("Courier New", 10),
            fg="#e8e8e8", bg="#080808",
            insertbackground="#7cfc7c",
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground="#222",
            wrap="word", cursor="arrow", state="disabled"
        )
        sb = tk.Scrollbar(body, command=self._text.yview)
        self._text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._text.pack(fill="both", expand=True)

        self._text.tag_configure("aev_hide",     foreground="#ff4444")
        self._text.tag_configure("aev_show",     foreground="#7cfc7c")
        self._text.tag_configure("aev_multi",    foreground="#c8a035")
        self._text.tag_configure("aev_boxes",    foreground="#ffffff", font=("Courier New", 7))
        self._text.tag_configure("box_aev_hide", foreground="#ff4444", font=("Courier New", 10))
        self._text.tag_configure("box_aev_show", foreground="#7cfc7c", font=("Courier New", 10))
        self._text.tag_configure("box_aev_multi",foreground="#c8a035", font=("Courier New", 10))
        self._text.tag_configure("newpage",   foreground="#c8a035", font=("Courier New", 8))
        self._text.tag_configure("hover",     background="#2a2000")
        self._text.tag_configure("separator", foreground="#555555")

        self._text.bind("<Motion>",   self._on_hover)
        self._text.bind("<Button-1>", self._on_click)
        self._text.bind("<Leave>",    lambda e: self._clear_hover())
        self._raw = ""



    def _browse(self):
        p = _browse_open(
            title="Select AEV Option .txt file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            key="aev_txt"
        )
        if p:
            self._txt_path.set(p)
            self._load()

    def _save(self):
        txt_path = self._txt_path.get().strip()
        if not txt_path:
            messagebox.showerror("Error", "No file loaded."); return
        if not self._raw:
            messagebox.showerror("Error", "Nothing to save."); return
        try:
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(self._raw)
            messagebox.showinfo("[+] Saved", f"Saved to:\n{txt_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _load(self):
        path = self._txt_path.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showerror("Error", "Select a valid .txt file first.")
            return
        try:
            raw_bytes = open(path, "rb").read()
            if raw_bytes[:2] in (b'\xff\xfe', b'\xfe\xff'):
                raw = raw_bytes.decode("utf-16", errors="ignore")
            elif raw_bytes[:3] == b'\xef\xbb\xbf':
                raw = raw_bytes[3:].decode("utf-8", errors="ignore")
            else:
                raw = raw_bytes.decode("utf-8", errors="ignore")
            self._raw = raw.replace("\r\n", "\n").replace("\r", "\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        self._render(self._raw)

    def _on_char_mode_change(self):
        if self._raw:
            self._render(self._raw)


    # ── Rendering ──────────────────────────────────────────────────────────────
    def _render(self, raw):
        """Render AEV text with color tags + separators.
        Rules:
          - Normal text (no YYXX before it in current block) → white
          - {0x0700}{0xFFXX} before word → red
          - {0x0700}{0xFEXX} before word → green
          - {0x0700} multiple YYXX → yellow
          Block ends on: {0x0700}(next), {0x0100}, {0x0300}, {0x0400}
          After each block end → insert " | " separator
        """
        import re as _re
        self._raw      = raw
        self._word_map = []  # [(char_start_in_raw, char_end_in_raw, aev_info)]

        self._text.configure(state="normal")
        self._text.delete("1.0", "end")

        TOKEN = _re.compile(r'\{0[xX][0-9A-Fa-f]+\}')
        tokens = list(TOKEN.finditer(raw))

        pos           = 0    # current position in raw
        i             = 0    # token index
        current_codes = []   # [(action, idx_val)] for current block

        SEP = " | "

        def insert_text(txt, aev_info):
            """Insert txt respecting char_mode; register word_map."""
            char_mode = getattr(self, "_char_mode", None)
            use_char  = char_mode and char_mode.get()

            if not txt:
                return

            # Determine tag
            if not aev_info:
                tag = ("hover_word",)
            elif len(aev_info) == 1:
                act = aev_info[0][0]
                tag = ("aev_hide" if act == "hide" else "aev_show", "hover_word")
            else:
                tag = ("aev_multi", "hover_word")

            if use_char:
                # Insert char by char
                for ch in txt:
                    if ch.strip():
                        ws = self._text.index("end-1c")
                        self._text.insert("end", ch, tag)
                        we = self._text.index("end-1c")
                        if aev_info:
                            self._word_map.append((ws, we, {"codes": list(aev_info)}))
                    else:
                        self._text.insert("end", ch)
            else:
                # Insert word by word, preserve spaces
                for m in _re.finditer(r'\S+|\s+', txt):
                    chunk = m.group(0)
                    if chunk.strip():
                        ws = self._text.index("end-1c")
                        self._text.insert("end", chunk, tag)
                        we = self._text.index("end-1c")
                        if aev_info:
                            self._word_map.append((ws, we, {"codes": list(aev_info)}))
                    else:
                        self._text.insert("end", chunk)

        while i <= len(tokens):
            m       = tokens[i] if i < len(tokens) else None
            end_pos = m.start() if m else len(raw)

            # Insert text between last token and this one
            if end_pos > pos:
                chunk = raw[pos:end_pos]
                insert_text(chunk, current_codes if current_codes else None)

            if m is None:
                break

            code_str = m.group(0).upper().replace(" ","")
            try:
                code_int = int(code_str[1:-1], 16)
            except Exception:
                pos = m.end(); i += 1; continue

            if code_int == 0x0100:
                if current_codes:
                    self._text.insert("end", SEP, ("separator",))
                current_codes = []
                self._text.insert("end", "\n" + chr(0x2500)*40 + "\n", ("newpage",))

            elif code_int == 0x0300:
                if current_codes:
                    self._text.insert("end", SEP, ("separator",))
                current_codes = []
                self._text.insert("end", "\n")

            elif code_int == 0x0400:
                if current_codes:
                    self._text.insert("end", SEP, ("separator",))
                current_codes = []
                self._text.insert("end", " [New Page] ", ("newpage",))

            elif code_int == 0x0700:
                # End previous block — always insert | separator
                self._text.insert("end", SEP, ("separator",))
                # Consume following YYXX codes
                current_codes = []
                j = i + 1
                while j < len(tokens):
                    nxt_str = tokens[j].group(0).upper().replace(" ","")[1:-1]
                    try:
                        nxt_int = int(nxt_str, 16)
                        hi = (nxt_int >> 8) & 0xFF
                        if hi in (0xFF, 0xFE):
                            lo = nxt_int & 0xFF
                            current_codes.append(("hide" if hi == 0xFF else "show", lo))
                            j += 1
                        else:
                            break
                    except Exception:
                        break
                pos = tokens[j-1].end() if j > i+1 else m.end()
                i   = j
                continue

            # else: 0x0000, 0x0800 etc — skip

            pos = m.end()
            i  += 1

        self._text.configure(state="disabled")


    def _on_hover(self, event):
        self._text.tag_remove("hover", "1.0", "end")
        idx  = self._text.index(f"@{event.x},{event.y}")
        tags = self._text.tag_names(idx)
        if "hover_word" in tags:
            if self._char_mode.get():
                start = idx
                end   = f"{idx}+1c"
            else:
                start = self._text.index(f"{idx} wordstart")
                end   = self._text.index(f"{idx} wordend")
            self._text.tag_add("hover", start, end)

    def _clear_hover(self):
        self._text.tag_remove("hover", "1.0", "end")


    def _on_click(self, event):
        idx  = self._text.index(f"@{event.x},{event.y}")
        tags = self._text.tag_names(idx)
        if "hover_word" not in tags:
            return

        char_mode = self._char_mode.get()
        if char_mode:
            start = idx
            end   = f"{idx}+1c"
        else:
            start = self._text.index(f"{idx} wordstart")
            end   = self._text.index(f"{idx} wordend")

        word = self._text.get(start, end).strip()
        if not word:
            return

        # Look up aev_info by exact start position
        aev_info = None
        for (ws, we, info) in self._word_map:
            try:
                if self._text.compare(ws, "==", start):
                    aev_info = info
                    break
            except Exception:
                pass

        if aev_info is None:
            self._show_aev_options(word, start, end)
        else:
            self._show_info_edit_dialog(word, start, end, aev_info)

    def _show_info_edit_dialog(self, word, start, end, aev_info):
        """Two-button dialog: INFO or EDIT."""
        dlg = tk.Toplevel(self)
        dlg.title("AEV Option")
        dlg.configure(bg="#0b0b0b")
        dlg.resizable(False, False)
        dlg.grab_set()

        codes = aev_info.get("codes", [])

        tk.Frame(dlg, bg="#e07b54", height=2).pack(fill="x")
        tk.Label(dlg, text=f'"{word[:28]}"',
                 fg="#c8a035", bg="#0b0b0b",
                 font=("Courier New", 10, "bold")).pack(padx=20, pady=(12,6))

        # Brief summary line
        if len(codes) == 1:
            action, idx_val = codes[0]
            color = "#ff4444" if action == "hide" else "#7cfc7c"
            summary = f"{'FF' if action=='hide' else 'FE'}{idx_val:02X}  →  {'Hide' if action=='hide' else 'Show'}  AEV#{idx_val}"
        else:
            summary = f"{len(codes)} AEV codes"
        tk.Label(dlg, text=summary, fg="#888", bg="#0b0b0b",
                 font=("Courier New", 8)).pack(padx=20, pady=(0,10))

        # Two big buttons
        bf = tk.Frame(dlg, bg="#0b0b0b")
        bf.pack(padx=20, pady=(0,16))

        def do_info():
            dlg.destroy()
            self._show_info_view(word, codes)

        def do_edit():
            dlg.destroy()
            self._show_aev_options(word, start, end, existing_codes=codes)

        tk.Button(bf, text=t("معلومات","INFO"),
                  font=("Courier New", 10, "bold"),
                  fg="#888", bg="#1a1a1a",
                  activeforeground="#cccccc", activebackground="#2a2a2a",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#2a2a2a",
                  padx=20, pady=8, command=do_info
                  ).pack(side="left", padx=6)
        tk.Button(bf, text=t("تعديل","EDIT"),
                  font=("Courier New", 10, "bold"),
                  fg="#7cfc7c", bg="#1a2a0a",
                  activeforeground="#7cfc7c", activebackground="#2a4a1a",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#2a5a2a",
                  padx=20, pady=8, command=do_edit
                  ).pack(side="left", padx=6)

    def _show_info_view(self, word, codes):
        """Display AEV code details."""
        dlg = tk.Toplevel(self)
        dlg.title("AEV Info")
        dlg.configure(bg="#0b0b0b")
        dlg.resizable(False, False)
        dlg.grab_set()

        tk.Frame(dlg, bg="#5b9bd5", height=2).pack(fill="x")
        tk.Label(dlg, text=f'"{word[:28]}"',
                 fg="#c8a035", bg="#0b0b0b",
                 font=("Courier New", 10, "bold")).pack(padx=20, pady=(12,6))

        for action, idx_val in codes:
            color = "#ff4444" if action == "hide" else "#7cfc7c"
            row = tk.Frame(dlg, bg="#0e0e0e")
            row.pack(fill="x", padx=16, pady=2, ipady=4)
            tk.Label(row,
                     text=f"  {'FF' if action=='hide' else 'FE'}{idx_val:02X}",
                     fg=color, bg="#0e0e0e",
                     font=("Courier New", 10, "bold"), width=8).pack(side="left")
            tk.Label(row,
                     text=f"{t('يخفي AEV','Hide AEV') if action=='hide' else t('يبقي AEV','Show AEV')}  —  INDEX: {idx_val} (0x{idx_val:02X})",
                     fg="#cccccc", bg="#0e0e0e",
                     font=("Courier New", 9)).pack(side="left", padx=8)

        tk.Frame(dlg, bg="#1a1a1a", height=1).pack(fill="x", padx=12, pady=8)
        tk.Button(dlg, text=t("إغلاق","Close"),
                  font=("Courier New", 9), fg="#888", bg="#1a1a1a",
                  relief="flat", bd=0, cursor="hand2", padx=12, pady=4,
                  command=dlg.destroy).pack(pady=(0,12))

    def _show_aev_dialog(self, word, start, end):
        self._show_aev_options(word, start, end)

    def _show_aev_options(self, word, start, end, existing_codes=None):
        """Show dialog to add/edit AEV codes for a word."""
        txt_path = self._txt_path.get().strip()
        if not txt_path or not os.path.isfile(txt_path):
            messagebox.showerror("Error", "Load a TXT file first.")
            return

        dlg = tk.Toplevel(self)
        dlg.title("AEV Options")
        dlg.resizable(False, True)
        dlg.configure(bg="#0b0b0b")
        dlg.grab_set()

        tk.Frame(dlg, bg="#e07b54", height=2).pack(fill="x")
        tk.Label(dlg, text=f'"{word[:28]}"',
                 fg="#c8a035", bg="#0b0b0b",
                 font=("Courier New", 10, "bold")).pack(padx=20, pady=(10,4))

        # Number of AEV entries
        num_frame = tk.Frame(dlg, bg="#0b0b0b")
        num_frame.pack(fill="x", padx=20, pady=4)
        tk.Label(num_frame, text=t("عدد AEV (0 = فقط {0x0700}):", "Number of AEV (0 = just {0x0700}):"),
                 fg="#888", bg="#0b0b0b",
                 font=("Courier New", 8)).pack(side="left")
        count_var = tk.IntVar(value=max(1, len(existing_codes)) if existing_codes else 1)
        count_spin = tk.Spinbox(num_frame, from_=0, to=10,
                                textvariable=count_var,
                                width=4, font=("Courier New", 9),
                                bg="#1a1a1a", fg="#cccccc",
                                buttonbackground="#2a2a2a")
        count_spin.pack(side="left", padx=8)

        body = tk.Frame(dlg, bg="#0b0b0b")
        body.pack(fill="both", expand=True, padx=20, pady=4)

        aev_rows = []  # list of (hide_var, idx_var)

        def rebuild_rows(*_):
            for w in body.winfo_children():
                w.destroy()
            aev_rows.clear()
            n = count_var.get()
            for i in range(n):
                fr = tk.Frame(body, bg="#0e0e0e",
                              highlightthickness=1, highlightbackground="#2a2a2a")
                fr.pack(fill="x", pady=3, ipady=4)

                lbl = f"AEV {i+1}" if n > 1 else "AEV"
                tk.Label(fr, text=lbl, fg="#c8a035", bg="#0e0e0e",
                         font=("Courier New", 8, "bold")).pack(anchor="w", padx=8, pady=(4,2))

                # Prefill from existing_codes if editing
                if existing_codes and i < len(existing_codes):
                    pre_action, pre_idx = existing_codes[i]
                    hide_default = (pre_action == "hide")
                    idx_default  = f"{pre_idx:02X}"
                else:
                    hide_default = True
                    idx_default  = "00"

                hide_var = tk.BooleanVar(value=hide_default)
                row1 = tk.Frame(fr, bg="#0e0e0e")
                row1.pack(fill="x", padx=8)
                tk.Label(row1, text=t("اخفاء AEV بعد الضغط؟", "Hide AEV after press?"),
                         fg="#cccccc", bg="#0e0e0e",
                         font=("Courier New", 8)).pack(side="left")
                tk.Radiobutton(row1, text=t("نعم","Yes"), variable=hide_var, value=True,
                               fg="#7cfc7c", bg="#0e0e0e",
                               activebackground="#0e0e0e", selectcolor="#0b0b0b",
                               font=("Courier New", 8)).pack(side="left", padx=6)
                tk.Radiobutton(row1, text=t("لا","No"), variable=hide_var, value=False,
                               fg="#ff5555", bg="#0e0e0e",
                               activebackground="#0e0e0e", selectcolor="#0b0b0b",
                               font=("Courier New", 8)).pack(side="left")

                idx_var = tk.StringVar(value=idx_default)
                row2 = tk.Frame(fr, bg="#0e0e0e")
                row2.pack(fill="x", padx=8, pady=(2,4))
                tk.Label(row2, text=t("رقم AEV (hex):", "AEV Index (hex):"),
                         fg="#cccccc", bg="#0e0e0e",
                         font=("Courier New", 8)).pack(side="left")
                tk.Entry(row2, textvariable=idx_var,
                         width=4, font=("Courier New", 9),
                         fg="#7cfc7c", bg="#0d1a0d",
                         insertbackground="#7cfc7c",
                         relief="flat", bd=0,
                         highlightthickness=1, highlightbackground="#2a5a2a"
                         ).pack(side="left", padx=8, ipady=2)
                aev_rows.append((hide_var, idx_var))

        count_var.trace_add("write", rebuild_rows)
        rebuild_rows()

        # Buttons
        bf = tk.Frame(dlg, bg="#0b0b0b")
        bf.pack(fill="x", padx=20, pady=(4,12))

        def do_apply():
            try:
                raw_bytes = open(txt_path, "rb").read()
                if raw_bytes[:2] in (b'\xff\xfe', b'\xfe\xff'):
                    raw = raw_bytes.decode("utf-16", errors="ignore")
                elif raw_bytes[:3] == b'\xef\xbb\xbf':
                    raw = raw_bytes[3:].decode("utf-8", errors="ignore")
                else:
                    raw = raw_bytes.decode("utf-8", errors="ignore")
                raw = raw.replace("\r\n", "\n").replace("\r", "\n")
            except Exception as e:
                messagebox.showerror("Error", str(e)); dlg.destroy(); return

            n = count_var.get()

            # Build new prefix (empty if n=0, otherwise {0x0700}{0xYYZZ}...)
            if n == 0:
                new_prefix = ""
            else:
                new_prefix = "{0x0700}"
                for hide_var, idx_var in aev_rows[:n]:
                    raw_idx = idx_var.get().strip().upper().zfill(2)
                    try:
                        int(raw_idx, 16)
                    except ValueError:
                        messagebox.showerror("Error", f"Invalid hex: {raw_idx}"); return
                    yy = "FF" if hide_var.get() else "FE"
                    new_prefix += "{0x" + yy + raw_idx + "}"

            # Find word position
            word_pos = raw.find(word)
            if word_pos < 0:
                messagebox.showwarning("Not found", f'"{word}" not found in file.')
                return

            # Remove any existing {0x0700}{0xYYZZ}* block immediately before word
            import re as _re
            TOKEN_BLOCK = _re.compile(
                r'(\{0[xX]0700\}(\{0[xX][Ff][Ee][0-9A-Fa-f]{2}\}|\{0[xX][Ff][Ff][0-9A-Fa-f]{2}\})*)',
                _re.IGNORECASE
            )
            # Check if there's a token block ending exactly at word_pos
            before = raw[:word_pos]
            m = None
            for m in TOKEN_BLOCK.finditer(before):
                pass  # find last match
            if m and m.end() == word_pos:
                # remove it
                raw = raw[:m.start()] + raw[word_pos:]
                word_pos = m.start()

            new_raw = raw[:word_pos] + new_prefix + raw[word_pos:]
            try:
                with open(txt_path, "w", encoding="utf-8", newline="\n") as f:
                    f.write(new_raw)
            except Exception as e:
                messagebox.showerror("Save Error", str(e)); return
            self._raw = new_raw
            self._render(new_raw)
            dlg.destroy()
            if n == 0:
                messagebox.showinfo("[+] Applied", f"AEV codes removed from \"{word[:20]}\"")
            else:
                messagebox.showinfo("[+] Applied", f"AEV codes updated for \"{word[:20]}\"")

        tk.Button(bf, text=t("إلغاء","Cancel"),
                  font=("Courier New", 9), fg="#888", bg="#1a1a1a",
                  relief="flat", bd=0, cursor="hand2", padx=10, pady=4,
                  command=dlg.destroy).pack(side="left")
        tk.Button(bf, text=t("تطبيق","Apply"),
                  font=("Courier New", 9, "bold"), fg="#7cfc7c", bg="#1a2a0a",
                  activeforeground="#7cfc7c", activebackground="#2a4a1a",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#2a5a2a",
                  padx=14, pady=4, command=do_apply).pack(side="right")


# ══════════════════════════════════════════════════════════════════
#  LockAEVPanel  —  wrapper with AVL Editor + events.cfg Editor
# ══════════════════════════════════════════════════════════════════

class LockAEVPanel(tk.Frame):

    _SECTIONS = [
        {"id": "avl",    "label": "AVL EDITOR"},
        {"id": "events", "label": "events.cfg Editor"},
    ]
    _COLORS = {"avl": "#c8a035", "events": "#5bc8c8"}

    def __init__(self, parent, master_app, **kw):
        super().__init__(parent, bg="#0b0b0b", **kw)
        self.master_app = master_app
        self._sub_panels = {}
        self._sub_btns   = {}
        self._active_id  = None
        self._built      = False

    def activate(self):
        if not self._built:
            self._build()
            self._built = True
        self._switch("avl")
        self._sub_panels["avl"].activate()

    def _build(self):
        hdr = tk.Frame(self, bg="#0e0e0e"); hdr.pack(fill="x")
        tk.Label(hdr, text="LOCK AEV WITH KEY",
                 fg="#e07b54", bg="#0e0e0e",
                 font=("Courier New", 13, "bold")).pack(side="left", padx=16, pady=8)
        tk.Label(hdr, text="avl editor & events.cfg editor",
                 fg="#666", bg="#0e0e0e",
                 font=("Courier New", 8)).pack(side="left", pady=8)
        tk.Frame(self, bg="#666", height=1).pack(fill="x")
        self._sep_line = None  # set after build

        # sub-tab bar
        tab_bar = tk.Frame(self, bg="#111"); tab_bar.pack(fill="x")
        for item in self._SECTIONS:
            sid   = item["id"]
            color = self._COLORS[sid]
            bf    = tk.Frame(tab_bar, bg="#111"); bf.pack(side="left")
            ind   = tk.Frame(bf, bg="#111", height=3); ind.pack(fill="x")
            btn   = tk.Button(bf, text=item["label"],
                              font=("Courier New", 9, "bold"),
                              fg="#3a3a3a", bg="#111",
                              activeforeground=color, activebackground="#1a1a1a",
                              relief="flat", bd=0, cursor="hand2",
                              padx=18, pady=6,
                              command=lambda s=sid: self._switch(s))
            btn.pack()
            btn.bind("<Enter>", lambda e,b=btn,i=ind,c=color: (b.configure(fg=c),i.configure(bg=c)))
            btn.bind("<Leave>", lambda e,b=btn,i=ind,k=sid: (
                b.configure(fg=self._COLORS[k] if self._active_id==k else "#3a3a3a"),
                i.configure(bg=self._COLORS[k] if self._active_id==k else "#111")
            ))
            self._sub_btns[sid] = (btn, ind)

        self._bot_sep = tk.Frame(self, bg="#222", height=1); self._bot_sep.pack(fill="x")

        # content
        self._content = tk.Frame(self, bg="#0b0b0b")
        self._content.pack(fill="both", expand=True)

        avl_panel    = AVLEditorPanel(self._content, self.master_app)
        events_panel = EventsCFGPanel(self._content, self.master_app)
        avl_panel.place(relx=0, rely=0, relwidth=1, relheight=1)
        events_panel.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._sub_panels["avl"]    = avl_panel
        self._sub_panels["events"] = events_panel

    def _switch(self, sid):
        if self._active_id:
            ob, oi = self._sub_btns[self._active_id]
            ob.configure(fg="#3a3a3a"); oi.configure(bg="#111")
        self._active_id = sid
        self._sub_panels[sid].lift()
        nb, ni = self._sub_btns[sid]
        nc = self._COLORS[sid]
        nb.configure(fg=nc); ni.configure(bg=nc)
        self._bot_sep.configure(bg=nc)
        if sid == "avl":
            self._sub_panels["avl"].activate()
        elif sid == "events":
            self._sub_panels["events"].activate()


# ══════════════════════════════════════════════════════════════════
#  EventsCFGPanel  —  events.cfg editor
# ══════════════════════════════════════════════════════════════════

class EventsCFGPanel(tk.Frame):
    """events.cfg editor — add/edit/remove AEV lock entries."""

    def __init__(self, parent, master_app, **kw):
        super().__init__(parent, bg="#0b0b0b", **kw)
        self.master_app = master_app
        self._cfg_path  = tk.StringVar()
        self._locks     = []   # list of lock dicts
        self._built     = False

    def activate(self):
        if not self._built:
            self._build()
            self._built = True

    # ── Build ────────────────────────────────────────────────────
    def _build(self):
        hdr = tk.Frame(self, bg="#0e0e0e"); hdr.pack(fill="x")
        tk.Label(hdr, text="events.cfg EDITOR",
                 fg="#5bc8c8", bg="#0e0e0e",
                 font=("Courier New", 12, "bold")).pack(side="left", padx=16, pady=8)
        tk.Label(hdr, text=t("إعداد قواعد قفل/فتح AEV","configure AEV lock / unlock rules"),
                 fg="#666", bg="#0e0e0e",
                 font=("Courier New", 8)).pack(side="left", pady=8)
        tk.Frame(self, bg="#5bc8c8", height=1).pack(fill="x")

        # path row
        top = tk.Frame(self, bg="#111"); top.pack(fill="x", padx=12, pady=8)
        tk.Label(top, text=t("ملف Cfg:","CFG File:"), fg="#999", bg="#111",
                 font=("Courier New", 9)).pack(side="left")
        tk.Entry(top, textvariable=self._cfg_path,
                 font=("Courier New", 9), fg="#5bc8c8", bg="#081a1a",
                 insertbackground="#5bc8c8",
                 relief="flat", bd=0,
                 highlightthickness=1, highlightbackground="#1a5a5a",
                 width=42).pack(side="left", ipady=3, padx=6)
        tk.Button(top, text=t("تصفح", "Browse"),
                  font=("Courier New", 8), fg="#c8a035", bg="#1a1500",
                  activeforeground="#c8a035", activebackground="#2a2000",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#c8a035",
                  command=self._browse, padx=8, pady=2).pack(side="left")
        tk.Button(top, text=t("تحميل", "Load"),
                  font=("Courier New", 8), fg="#5bc8c8", bg="#081a1a",
                  activeforeground="#5bc8c8", activebackground="#0f2a2a",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#5bc8c8",
                  command=self._load, padx=8, pady=2).pack(side="left", padx=4)

        # count + buttons
        ctrl = tk.Frame(self, bg="#0b0b0b"); ctrl.pack(fill="x", padx=16, pady=(0,4))
        self._count_var = tk.StringVar(value=t("عدد الأقفال: 0","Locks: 0"))
        tk.Label(ctrl, textvariable=self._count_var,
                 fg="#5bc8c8", bg="#0b0b0b",
                 font=("Courier New", 9)).pack(side="left")
        tk.Button(ctrl, text=t("حفظ الملف", "Save File"),
                  font=("Courier New", 8), fg="#c8a035", bg="#1a1500",
                  activeforeground="#c8a035", activebackground="#2a2000",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#c8a035",
                  command=self._save, padx=8, pady=2).pack(side="right")
        tk.Button(ctrl, text=t("+ إضافة قفل", "+ Add Lock"),
                  font=("Courier New", 8), fg="#5bc8c8", bg="#081a1a",
                  activeforeground="#5bc8c8", activebackground="#0f2a2a",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#5bc8c8",
                  command=self._add_lock, padx=8, pady=2).pack(side="right", padx=4)

        tk.Frame(self, bg="#222", height=1).pack(fill="x")

        # scrollable area
        cf = tk.Frame(self, bg="#0b0b0b"); cf.pack(fill="both", expand=True)
        self._canvas = tk.Canvas(cf, bg="#0b0b0b", highlightthickness=0)
        sb = tk.Scrollbar(cf, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)
        self._entries_frame = tk.Frame(self._canvas, bg="#0b0b0b")
        self._cw = self._canvas.create_window((0,0), window=self._entries_frame, anchor="nw")
        self._entries_frame.bind("<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
            lambda e: self._canvas.itemconfig(self._cw, width=e.width))
        self._canvas.bind("<MouseWheel>",
            lambda e: self._canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    # ── Browse / Load / Save ─────────────────────────────────────
    def _browse(self):
        p = _browse_open(
            title="Select events.cfg file",
            filetypes=[("CFG files", "*.cfg"), ("All files", "*.*")],
            key="events_cfg"
        )
        if p:
            self._cfg_path.set(p)
            self._load()

    def _load(self):
        path = self._cfg_path.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showerror("Error", "Select a valid .cfg file first."); return
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                raw = f.read()
        except Exception as e:
            messagebox.showerror("Error", str(e)); return
        self._locks = self._parse(raw)
        self._count_var.set(f'{t("عدد الأقفال","Locks")}: {len(self._locks)}')
        self._render()

    def _save(self):
        path = self._cfg_path.get().strip()
        if not path:
            messagebox.showerror("Error", "No file loaded."); return
        try:
            content = self._serialize()
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
            messagebox.showinfo("[+] Saved", f"Saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ── Parser ───────────────────────────────────────────────────
    def _parse(self, raw):
        import re as _re
        locks = []
        # match event_lock0 { ... } blocks
        pattern = _re.compile(
            r'event_lock\d+\s*\{(.*?)\}', _re.DOTALL)
        for m in pattern.finditer(raw):
            block = m.group(1)
            def gv(key, default="0x00"):
                r = _re.search(rf'{key}\s+(0x[0-9A-Fa-f]+|\d+)', block)
                return r.group(1) if r else default
            def gvs(key, default="false"):
                r = _re.search(rf'{key}\s+(\w+)', block)
                return r.group(1) if r else default
            # unlock block
            unlock_m = _re.search(r'event_unlock\s*\{(.*?)\}', block, _re.DOTALL)
            unlock = {}
            if unlock_m:
                ub = unlock_m.group(1)
                def gu(key, default="0x00"):
                    r = _re.search(rf'{key}\s+(0x[0-9A-Fa-f]+|\d+)', ub)
                    return r.group(1) if r else default
                unlock = {
                    "ItemID":         gu("ItemID",         "0x00"),
                    "Sound":          gu("Sound",          "0x0B"),
                    "Message":        gu("Message",        "0x06"),
                    "LockEventIndex": gu("LockEventIndex", "0x00"),
                    "Unlocked":       gvs("Unlocked") if _re.search(r'Unlocked\s+\w+', ub) else "false",
                }
            locks.append({
                "ItemID":     gv("ItemID",     "0x00"),
                "Message":    gv("Message",    "0x05"),
                "Sound":      gv("Sound",      "0x0A"),
                "Unknown0":   gv("Unknown0",   "0xFF"),
                "Unknown1":   gv("Unknown1",   "0x00"),
                "EventIndex": gv("EventIndex", "0x00"),
                "unlock":     unlock or {
                    "ItemID":         "0x00",
                    "Sound":          "0x0B",
                    "Message":        "0x06",
                    "LockEventIndex": "0x00",
                    "Unlocked":       "false",
                },
            })
        return locks

    # ── Serializer ───────────────────────────────────────────────
    def _serialize(self):
        lines = []
        for i, lk in enumerate(self._locks):
            ul = lk["unlock"]
            lines.append(f"event_lock{i}")
            lines.append("{")
            lines.append(f"    ItemID {lk['ItemID']}")
            lines.append(f"    Message {lk['Message']}")
            lines.append(f"    Sound {lk['Sound']}")
            lines.append(f"    Unknown0 {lk['Unknown0']}")
            lines.append(f"    Unknown1 {lk['Unknown1']}")
            lines.append(f"    EventIndex {lk['EventIndex']}")
            lines.append("    event_unlock")
            lines.append("    {")
            lines.append(f"        ItemID {ul['ItemID']}")
            lines.append(f"        Sound {ul['Sound']}")
            lines.append(f"        Message {ul['Message']}")
            lines.append(f"        LockEventIndex {ul['LockEventIndex']}")
            lines.append(f"        Unlocked {ul['Unlocked']}")
            lines.append("    }")
            lines.append("}")
            lines.append("")
        return "\n".join(lines)

    # ── Render ───────────────────────────────────────────────────
    def _render(self):
        for w in self._entries_frame.winfo_children():
            w.destroy()
        self._lock_vars = []

        for n, lk in enumerate(self._locks):
            if n > 0:
                tk.Frame(self._entries_frame, bg="#5bc8c8", height=1
                         ).pack(fill="x", padx=0, pady=6)

            # header
            hr = tk.Frame(self._entries_frame, bg="#111"); hr.pack(fill="x")
            tk.Label(hr, text=f'{t("القفل رقم","Lock")} {n}',
                     fg="#5bc8c8", bg="#111",
                     font=("Courier New", 9, "bold")).pack(side="left", padx=12, pady=4)

            def make_del(idx=n):
                def do():
                    if messagebox.askyesno("Delete", f"Delete Lock {idx}?"):
                        del self._locks[idx]
                        self._count_var.set(f"Locks: {len(self._locks)}")
                        self._render()
                return do
            tk.Button(hr, text=t("حذف", "Delete"),
                      font=("Courier New", 7), fg="#ff6060", bg="#2a0a0a",
                      activeforeground="#ff6060", activebackground="#3a1010",
                      relief="flat", bd=0, cursor="hand2",
                      highlightthickness=1, highlightbackground="#ff6060",
                      command=make_del(), padx=6, pady=1).pack(side="right", padx=8)

            # two columns: Lock fields | Unlock fields
            cols = tk.Frame(self._entries_frame, bg="#0b0b0b")
            cols.pack(fill="x", padx=16, pady=4)

            lock_frame   = tk.LabelFrame(cols, text=f" {t('مقفل','Lock')} ",
                fg="#e07b54", bg="#0b0b0b",
                font=("Courier New", 8, "bold"), padx=8, pady=6)
            lock_frame.pack(side="left", padx=(0,12), anchor="n")

            unlock_frame = tk.LabelFrame(cols, text=f" {t('فك القفل','Unlock')} ",
                fg="#7ec8a0", bg="#0b0b0b",
                font=("Courier New", 8, "bold"), padx=8, pady=6)
            unlock_frame.pack(side="left", anchor="n")

            lock_fields = [
                (t("AEV index","EventIndex"), t("رقم AEV","AEV Event Index"),   "hex"),
                ("ItemID",     t("العنصر المطلوب","Item Required"),     "item"),
                ("Message",    t("الرسالة عند قفل الباب","Lock Message"),      "hex"),
                ("Sound",      t("الصوت عند قفل الباب","Lock Sound"),        "hex"),
                ("Unknown0",   t("الكاميرا عند قفل الباب","Lock CAM"),          "hex"),
                ("Unknown1",   t("Unknown1","Unknown1"),          "hex"),
            ]
            unlock_fields = [
                (t("AEV index","LockEventIndex"), t("رقم AEV","AEV Event Index"),   "hex"),
                ("ItemID",         t("العنصر المطلوب","Item Required"),     "item"),
                ("Sound",          t("الصوت عند فتح الباب","Unlock Sound"),      "hex"),
                ("Message",        t("الرسالة عند فتح الباب","Unlock Message"),    "hex"),
                ("Unlocked",       t("مفتوح مسبقًا","Already Unlocked?"), "bool"),
            ]

            lk_vars = {}

            def make_fields(parent, fields, data, prefix):
                for row_i, (key, label, ftype) in enumerate(fields):
                    tk.Label(parent, text=f"{label}:",
                             fg="#888", bg="#0b0b0b",
                             font=("Courier New", 8), anchor="w", width=16
                             ).grid(row=row_i, column=0, sticky="w", pady=2)
                    val = data.get(key, "0x00")
                    if ftype == "bool":
                        var = tk.StringVar(value=val)
                        cb = ttk.Combobox(parent, textvariable=var,
                                          values=["false","true"],
                                          state="readonly", width=7,
                                          font=("Courier New", 8))
                        cb.grid(row=row_i, column=1, sticky="w", padx=4, pady=2)
                        lk_vars[f"{prefix}_{key}"] = var
                    elif ftype == "item":
                        var = tk.StringVar(value=val.replace("0x","").replace("0X","").upper().zfill(2))
                        item_row_f = tk.Frame(parent, bg="#0b0b0b"); item_row_f.grid(row=row_i, column=1, sticky="w", padx=4, pady=2)
                        hv = var.get()
                        name = next((nm for hx,nm in ITEM_LIST if hx.upper()==f"0x{hv}".upper()), "Unknown")
                        disp = tk.Label(item_row_f, text=f"{hv} - {name}",
                                        fg="#c8a035", bg="#0b0b0b",
                                        font=("Courier New", 8), width=22, anchor="w")
                        disp.pack(side="left")
                        def make_pick_cfg(v=var, d=disp):
                            def do():
                                def cb2(item_name):
                                    for hx, nm in ITEM_LIST:
                                        if nm == item_name:
                                            hex_only = hx.replace("0x","").replace("0X","").upper()
                                            v.set(hex_only)
                                            d.configure(text=f"{hex_only} - {item_name}")
                                            return
                                ItemSelector(self, _get_item_list_categorized(), cb2, title="Select Item")
                            return do
                        tk.Button(item_row_f, text="...",
                                  font=("Courier New", 8), fg="#c8a035", bg="#1a1500",
                                  relief="flat", bd=0, cursor="hand2",
                                  highlightthickness=1, highlightbackground="#c8a035",
                                  command=make_pick_cfg(var, disp), padx=6, pady=1
                                  ).pack(side="left", padx=4)
                        lk_vars[f"{prefix}_{key}"] = var
                    else:
                        var = tk.StringVar(value=val.replace("0x","").replace("0X","").upper().zfill(2))
                        _make_validated_entry(parent, var, mode="hex2",
                                 font=("Courier New", 9),
                                 fg="#5bc8c8", bg="#081a1a",
                                 insertbackground="#5bc8c8",
                                 relief="flat", bd=0,
                                 highlightthickness=1, highlightbackground="#1a5a5a",
                                 width=6, justify="center"
                                 ).grid(row=row_i, column=1, sticky="w", padx=4, pady=2)
                        lk_vars[f"{prefix}_{key}"] = var

            make_fields(lock_frame,   lock_fields,   lk,            "lock")
            make_fields(unlock_frame, unlock_fields, lk.get("unlock",{}), "unlock")

            self._lock_vars.append(lk_vars)

        # bind vars to _locks on change
        self._lock_vars  # available for _save via _collect_vars

    def _collect_vars(self):
        """Sync StringVars back to self._locks before saving."""
        for i, lk_vars in enumerate(self._lock_vars):
            lk = self._locks[i]
            def fmthex(v):
                s = v.get().strip().upper().zfill(2)
                return f"0x{s}"
            lk["ItemID"]     = fmthex(lk_vars["lock_ItemID"])
            lk["Message"]    = fmthex(lk_vars["lock_Message"])
            lk["Sound"]      = fmthex(lk_vars["lock_Sound"])
            lk["Unknown0"]   = fmthex(lk_vars["lock_Unknown0"])
            lk["Unknown1"]   = fmthex(lk_vars["lock_Unknown1"])
            lk["EventIndex"] = fmthex(lk_vars["lock_EventIndex"])
            ul = lk.setdefault("unlock", {})
            ul["ItemID"]         = fmthex(lk_vars["unlock_ItemID"])
            ul["Sound"]          = fmthex(lk_vars["unlock_Sound"])
            ul["Message"]        = fmthex(lk_vars["unlock_Message"])
            ul["LockEventIndex"] = fmthex(lk_vars["unlock_LockEventIndex"])
            ul["Unlocked"]       = lk_vars["unlock_Unlocked"].get()

    def _add_lock(self):
        self._locks.append({
            "ItemID":     "0x00",
            "Message":    "0x05",
            "Sound":      "0x0A",
            "Unknown0":   "0xFF",
            "Unknown1":   "0x00",
            "EventIndex": "0x00",
            "unlock": {
                "ItemID":         "0x00",
                "Sound":          "0x0B",
                "Message":        "0x06",
                "LockEventIndex": "0x00",
                "Unlocked":       "false",
            }
        })
        self._count_var.set(f"Locks: {len(self._locks)}")
        self._render()

    def _save(self):
        path = self._cfg_path.get().strip()
        if not path:
            messagebox.showerror("Error", "No file loaded."); return
        if hasattr(self, "_lock_vars"):
            self._collect_vars()
        try:
            content = self._serialize()
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
            messagebox.showinfo("[+] Saved", f"Saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))



class AVLEditorPanel(tk.Frame):
    """AVL Editor  read/write AVL binary files."""

    def __init__(self, parent, master_app, **kw):
        super().__init__(parent, bg="#0b0b0b", **kw)
        self.master_app = master_app
        self._avl_path  = tk.StringVar()
        self._entries   = []   # list of dicts, one per AVL entry
        self._built     = False

    def activate(self):
        if not self._built:
            self._build()
            self._built = True

    def _build(self):
        hdr = tk.Frame(self, bg="#0e0e0e")
        hdr.pack(fill="x")
        tk.Label(hdr, text="AVL EDITOR",
                 fg="#c8a035", bg="#0e0e0e",
                 font=("Courier New", 13, "bold")).pack(side="left", padx=16, pady=8)
        tk.Label(hdr, text=t("تعديل بيانات القفل / المفتاح AVL", "edit AVL lock / key data"),
                 fg="#666666", bg="#0e0e0e",
                 font=("Courier New", 8)).pack(side="left", pady=8)
        tk.Frame(self, bg="#c8a035", height=1).pack(fill="x")

        # path row
        top = tk.Frame(self, bg="#111")
        top.pack(fill="x", padx=12, pady=8)

        tk.Label(top, text=t("ملف AVL:", "AVL File:"), fg="#999", bg="#111",
                 font=("Courier New", 9)).pack(side="left")

        tk.Entry(top, textvariable=self._avl_path,
                 font=("Courier New", 9), fg="#7cfc7c", bg="#0d1a0d",
                 insertbackground="#7cfc7c",
                 relief="flat", bd=0,
                 highlightthickness=1, highlightbackground="#2a5a2a",
                 width=40).pack(side="left", ipady=3, padx=6)

        tk.Button(top, text=t("تصفح", "Browse"),
                  font=("Courier New", 8), fg="#c8a035", bg="#1a1500",
                  activeforeground="#c8a035", activebackground="#2a2000",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#c8a035",
                  command=self._browse, padx=8, pady=2
                  ).pack(side="left")

        tk.Button(top, text=t("تحميل", "Load"),
                  font=("Courier New", 8), fg="#7cfc7c", bg="#1a2a0a",
                  activeforeground="#7cfc7c", activebackground="#2a4a1a",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#7cfc7c",
                  command=self._load, padx=8, pady=2
                  ).pack(side="left", padx=4)

        # count display
        count_row = tk.Frame(self, bg="#0b0b0b")
        count_row.pack(fill="x", padx=16, pady=(0, 4))
        self._count_var = tk.StringVar(value=t("عدد الأقفال: ","Locks: "))
        tk.Label(count_row, textvariable=self._count_var,
                 fg="#c8a035", bg="#0b0b0b",
                 font=("Courier New", 9)).pack(side="left")

        tk.Button(count_row, text=t("حفظ الملف", "Save File"),
                  font=("Courier New", 8), fg="#c8a035", bg="#1a1500",
                  activeforeground="#c8a035", activebackground="#2a2000",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#c8a035",
                  command=self._save, padx=8, pady=2
                  ).pack(side="right", padx=4)

        tk.Button(count_row, text=t("+ إضافة قفل","+ Add Lock"),
                  font=("Courier New", 8), fg="#7cfc7c", bg="#1a2a0a",
                  activeforeground="#7cfc7c", activebackground="#2a4a1a",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#7cfc7c",
                  command=self._add_entry, padx=8, pady=2
                  ).pack(side="right")

        tk.Frame(self, bg="#222", height=1).pack(fill="x", padx=0)

        # scrollable entries area
        canvas_frame = tk.Frame(self, bg="#0b0b0b")
        canvas_frame.pack(fill="both", expand=True, padx=0)

        self._canvas = tk.Canvas(canvas_frame, bg="#0b0b0b",
                                  highlightthickness=0)
        sb = tk.Scrollbar(canvas_frame, orient="vertical",
                           command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._entries_frame = tk.Frame(self._canvas, bg="#0b0b0b")
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._entries_frame, anchor="nw"
        )
        self._entries_frame.bind("<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
            lambda e: self._canvas.itemconfig(
                self._canvas_window, width=e.width))

    def _browse(self):
        p = _browse_open(
            title="Select AVL file",
            filetypes=[("AVL files", "*.avl"), ("All files", "*.*")],
            key="avl"
        )
        if p:
            self._avl_path.set(p)
            self._load()

    def _save(self):
        txt_path = self._txt_path.get().strip()
        if not txt_path:
            messagebox.showerror("Error", "No file loaded."); return
        if not self._raw:
            messagebox.showerror("Error", "Nothing to save."); return
        try:
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(self._raw)
            messagebox.showinfo("[+] Saved", f"Saved to:\n{txt_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _load(self):
        path = self._avl_path.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showerror("Error", "Select a valid AVL file first.")
            return
        try:
            with open(path, "rb") as f:
                data = f.read()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        # parse entries
        # look for header "Number of Aev--"
        header = bytes.fromhex("4E756D62657220 6F6620416576 2D2D".replace(" ", ""))
        entries = []
        pos = 0
        while True:
            idx = data.find(header, pos)
            if idx < 0:
                break
            # read 8 values (XX bytes) at their fixed offsets within the entry
            entry_vals = {}
            offsets = [15, 30, 47, 63, 79, 95, 111]
            for i, off in enumerate(offsets):
                byte_pos = idx + off
                if byte_pos < len(data):
                    entry_vals[i] = data[byte_pos]
                else:
                    entry_vals[i] = 0
            entries.append({"start": idx, "vals": entry_vals})
            pos = idx + 16  # move past header

        self._entries = entries
        self._count_var.set(f'{t("عدد الأقفال","AVL count")}: {len(entries)}')
        self._render_entries()

    def _render_entries(self):
        for w in self._entries_frame.winfo_children():
            w.destroy()
        self._entry_vars = []

        for n, entry in enumerate(self._entries):
            # separator between entries
            if n > 0:
                tk.Frame(self._entries_frame, bg="#c8a035", height=1
                         ).pack(fill="x", padx=0, pady=4)

            hdr_row = tk.Frame(self._entries_frame, bg="#111")
            hdr_row.pack(fill="x", padx=0)
            tk.Label(hdr_row, text=f'{t("القفل رقم","Lock")} {n+1}',
                     fg="#c8a035", bg="#111",
                     font=("Courier New", 9, "bold")).pack(side="left", padx=12, pady=4)
            # delete button
            def make_delete(idx=n):
                def do():
                    if messagebox.askyesno(
                        "Delete AVL" if CURRENT_LANG=="en" else "حذف AVL",
                        f"Delete Lock {idx+1}?"
                        if CURRENT_LANG=="en" else
                        f"حذف Lock {idx+1}؟"
                    ):
                        del self._entries[idx]
                        self._count_var.set(f'{t("عدد الأقفال","AVL count")}: {len(self._entries)}')
                        self._render_entries()
                return do
            tk.Button(hdr_row, text="Delete" if CURRENT_LANG=="en" else "حذف",
                      font=("Courier New", 7),
                      fg="#ff6060", bg="#2a0a0a",
                      activeforeground="#ff6060", activebackground="#3a1010",
                      relief="flat", bd=0, cursor="hand2",
                      highlightthickness=1, highlightbackground="#ff6060",
                      command=make_delete(), padx=6, pady=1
                      ).pack(side="right", padx=8)

            grid = tk.Frame(self._entries_frame, bg="#0b0b0b")
            grid.pack(padx=16, pady=4, anchor="w")

            row_vars = {}
            field_labels = [
                ("AEV Number",     "رقم AEV"),
                ("Key ID",         "رقم المفتاح"),
                ("Lock Message",   "الرسالة عند قفل الباب"),
                ("Lock Sound",     "الصوت عند قفل الباب"),
                ("Lock Camera",    "الكاميرا عند قفل الباب"),
                ("Unlock Message", "الرسالة عند فتح الباب"),
                ("Unlock Sound",   "الصوت عند فتح الباب"),
            ]

            for i, (lbl_en, lbl_ar) in enumerate(field_labels):
                lbl = lbl_en if CURRENT_LANG == "en" else lbl_ar
                row = i

                tk.Label(grid, text=f"{lbl:<20}",
                         fg="#c8a035", bg="#0b0b0b",
                         font=("Courier New", 9),
                         width=22, anchor="w"
                         ).grid(row=row, column=0, padx=(0, 8), pady=3, sticky="w")

                val = entry["vals"].get(i, 0)
                hex_val = f"{val:02X}"

                if lbl_en == "Key ID":
                    # show hex value + button to open item picker
                    var = tk.StringVar(value=hex_val)
                    row_vars[i] = ("item_pick", var, None, None)

                    item_row = tk.Frame(grid, bg="#0b0b0b")
                    item_row.grid(row=row, column=1, padx=(0,8), pady=3, sticky="w")

                    # display label
                    disp_lbl = tk.Label(item_row,
                        text=f"{hex_val} - " + next((nm for hx,nm in ITEM_LIST if hx.upper()==f"0x{hex_val}".upper()), "Unknown"),
                        fg="#c8a035", bg="#0b0b0b",
                        font=("Courier New", 8), width=24, anchor="w")
                    disp_lbl.pack(side="left")

                    def make_pick(v=var, lbl=disp_lbl):
                        def do():
                            self._pick_item(v, lbl)
                        return do

                    tk.Button(item_row, text="...",
                              font=("Courier New", 8),
                              fg="#c8a035", bg="#1a1500",
                              activeforeground="#c8a035", activebackground="#2a2000",
                              relief="flat", bd=0, cursor="hand2",
                              highlightthickness=1, highlightbackground="#c8a035",
                              command=make_pick(), padx=6, pady=1
                              ).pack(side="left", padx=4)
                else:
                    var = tk.StringVar(value=hex_val)
                    _make_validated_entry(grid, var, mode="hex2",
                             font=("Courier New", 9),
                             fg="#7cfc7c", bg="#0d1a0d",
                             insertbackground="#7cfc7c",
                             relief="flat", bd=0,
                             highlightthickness=1, highlightbackground="#2a5a2a",
                             width=6, justify="center"
                             ).grid(row=row, column=1, padx=(0, 8), pady=3)
                    row_vars[i] = ("entry", var, None, None)

                tk.Label(grid, text="(hex)",
                         fg="#666", bg="#0b0b0b",
                         font=("Courier New", 7)
                         ).grid(row=row, column=2, pady=3, sticky="w")

            self._entry_vars.append(row_vars)

    def _add_entry(self):
        new_entry = {"start": -1, "vals": {i: 0 for i in range(7)}}
        self._entries.append(new_entry)
        self._count_var.set(f"AVL count: {len(self._entries)}")
        self._render_entries()
        # scroll to bottom
        self._canvas.after(50, lambda: self._canvas.yview_moveto(1.0))

    def _pick_item(self, var, disp_lbl):
        """Open item picker using shared ITEM_LIST categorized."""
        def callback(item_name):
            for hx, nm in ITEM_LIST:
                if nm == item_name:
                    hex_id = hx.replace("0x","").replace("0X","").upper()
                    var.set(hex_id)
                    disp_lbl.configure(text=f"{hex_id} - {item_name}")
                    return
        ItemSelector(self, _get_item_list_categorized(), callback, title="Select Item")

    def _save(self):
        path = self._avl_path.get().strip()
        if not path:
            messagebox.showerror("Error", "No file loaded.")
            return
        try:
            with open(path, "rb") as f:
                raw = bytearray(f.read())
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        header   = bytes.fromhex("4E756D62657220 6F66204165762D2D".replace(" ",""))
        offsets  = [15, 30, 47, 63, 79, 95, 111]
        sep_3E   = bytes.fromhex("3E" * 16)

        # gather values from UI
        all_vals = []
        for row_vars in self._entry_vars:
            vals = {}
            for i, (kind, var, *_) in row_vars.items():
                if kind == "item_pick":
                    try: vals[i] = int(var.get().strip(), 16)
                    except: vals[i] = 0
                else:
                    try: vals[i] = int(var.get().strip(), 16)
                    except: vals[i] = 0
            all_vals.append(vals)

        # find existing entry positions
        positions = []
        pos = 0
        while True:
            idx = raw.find(header, pos)
            if idx < 0: break
            positions.append(idx)
            pos = idx + 16

        n_existing = len(positions)
        n_ui       = len(all_vals)

        # update existing entries
        for n in range(min(n_existing, n_ui)):
            start = positions[n]
            for i, off in enumerate(offsets):
                if start + off < len(raw):
                    raw[start + off] = all_vals[n].get(i, 0)

        # add new entries if needed
        for n in range(n_existing, n_ui):
            # find end of last entry  look for sep_3E
            # if last entry has sep_3E, append after it
            # if not, add sep_3E first, then new entry
            last_header_pos = positions[-1] if positions else -1

            has_sep = sep_3E in raw[last_header_pos:last_header_pos + 200] if last_header_pos >= 0 else False

            if not has_sep:
                raw += sep_3E

            # build new entry template
            tmpl_str = (
                "4E756D62657220 6F66204165762D2D 00"
                " 4B65792049445F5F5F5F5F5F5F5F 00 00"
                " 6C6F636B206D6573736167652D2D2D 00"
                " 6C6F636B20736F756E642D2D2D2D2D 00"
                " 6C6F636B2063616D6572612D2D2D2D 00"
                " 756E6C6F636B206D6573736167652D 00"
                " 756E6C6F636B20736F756E642D2D2D 00"
                " 3E3E3E3E3E3E3E3E3E3E3E3E3E3E3E3E"
            ).replace(" ","")
            new_entry = bytearray(bytes.fromhex(tmpl_str))
            for i, off in enumerate(offsets):
                if off < len(new_entry):
                    new_entry[off] = all_vals[n].get(i, 0)
            raw += new_entry
            # update positions list
            positions.append(len(raw) - len(new_entry))

        # count is determined by number of headers in file  no need to write it

        try:
            with open(path, "wb") as f:
                f.write(raw)
            messagebox.showinfo("[+] Saved", f"Saved: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))



# 
# TOOLS REGISTRY + MASTER APP
# 

# 
# OSD EDITOR PANEL
# 

import struct as _struct

# OSD binary constants
OSD_MAGIC     = bytes([0x44, 0x69, 0x73, 0x63])  # "Disc"
OSD_FALSE_HDR = bytes([0x00, 0x00, 0x00, 0x00])
OSD_FOOTER    = bytes([0xCD, 0xCD, 0xCD, 0xCD])


def _make_validated_entry(parent, var, mode="hex2", **kw):
    """
    Validated Entry. Uses vcmd (validatecommand) for instant block.
    mode: hex2 (max FF/2chars), hex4 (max FFFF/4chars),
          dec3 (max 255/3chars), dec5 (max 65535/5chars)
    """
    max_len = {"hex2": 2, "hex4": 4, "dec3": 3, "dec5": 5}.get(mode, 2)
    max_val = {"hex2": 255, "hex4": 65535, "dec3": 255, "dec5": 65535}.get(mode, 255)
    is_hex  = mode.startswith("hex")

    def vcmd_func(P):
        if P == "": return True
        if len(P) > max_len: return False
        try:
            v = int(P, 16 if is_hex else 10)
            return 0 <= v <= max_val
        except ValueError:
            # allow partial hex like "F" mid-typing
            if is_hex and all(c in "0123456789ABCDEFabcdef" for c in P):
                return len(P) <= max_len
            return False

    vcmd = (parent.register(vcmd_func), "%P")
    e = tk.Entry(parent, textvariable=var,
                 validate="key", validatecommand=vcmd, **kw)
    return e
def _osd_read_block(data, pos):
    try:
        aev = data[pos];  pos += 1
        n   = data[pos];  pos += 1
        items, qtys = [], []
        for _ in range(n):
            items.append(_struct.unpack_from('<H', data, pos)[0]); pos += 2
            qtys.append(_struct.unpack_from('<H', data, pos)[0]);  pos += 2
        nsf  = data[pos]; pos += 1
        suc  = list(data[pos:pos+nsf]); pos += nsf
        fail = list(data[pos:pos+nsf]); pos += nsf
        return aev, items, qtys, nsf, suc, fail, pos
    except Exception:
        return None


def _osd_block_to_bytes(b):
    buf = bytearray()
    buf += OSD_MAGIC if b["osd_op"] else OSD_FALSE_HDR
    buf.append(b["aev_index"])
    buf.append(len(b["items"]))
    for item, qty in zip(b.get("items",[]), b.get("quantities",[])):
        buf += _struct.pack('<H', item)
        buf += _struct.pack('<H', qty)
    buf.append(b["num_sf"])
    buf += bytes(b["success_aevs"])
    buf += bytes(b["fail_aevs"])
    return bytes(buf)


def _osd_parse_file(raw):
    data = raw.rstrip(b'\xCD')
    first = data.find(OSD_MAGIC)
    if first == -1:
        return []
    true_blocks = []
    p = first
    while True:
        idx = data.find(OSD_MAGIC, p)
        if idx == -1: break
        res = _osd_read_block(data, idx + 4)
        if res is None: p = idx + 4; continue
        aev, items, qtys, nsf, suc, fail, end = res
        tb = {"osd_op": True, "aev_index": aev, "items": items,
              "quantities": qtys, "num_sf": nsf,
              "success_aevs": suc, "fail_aevs": fail,
              "file_offset": idx, "file_size": end - idx}
        true_blocks.append((idx, end, tb))
        p = idx + 4
    if not true_blocks:
        return []
    all_blocks = []
    first_block = True
    for i, (t_start, t_end, tb) in enumerate(true_blocks):
        if tb["aev_index"] == 0 and len(tb["items"]) == 0:
            if first_block:
                tb["osd_op"] = False
                all_blocks.append(tb)
        else:
            all_blocks.append(tb)
        first_block = False
        zone_start = t_end
        zone_end   = true_blocks[i+1][0] if i+1 < len(true_blocks) else len(data)
        zone = data[zone_start:zone_end]
        zp = 0
        while zp + 4 <= len(zone):
            res = _osd_read_block(zone, zp + 4)
            if res is None: zp += 1; continue
            aev, items, qtys, nsf, suc, fail, new_zp = res
            if aev == 0 and len(items) == 0: zp = new_zp; continue
            fb = {"osd_op": False, "aev_index": aev, "items": items,
                  "quantities": qtys, "num_sf": nsf,
                  "success_aevs": suc, "fail_aevs": fail,
                  "file_offset": zone_start + zp, "file_size": new_zp - zp}
            all_blocks.append(fb)
            zp = new_zp
    return all_blocks


class OSDEditorPanel(tk.Frame):
    """OSD Editor  GUI for reading/writing RE4 .OSD files."""

    def __init__(self, parent, master_app, **kw):
        super().__init__(parent, bg="#0b0b0b", **kw)
        self.master_app  = master_app
        self._osd_path   = tk.StringVar()
        self._blocks     = []
        self._block_vars = []
        self._add_footer = tk.BooleanVar(value=False)
        self._built      = False

    def activate(self):
        if not self._built:
            self._build()
            self._built = True

    def _build(self):
        # header
        hdr = tk.Frame(self, bg="#0e0e0e")
        hdr.pack(fill="x")
        tk.Label(hdr, text="OSD EDITOR",
                 fg="#c8a035", bg="#0e0e0e",
                 font=("Courier New", 12, "bold")).pack(side="left", padx=16, pady=10)
        tk.Frame(self, bg="#c8a035", height=1).pack(fill="x")

        # path row
        top = tk.Frame(self, bg="#111")
        top.pack(fill="x", padx=12, pady=8)
        tk.Label(top, text=t("ملف OSD:", "OSD File:"), fg="#999", bg="#111",
                 font=("Courier New", 9)).pack(side="left")
        tk.Entry(top, textvariable=self._osd_path,
                 font=("Courier New", 9), fg="#7cfc7c", bg="#0d1a0d",
                 insertbackground="#7cfc7c",
                 relief="flat", bd=0,
                 highlightthickness=1, highlightbackground="#2a5a2a",
                 width=44).pack(side="left", ipady=3, padx=6)
        tk.Button(top, text=t("تصفح","Browse"),
                  font=("Courier New", 8), fg="#c8a035", bg="#1a1500",
                  activeforeground="#c8a035", activebackground="#2a2000",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#c8a035",
                  command=self._browse, padx=8, pady=2).pack(side="left")
        tk.Button(top, text=t("تحميل","Load"),
                  font=("Courier New", 8), fg="#7cfc7c", bg="#1a2a0a",
                  activeforeground="#7cfc7c", activebackground="#2a4a1a",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#7cfc7c",
                  command=self._load, padx=8, pady=2).pack(side="left", padx=4)

        # options row
        opt_row = tk.Frame(self, bg="#0b0b0b")
        opt_row.pack(fill="x", padx=16, pady=(0, 4))
        self._count_var = tk.StringVar(value=t("عدد OSD: ", "OSD count: "))
        tk.Label(opt_row, textvariable=self._count_var,
                 fg="#c8a035", bg="#0b0b0b",
                 font=("Courier New", 9)).pack(side="left")

        tk.Checkbutton(opt_row,
                       text=t("إضافة CD CD CD CD", "Add CD CD CD CD footer"),
                       variable=self._add_footer,
                       fg="#ccc", bg="#0b0b0b",
                       activebackground="#0b0b0b", selectcolor="#1a1a1a",
                       font=("Courier New", 8), relief="flat"
                       ).pack(side="left", padx=20)

        tk.Button(opt_row, text=t("+ إضافة OSD", "+ Add OSD"),
                  font=("Courier New", 8), fg="#7cfc7c", bg="#1a2a0a",
                  activeforeground="#7cfc7c", activebackground="#2a4a1a",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#7cfc7c",
                  command=self._add_block, padx=8, pady=2).pack(side="right", padx=4)
        tk.Button(opt_row, text=t("حفظ الملف","Save File"),
                  font=("Courier New", 8), fg="#c8a035", bg="#1a1500",
                  activeforeground="#c8a035", activebackground="#2a2000",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#c8a035",
                  command=self._save, padx=8, pady=2).pack(side="right")

        tk.Frame(self, bg="#222", height=1).pack(fill="x")

        # scrollable area
        cf = tk.Frame(self, bg="#0b0b0b")
        cf.pack(fill="both", expand=True)
        self._canvas = tk.Canvas(cf, bg="#0b0b0b", highlightthickness=0)
        sb = tk.Scrollbar(cf, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)
        self._blocks_frame = tk.Frame(self._canvas, bg="#0b0b0b")
        self._cwin = self._canvas.create_window((0,0), window=self._blocks_frame, anchor="nw")
        self._blocks_frame.bind("<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
            lambda e: self._canvas.itemconfig(self._cwin, width=e.width))

    def _browse(self):
        p = _browse_open(
            title="Select OSD file",
            filetypes=[("OSD files", "*.osd"), ("All files", "*.*")],
            key="osd"
        )
        if p:
            self._osd_path.set(p)
            self._load()

    def _save(self):
        txt_path = self._txt_path.get().strip()
        if not txt_path:
            messagebox.showerror("Error", "No file loaded."); return
        if not self._raw:
            messagebox.showerror("Error", "Nothing to save."); return
        try:
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(self._raw)
            messagebox.showinfo("[+] Saved", f"Saved to:\n{txt_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _load(self):
        path = self._osd_path.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showerror("Error", "Select a valid OSD file first.")
            return
        try:
            with open(path, "rb") as f:
                raw = f.read()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        self._add_footer.set(raw.endswith(OSD_FOOTER))
        blocks = _osd_parse_file(raw)
        if not blocks:
            blocks = [{"osd_op": False, "aev_index": 0, "items": [],
                       "quantities": [], "num_sf": 0,
                       "success_aevs": [], "fail_aevs": []}]
        self._blocks = blocks
        self._count_var.set(f'{t("عدد OSD", "OSD count")}: {len(blocks)}')
        self._render_blocks()

    def _render_blocks(self):
        for w in self._blocks_frame.winfo_children():
            w.destroy()
        self._block_vars = []

        for n, block in enumerate(self._blocks):
            if n > 0:
                tk.Frame(self._blocks_frame, bg="#c8a035", height=1).pack(fill="x", pady=4)

            hdr_row = tk.Frame(self._blocks_frame, bg="#111")
            hdr_row.pack(fill="x")
            tk.Label(hdr_row, text=f'{t("إدخال OSD", "OSD Entry")} {n+1}',
                     fg="#c8a035", bg="#111",
                     font=("Courier New", 9, "bold")).pack(side="left", padx=12, pady=4)

            def make_del(idx=n):
                def do():
                    if messagebox.askyesno(
                        "Delete OSD", f"Delete OSD Entry {idx+1}?"):
                        del self._blocks[idx]
                        self._count_var.set(f'{t("عدد OSD", "OSD count")}: {len(self._blocks)}')
                        self._render_blocks()
                return do
            tk.Button(hdr_row, text=t("حذف","Delete"),
                      font=("Courier New", 7), fg="#ff6060", bg="#2a0a0a",
                      activeforeground="#ff6060", activebackground="#3a1010",
                      relief="flat", bd=0, cursor="hand2",
                      highlightthickness=1, highlightbackground="#ff6060",
                      command=make_del(), padx=6, pady=1).pack(side="right", padx=8)

            grid = tk.Frame(self._blocks_frame, bg="#0b0b0b")
            grid.pack(padx=16, pady=4, anchor="w")

            bvars = {}

            # OSD Operation (toggle)
            op_var = tk.BooleanVar(value=block.get("osd_op", False))
            bvars["osd_op"] = op_var
            op_row = tk.Frame(grid, bg="#0b0b0b")
            op_row.grid(row=0, column=0, columnspan=4, padx=0, pady=3, sticky="w")
            tk.Label(op_row, text=t("عملية OSD (غير نشط/نشط):", "OSD Operation (Disc/active):"),
                     fg="#c8a035", bg="#0b0b0b",
                     font=("Courier New", 9), width=30, anchor="w").pack(side="left")
            op_btn = tk.Button(op_row,
                               text="TRUE" if op_var.get() else "FALSE",
                               width=7, font=("Courier New", 8),
                               fg="#7cfc7c" if op_var.get() else "#bbbbbb",
                               bg="#1a2a0a" if op_var.get() else "#1a1a1a",
                               relief="flat", bd=0, cursor="hand2",
                               highlightthickness=1,
                               highlightbackground="#7cfc7c" if op_var.get() else "#888")
            op_btn.pack(side="left")
            def make_toggle_op(v=op_var, btn=op_btn):
                def do():
                    v.set(not v.get())
                    btn.configure(
                        text="TRUE" if v.get() else "FALSE",
                        fg="#7cfc7c" if v.get() else "#bbbbbb",
                        bg="#1a2a0a" if v.get() else "#1a1a1a",
                        highlightbackground="#7cfc7c" if v.get() else "#888"
                    )
                return do
            op_btn.configure(command=make_toggle_op())

            # AEV Index (hex)
            self._add_hex_field(grid, bvars, 1, t("مؤشر AEV (هكس)", t("رقم AEV (hex)","AEV INDEX (hex)")),
                                f"{block.get('aev_index', 0):02X}", "aev_index")

            # Number of Items
            n_items = len(block.get("items", []))
            n_items_var = tk.StringVar(value=str(n_items))
            bvars["n_items_var"] = n_items_var
            self._add_dec_field(grid, bvars, 2, t("عدد العناصر (عشري)", "Number of Items (dec)"),
                                str(n_items), "n_items_str",
                                on_change=lambda v=n_items_var, b=bvars, g=grid, blk=block:
                                    self._refresh_dynamic(g, b, blk))

            # Dynamic item fields
            items_frame = tk.Frame(grid, bg="#0b0b0b")
            items_frame.grid(row=3, column=0, columnspan=6, sticky="w")
            bvars["items_frame"] = items_frame
            bvars["items"]       = []
            bvars["quantities"]  = []
            self._build_item_fields(items_frame, bvars, block)

            # Number of Success/Fail
            n_sf = block.get("num_sf", 0)
            bvars["n_sf_var"] = tk.StringVar(value=str(n_sf))
            self._add_dec_field(grid, bvars, 4, t("عدد AEV نجاح/فشل (عشري)", "Number of Success/Fail AEVs (dec)"),
                                str(n_sf), "n_sf_str",
                                on_change=lambda b=bvars, g=grid, blk=block:
                                    self._refresh_sf(g, b, blk))

            # Dynamic SF fields
            sf_frame = tk.Frame(grid, bg="#0b0b0b")
            sf_frame.grid(row=5, column=0, columnspan=6, sticky="w")
            bvars["sf_frame"]  = sf_frame
            bvars["suc_aevs"]  = []
            bvars["fail_aevs"] = []
            self._build_sf_fields(sf_frame, bvars, block)

            self._block_vars.append(bvars)

    def _add_hex_field(self, grid, bvars, row, label, val, key, mode="hex2"):
        tk.Label(grid, text=f"{label}:",
                 fg="#c8a035", bg="#0b0b0b",
                 font=("Courier New", 8), width=36, anchor="w"
                 ).grid(row=row, column=0, padx=(0,6), pady=3, sticky="w")
        var = tk.StringVar(value=val)
        bvars[key] = var
        e = _make_validated_entry(grid, var, mode=mode,
                 font=("Courier New", 9),
                 fg="#7cfc7c", bg="#0d1a0d", insertbackground="#7cfc7c",
                 relief="flat", bd=0,
                 highlightthickness=1, highlightbackground="#2a5a2a",
                 width=6, justify="center")
        e.grid(row=row, column=1, pady=3)
        tk.Label(grid, text="HEX", fg="#666", bg="#0b0b0b",
                 font=("Courier New", 7)).grid(row=row, column=2, pady=3, sticky="w", padx=4)

    def _add_dec_field(self, grid, bvars, row, label, val, key, on_change=None, mode="dec3"):
        tk.Label(grid, text=f"{label}:",
                 fg="#c8a035", bg="#0b0b0b",
                 font=("Courier New", 8), width=36, anchor="w"
                 ).grid(row=row, column=0, padx=(0,6), pady=3, sticky="w")
        var = tk.StringVar(value=val)
        bvars[key] = var
        e = _make_validated_entry(grid, var, mode=mode,
                     font=("Courier New", 9),
                     fg="#7cfc7c", bg="#0d1a0d", insertbackground="#7cfc7c",
                     relief="flat", bd=0,
                     highlightthickness=1, highlightbackground="#2a5a2a",
                     width=6, justify="center")
        e.grid(row=row, column=1, pady=3)
        tk.Label(grid, text="Dec", fg="#666", bg="#0b0b0b",
                 font=("Courier New", 7)).grid(row=row, column=2, pady=3, sticky="w", padx=4)
        if on_change:
            var.trace_add("write", lambda *_: on_change())

    def _build_item_fields(self, frame, bvars, block):
        for w in frame.winfo_children():
            w.destroy()
        bvars["items"]      = []
        bvars["quantities"] = []
        items = block.get("items", [])
        qtys  = block.get("quantities", [])
        try:
            n = int(bvars.get("n_items_str", tk.StringVar(value="0")).get())
        except Exception:
            n = len(items)
        for i in range(n):
            row_f = tk.Frame(frame, bg="#0b0b0b")
            row_f.pack(anchor="w", pady=1)
            tk.Label(row_f, text=f'  {t("عنصر", "Item")} {i+1} ID:',
                     fg="#aaa", bg="#0b0b0b",
                     font=("Courier New", 8), width=14, anchor="w").pack(side="left")
            item_val = f"{items[i]:02X}" if i < len(items) else "00"
            item_var = tk.StringVar(value=item_val)
            bvars["items"].append(item_var)
            # show item name instead of raw hex ID
            item_name = next((nm for hx, nm in ITEM_LIST if hx.upper() == f"0x{item_val}".upper()), item_val)
            disp_lbl = tk.Label(row_f,
                                text=f"{item_val} - {item_name}",
                                fg="#c8a035", bg="#0b0b0b", font=("Courier New", 8), width=26, anchor="w")
            disp_lbl.pack(side="left", padx=2)
            def make_pick(v=item_var, lbl=disp_lbl):
                def do(): self._pick_item_osd(v, lbl)
                return do
            tk.Button(row_f, text="...",
                      font=("Courier New", 7), fg="#c8a035", bg="#1a1500",
                      activeforeground="#c8a035", activebackground="#2a2000",
                      relief="flat", bd=0, cursor="hand2",
                      highlightthickness=1, highlightbackground="#c8a035",
                      command=make_pick(), padx=4, pady=1).pack(side="left")
            tk.Label(row_f, text=f'  {t("الكمية","Qty")} {i+1}:',
                     fg="#aaa", bg="#0b0b0b",
                     font=("Courier New", 8), width=8, anchor="w").pack(side="left", padx=(10,0))
            qty_val = str(qtys[i]) if i < len(qtys) else "65535"
            qty_var = tk.StringVar(value=qty_val)
            bvars["quantities"].append(qty_var)
            _make_validated_entry(row_f, qty_var, mode="dec5",
                     font=("Courier New", 8), fg="#7cfc7c", bg="#0d1a0d",
                     insertbackground="#7cfc7c", relief="flat", bd=0,
                     highlightthickness=1, highlightbackground="#2a5a2a",
                     width=6, justify="center").pack(side="left", ipady=2)
            tk.Label(row_f, text="(dec)", fg="#666", bg="#0b0b0b",
                     font=("Courier New", 7)).pack(side="left", padx=2)

    def _build_sf_fields(self, frame, bvars, block):
        for w in frame.winfo_children():
            w.destroy()
        bvars["suc_aevs"]  = []
        bvars["fail_aevs"] = []
        suc  = block.get("success_aevs", [])
        fail = block.get("fail_aevs", [])
        try:
            n = int(bvars["n_sf_str"].get())
        except Exception:
            n = block.get("num_sf", 0)
        for i in range(n):
            row_f = tk.Frame(frame, bg="#0b0b0b")
            row_f.pack(anchor="w", pady=1)
            tk.Label(row_f, text=f"  Success AEV {i+1} (hex):",
                     fg="#aaa", bg="#0b0b0b",
                     font=("Courier New", 8), width=22, anchor="w").pack(side="left")
            sv = tk.StringVar(value=f"{suc[i]:02X}" if i < len(suc) else "FF")
            bvars["suc_aevs"].append(sv)
            _make_validated_entry(row_f, sv, mode="hex2",
                     font=("Courier New", 8),
                     fg="#7cfc7c", bg="#0d1a0d", insertbackground="#7cfc7c",
                     relief="flat", bd=0,
                     highlightthickness=1, highlightbackground="#2a5a2a",
                     width=5, justify="center").pack(side="left", ipady=2)
            tk.Label(row_f, text=f"   Fail AEV {i+1} (hex):",
                     fg="#aaa", bg="#0b0b0b",
                     font=("Courier New", 8), width=18, anchor="w").pack(side="left", padx=(16,0))
            fv = tk.StringVar(value=f"{fail[i]:02X}" if i < len(fail) else "FF")
            bvars["fail_aevs"].append(fv)
            _make_validated_entry(row_f, fv, mode="hex2",
                     font=("Courier New", 8),
                     fg="#7cfc7c", bg="#0d1a0d", insertbackground="#7cfc7c",
                     relief="flat", bd=0,
                     highlightthickness=1, highlightbackground="#2a5a2a",
                     width=5, justify="center").pack(side="left", ipady=2)

    def _refresh_dynamic(self, grid, bvars, block):
        # debounce  only rebuild after 400ms of no typing
        if hasattr(self, "_refresh_after"):
            self.after_cancel(self._refresh_after)
        def do_refresh():
            try:
                n = max(0, min(16, int(bvars["n_items_str"].get())))
            except Exception:
                return
            frame = bvars["items_frame"]
            block["items"]      = list(block.get("items", []))
            block["quantities"] = list(block.get("quantities", []))
            self._build_item_fields(frame, bvars, block)
        self._refresh_after = self.after(400, do_refresh)

    def _refresh_sf(self, grid, bvars, block):
        if hasattr(self, "_refresh_sf_after"):
            self.after_cancel(self._refresh_sf_after)
        def do_refresh():
            try:
                n = max(0, min(16, int(bvars["n_sf_str"].get())))
            except Exception:
                return
            frame = bvars["sf_frame"]
            self._build_sf_fields(frame, bvars, block)
        self._refresh_sf_after = self.after(400, do_refresh)

    def _pick_item_osd(self, var, disp_lbl):
        def callback(item_name):
            for hx, nm in ITEM_LIST:
                if nm == item_name:
                    hex_id = hx.replace("0x","").replace("0X","").upper()
                    var.set(hex_id)
                    disp_lbl.configure(text=f"{hex_id} - {item_name}")
                    return
        ItemSelector(self, _get_item_list_categorized(), callback, title="Select Item")

    def _add_block(self):
        # sync current UI state back to _blocks before adding
        try:
            current = self._collect_blocks()
            self._blocks = current
        except Exception:
            pass
        self._blocks.append({"osd_op": False, "aev_index": 0, "items": [],
                             "quantities": [], "num_sf": 0,
                             "success_aevs": [], "fail_aevs": []})
        self._count_var.set(f"OSD count: {len(self._blocks)}")
        self._render_blocks()
        self._canvas.after(50, lambda: self._canvas.yview_moveto(1.0))

    def _collect_blocks(self):
        """Build block list from current UI vars."""
        blocks = []
        for i, bvars in enumerate(self._block_vars):
            op  = bvars["osd_op"].get()
            aev = int(bvars["aev_index"].get().strip() or "0", 16)
            items, qtys = [], []
            for iv, qv in zip(bvars.get("items",[]), bvars.get("quantities",[])):
                try: items.append(int(iv.get().strip() or "0", 16))
                except: items.append(0)
                try: qtys.append(int(qv.get().strip() or "65535"))
                except: qtys.append(65535)
            suc, fail = [], []
            for sv in bvars.get("suc_aevs", []):
                try: suc.append(int(sv.get().strip() or "FF", 16))
                except: suc.append(0xFF)
            for fv in bvars.get("fail_aevs", []):
                try: fail.append(int(fv.get().strip() or "FF", 16))
                except: fail.append(0xFF)
            nsf = max(len(suc), len(fail))
            suc  = (suc  + [0xFF]*nsf)[:nsf]
            fail = (fail + [0xFF]*nsf)[:nsf]
            blocks.append({"osd_op": op, "aev_index": aev, "items": items,
                           "quantities": qtys, "num_sf": nsf,
                           "success_aevs": suc, "fail_aevs": fail})
        return blocks

    def _save(self):
        path = self._osd_path.get().strip()
        if not path:
            messagebox.showerror("Error", "No OSD file loaded.")
            return
        try:
            blocks = self._collect_blocks()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        try:
            with open(path, "rb") as f:
                raw = bytearray(f.read())
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        has_footer = raw[-4:] == bytearray(OSD_FOOTER)
        if has_footer:
            raw = raw[:-4]

        orig_blocks = _osd_parse_file(bytes(raw))

        # build new bytes
        new_bufs = [_osd_block_to_bytes(b) for b in blocks]

        if not orig_blocks:
            # file is all zeros  write from start
            pos = 0
            for nb in new_bufs:
                nsz = len(nb)
                if pos + nsz <= len(raw):
                    raw[pos:pos+nsz] = nb
                else:
                    raw[pos:] = bytearray(nb[:len(raw)-pos])
                    raw += bytearray(nb[len(raw)-pos:])
                pos += nsz
        else:
            size_added = 0
            for i, (nb, orig) in enumerate(zip(new_bufs, orig_blocks)):
                file_off = orig["file_offset"] + size_added
                orig_sz  = orig["file_size"]
                new_sz   = len(nb)
                extra    = new_sz - orig_sz
                if extra <= 0:
                    raw[file_off:file_off+new_sz] = nb
                    if extra < 0:
                        raw[file_off+new_sz:file_off+orig_sz] = bytes(-extra)
                else:
                    after    = bytes(raw[file_off+orig_sz:])
                    tail     = after.rstrip(b'\x00')
                    trailing = len(after) - len(tail)
                    new_after = tail + bytes(trailing - extra) if trailing >= extra else tail
                    raw = bytearray(raw[:file_off]) + bytearray(nb) + bytearray(new_after)
                    size_added += extra
            # append extra new blocks
            if len(new_bufs) > len(orig_blocks):
                last = orig_blocks[-1]
                pos  = last["file_offset"] + last["file_size"] + size_added
                for nb in new_bufs[len(orig_blocks):]:
                    nsz = len(nb)
                    if pos + nsz <= len(raw):
                        raw[pos:pos+nsz] = nb
                    else:
                        fill = max(0, len(raw) - pos)
                        raw[pos:] = bytearray(nb[:fill])
                        raw += bytearray(nb[fill:])
                    pos += nsz

        if self._add_footer.get() or has_footer:
            raw += bytearray(OSD_FOOTER)

        try:
            with open(path, "wb") as f:
                f.write(raw)
            messagebox.showinfo("[+] Saved", f"Saved: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


# 
# ROOM INIT EDITOR PANEL
# 

ROOM_INIT_CONFIG = {
    "ST1": {"base_address": 0x4DE450, "rooms": {
        "0":"100","1":"101","2":"102","3":"103","4":"104","5":"105",
        "6":"106","7":"107","8":"108","9":"109","A":"10a","B":"10b",
        "C":"10c","D":"10d","E":"10e","F":"10f","10":"111","11":"112",
        "12":"113","13":"117","14":"118","15":"119","16":"11a","17":"11b",
        "18":"11c","19":"11d","1A":"11e","1B":"11f","1C":"120","1D":"121",
        "1E":"122","1F":"123","20":"124","21":"125","22":"126","23":"127",
        "24":"128","25":"129","26":"12a","27":"12b","28":"12c","29":"12d",
        "2A":"12e","2B":"12f","2C":"130","2D":"131","2E":"132","2F":"133",
        "30":"134","31":"135","32":"136","33":"137"}},
    "ST2": {"base_address": 0x4A9E70, "rooms": {
        "0":"200","1":"201","2":"202","3":"203","4":"204","5":"205",
        "6":"206","7":"207","8":"208","9":"209","A":"20a","B":"20b",
        "C":"20c","D":"20d","E":"20e","F":"20f","10":"210","11":"211",
        "12":"212","13":"213","14":"214","15":"215","16":"216","17":"217",
        "18":"218","19":"219","1A":"21a","1B":"21b","1C":"21d","1D":"220",
        "1E":"221","1F":"222","20":"223","21":"224","22":"225","23":"226",
        "24":"227","25":"228","26":"229","27":"22a","28":"22b","29":"22c",
        "2A":"22e","2B":"22f","2C":"230","2D":"231","2E":"232","2F":"233",
        "30":"234","31":"235","32":"236","33":"237","34":"238","35":"239",
        "36":"240","37":"241","38":"242","39":"243","3A":"244","3B":"245"}},
    "ST3": {"base_address": 0x43E530, "rooms": {
        "0":"300","1":"301","2":"302","3":"303","4":"304","5":"305",
        "6":"306","7":"307","8":"308","9":"309","A":"30a","B":"30b",
        "C":"30c","D":"30d","E":"30e","F":"30f","10":"310","11":"311",
        "12":"312","13":"315","14":"316","15":"317","16":"318","17":"31a",
        "18":"31b","19":"31c","1A":"31d","1B":"320","1C":"321","1D":"325",
        "1E":"326","1F":"327","20":"328","21":"329","22":"330","23":"331",
        "24":"332","25":"333","26":"335","27":"336","28":"337","29":"338",
        "2A":"339","2B":"340","2C":"341","2D":"342","2E":"343","2F":"344",
        "30":"345","31":"346","32":"347","33":"348","34":"349","35":"350",
        "36":"351","37":"352","38":"353","39":"354","3A":"355","3B":"356",
        "3C":"357","3D":"358"}},
}


class RoomInitPanel(tk.Frame):
    """Room Init Editor  clone room INIT IDs in bio4.exe."""

    def __init__(self, parent, master_app, **kw):
        super().__init__(parent, bg="#0b0b0b", **kw)
        self.master_app    = master_app
        self._re4lfs_path  = None
        self._bio4_path    = None
        self._built        = False

    def activate(self):
        if not self._built:
            self._build()
            self._built = True
        self._refresh_exe()

    def _get_exe(self):
        return self.master_app.exe_path.get().strip()

    def _refresh_exe(self):
        exe = self._get_exe()
        if exe and os.path.isfile(exe):
            exe_dir = os.path.dirname(exe)
            self._bio4_path = os.path.join(os.path.dirname(exe_dir), "BIO4")
            # re4lfs.exe next to the master EXE in Room Init folder
            self._re4lfs_path = os.path.join(MASTER_DIR, "ROOM INIT EDITOR", "re4lfs.exe")
            enabled = True
        else:
            enabled = False
        self._set_controls(enabled)
        if enabled:
            self._update_source_id()
            self._update_target_id()

    def _build(self):
        # dark text in combobox dropdowns
        _ri_style = ttk.Style()
        _ri_style.theme_use("default")
        _ri_style.configure("RoomInit.TCombobox",
                            foreground="#111111",
                            fieldbackground="#b8d0b8",
                            background="#b8d0b8",
                            selectforeground="#111111",
                            selectbackground="#b8d0b8",
                            arrowcolor="#111111")
        hdr = tk.Frame(self, bg="#0e0e0e")
        hdr.pack(fill="x")
        tk.Label(hdr, text="ROOM INIT EDITOR",
                 fg="#7ec8a0", bg="#0e0e0e",
                 font=("Courier New", 13, "bold")).pack(side="left", padx=16, pady=8)
        tk.Label(hdr, text="clone & extract room init data",
                 fg="#666666", bg="#0e0e0e",
                 font=("Courier New", 8)).pack(side="left", pady=8)
        tk.Frame(self, bg="#7ec8a0", height=1).pack(fill="x")

        desc = tk.Label(self,
                        text="bio4.exe path is set from the top bar. Place re4lfs.exe in: RE4 MASTER EDITOR/ROOM INIT EDITOR/",
                        fg="#888", bg="#0b0b0b", font=("Courier New", 8))
        desc.pack(anchor="w", padx=16, pady=(8,4))

        # room selection
        sel_frame = tk.Frame(self, bg="#0b0b0b")
        sel_frame.pack(fill="x", padx=16, pady=4)

        # Source
        src_box = tk.LabelFrame(sel_frame, text="Source Room (Copy From)",
                                fg="#c8a035", bg="#0b0b0b",
                                font=("Courier New", 8, "bold"))
        src_box.grid(row=0, column=0, padx=(0,12), sticky="ew")

        tk.Label(src_box, text="Stage:", fg="#ccc", bg="#0b0b0b",
                 font=("Courier New", 8)).grid(row=0, column=0, padx=8, pady=4, sticky="w")
        self._src_stage = ttk.Combobox(src_box, values=sorted(ROOM_INIT_CONFIG.keys()),
                                        state="readonly", width=8,
                                        font=("Courier New", 8),
                                        style="RoomInit.TCombobox")
        self._src_stage.grid(row=0, column=1, padx=4, pady=4)
        self._src_stage.current(0)

        tk.Label(src_box, text="Room:", fg="#ccc", bg="#0b0b0b",
                 font=("Courier New", 8)).grid(row=1, column=0, padx=8, pady=4, sticky="w")
        self._src_room = ttk.Combobox(src_box, state="readonly", width=14,
                                       font=("Courier New", 8),
                                       style="RoomInit.TCombobox")
        self._src_room.grid(row=1, column=1, padx=4, pady=4)

        tk.Label(src_box, text="INIT ID:", fg="#ccc", bg="#0b0b0b",
                 font=("Courier New", 8)).grid(row=2, column=0, padx=8, pady=4, sticky="w")
        self._src_id = tk.Entry(src_box, font=("Courier New", 9),
                                fg="#7cfc7c", bg="#0d1a0d",
                                relief="flat", bd=0,
                                highlightthickness=1, highlightbackground="#2a5a2a",
                                width=12, state="readonly")
        self._src_id.grid(row=2, column=1, padx=4, pady=4, ipady=2)

        # Target
        tgt_box = tk.LabelFrame(sel_frame, text="Target Room (Paste To)",
                                fg="#c8a035", bg="#0b0b0b",
                                font=("Courier New", 8, "bold"))
        tgt_box.grid(row=0, column=1, sticky="ew")

        tk.Label(tgt_box, text="Stage:", fg="#ccc", bg="#0b0b0b",
                 font=("Courier New", 8)).grid(row=0, column=0, padx=8, pady=4, sticky="w")
        self._tgt_stage = ttk.Combobox(tgt_box, values=sorted(ROOM_INIT_CONFIG.keys()),
                                        state="readonly", width=8,
                                        font=("Courier New", 8),
                                        style="RoomInit.TCombobox")
        self._tgt_stage.grid(row=0, column=1, padx=4, pady=4)
        self._tgt_stage.current(0)

        tk.Label(tgt_box, text="Room:", fg="#ccc", bg="#0b0b0b",
                 font=("Courier New", 8)).grid(row=1, column=0, padx=8, pady=4, sticky="w")
        self._tgt_room = ttk.Combobox(tgt_box, state="readonly", width=14,
                                       font=("Courier New", 8),
                                       style="RoomInit.TCombobox")
        self._tgt_room.grid(row=1, column=1, padx=4, pady=4)

        tk.Label(tgt_box, text="INIT ID:", fg="#ccc", bg="#0b0b0b",
                 font=("Courier New", 8)).grid(row=2, column=0, padx=8, pady=4, sticky="w")
        self._tgt_id = tk.Entry(tgt_box, font=("Courier New", 9),
                                fg="#7cfc7c", bg="#0d1a0d",
                                relief="flat", bd=0,
                                highlightthickness=1, highlightbackground="#2a5a2a",
                                width=12, state="readonly")
        self._tgt_id.grid(row=2, column=1, padx=4, pady=4, ipady=2)

        sel_frame.columnconfigure(0, weight=1)
        sel_frame.columnconfigure(1, weight=1)

        # populate rooms
        self._populate_rooms(self._src_stage, self._src_room)
        self._populate_rooms(self._tgt_stage, self._tgt_room)

        # bind changes
        self._src_stage.bind("<<ComboboxSelected>>",
            lambda e: (self._populate_rooms(self._src_stage, self._src_room),
                       self._update_source_id()))
        self._src_room.bind("<<ComboboxSelected>>", lambda e: self._update_source_id())
        self._tgt_stage.bind("<<ComboboxSelected>>",
            lambda e: (self._populate_rooms(self._tgt_stage, self._tgt_room),
                       self._update_target_id()))
        self._tgt_room.bind("<<ComboboxSelected>>", lambda e: self._update_target_id())

        # Advanced options
        adv_frame = tk.Frame(self, bg="#0b0b0b")
        adv_frame.pack(fill="x", padx=16, pady=8)

        opts = [
            ("Clone Advanced (assets, sounds, etc.)", "_clone_adv"),
            ("Auto-Extract LFS Files",                "_auto_lfs"),
            ("Force LFS (overwrite existing)",         "_force_lfs"),
            ("Disable original LFS (rename to .org)", "_disable_lfs"),
        ]
        self._opt_vars = {}
        defaults = [True, True, False, True]
        for i, ((lbl, key), default) in enumerate(zip(opts, defaults)):
            var = tk.BooleanVar(value=default)
            self._opt_vars[key] = var
            row_f = tk.Frame(adv_frame, bg="#0b0b0b")
            row_f.pack(anchor="w", pady=2)
            tk.Checkbutton(row_f, text=lbl, variable=var,
                           fg="#ccc", bg="#0b0b0b",
                           activebackground="#0b0b0b", selectcolor="#1a1a1a",
                           font=("Courier New", 8), relief="flat").pack(side="left")

        # Clone button
        tk.Frame(self, bg="#222", height=1).pack(fill="x", padx=16)
        btn_row = tk.Frame(self, bg="#0b0b0b")
        btn_row.pack(pady=10)
        self._clone_btn = tk.Button(btn_row,
                                    text="Clone Room Data",
                                    font=("Courier New", 11, "bold"),
                                    fg="#0a0a0a", bg="#c8a035",
                                    activeforeground="#0a0a0a", activebackground="#b8902a",
                                    relief="flat", bd=0, cursor="hand2",
                                    highlightthickness=0,
                                    command=self._clone, padx=24, pady=8)
        self._clone_btn.pack()

        # Status
        self._status_var = tk.StringVar(value="")
        tk.Label(self, textvariable=self._status_var,
                 fg="#7cfc7c", bg="#0b0b0b",
                 font=("Courier New", 8), wraplength=600).pack(pady=4)

        self._controls = [self._src_stage, self._src_room,
                          self._tgt_stage, self._tgt_room, self._clone_btn]
        self._set_controls(False)

    def _set_controls(self, enabled):
        state = "normal" if enabled else "disabled"
        if hasattr(self, "_controls"):
            for w in self._controls:
                try: w.configure(state=state)
                except Exception: pass

    def _populate_rooms(self, stage_combo, room_combo):
        stage_key = stage_combo.get()
        if not stage_key or stage_key not in ROOM_INIT_CONFIG:
            return
        rooms = ROOM_INIT_CONFIG[stage_key]["rooms"]
        sorted_rooms = sorted(
            [(f"r{room_id} (val {val})", val) for val, room_id in rooms.items()],
            key=lambda x: x[0]
        )
        room_combo["values"] = [t for t, _ in sorted_rooms]
        room_combo._vals      = [v for _, v in sorted_rooms]
        if sorted_rooms:
            room_combo.current(0)

    def _get_room_val(self, combo):
        idx = combo.current()
        vals = getattr(combo, "_vals", [])
        if 0 <= idx < len(vals):
            return vals[idx]
        return None

    def _calc_offset(self, stage_key, room_val):
        return ROOM_INIT_CONFIG[stage_key]["base_address"] + (int(room_val, 16) * 0x14) + 0x06

    def _read_init_id(self, stage_key, room_val):
        exe = self._get_exe()
        if not exe or not os.path.isfile(exe):
            return ""
        try:
            off = self._calc_offset(stage_key, room_val)
            with open(exe, "rb") as f:
                f.seek(off)
                data = f.read(4)
            if len(data) < 4:
                return "????"
            return data.hex().upper()
        except Exception:
            return ""

    def _update_source_id(self):
        stage = self._src_stage.get()
        val   = self._get_room_val(self._src_room)
        if stage and val:
            id_hex = self._read_init_id(stage, val)
            self._src_id.configure(state="normal")
            self._src_id.delete(0, "end")
            self._src_id.insert(0, id_hex)
            self._src_id.configure(state="readonly")

    def _update_target_id(self):
        stage = self._tgt_stage.get()
        val   = self._get_room_val(self._tgt_room)
        if stage and val:
            id_hex = self._read_init_id(stage, val)
            self._tgt_id.configure(state="normal")
            self._tgt_id.delete(0, "end")
            self._tgt_id.insert(0, id_hex)
            self._tgt_id.configure(state="readonly")

    def _clone(self):
        exe = self._get_exe()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("Error", "Select bio4.exe first.")
            return
        src_id = self._src_id.get().strip()
        if len(src_id) != 8:
            messagebox.showerror("Error", "Source INIT ID is not valid.")
            return
        src_stage = self._src_stage.get()
        tgt_stage = self._tgt_stage.get()
        src_val   = self._get_room_val(self._src_room)
        tgt_val   = self._get_room_val(self._tgt_room)
        if not src_val or not tgt_val:
            messagebox.showerror("Error", "Invalid room selection.")
            return

        src_room_id = ROOM_INIT_CONFIG[src_stage]["rooms"].get(src_val)
        tgt_room_id = ROOM_INIT_CONFIG[tgt_stage]["rooms"].get(tgt_val)

        clone_adv    = self._opt_vars["_clone_adv"].get()
        auto_lfs     = self._opt_vars["_auto_lfs"].get()
        force_lfs    = self._opt_vars["_force_lfs"].get()
        disable_lfs  = self._opt_vars["_disable_lfs"].get()

        if not clone_adv:
            if not messagebox.askyesno("Confirm Simple Clone",
                "Patch target room INIT ID in EXE only. Proceed?"):
                return
            if _check_game_not_running(exe):
                return
            try:
                off = self._calc_offset(tgt_stage, tgt_val)
                with open(exe, "rb+") as f:
                    f.seek(off); f.write(bytes.fromhex(src_id))
                self._update_target_id()
                self._status_var.set(f"Simple Clone done. Target INIT ID patched.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            return

        # Advanced clone
        if not self._bio4_path or not os.path.isdir(self._bio4_path):
            messagebox.showerror("Error",
                "BIO4 folder not found. Ensure bio4.exe is in Bin32 folder.")
            return

        import subprocess

        def get_files(stage_key, room_id):
            stage_dir  = os.path.join(self._bio4_path, stage_key)
            img_dir    = os.path.join(self._bio4_path, "ImagePackHD")
            snd_room   = os.path.join(self._bio4_path, "Snd", "room", stage_key)
            snd_foot   = os.path.join(self._bio4_path, "Snd", "foot", stage_key)
            files = [
                os.path.join(stage_dir, f"r{room_id}.udas"),
                os.path.join(img_dir,   f"44000{room_id}.pack"),
                os.path.join(snd_room,  f"r{room_id}.xwb"),
                os.path.join(snd_room,  f"r{room_id}.xsb"),
                os.path.join(snd_foot,  f"r{room_id}f.xwb"),
                os.path.join(snd_foot,  f"r{room_id}f.xsb"),
            ]
            return files

        src_files = get_files(src_stage, src_room_id)
        tgt_files = get_files(tgt_stage, tgt_room_id)
        lfs_ok    = self._re4lfs_path and os.path.isfile(self._re4lfs_path)

        if not messagebox.askyesno("Confirm Advanced Clone",
            f"Clone r{src_room_id}  r{tgt_room_id}\n\n"
            f"Advanced: {clone_adv}  Auto-LFS: {auto_lfs}  Force: {force_lfs}  Disable-LFS: {disable_lfs}\n\n"
            "Proceed?"):
            return

        try:
            for src_f, tgt_f in zip(src_files, tgt_files):
                ext = os.path.splitext(src_f)[1].lower()
                if ext in (".xwb", ".xsb"):
                    if not os.path.isfile(src_f):
                        messagebox.showerror("Error", f"Sound file not found:\n{os.path.basename(src_f)}")
                        return
                    import shutil
                    os.makedirs(os.path.dirname(tgt_f), exist_ok=True)
                    shutil.copy2(src_f, tgt_f)
                    continue

                if auto_lfs and lfs_ok:
                    lfs = src_f + ".lfs"
                    lfs_org = src_f + ".lfs.org"
                    lfs_src = lfs if os.path.isfile(lfs) else (lfs_org if os.path.isfile(lfs_org) else None)
                    if not os.path.isfile(src_f) and lfs_src:
                        subprocess.run([self._re4lfs_path, lfs_src], check=True,
                                       capture_output=True, creationflags=0x08000000)
                    elif force_lfs and lfs_src:
                        if os.path.isfile(src_f):
                            os.rename(src_f, src_f + ".preclone")
                        subprocess.run([self._re4lfs_path, lfs_src], check=True,
                                       capture_output=True, creationflags=0x08000000)

                if not os.path.isfile(src_f):
                    messagebox.showerror("Error", f"Source file not found:\n{os.path.basename(src_f)}")
                    return

                os.makedirs(os.path.dirname(tgt_f), exist_ok=True)
                import shutil
                shutil.copy2(src_f, tgt_f)

                # patch room IDs in file
                src_pat = self._make_pattern(src_room_id)
                tgt_pat = self._make_pattern(tgt_room_id)
                with open(tgt_f, "rb") as f:
                    data = f.read()
                with open(tgt_f, "wb") as f:
                    f.write(data.replace(src_pat, tgt_pat))

                if disable_lfs:
                    lfs_tgt = tgt_f + ".lfs"
                    if os.path.isfile(lfs_tgt):
                        os.rename(lfs_tgt, lfs_tgt + ".org")

            # patch EXE
            off = self._calc_offset(tgt_stage, tgt_val)
            with open(exe, "rb+") as f:
                f.seek(off); f.write(bytes.fromhex(src_id))
            self._update_target_id()
            self._status_var.set(f"Advanced Clone done: r{src_room_id}  r{tgt_room_id}")
        except Exception as e:
            messagebox.showerror("Error During Clone", str(e))

    def _make_pattern(self, room_id_str):
        stage_char   = room_id_str[0]
        room_hex_str = room_id_str[1:]
        try:
            stage_byte = int(stage_char).to_bytes(1, "little")
        except ValueError:
            stage_byte = stage_char.encode("ascii")[:1]
        room_byte  = int(room_hex_str, 16).to_bytes(1, "little")
        return room_byte + stage_byte + b"\x00\x44"


# 
# WEAPONS AND ITEMS EDITOR PANEL
# 


# 
# WEAPONS AND ITEMS EDITOR PANEL
# 




class _WScrollFrame(tk.Frame):
    """Scrollable tk.Frame — replacement for CTkScrollableFrame."""
    def __init__(self, parent, bg="#1e1e1e", label=None, **kw):
        super().__init__(parent, bg=bg, **kw)
        if label:
            tk.Label(self, text=label, bg=bg, fg="#c8a035",
                     font=("Courier New", 8, "bold")).pack(anchor="w", padx=4, pady=(4,0))
        canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        vsb    = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(canvas, bg=bg)
        self._win  = canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(self._win, width=e.width))
        canvas.bind("<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll( 1, "units"))
        self.inner.grid_columnconfigure(0, weight=1)
        self._canvas = canvas
        self._parent_canvas = canvas

    def _parent_canvas_yview_moveto(self, pos):
        self._canvas.yview_moveto(pos)

    def yview_moveto(self, pos):
        self._canvas.yview_moveto(pos)


# Alias used by original code
_ScrollableFrame = _WScrollFrame


# ── Master Editor UI Constants ────────────────────────────────────────────────
_BG    = "#080808"
_NAV   = "#0d0d0d"
_GOLD  = "#c8a035"
_GREEN = "#7cfc7c"
_MUTED = "#888888"

TOOLS_DEF = [
    {"id": "code_manager",    "label": "CODE MANAGER",    "lock": None,                          "row": 1, "needs_exe": True,  "color": "#5b9bd5"},
    {"id": "osd_editor",      "label": "OSD EDITOR",      "lock": ("aev_osd",   "AEV-OSD"),      "row": 1, "needs_exe": False, "color": "#c8a035"},
    {"id": "cns_editor",      "label": "CNS EDITOR",      "lock": None,                          "row": 1, "needs_exe": True,  "color": "#e07b54"},
    {"id": "snd_editor",      "label": "SND EDITOR",      "lock": None,                          "row": 1, "needs_exe": False, "color": "#7ec8a0"},
    {"id": "aev_editor",      "label": "AEV OPTION",      "lock": ("aev_option","AEV OPTION"),   "row": 1, "needs_exe": False, "color": "#c8a035"},
    {"id": "mdt_color_editor","label": "MDT COLOR",       "lock": None,                          "row": 2, "needs_exe": True,  "color": "#d46fc8"},
    {"id": "room_init_editor","label": "ROOM INIT",       "lock": None,                          "row": 2, "needs_exe": False, "color": "#7ec8a0"},
    {"id": "avl_editor",      "label": "Lock AEV\nwith Key", "lock": None,                       "row": 2, "needs_exe": False, "color": "#e07b54"},
    {"id": "scripts",         "label": "Scripts",         "lock": None,                          "row": 3, "needs_exe": False, "color": "#5bc8c8"},
]



# ══════════════════════════════════════════════════════════════════
#  ScriptsPanel  —  sub-navigation panel
# ══════════════════════════════════════════════════════════════════

class ScriptsPanel(tk.Frame):

    # ── Sub-items definition ──────────────────────────────────────
    _SECTIONS = [
        {"header": "Scripts",         "selectable": False},
        {"id": "data_udas",           "label": "Data to UDAS",        "header": False},
        {"id": "binary_differ",       "label": "Binary File Differ",  "header": False},
        {"id": "exe_identifier",      "label": "EXE Patch Identifier","header": False},
        {"header": "Blender Scripts", "selectable": False},
        {"id": "smd_renamer",         "label": "SMD Renamer",    "header": False},
        {"id": "bin_renamer",         "label": "BIN Renamer",    "header": False},
    ]

    _INFO = {
        "data_udas": {
            "title":      "Data to UDAS",
            "subtitle":   "File Injection Engine",
            "subtitle_ar":"محرك حقن الملفات",
            "color":      "#5bc8c8",
            "icon":       "⚙",
            "desc": (
                "Copies modded files from a DATA source folder\n"
                "into the correct ST stage folders automatically.\n\n"
                "• Detects matching RXXX folders per ST stage\n"
                "• Skips forbidden formats (IDX, AVL, PACK, XWB …)\n"
                "• Smart LIT file selection (_2 pattern)\n"
                "• Conflict resolution dialog for multiple matches\n"
                "• Optional: IDXJ auto-repack via JADERLINK tool\n"
                "• Optional: Master ITM/ETM injection across all rooms\n"
                "• Optional: LFS/UDAS auto-extraction"
            ),
            "desc_ar": (
                "ينسخ ملفات المود من مجلد DATA المصدر\n"
                "إلى مجلدات المراحل ST الصحيحة تلقائياً.\n\n"
                "• يكتشف مجلدات RXXX المطابقة لكل مرحلة ST\n"
                "• يتجاهل الصيغ الممنوعة (IDX، AVL، PACK، XWB …)\n"
                "• اختيار ذكي لملفات LIT (نمط _2)\n"
                "• نافذة حل التعارضات عند وجود تطابقات متعددة\n"
                "• اختياري: إعادة تجميع IDXJ عبر أداة JADERLINK\n"
                "• اختياري: حقن ITM/ETM لجميع الغرف\n"
                "• اختياري: استخراج LFS/UDAS"
            ),
            "tag":   "INJECTION",
            "tag_c": "#e07b54",
        },
        "binary_differ": {
            "title":      "Binary File Differ",
            "subtitle":   "File Comparison Tool",
            "subtitle_ar":"أداة مقارنة الملفات",
            "color":      "#2ECC71",
            "icon":       "⊟",
            "desc": (
                "Compares two binary files byte-by-byte\n"
                "and outputs a hex difference report.\n\n"
                "• Detects all differing byte blocks\n"
                "• Merges nearby diffs (32-byte threshold)\n"
                "• Shows offset + hex bytes for each block\n"
                "• Saves report as .txt file"
            ),
            "desc_ar": (
                "يقارن ملفين ثنائيين بايت بايت\n"
                "ويُخرج تقرير الفروقات بالهكس.\n\n"
                "• يكتشف جميع بلوكات البايتات المختلفة\n"
                "• يدمج الفروقات القريبة (حد 32 بايت)\n"
                "• يعرض الأوفست + البايتات لكل بلوك\n"
                "• يحفظ التقرير كملف .txt"
            ),
            "tag":   "COMPARE",
            "tag_c": "#2ECC71",
        },
        "exe_identifier": {
            "title":      "EXE Patch Identifier",
            "subtitle":   "EXE Modification Checker",
            "subtitle_ar":"فاحص تعديلات EXE",
            "color":      "#3498DB",
            "icon":       "⊞",
            "desc": (
                "Compares original vs modified EXE\n"
                "and identifies all patched offsets.\n\n"
                "• Shows exact offset + original/modified bytes\n"
                "• Merges nearby diffs (32-byte threshold)\n"
                "• Useful for extracting patch data\n"
                "• Saves report as .txt file"
            ),
            "desc_ar": (
                "يقارن EXE الأصلي بالمعدّل\n"
                "ويحدد جميع الأوفستات المُعدَّلة.\n\n"
                "• يعرض الأوفست الدقيق + البايتات الأصلية/المعدَّلة\n"
                "• يدمج الفروقات القريبة (حد 32 بايت)\n"
                "• مفيد لاستخراج بيانات الباتش\n"
                "• يحفظ التقرير كملف .txt"
            ),
            "tag":   "EXE",
            "tag_c": "#3498DB",
        },
        "smd_renamer": {
            "title":      "SMD Renamer",
            "subtitle":   "Blender OBJ Utility",
            "subtitle_ar":"أداة Blender OBJ",
            "color":      "#7ec8a0",
            "icon":       "◈",
            "desc": (
                "Renames SMD indices inside an OBJ file\n"
                "sequentially  →  000, 001, 002 …\n\n"
                "• Targets UHDSCENARIO#SMD_XXX# naming pattern\n"
                "• Sorts objects before renumbering\n"
                "• Keeps SMX, TYPE, and BIN values untouched\n"
                "• Safe in-place rewrite (UTF-8, no BOM)"
            ),
            "desc_ar": (
                "يُعيد تسمية مؤشرات SMD داخل ملف OBJ\n"
                "بالتسلسل  →  000، 001، 002 …\n\n"
                "• يستهدف نمط تسمية UHDSCENARIO#SMD_XXX#\n"
                "• يرتب الكائنات قبل إعادة الترقيم\n"
                "• يحافظ على قيم SMX و TYPE و BIN\n"
                "• إعادة كتابة آمنة في المكان (UTF-8، بدون BOM)"
            ),
            "tag":   "BLENDER",
            "tag_c": "#5b9bd5",
        },
        "bin_renamer": {
            "title":      "BIN Renamer",
            "subtitle":   "Blender OBJ Utility",
            "subtitle_ar":"أداة Blender OBJ",
            "color":      "#c8a035",
            "icon":       "◉",
            "desc": (
                "Renames BIN indices inside an OBJ file\n"
                "sequentially  →  000, 001, 002 …  (max 1000)\n\n"
                "• Targets UHDSCENARIO#BIN_XXX# naming pattern\n"
                "• Sorts objects before renumbering\n"
                "• Keeps SMD, SMX, and TYPE values untouched\n"
                "• Safe in-place rewrite (UTF-8, no BOM)"
            ),
            "desc_ar": (
                "يُعيد تسمية مؤشرات BIN داخل ملف OBJ\n"
                "بالتسلسل  →  000، 001، 002 …  (حد 1000)\n\n"
                "• يستهدف نمط تسمية UHDSCENARIO#BIN_XXX#\n"
                "• يرتب الكائنات قبل إعادة الترقيم\n"
                "• يحافظ على قيم SMD و SMX و TYPE\n"
                "• إعادة كتابة آمنة في المكان (UTF-8، بدون BOM)"
            ),
            "tag":   "BLENDER",
            "tag_c": "#5b9bd5",
        },
    }

    def __init__(self, parent, master_app, **kw):
        super().__init__(parent, bg="#0b0b0b", **kw)
        self.master_app  = master_app
        self._active_id  = None
        self._sub_btns   = {}
        self._sub_panels = {}
        self._built      = False

    def activate(self):
        if not self._built:
            self._build()
            self._built = True
        self._switch("data_udas")

    # ── Build ────────────────────────────────────────────────────
    def _build(self):
        # header bar
        hdr = tk.Frame(self, bg="#0e0e0e")
        hdr.pack(fill="x")
        tk.Label(hdr, text="SCRIPTS", fg="#5bc8c8", bg="#0e0e0e",
                 font=("Courier New", 13, "bold")).pack(side="left", padx=16, pady=8)
        tk.Label(hdr, text="tools & utilities", fg="#444", bg="#0e0e0e",
                 font=("Courier New", 8)).pack(side="left", pady=8)
        tk.Frame(self, bg="#5bc8c8", height=1).pack(fill="x")

        # body: sidebar + content
        body = tk.Frame(self, bg="#0b0b0b")
        body.pack(fill="both", expand=True)

        # ── sidebar ──
        sidebar = tk.Frame(body, bg="#080808", width=150)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Frame(sidebar, bg="#1a1a1a", height=1).pack(fill="x", pady=(6,2))

        for item in self._SECTIONS:
            if item.get("header"):
                # section header label (not clickable)
                tk.Label(sidebar, text=item["header"].upper(),
                         fg="#5bc8c8", bg="#080808",
                         font=("Courier New", 7, "bold")
                         ).pack(anchor="w", padx=12, pady=(10,2))
                tk.Frame(sidebar, bg="#1a1a1a", height=1).pack(fill="x", padx=8, pady=1)
            else:
                sid   = item["id"]
                info  = self._INFO[sid]
                color = info["color"]

                bf = tk.Frame(sidebar, bg="#080808")
                bf.pack(fill="x")
                ind = tk.Frame(bf, bg="#080808", width=3)
                ind.pack(side="left", fill="y")
                btn = tk.Button(bf, text=item["label"],
                                font=("Courier New", 9),
                                fg="#3a3a3a", bg="#080808",
                                activeforeground=color,
                                activebackground="#111",
                                relief="flat", bd=0,
                                anchor="w", padx=10, pady=7,
                                cursor="hand2",
                                command=lambda s=sid: self._switch(s))
                btn.pack(fill="x", expand=True)
                btn.bind("<Enter>", lambda e, b=btn, i=ind, c=color: (b.configure(fg=c), i.configure(bg=c)))
                btn.bind("<Leave>", lambda e, b=btn, i=ind: (
                    b.configure(fg=color if getattr(b,"_active",False) else "#3a3a3a"),
                    i.configure(bg=color if getattr(b,"_active",False) else "#080808")
                ))
                self._sub_btns[sid] = (btn, ind)

        # ── content area ──
        self._content = tk.Frame(body, bg="#0b0b0b")
        self._content.pack(side="left", fill="both", expand=True)

        # build all sub-panels
        for sid, info in self._INFO.items():
            panel = self._build_info_panel(sid, info)
            panel.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._sub_panels[sid] = panel

    def _build_info_panel(self, sid, info):
        """Info card + Launch button for each script."""
        f = tk.Frame(self._content, bg="#0b0b0b")
        color = info["color"]
        tag_c = info["tag_c"]

        # top accent line
        tk.Frame(f, bg=color, height=2).pack(fill="x")

        # inner padding
        body = tk.Frame(f, bg="#0b0b0b")
        body.pack(expand=True)

        # icon + title row
        title_row = tk.Frame(body, bg="#0b0b0b")
        title_row.pack(pady=(50, 0))
        tk.Label(title_row, text=info["icon"],
                 fg=color, bg="#0b0b0b",
                 font=("Courier New", 28)).pack(side="left", padx=(0,12))
        title_col = tk.Frame(title_row, bg="#0b0b0b")
        title_col.pack(side="left")
        tk.Label(title_col, text=info["title"],
                 fg="#e8e8e8", bg="#0b0b0b",
                 font=("Courier New", 16, "bold")).pack(anchor="w")
        tk.Label(title_col,
                 text=info.get("subtitle_ar", info["subtitle"]) if CURRENT_LANG == "ar" else info["subtitle"],
                 fg="#555", bg="#0b0b0b",
                 font=("Courier New", 9)).pack(anchor="w")

        # tag badge
        badge_row = tk.Frame(body, bg="#0b0b0b")
        badge_row.pack(pady=(6,0))
        tk.Label(badge_row, text=f" {info['tag']} ",
                 fg=tag_c, bg="#0f0f0f",
                 font=("Courier New", 7, "bold"),
                 relief="flat", bd=0,
                 highlightthickness=1, highlightbackground=tag_c,
                 padx=4, pady=2).pack()

        # divider
        tk.Frame(body, bg="#1e1e1e", height=1).pack(fill="x", pady=(18,0), padx=40)

        # description
        tk.Label(body,
                 text=info.get("desc_ar", info["desc"]) if CURRENT_LANG == "ar" else info["desc"],
                 fg="#666", bg="#0b0b0b",
                 font=("Courier New", 9),
                 justify="left").pack(pady=18, padx=40, anchor="w")

        # launch button
        btn_frame = tk.Frame(body, bg="#0b0b0b")
        btn_frame.pack(pady=4)

        launch_btn = tk.Button(btn_frame,
                               text=f"  {t('تشغيل', 'Launch')}  {info['title']}  ",
                               font=("Courier New", 11, "bold"),
                               fg="#0a0a0a", bg=color,
                               activeforeground="#0a0a0a",
                               activebackground=color,
                               relief="flat", bd=0,
                               cursor="hand2",
                               padx=24, pady=10,
                               command=lambda s=sid: self._launch(s))
        launch_btn.pack()

        # hover effect on launch button
        def _dim(c):
            # darken hex color slightly
            try:
                r,g,b = int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)
                return f"#{max(r-30,0):02x}{max(g-30,0):02x}{max(b-30,0):02x}"
            except Exception:
                return c
        launch_btn.bind("<Enter>", lambda e,b=launch_btn,c=color: b.configure(bg=_dim(c)))
        launch_btn.bind("<Leave>", lambda e,b=launch_btn,c=color: b.configure(bg=c))

        return f

    # ── Navigation ───────────────────────────────────────────────
    def _switch(self, sid):
        # deactivate old
        if self._active_id and self._active_id in self._sub_btns:
            ob, oi = self._sub_btns[self._active_id]
            oc = self._INFO[self._active_id]["color"]
            ob._active = False
            ob.configure(fg="#3a3a3a"); oi.configure(bg="#080808")

        self._active_id = sid
        panel = self._sub_panels.get(sid)
        if panel:
            panel.lift()

        if sid in self._sub_btns:
            nb, ni = self._sub_btns[sid]
            nc = self._INFO[sid]["color"]
            nb._active = True
            nb.configure(fg=nc); ni.configure(bg=nc)

    # ── Launchers ────────────────────────────────────────────────
    def _launch(self, sid):
        if sid == "data_udas":
            _launch_data_to_udas(self.master_app)
        elif sid == "smd_renamer":
            _launch_smd_renamer(self.master_app)
        elif sid == "bin_renamer":
            _launch_bin_renamer(self.master_app)
        elif sid == "binary_differ":
            _launch_binary_differ(self.master_app)
        elif sid == "exe_identifier":
            _launch_exe_identifier(self.master_app)



# ── Script Launchers ────────────────────────────────────────────

def _launch_data_to_udas(root):
    import shutil as _shutil, threading as _threading, subprocess as _sp

    win = tk.Toplevel(root)
    win.title("Data to UDAS")
    win.geometry("820x900")
    win.configure(bg="#0c0c0c")
    win.transient(root)

    C = {"bg":"#0c0c0c","fg":"#e0e0e0","accent":"#ff4444",
         "entry_bg":"#1a1a1a","btn_bg":"#333333","log_bg":"#050505","success":"#00ff41"}
    FORBIDDEN = {'.IDX','.AVL','.PACK','.XWB','.XSB','.IDX_UHD_EFF_SPLIT','.bak','.EFFBLOB'}

    data_path   = tk.StringVar()
    st_paths    = [tk.StringVar() for _ in range(7)]
    auto_repack  = tk.BooleanVar()
    with_master  = tk.BooleanVar()
    auto_extract = tk.BooleanVar()

    def log(msg):
        log_text.config(state=tk.NORMAL)
        log_text.insert(tk.END, msg + "\n")
        log_text.see(tk.END)
        log_text.config(state=tk.DISABLED)
        win.update_idletasks()

    def browse_folder(var):
        d = filedialog.askdirectory(parent=win)
        if d: var.set(d)

    def make_row(parent, label, var):
        row = tk.Frame(parent, bg=C["bg"]); row.pack(fill="x", pady=2)
        tk.Label(row, text=label, fg=C["fg"], bg=C["bg"], width=15,
                 anchor="w", font=("Consolas", 9)).pack(side="left")
        tk.Entry(row, textvariable=var, bg=C["entry_bg"], fg="white",
                 bd=0, font=("Consolas", 9)).pack(side="left", fill="x", expand=True, padx=5, ipady=3)
        tk.Button(row, text="...", command=lambda: browse_folder(var),
                  bg=C["btn_bg"], fg="white", bd=0, width=5).pack(side="left")

    tk.Label(win, text="RE4 DATA TO UDAS", font=("Consolas", 18, "bold"),
             fg=C["accent"], bg=C["bg"]).pack(pady=10)
    pc = tk.Frame(win, bg=C["bg"]); pc.pack(fill="x", padx=20)
    make_row(pc, "DATA SOURCE:", data_path)
    tk.Frame(pc, height=1, bg="#444").pack(fill="x", pady=8)
    for i in range(7): make_row(pc, f"ST{i} STAGE:", st_paths[i])
    tk.Frame(win, height=1, bg="#444").pack(fill="x", padx=20, pady=6)
    opt = tk.LabelFrame(win, text=" ENGINE OPTIONS ", fg=C["fg"], bg=C["bg"],
                        font=("Consolas", 10, "bold"), padx=10, pady=8)
    opt.pack(fill="x", padx=20, pady=6)
    for text, var in [("AUTOMATIC REPACK (.IDXJ)", auto_repack),
                      ("INJECT MASTER ITM/ETM", with_master),
                      ("LFS/UDAS AUTO-EXTRACTION", auto_extract)]:
        tk.Checkbutton(opt, text=text, variable=var, bg=C["bg"], fg=C["fg"],
                       selectcolor=C["bg"], font=("Consolas", 10)).pack(anchor="w", pady=2)
    tk.Button(win, text="EXECUTE PROCESS",
              bg=C["btn_bg"], fg=C["success"], font=("Consolas", 13, "bold"),
              activebackground=C["accent"], cursor="hand2", bd=0, height=2,
              command=lambda: _threading.Thread(target=run_process, daemon=True).start()
              ).pack(fill="x", padx=20, pady=8)
    lf = tk.Frame(win, bg=C["bg"]); lf.pack(fill="both", expand=True, padx=20, pady=4)
    log_text = tk.Text(lf, bg=C["log_bg"], fg=C["success"], font=("Consolas", 9),
                       wrap="word", state="disabled")
    sb = tk.Scrollbar(lf, command=log_text.yview)
    log_text.configure(yscrollcommand=sb.set)
    log_text.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")
    prog = ttk.Progressbar(win, mode="indeterminate")
    prog.pack(fill="x", padx=20, pady=6)

    def get_active():
        return [(i, v.get()) for i, v in enumerate(st_paths) if v.get() and os.path.exists(v.get())]
    def get_st_num(name):
        m = re.match(r'[Rr](\d)', name); return int(m.group(1)) if m else None
    def find_ext(directory, ext):
        if not os.path.exists(directory): return []
        return [f for f in os.listdir(directory) if f.upper().endswith(ext.upper())]
    def get_match_folder(st_folder, name):
        if not os.path.exists(st_folder): return None
        for f in os.listdir(st_folder):
            if f.lower() == name.lower() and os.path.isdir(os.path.join(st_folder, f)): return f
        return None
    def extract_num(filename):
        m = re.search(r'_(\d{1,3})$', os.path.splitext(filename)[0]); return int(m.group(1)) if m else None
    def get_tools_dir():
        return os.path.join(MASTER_DIR, "Scripts", "Data To Udas")
    def find_exe(name):
        td = get_tools_dir()
        if os.path.exists(td):
            for f in os.listdir(td):
                if f.lower() == name.lower(): return os.path.join(td, f)
        return None
    def collect_files(ext):
        out = []
        for si, sp in get_active():
            for f in os.listdir(sp):
                if f.upper().endswith(ext.upper()) and os.path.isfile(os.path.join(sp, f)):
                    out.append((si, os.path.join(sp, f)))
        return out
    def process_folder(src_folder, st_path, multi):
        name = os.path.basename(src_folder)
        match_name = get_match_folder(st_path, name)
        if not match_name: log(f"  [WARNING] {name} not found in ST"); return
        dst = os.path.join(st_path, match_name)
        for file in os.listdir(src_folder):
            fp = os.path.join(src_folder, file)
            if not os.path.isfile(fp) or not file.lower().startswith("0000."): continue
            parts = file.split('.', 1)
            if len(parts) < 2: continue
            ext = '.' + parts[1].upper()
            if ext in {e.upper() for e in FORBIDDEN}: log(f"  [SKIP] {file}"); continue
            mfiles = find_ext(dst, ext)
            if not mfiles: log(f"  [INFO] No {ext} in ST"); continue
            if ext == '.LIT' and len(mfiles) > 1:
                sel = [f for f in mfiles if extract_num(f) in [2]]
                if sel:
                    old = os.path.join(dst, sel[0])
                    os.remove(old); _shutil.copy2(fp, old); os.remove(fp)
                    log(f"  [REPLACE] {file} -> {sel[0]}")
                else: log(f"  [INFO] No LIT _2 found")
                continue
            if len(mfiles) == 1:
                old = os.path.join(dst, mfiles[0])
                os.remove(old); _shutil.copy2(fp, old); os.remove(fp)
                log(f"  [REPLACE] {file} -> {mfiles[0]}")
            else:
                multi.append({"src_file":fp,"src_name":file,"dst_folder":dst,
                               "ext":ext,"matching_files":mfiles,"folder":name})
                log(f"  [CONFLICT] Multiple {ext} files queued")
    def show_conflicts(items):
        if not items: return
        d = tk.Toplevel(win); d.title("Conflict Resolution"); d.geometry("600x500")
        d.configure(bg="#0c0c0c")
        tk.Label(d, text="MULTIPLE FILES DETECTED", fg="#ff4444", bg="#0c0c0c",
                 font=("Consolas", 12, "bold")).pack(pady=10)
        mf = tk.Frame(d, bg="#0c0c0c"); mf.pack(fill="both", expand=True, padx=10)
        cv = tk.Canvas(mf, bg="#0c0c0c", highlightthickness=0)
        sb2 = tk.Scrollbar(mf, orient="vertical", command=cv.yview)
        sf2 = tk.Frame(cv, bg="#0c0c0c")
        sf2.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0,0), window=sf2, anchor="nw"); cv.configure(yscrollcommand=sb2.set)
        sels = {}; cur = None
        for item in items:
            if item["folder"] != cur:
                cur = item["folder"]
                tk.Label(sf2, text=f"[FOLDER] {cur}", fg="#ff4444", bg="#0c0c0c",
                         font=("Consolas", 10, "bold")).pack(anchor="w", pady=(8,2))
            gf = tk.Frame(sf2, bg="#1a1a1a"); gf.pack(fill="x", pady=3, padx=8)
            tk.Label(gf, text=f"  {item['ext']} - {item['src_name']}", fg="#00ff41",
                     bg="#1a1a1a", font=("Consolas", 8, "bold")).pack(anchor="w", padx=4, pady=2)
            for m in item["matching_files"]:
                v = tk.BooleanVar(value=True)
                sels[f"{item['src_file']}|{m}|{item['dst_folder']}"] = v
                tk.Checkbutton(gf, text=f"  {m}", variable=v, bg="#1a1a1a", fg="#e0e0e0",
                               selectcolor="#0c0c0c", font=("Consolas", 9)).pack(anchor="w", padx=16)
        cv.pack(side="left", fill="both", expand=True); sb2.pack(side="right", fill="y")
        def apply_conf():
            for key, v in sels.items():
                if v.get():
                    sf3, mn, df = key.split("|")
                    mp = os.path.join(df, mn)
                    if os.path.exists(mp): os.remove(mp)
                    _shutil.copy2(sf3, mp)
                    if os.path.exists(sf3): os.remove(sf3)
                    log(f"  [REPLACE] {os.path.basename(sf3)} -> {mn}")
            d.destroy()
        tk.Button(d, text="CONFIRM", command=apply_conf, bg="#333", fg="#00ff41",
                  font=("Consolas", 11, "bold"), bd=0, height=2).pack(fill="x", padx=20, pady=10)
    def run_process():
        try:
            prog.start()
            dr = data_path.get()
            if not os.path.exists(dr): log("[ERROR] DATA path not found!"); return
            dfolders = [d for d in os.listdir(dr)
                        if os.path.isdir(os.path.join(dr,d)) and d.lower().startswith('r')]
            log(f"[SYSTEM] {len(dfolders)} RXXX folders found")
            multi = []
            for si, sp in get_active():
                mf2 = [f for f in dfolders if get_st_num(f) == si]
                log(f"\n[ST{si}] {len(mf2)} matching folders")
                for folder in mf2:
                    log(f"\n[PROCESSING] {folder}")
                    process_folder(os.path.join(dr, folder), sp, multi)
            if with_master.get():
                log("\n[MASTER INJECT] Starting...")
                itm = etm = None
                for f in os.listdir(dr):
                    if f.lower()=="0000.itm": itm=os.path.join(dr,f)
                    elif f.lower()=="0000.etm": etm=os.path.join(dr,f)
                for si, sp in get_active():
                    for folder in os.listdir(sp):
                        fp2 = os.path.join(sp, folder)
                        if not os.path.isdir(fp2) or not folder.lower().startswith('r'): continue
                        for mf3 in [itm, etm]:
                            if not mf3: continue
                            ext2 = '.' + os.path.basename(mf3).split('.',1)[1].upper()
                            for m in find_ext(fp2, ext2):
                                _shutil.copy2(mf3, os.path.join(fp2, m))
                                log(f"  [SYNC] {os.path.basename(mf3)} -> {m}")
            if multi: win.after(0, lambda: show_conflicts(multi))
            if auto_repack.get():
                exe = find_exe("JADERLINK_DATUDAS_TOOL.exe")
                files = [f[1] for f in collect_files('.IDXJ')]
                if exe and files: _sp.Popen([exe]+files); log(f"[REPACK] {len(files)} IDXJ files sent")
                else: log("[REPACK] Tool or IDXJ files not found")
            if auto_extract.get():
                lfs_exe = find_exe("re4lfs.exe"); udas_exe = find_exe("JADERLINK_DATUDAS_TOOL.exe")
                lfs = collect_files('.LFS')
                if lfs and lfs_exe: _sp.run([lfs_exe]+[f[1] for f in lfs],check=True); log(f"[LFS] {len(lfs)} extracted")
                udas = collect_files('.UDAS')
                if udas and udas_exe: _sp.run([udas_exe]+[f[1] for f in udas],check=True); log(f"[UDAS] {len(udas)} extracted")
            log("\n[COMPLETE] ALL DONE!")
        except Exception as e:
            import traceback; log(f"[ERROR] {e}\n{traceback.format_exc()}")
        finally:
            win.after(0, prog.stop)

    win.after(50, lambda: (win.lift(), win.focus_force()))


def _launch_smd_renamer(root):
    import re as _re
    win = tk.Toplevel(root); win.title("SMD Renamer"); win.geometry("500x220")
    win.configure(bg="#121212"); win.transient(root); win.resizable(False, False)
    pattern = r"UHDSCENARIO#SMD_([A-Za-z0-9]{3})#SMX_([A-Za-z0-9]{3})#TYPE_([A-Za-z0-9]{2})#BIN_(\d{3})#"
    entry = tk.Entry(win, width=54, bg="#1e1e1e", fg="#ffffff",
                     insertbackground="white", bd=1, relief="solid", font=("Arial", 10))
    entry.pack(pady=20, padx=20)
    def browse():
        p = filedialog.askopenfilename(parent=win, filetypes=[("OBJ files","*.obj")])
        if p: entry.delete(0,"end"); entry.insert(0,p)
    def apply():
        path = entry.get()
        if not path: messagebox.showerror("Error","No file selected",parent=win); return
        try:
            with open(path,"r",encoding="utf-8",errors="ignore") as f: lines=f.readlines()
            objects = sorted([(i,l) for i,l in enumerate(lines)
                               if l.startswith("o ") and _re.search(pattern,l)], key=lambda x:x[1])
            for n,(i,line) in enumerate(objects):
                lines[i] = _re.sub(pattern, rf"UHDSCENARIO#SMD_{n:03d}#SMX_\2#TYPE_\3#BIN_\4#", line)
            with open(path,"w",encoding="utf-8",newline="") as f: f.writelines(lines)
            messagebox.showinfo("Done","SMD renaming completed",parent=win)
        except Exception as e: messagebox.showerror("Error",str(e),parent=win)
    tk.Button(win,text="Select OBJ",command=browse,bg="#2d2d2d",fg="#fff",
              activebackground="#3d3d3d",bd=0,font=("Arial",10,"bold"),padx=15,pady=5).pack(pady=4)
    tk.Button(win,text="Apply",command=apply,bg="#007acc",fg="#fff",
              activebackground="#0098ff",bd=0,font=("Arial",11,"bold"),width=22,pady=8).pack(pady=12)
    win.after(50, lambda: (win.lift(), win.focus_force()))


def _launch_bin_renamer(root):
    import re as _re
    win = tk.Toplevel(root); win.title("BIN Renamer"); win.geometry("500x220")
    win.configure(bg="#121212"); win.transient(root); win.resizable(False, False)
    pattern = r"UHDSCENARIO#SMD_([A-Za-z0-9]{3})#SMX_([A-Za-z0-9]{3})#TYPE_([A-Za-z0-9]{2})#BIN_(\d{3})#"
    entry = tk.Entry(win, width=54, bg="#1e1e1e", fg="#ffffff",
                     insertbackground="white", bd=1, relief="solid", font=("Arial", 10))
    entry.pack(pady=20, padx=20)
    def browse():
        p = filedialog.askopenfilename(parent=win, filetypes=[("OBJ files","*.obj")])
        if p: entry.delete(0,"end"); entry.insert(0,p)
    def apply():
        path = entry.get()
        if not path: messagebox.showerror("Error","No file selected",parent=win); return
        try:
            with open(path,"r",encoding="utf-8",errors="ignore") as f: lines=f.readlines()
            objects = sorted([(i,l) for i,l in enumerate(lines)
                               if l.startswith("o ") and _re.search(pattern,l)], key=lambda x:x[1])
            for n,(i,line) in enumerate(objects):
                nb = f"{min(n,1000):03d}"
                lines[i] = _re.sub(pattern, rf"UHDSCENARIO#SMD_\1#SMX_\2#TYPE_\3#BIN_{nb}#", line)
            with open(path,"w",encoding="utf-8",newline="") as f: f.writelines(lines)
            messagebox.showinfo("Done","BIN renaming completed",parent=win)
        except Exception as e: messagebox.showerror("Error",str(e),parent=win)
    tk.Button(win,text="Select OBJ",command=browse,bg="#2d2d2d",fg="#fff",
              activebackground="#3d3d3d",bd=0,font=("Arial",10,"bold"),padx=15,pady=5).pack(pady=4)
    tk.Button(win,text="Apply",command=apply,bg="#28a745",fg="#fff",
              activebackground="#218838",bd=0,font=("Arial",11,"bold"),width=22,pady=8).pack(pady=12)
    win.after(50, lambda: (win.lift(), win.focus_force()))


def _launch_binary_differ(root):
    MERGE_DISTANCE = 32
    win = tk.Toplevel(root)
    win.title("Binary File Differ")
    win.geometry("620x210")
    win.configure(bg="#121212")
    win.transient(root)
    win.resizable(False, False)

    bg_color  = "#121212"; fg_color = "#E0E0E0"
    entry_bg  = "#1E1E1E"; btn_bg   = "#2D2D2D"
    btn_active= "#3D3D3D"; accent   = "#2ECC71"

    tk.Label(win, text="Binary File Differ", bg=bg_color, fg="#FFFFFF",
             font=("Helvetica", 12, "bold")).pack(pady=10)

    frame = tk.Frame(win, bg=bg_color)
    frame.pack(padx=20, pady=5, fill="both", expand=True)

    def _browse_entry(e):
        p = filedialog.askopenfilename(parent=win)
        if p: e.delete(0, tk.END); e.insert(0, p)

    tk.Label(frame, text="File A:", bg=bg_color, fg=fg_color,
             font=("Helvetica", 10)).grid(row=0, column=0, padx=5, pady=8, sticky="w")
    entry_a = tk.Entry(frame, width=52, bg=entry_bg, fg="#FFFFFF",
                       insertbackground="white", bd=1, relief="solid", font=("Consolas", 9))
    entry_a.grid(row=0, column=1, padx=10, pady=8)
    tk.Button(frame, text="Browse...", bg=btn_bg, fg=fg_color,
              activebackground=btn_active, relief="flat", width=10,
              command=lambda: _browse_entry(entry_a)).grid(row=0, column=2, padx=5, pady=8)

    tk.Label(frame, text="File B:", bg=bg_color, fg=fg_color,
             font=("Helvetica", 10)).grid(row=1, column=0, padx=5, pady=8, sticky="w")
    entry_b = tk.Entry(frame, width=52, bg=entry_bg, fg="#FFFFFF",
                       insertbackground="white", bd=1, relief="solid", font=("Consolas", 9))
    entry_b.grid(row=1, column=1, padx=10, pady=8)
    tk.Button(frame, text="Browse...", bg=btn_bg, fg=fg_color,
              activebackground=btn_active, relief="flat", width=10,
              command=lambda: _browse_entry(entry_b)).grid(row=1, column=2, padx=5, pady=8)

    def _run():
        path_a = entry_a.get(); path_b = entry_b.get()
        if not path_a or not path_b:
            messagebox.showerror("Error", "Select both files.", parent=win); return
        if not os.path.isfile(path_a) or not os.path.isfile(path_b):
            messagebox.showerror("Error", "Invalid path(s).", parent=win); return
        out = filedialog.asksaveasfilename(parent=win, title="Save Report",
              defaultextension=".txt", filetypes=[("Text","*.txt"),("All","*.*")])
        if not out: return
        try:
            na = os.path.basename(path_a); nb_name = os.path.basename(path_b)
            with open(path_a,"rb") as f: a = f.read()
            with open(path_b,"rb") as f: b = f.read()
            max_len = max(len(a),len(b)); diffs = []; i = 0
            while i < max_len:
                ba = a[i] if i<len(a) else None; bb = b[i] if i<len(b) else None
                if ba != bb:
                    start = i; block_a = []; block_b = []
                    while i < max_len:
                        ca = a[i] if i<len(a) else None; cb = b[i] if i<len(b) else None
                        if ca != cb:
                            block_a.append(ca if ca is not None else 0)
                            block_b.append(cb if cb is not None else 0); i += 1
                        else: break
                    diffs.append((start, block_a, block_b))
                else: i += 1
            merged = []
            if diffs:
                co, ca2, cb2 = diffs[0]; ce = co+len(ca2)
                for off, ba2, bb2 in diffs[1:]:
                    if off - ce <= MERGE_DISTANCE:
                        gap = off - ce
                        if gap > 0: ca2.extend(a[ce:off]); cb2.extend(b[ce:off])
                        ca2.extend(ba2); cb2.extend(bb2); ce = off+len(ba2)
                    else:
                        merged.append((co,ca2,cb2)); co,ca2,cb2=off,ba2,bb2; ce=off+len(ba2)
                merged.append((co,ca2,cb2))
            cw = max(len(na),len(nb_name))+2
            with open(out,"w",encoding="utf-8") as f:
                f.write(f"Comparison report\nFile A: {na}  ({len(a)} bytes)\nFile B: {nb_name}  ({len(b)} bytes)\n"+"="*72+"\n\n")
                if not merged:
                    f.write("No differences found.\n")
                else:
                    for off,ba2,cb2 in merged:
                        f.write(f"Offset: 0x{off:08X}\n")
                        f.write(f"{na+':':<{cw}}"+" ".join(f"{x:02X}" for x in ba2)+"\n")
                        f.write(f"{nb_name+':':<{cw}}"+" ".join(f"{x:02X}" for x in cb2)+"\n")
                        f.write("-"*72+"\n")
            messagebox.showinfo("Done", f"Report saved:\n{out}", parent=win)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=win)

    tk.Button(win, text="Compare & Save Report", width=30, bg=accent,
              fg="#FFFFFF", activebackground="#27AE60", font=("Helvetica",10,"bold"),
              relief="flat", command=_run).pack(pady=15)
    win.after(50, lambda: (win.lift(), win.focus_force()))


def _launch_exe_identifier(root):
    MERGE_DISTANCE = 32
    win = tk.Toplevel(root)
    win.title("EXE Patch Identifier")
    win.geometry("620x210")
    win.configure(bg="#121212")
    win.transient(root)
    win.resizable(False, False)

    bg_color  = "#121212"; fg_color = "#E0E0E0"
    entry_bg  = "#1E1E1E"; btn_bg   = "#2D2D2D"
    btn_active= "#3D3D3D"; accent   = "#3498DB"

    tk.Label(win, text="EXE Binary Patch Identifier", bg=bg_color, fg="#FFFFFF",
             font=("Helvetica", 12, "bold")).pack(pady=10)

    frame = tk.Frame(win, bg=bg_color)
    frame.pack(padx=20, pady=5, fill="both", expand=True)

    def _browse_exe_entry(e):
        p = filedialog.askopenfilename(parent=win,
              filetypes=[("EXE files","*.exe"),("All","*.*")])
        if p: e.delete(0, tk.END); e.insert(0, p)

    tk.Label(frame, text="Original:", bg=bg_color, fg=fg_color,
             font=("Helvetica", 10)).grid(row=0, column=0, padx=5, pady=8, sticky="w")
    entry_orig = tk.Entry(frame, width=52, bg=entry_bg, fg="#FFFFFF",
                          insertbackground="white", bd=1, relief="solid", font=("Consolas", 9))
    entry_orig.grid(row=0, column=1, padx=10, pady=8)
    tk.Button(frame, text="Browse...", bg=btn_bg, fg=fg_color,
              activebackground=btn_active, relief="flat", width=10,
              command=lambda: _browse_exe_entry(entry_orig)).grid(row=0, column=2, padx=5, pady=8)

    tk.Label(frame, text="Modified:", bg=bg_color, fg=fg_color,
             font=("Helvetica", 10)).grid(row=1, column=0, padx=5, pady=8, sticky="w")
    entry_mod = tk.Entry(frame, width=52, bg=entry_bg, fg="#FFFFFF",
                         insertbackground="white", bd=1, relief="solid", font=("Consolas", 9))
    entry_mod.grid(row=1, column=1, padx=10, pady=8)
    tk.Button(frame, text="Browse...", bg=btn_bg, fg=fg_color,
              activebackground=btn_active, relief="flat", width=10,
              command=lambda: _browse_exe_entry(entry_mod)).grid(row=1, column=2, padx=5, pady=8)

    def _run():
        orig_path = entry_orig.get(); mod_path = entry_mod.get()
        if not orig_path or not mod_path:
            messagebox.showerror("Error", "Select both EXE files.", parent=win); return
        if not os.path.isfile(orig_path) or not os.path.isfile(mod_path):
            messagebox.showerror("Error", "Invalid path(s).", parent=win); return
        out = filedialog.asksaveasfilename(parent=win, title="Save EXE Report",
              defaultextension=".txt", filetypes=[("Text","*.txt"),("All","*.*")])
        if not out: return
        try:
            on = os.path.basename(orig_path); mn = os.path.basename(mod_path)
            with open(orig_path,"rb") as f: orig = f.read()
            with open(mod_path,"rb") as f:  mod  = f.read()
            max_len = max(len(orig),len(mod)); diffs = []; i = 0
            while i < max_len:
                ob = orig[i] if i<len(orig) else None; mb = mod[i] if i<len(mod) else None
                if ob != mb:
                    start = i; ob_blk = []; mb_blk = []
                    while i < max_len:
                        co = orig[i] if i<len(orig) else None; cm = mod[i] if i<len(mod) else None
                        if co != cm:
                            ob_blk.append(co if co is not None else 0)
                            mb_blk.append(cm if cm is not None else 0); i += 1
                        else: break
                    diffs.append((start, ob_blk, mb_blk))
                else: i += 1
            merged = []
            if diffs:
                co, ca, cb = diffs[0]; ce = co+len(ca)
                for off, oa, ma in diffs[1:]:
                    if off - ce <= MERGE_DISTANCE:
                        gap = off - ce
                        if gap > 0: ca.extend(orig[ce:off]); cb.extend(mod[ce:off])
                        ca.extend(oa); cb.extend(ma); ce = off+len(oa)
                    else:
                        merged.append((co,ca,cb)); co,ca,cb=off,oa,ma; ce=off+len(oa)
                merged.append((co,ca,cb))
            with open(out,"w",encoding="utf-8") as f:
                f.write(f"EXE Comparison Report\nOriginal: {on}  ({len(orig)} bytes)\nModified: {mn}  ({len(mod)} bytes)\n"+"="*72+"\n\n")
                if not merged:
                    f.write("No differences found.\n")
                else:
                    for off, oa, ma in merged:
                        f.write(f"Offset: 0x{off:08X}\n")
                        f.write(f"{on}: "+" ".join(f"{x:02X}" for x in oa)+"\n")
                        f.write(f"{mn}: "+" ".join(f"{x:02X}" for x in ma)+"\n")
                        f.write("-"*60+"\n")
            messagebox.showinfo("Done", f"Found {len(merged)} diff block(s).\nReport saved:\n{out}", parent=win)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=win)

    tk.Button(win, text="Compare & Save Modifications", width=30, bg=accent,
              fg="#FFFFFF", activebackground="#2980B9", font=("Helvetica",10,"bold"),
              relief="flat", command=_run).pack(pady=15)
    win.after(50, lambda: (win.lift(), win.focus_force()))


# ══════════════════════════════════════════════════════════════════
#  Info Window Data  —  AR + EN
# ══════════════════════════════════════════════════════════════════

_INFO_AR_CODE_MANAGER = """## وش يسوي؟
هذا القسم يجمع لك أكثر من 180 كود في مكان واحد، بواجهة مرتبة، وكل كود داخل قسمه الخاص.

## ما الفائدة؟
تجميع جميع أكواد اللعبة وتنظيمها داخل مكان واحد لتسهيل الوصول والتعديل.

## الأسئلة الشائعة

## كم عدد الأكواد؟
تقريبًا 188 كود.

## هل جميع الأكواد تعمل بضغطة زر؟
لا، بعض الأكواد تحتاج إدخال قيم أو أرقام مخصصة، وبعضها يحتوي على خيارات متعددة.

## هل يدعم أكواد ITA-AEV بحالاتها المختلفة؟
نعم، جميع الحالات مدعومة. عند اختيار الكود تظهر لك الخيارات المتوفرة.

## كيف أشغل القسم؟
+ حدد مسار BIO4.EXE من قسم Master Editor
+ ادخل إلى القسم
+ اضغط Scan

## هل أقدر أرجع الكود لوضعه الأصلي؟
نعم، تقدر تطفي الكود وترجع الوضع الطبيعي.

## هل أقدر أفعّل مجموعة أكواد بضغطة واحدة؟
نعم، تقدر تنشئ مجموعة وتفعّلها مباشرة."""

_INFO_AR_OSD = """## وش يسوي؟
يمكنك تعديل ملف OSD من خلال واجهة مرتبة وسهلة بدون الحاجة لاستخدام HxD.

## ما الفائدة؟
تسهيل تعديل ملف OSD بدل التعديل اليدوي داخل محرر Hex.

## الأسئلة الشائعة

## وش وظيفة ملف OSD؟
ملف OSD مسؤول عن سحب أيتمات من الشنطة مقابل تفعيل AEV معين.

## الفرق بين AEV النجاح وAEV الفشل؟
+ AEV النجاح: يتفعل إذا نجح النظام في سحب الأيتم المطلوب.
+ AEV الفشل: يتفعل إذا فشل سحب الأيتم من اللاعب.

## هل فيه متطلبات؟
نعم:
+ تفعيل كود AEV-OSD من Code Manager داخل AEV CODES
+ تغيير خيار OSD OPERATION من False إلى True

## هل يدعم Side Load؟
لا، الدعم فقط عبر UDAS.

## وش يصير إذا خليت كمية السحب 0؟
غير معروف بشكل كامل، لكن قد يسبب Crash."""

_INFO_AR_CNS = """## وش يسوي؟
هذا القسم يسمح لك بتعديل حدود محرك اللعبة بسهولة.

## ما الفائدة؟
تعديل قيم وحدود المحرك بدون الحاجة للتعديل اليدوي داخل Hex.

## الأسئلة الشائعة

## وش الأشياء اللي أقدر أعدلها؟
تقدر تعدل حدود كثيرة مثل حدود الأعداء، الأيتمات، وقيود المراحل الداخلية.

## هل يحتاج خبرة Hex؟
لا، أغلب التعديلات تتم مباشرة من الواجهة.

## هل التعديلات تنحفظ مباشرة؟
نعم، يتم حفظ التعديلات مباشرة داخل الملف."""

_INFO_AR_SND = """قسم تحت التطوير حالياً."""

_INFO_AR_AEV = """## وش يسوي؟
يعدل AEV OPTION من خلال واجهة واضحة وسهلة الاستخدام.

## ما الفائدة؟
تعديل خيارات AEV بسهولة بدون الحاجة للتعديل اليدوي داخل ملفات TXT.

## الأسئلة الشائعة

## وش هو AEV OPTION؟
نظام يسمح بتفعيل AEV عن طريق اختيار نص داخل اللعبة.
مثال:
Hi my name is
Michael-
Kfc-
إذا ضغطت على Kfc يتم تفعيل AEV المحدد.

## هل يحتاج إعدادات؟
نعم، لازم تفعل كود AEV OPTION من Code Manager.

## وش يصير إذا حطيت القيمة 0؟
الكلمة تتحول إلى خيار عادي بدون تفعيل أي AEV.

## هل يدعم Jaderlink MDT Tool؟
لا، الدعم فقط لملفات SOP."""

_INFO_AR_MDT = """## وش يسوي؟
يعدل ألوان النصوص داخل ملفات MDT، ويحتوي على قسم Custom Color لإنشاء ألوان مخصصة.

## ما الفائدة؟
تسهيل تعديل ألوان النصوص وتأثيراتها داخل اللعبة من واجهة مباشرة.

## الأسئلة الشائعة

## هل يدعم Jaderlink MDT Tool؟
لا، غير مدعوم حالياً."""

_INFO_AR_ROOM = """## وش يسوي؟
ينسخ برمجيات أي ماب إلى ماب آخر.
مثال: نقل برمجيات r101 إلى r103.

## ما الفائدة؟
تعديل Room Init ونقل البرمجيات بين المابات بطريقة سهلة.

## الأسئلة الشائعة

## هل جميع الـ ST مدعومة؟
لا، حالياً المدعوم فقط:
+ ST1
+ ST2
+ ST3"""

_INFO_AR_AVL = """## وش يسوي؟
من هذا القسم تقدر تخلي الـ AEV يتقفل بمفتاح بسهولة، مع توفير جميع الملفات المطلوبة سواء AVL أو Events.cfg لتطبيق النظام بدون تعديل يدوي داخل HxD أو Notepad.

## ما الفائدة؟
يسهّل تعديل الـ AEV وربطه بالمفاتيح بشكل مباشر، بدل التعديل اليدوي على الهكس أو ملفات الإعدادات.

## الأسئلة الشائعة

## هل AVL / Events.cfg ينفع أحطهم داخل UDAS؟
لا.

## هل AVL يدعم DLL RAZ0R؟
لا.

## هل AVL يدعم DLL Qingsheng؟
نعم، وملف AVL مخصص له.

## هل Events.cfg يدعم DLL RAZ0R؟
نعم، وملف Events.cfg مخصص له.

## هل Events.cfg يدعم DLL Qingsheng؟
لا.

## ما الفرق بين AVL و Events.cfg؟
تقريبًا ما فيه فرق كبير، لكن بعض الأكواد تشتغل فقط على Events.cfg.
غير كذا، الاثنين يؤدون نفس الوظيفة.

## أيهم أفضل؟
بالنسبة لي، AVL أفضل لأنه أبسط وأسهل بالتعامل.

## هل أحتاج أفعل أكواد إضافية؟
لا، ما يحتاج.

## هل لازم أركب DLL؟
نعم، كل ملف يحتاج DLL معين:
+ Events.cfg = DLL RAZ0R فقط
+ AVL = DLL Qingsheng فقط"""


_INFO_AR_SCRIPTS = """## وش يسوي؟
يجمع السكربتات داخل مكان واحد.

## ما الفائدة؟
بدل البحث عن السكربتات بشكل يدوي، أغلب السكربتات تكون مجمعة داخل القسم.

## الأسئلة الشائعة
القسم مباشر وواضح، لا توجد أسئلة شائعة."""

# ── English ──────────────────────────────────────────────────────

_INFO_EN_CODE_MANAGER = """## What does it do?
Gathers more than 180 codes in one place with an organized interface, each code inside its own category.

## What is the benefit?
Organizes all game codes into a single place to make access and modification easier.

## Frequently Asked Questions

## How many codes are available?
Around 188 codes.

## Do all codes work with a single button press?
No. Some codes require custom values, and some contain multiple modes or options.

## Does it support ITA-AEV codes with multiple states?
Yes. All states are supported. Once you select the code, available options appear.

## How do I use this section?
+ Set the BIO4.EXE path from Master Editor
+ Open the section
+ Press Scan

## Can I disable a code after enabling it?
Yes. You can disable the code and restore the original state.

## Can I activate a group of codes with one click?
Yes. You can create code groups and activate them instantly."""

_INFO_EN_OSD = """## What does it do?
Allows you to edit OSD files through a clean interface without using HxD.

## What is the benefit?
Makes OSD editing easier instead of manually editing inside a Hex editor.

## Frequently Asked Questions

## What does the OSD file do?
The OSD file removes items from the inventory in exchange for activating a specific AEV.

## What is the difference between Success AEV and Fail AEV?
+ Success AEV: Activated if the item is successfully removed.
+ Fail AEV: Activated if the game fails to remove the item.

## Does it require setup?
Yes:
+ Enable the AEV-OSD code from Code Manager inside AEV CODES
+ Change OSD OPERATION from False to True

## Does it support Side Load?
No. Only UDAS is supported.

## What happens if the remove amount is set to 0?
Currently unknown, but it may cause a crash."""

_INFO_EN_CNS = """## What does it do?
Allows you to modify engine limits easily.

## What is the benefit?
Modify engine limits without manual Hex editing.

## Frequently Asked Questions

## What can I modify inside CNS?
Enemy limits, item limits, and other internal stage or system restrictions.

## Does it require Hex knowledge?
No. Most modifications are done directly from the interface.

## Are changes saved directly?
Yes. Changes are saved directly into the file."""

_INFO_EN_SND = """This section is currently under development."""

_INFO_EN_AEV = """## What does it do?
Edits AEV OPTION through a clean and easy interface.

## What is the benefit?
Makes AEV OPTION editing easier instead of editing TXT files manually.

## Frequently Asked Questions

## What is AEV OPTION?
A system that activates an AEV through text choices inside the game.
Example:
Hi my name is
Michael-
Kfc-
If the player selects Kfc, the assigned AEV activates.

## Does it require setup?
Yes. Enable the AEV OPTION code from Code Manager.

## What happens if the value is set to 0?
The text becomes a normal option without activating any AEV.

## Does it support Jaderlink MDT Tool?
No. Only SOP files are supported."""

_INFO_EN_MDT = """## What does it do?
Edits text colors inside MDT files. Also contains a Custom Color section.

## What is the benefit?
Makes text color editing easier through a direct interface.

## Frequently Asked Questions

## Does it support Jaderlink MDT Tool?
No. Currently unsupported."""

_INFO_EN_ROOM = """## What does it do?
Copies room scripts and logic from one map to another.
Example: copying logic from r101 to r103.

## What is the benefit?
Makes Room Init editing and map logic transfer easier.

## Frequently Asked Questions

## Are all ST versions supported?
No. Currently supported:
+ ST1
+ ST2
+ ST3"""

_INFO_EN_AVL = """## What does it do?
From this section, you can make an AEV require a key to open.
All required files are included, whether AVL or Events.cfg, so you can set it up without manually editing HxD or Notepad.

## What is the benefit?
Makes editing AEVs much easier by allowing you to lock them with a key directly, instead of manually editing hex values or configuration files.

## Frequently Asked Questions

## Can I use AVL / Events.cfg inside UDAS?
No.

## Does AVL support the RAZ0R DLL?
No.

## Does AVL support the Qingsheng DLL?
Yes. The AVL file is specifically made for it.

## Does Events.cfg support the RAZ0R DLL?
Yes. The Events.cfg file is specifically made for it.

## Does Events.cfg support the Qingsheng DLL?
No.

## What is the difference between AVL and Events.cfg?
There is almost no difference, except that some codes only work with Events.cfg.
Other than that, both files perform the same function.

## Which one is better?
In my opinion, AVL is better because it is simpler and easier to use.

## Do I need to enable extra codes?
No, no additional codes are required.

## Do I need a DLL?
Yes. Each file requires a specific DLL:
+ Events.cfg = RAZ0R DLL only
+ AVL = Qingsheng DLL only"""


_INFO_EN_SCRIPTS = """## What does it do?
Collects scripts in one place.

## What is the benefit?
Instead of searching manually, most scripts are available inside one section.

## Frequently Asked Questions
The section is straightforward. No common questions."""

_INFO_DATA_AR = {
    "Code Manager":      ("Code Manager",      "#5b9bd5", _INFO_AR_CODE_MANAGER),
    "OSD Editor":        ("OSD Editor",        "#c8a035", _INFO_AR_OSD),
    "CNS Editor":        ("CNS Editor",        "#e07b54", _INFO_AR_CNS),
    "SND Editor":        ("SND Editor",        "#7ec8a0", _INFO_AR_SND),
    "AEV Option Editor": ("AEV Option Editor", "#c8a035", _INFO_AR_AEV),
    "MDT Color Editor":  ("MDT Color Editor",  "#d46fc8", _INFO_AR_MDT),
    "Room Init":         ("Room Init",         "#7ec8a0", _INFO_AR_ROOM),
    "Lock AEV with Key": ("Lock AEV with Key", "#e07b54", _INFO_AR_AVL),
    "Scripts":           ("Scripts",           "#5bc8c8", _INFO_AR_SCRIPTS),
}
_INFO_DATA_EN = {
    "Code Manager":      ("Code Manager",      "#5b9bd5", _INFO_EN_CODE_MANAGER),
    "OSD Editor":        ("OSD Editor",        "#c8a035", _INFO_EN_OSD),
    "CNS Editor":        ("CNS Editor",        "#e07b54", _INFO_EN_CNS),
    "SND Editor":        ("SND Editor",        "#7ec8a0", _INFO_EN_SND),
    "AEV Option Editor": ("AEV Option Editor", "#c8a035", _INFO_EN_AEV),
    "MDT Color Editor":  ("MDT Color Editor",  "#d46fc8", _INFO_EN_MDT),
    "Room Init":         ("Room Init",         "#7ec8a0", _INFO_EN_ROOM),
    "Lock AEV with Key": ("Lock AEV with Key", "#e07b54", _INFO_EN_AVL),
    "Scripts":           ("Scripts",           "#5bc8c8", _INFO_EN_SCRIPTS),
}


# ══════════════════════════════════════════════════════════════════
#  Auto-Update  —  GitHub Releases
# ══════════════════════════════════════════════════════════════════

def _check_for_update(master_win, manual=False):
    """Check GitHub for a newer release. Run in background thread."""
    import threading, urllib.request, urllib.error, zipfile, shutil, tempfile

    # Check if user disabled update notifications (only skip for auto-check)
    if not manual and MASTER_SETTINGS.get("skip_update_notify", False):
        return

    def _worker():
        try:
            req = urllib.request.Request(GITHUB_API,
                  headers={"User-Agent": "RE4MasterEditor"})
            with urllib.request.urlopen(req, timeout=6) as r:
                import json as _json
                data = _json.loads(r.read().decode())

            latest_tag = data.get("tag_name", "").strip()
            if not latest_tag:
                if manual:
                    master_win.after(0, lambda: _show_up_to_date_dialog(master_win))
                return

            # Compare: strip 'V' prefix, compare as integer
            def _ver(s):
                # Supports: V3, V3.1, V3.1.2, v0.7.8.5E — strips leading V/v then splits by dots
                s = s.strip().lstrip("vV")
                # Remove trailing non-numeric suffix per part (e.g. "5E" -> 5)
                parts = []
                for p in s.split("."):
                    num = ""
                    for c in p:
                        if c.isdigit():
                            num += c
                        else:
                            break
                    parts.append(int(num) if num else 0)
                # Pad to 4 parts
                while len(parts) < 4:
                    parts.append(0)
                return tuple(parts)

            if _ver(latest_tag) <= _ver(APP_VERSION):
                if manual:
                    master_win.after(0, lambda: _show_up_to_date_dialog(master_win))
                return  # already up to date

            # Find download URL for RE4.Master.Editor.zip
            dl_url   = None
            dl_size  = 0
            for asset in data.get("assets", []):
                if asset.get("name") == GITHUB_ZIP:
                    dl_url  = asset["browser_download_url"]
                    dl_size = asset.get("size", 0)
                    break
            if not dl_url:
                dl_url = data.get("zipball_url", "")

            # Changelog: body of the release
            changelog = data.get("body", "").strip()

            # Show dialog on main thread
            master_win.after(0, lambda: _show_update_dialog(
                master_win, latest_tag, dl_url, dl_size, changelog))

        except Exception:
            if manual:
                master_win.after(0, lambda: _show_up_to_date_dialog(master_win, error=True))

    threading.Thread(target=_worker, daemon=True).start()


def _show_up_to_date_dialog(master_win, error=False):
    _GOLD = "#c8a035"
    _BG   = "#0b0b0b"
    dlg = tk.Toplevel(master_win)
    dlg.title(t("تحقق من التحديثات", "Check for Updates"))
    dlg.geometry("340x130")
    dlg.resizable(False, False)
    dlg.configure(bg=_BG)
    dlg.grab_set()
    dlg.transient(master_win)
    if error:
        msg = t("تعذّر الاتصال بالخادم.", "Could not connect to the server.")
        clr = "#e07070"
    else:
        msg = t(f"أنت تستخدم أحدث إصدار  ({APP_VERSION})  ✓",
                f"You are on the latest version  ({APP_VERSION})  ✓")
        clr = "#7cfc7c"
    tk.Label(dlg, text=msg, fg=clr, bg=_BG,
             font=("Courier New", 9, "bold"), wraplength=300).pack(pady=(28, 10))
    tk.Button(dlg, text=t("إغلاق", "Close"),
              font=("Courier New", 9), fg="#888", bg="#1a1a1a",
              activeforeground="#aaa", activebackground="#222",
              relief="flat", bd=0, cursor="hand2", padx=14, pady=4,
              command=dlg.destroy).pack()


def _show_update_dialog(master_win, latest_tag, dl_url, dl_size=0, changelog=""):
    import urllib.request, zipfile, shutil, tempfile, threading

    _GOLD  = "#c8a035"
    _BG    = "#0b0b0b"
    _GREEN = "#7cfc7c"

    # Dynamic height based on changelog presence
    win_h = 420 if changelog else 270

    dlg = tk.Toplevel(master_win)
    dlg.title(t("تحديث متاح", "Update Available"))
    dlg.geometry(f"460x{win_h}")
    dlg.resizable(False, False)
    dlg.configure(bg=_BG)
    dlg.grab_set()
    dlg.transient(master_win)

    tk.Label(dlg, text="⬆  " + t("تحديث جديد متاح", "New Update Available"),
             fg=_GOLD, bg=_BG, font=("Courier New", 12, "bold")).pack(pady=(16, 4))

    # Version info
    size_str = ""
    if dl_size > 0:
        size_str = f"   |   {t('الحجم','Size')}: {dl_size / 1024 / 1024:.1f} MB"
    tk.Label(dlg,
             text=f"{t('الإصدار الحالي','Current')}: {APP_VERSION}    "
                  f"{t('الإصدار الجديد','Latest')}: {latest_tag}{size_str}",
             fg="#888", bg=_BG, font=("Courier New", 9)).pack(pady=2)

    # Changelog box
    if changelog:
        cl_frame = tk.Frame(dlg, bg="#111", highlightthickness=1, highlightbackground="#333")
        cl_frame.pack(fill="x", padx=20, pady=(8, 4))
        cl_label = tk.Label(cl_frame,
                            text=t("سجل التغييرات:", "Changelog:"),
                            fg=_GOLD, bg="#111", font=("Courier New", 8, "bold"),
                            anchor="w")
        cl_label.pack(anchor="w", padx=8, pady=(4, 0))
        cl_sb = tk.Scrollbar(cl_frame, orient="vertical")
        cl_txt = tk.Text(cl_frame, height=6, font=("Courier New", 8),
                         fg="#cccccc", bg="#0d0d0d",
                         relief="flat", bd=0, wrap="word",
                         yscrollcommand=cl_sb.set,
                         highlightthickness=0)
        cl_sb.config(command=cl_txt.yview)
        cl_sb.pack(side="right", fill="y")
        cl_txt.pack(fill="x", padx=8, pady=(2, 6))
        cl_txt.insert("1.0", changelog)
        cl_txt.configure(state="disabled")

    tk.Label(dlg,
             text=t("هل تريد تحميل التحديث وتثبيته الآن؟",
                    "Do you want to download and install the update now?"),
             fg="#ccc", bg=_BG, font=("Courier New", 9)).pack(pady=(8, 0))

    # Progress bar frame
    prog_frame = tk.Frame(dlg, bg=_BG)
    prog_frame.pack(fill="x", padx=20, pady=6)

    prog_var = tk.StringVar(value="")
    prog_lbl = tk.Label(prog_frame, textvariable=prog_var, fg="#555", bg=_BG,
                        font=("Courier New", 8))
    prog_lbl.pack()

    # Canvas-based progress bar
    bar_canvas = tk.Canvas(prog_frame, height=6, bg="#1a1a1a",
                           highlightthickness=0, relief="flat")
    bar_canvas.pack(fill="x", pady=(2, 0))
    bar_rect = [None]

    def _set_progress(pct):
        bar_canvas.update_idletasks()
        w = bar_canvas.winfo_width()
        if w < 2:
            w = 420
        if bar_rect[0]:
            bar_canvas.delete(bar_rect[0])
        fill_w = int(w * pct / 100)
        bar_rect[0] = bar_canvas.create_rectangle(0, 0, fill_w, 6,
                                                   fill="#7cfc7c", outline="")

    # "Don't show again" checkbox
    skip_var = tk.BooleanVar(value=False)
    skip_frame = tk.Frame(dlg, bg=_BG)
    skip_frame.pack(pady=(2, 0))
    tk.Checkbutton(skip_frame,
                   text=t("لا تُظهر هذه الرسالة مجدداً", "Don't show this message again"),
                   variable=skip_var,
                   fg="#555", bg=_BG,
                   activebackground=_BG, selectcolor="#111",
                   font=("Courier New", 8), relief="flat"
                   ).pack(side="left")

    btn_frame = tk.Frame(dlg, bg=_BG)
    btn_frame.pack(pady=8)

    def _do_update():
        # Save "don't show again" preference before downloading
        if skip_var.get():
            MASTER_SETTINGS["skip_update_notify"] = True
            save_master_settings(MASTER_SETTINGS)

        btn_yes.configure(state="disabled")
        btn_no.configure(state="disabled")

        def _download():
            try:
                prog_var.set(t("جاري التحميل...", "Downloading..."))
                _set_progress(0)

                # Download zip to temp
                tmp_dir = tempfile.mkdtemp()
                zip_path = os.path.join(tmp_dir, GITHUB_ZIP)

                def _reporthook(count, block, total):
                    if total > 0:
                        pct = min(100, int(count * block * 100 / total))
                        prog_var.set(f"{t('تحميل', 'Downloading')}... {pct}%")
                        dlg.after(0, lambda p=pct: _set_progress(p))

                urllib.request.urlretrieve(dl_url, zip_path, reporthook=_reporthook)
                prog_var.set(t("جاري الاستخراج...", "Extracting..."))
                _set_progress(100)

                # Extract next to current script
                extract_dir = os.path.dirname(os.path.abspath(__file__))
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zf.extractall(extract_dir)

                shutil.rmtree(tmp_dir, ignore_errors=True)

                prog_var.set(t("تم التحديث ✓", "Done ✓"))
                dlg.after(800, lambda: _restart(dlg, master_win))

            except Exception as e:
                prog_var.set(f"{t('فشل', 'Failed')}: {e}")
                btn_yes.configure(state="normal")
                btn_no.configure(state="normal")

        threading.Thread(target=_download, daemon=True).start()

    def _dismiss():
        if skip_var.get():
            MASTER_SETTINGS["skip_update_notify"] = True
            save_master_settings(MASTER_SETTINGS)
        dlg.destroy()

    def _restart(d, w):
        import sys, subprocess
        d.destroy()
        subprocess.Popen([sys.executable] + sys.argv)
        w.quit()
        w.destroy()

    btn_yes = tk.Button(btn_frame,
                        text=t("نعم، حدّث الآن", "Yes, Update Now"),
                        font=("Courier New", 9, "bold"),
                        fg=_GREEN, bg="#1a2a0a",
                        activeforeground=_GREEN, activebackground="#2a4a1a",
                        relief="flat", bd=0, cursor="hand2",
                        highlightthickness=1, highlightbackground=_GREEN,
                        padx=14, pady=4,
                        command=_do_update)
    btn_yes.pack(side="left", padx=8)

    btn_no = tk.Button(btn_frame,
                       text=t("لا، لاحقاً", "No, Later"),
                       font=("Courier New", 9),
                       fg="#888", bg="#1a1a1a",
                       activeforeground="#aaa", activebackground="#222",
                       relief="flat", bd=0, cursor="hand2",
                       padx=14, pady=4,
                       command=_dismiss)
    btn_no.pack(side="left", padx=8)

def _show_first_run_setup(parent_win, on_done):
    """
    Language picker — modal Toplevel over the already-built main window.
    Main window is visible behind it but fully blocked until language is chosen.
    """
    _BG   = "#0a0a0a"
    _GOLD = "#c8a035"

    dlg = tk.Toplevel(parent_win)
    dlg.title("RE4 Master Editor")
    dlg.geometry("500x330")
    dlg.resizable(False, False)
    dlg.configure(bg=_BG)
    dlg.grab_set()
    dlg.transient(parent_win)
    dlg.protocol("WM_DELETE_WINDOW", lambda: None)   # force choice — no X close

    # Center over parent
    parent_win.update_idletasks()
    px = parent_win.winfo_x() + (parent_win.winfo_width()  - 500) // 2
    py = parent_win.winfo_y() + (parent_win.winfo_height() - 330) // 2
    dlg.geometry(f"500x330+{px}+{py}")

    # ── top gold accent bar ──
    tk.Frame(dlg, bg=_GOLD, height=2).pack(fill="x")

    # ── header block ──
    head = tk.Frame(dlg, bg="#0d0d0d")
    head.pack(fill="x")

    title_row = tk.Frame(head, bg="#0d0d0d")
    title_row.pack(pady=(16, 12))
    tk.Label(title_row, text="RE4", fg=_GOLD, bg="#0d0d0d",
             font=("Courier New", 22, "bold")).pack(side="left")
    tk.Label(title_row, text="  MASTER EDITOR", fg="#444", bg="#0d0d0d",
             font=("Courier New", 14, "bold")).pack(side="left", pady=4)

    tk.Frame(dlg, bg="#1c1c1c", height=1).pack(fill="x")

    # ── subtitle ──
    tk.Label(dlg,
             text="Select your language  ·  اختر لغتك",
             fg="#555", bg=_BG,
             font=("Courier New", 9),
             pady=14).pack()

    # ── language cards ──
    lang_var = tk.StringVar(value="en")
    cards_meta = []   # (outer, inner, widgets..., val)

    def _refresh():
        sel = lang_var.get()
        for meta in cards_meta:
            outer, inner, lbl_main, lbl_sub, val = meta
            active = (val == sel)
            card_bg  = "#1a1500" if active else "#0f0f0f"
            card_brd = _GOLD    if active else "#2a2a2a"
            lbl_fg   = _GOLD    if active else "#3a3a3a"
            sub_fg   = "#888"   if active else "#2e2e2e"
            outer.configure(highlightbackground=card_brd, bg=card_bg)
            inner.configure(bg=card_bg)
            lbl_main.configure(fg=lbl_fg, bg=card_bg)
            lbl_sub.configure(fg=sub_fg,  bg=card_bg)

    def _make_card(parent, text_main, text_sub, val):
        outer = tk.Frame(parent, bg="#0f0f0f",
                         highlightthickness=1, highlightbackground="#2a2a2a")
        outer.pack(side="left", padx=16)
        inner = tk.Frame(outer, bg="#0f0f0f", padx=28, pady=16, cursor="hand2")
        inner.pack()
        lbl_main = tk.Label(inner, text=text_main, fg="#3a3a3a",
                            bg="#0f0f0f", font=("Courier New", 14, "bold"))
        lbl_main.pack()
        lbl_sub  = tk.Label(inner, text=text_sub, fg="#2e2e2e",
                            bg="#0f0f0f", font=("Courier New", 7))
        lbl_sub.pack(pady=(3, 0))
        meta = (outer, inner, lbl_main, lbl_sub, val)
        cards_meta.append(meta)

        def _sel(e=None):
            lang_var.set(val)
            _refresh()

        for w in (outer, inner, lbl_main, lbl_sub):
            w.bind("<Button-1>", _sel)

    card_row = tk.Frame(dlg, bg=_BG)
    card_row.pack()
    _make_card(card_row, "English",  "English Interface",  "en")
    _make_card(card_row, "العربية",  "واجهة عربية",        "ar")
    _refresh()   # highlight English by default

    # ── confirm button ──
    def _confirm():
        chosen = lang_var.get()
        MASTER_SETTINGS["lang"]      = chosen
        MASTER_SETTINGS["first_run"] = False
        save_master_settings(MASTER_SETTINGS)
        global CURRENT_LANG
        CURRENT_LANG = chosen
        dlg.destroy()
        on_done(chosen)

    tk.Button(dlg,
              text="Confirm  /  تأكيد",
              font=("Courier New", 10, "bold"),
              fg="#0a0a0a", bg=_GOLD,
              activeforeground="#0a0a0a", activebackground="#e0b840",
              relief="flat", bd=0, cursor="hand2",
              padx=30, pady=8,
              command=_confirm).pack(pady=(18, 0))

    # ── bottom dim bar ──
    tk.Frame(dlg, bg="#1c1c1c", height=1).pack(fill="x", side="bottom")


class RE4MasterEditor(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("RE4 Master Editor")
        self.geometry("1120x730")
        self.minsize(920, 620)
        self.configure(bg=_BG)

        # ── App icon (window + taskbar) ──
        _icon_path = os.path.join(MASTER_DIR, "icon.ico")
        if not os.path.isfile(_icon_path):
            # also check next to the script/exe
            _icon_path = os.path.join(
                os.path.dirname(sys.executable if getattr(sys, "frozen", False)
                                else os.path.abspath(__file__)),
                "icon.ico"
            )
        if os.path.isfile(_icon_path):
            try:
                self.iconbitmap(_icon_path)
            except Exception:
                pass
        # Tell Windows to use our AppID so the taskbar groups correctly
        # and shows the EXE icon instead of Python's
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "YEMENI.RE4MasterEditor.1"
            )
        except Exception:
            pass

        self.exe_path        = tk.StringVar()
        self._panels         = {}
        self._nav_btns       = {}
        self._cm_app         = None
        self._unlocked_codes = set()

        if MASTER_SETTINGS.get("remember_exe", True):
            last = MASTER_SETTINGS.get("last_exe", "")
            if last and os.path.isfile(last):
                self.exe_path.set(last)

        self.exe_path.trace_add("write", self._on_exe_change)
        self._build_ui()
        self._show_welcome()
        # Check for updates after 2 seconds (non-blocking)
        self.after(2000, lambda: _check_for_update(self, manual=False))

    def _build_ui(self):
        # ── Top bar ──
        topbar = tk.Frame(self, bg="#0c0c0c")
        topbar.pack(fill="x")
        tk.Frame(self, bg=_GOLD, height=1).pack(fill="x")

        # Left: title
        left = tk.Frame(topbar, bg="#0c0c0c")
        left.pack(side="left", padx=(14, 0))
        tk.Label(left, text="RE4 ", fg=_GOLD, bg="#0c0c0c",
                 font=("Courier New", 14, "bold")).pack(side="left", pady=8)
        tk.Label(left, text="MASTER EDITOR", fg="#dddddd", bg="#0c0c0c",
                 font=("Courier New", 14, "bold")).pack(side="left")
        tk.Label(left, text="  v1.0.1", fg="#666666", bg="#0c0c0c",
                 font=("Courier New", 7)).pack(side="left")

        # Right: Settings + Credit + Info
        right = tk.Frame(topbar, bg="#0c0c0c")
        right.pack(side="right", padx=10)
        for label, cmd in [(t("الإعدادات","Settings"), self._open_settings), (t("المطورين","Credit"), self._show_credit), (t("معلومات","Info"), self._show_info)]:
            tk.Button(right, text=label,
                      font=("Courier New", 8),
                      fg="#888888", bg="#0c0c0c",
                      activeforeground=_GOLD, activebackground="#16110a",
                      relief="flat", bd=0, cursor="hand2",
                      command=cmd, padx=8, pady=7
                      ).pack(side="left")

        # Center: exe path + Browse
        center = tk.Frame(topbar, bg="#0c0c0c")
        center.pack(expand=True)
        tk.Label(center, text="bio4.exe:", fg="#888888", bg="#0c0c0c",
                 font=("Courier New", 8)).pack(side="left", padx=(0, 5))
        self._path_entry = tk.Entry(
            center, textvariable=self.exe_path,
            font=("Courier New", 8), fg=_GREEN, bg="#0d1a0d",
            insertbackground=_GREEN, relief="flat", bd=0,
            highlightthickness=1, highlightbackground="#2a5a2a",
            width=40
        )
        self._path_entry.pack(side="left", ipady=3)
        self._add_paste_menu(self._path_entry)
        tk.Button(center, text=t("تصفح","Browse"),
                  font=("Courier New", 7),
                  fg=_GOLD, bg="#1a1500",
                  activeforeground=_GOLD, activebackground="#2a2000",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground=_GOLD,
                  command=self._browse_exe, padx=7, pady=2
                  ).pack(side="left", padx=6)
        tk.Button(center, text=t("إنشاء نسخة احتياطية","Create Backup"),
                  font=("Courier New", 8, "bold"),
                  fg=_GREEN, bg="#0d1a0d",
                  activeforeground=_GREEN, activebackground="#1a2a1a",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground="#2a5a2a",
                  command=self._create_backup, padx=10, pady=3
                  ).pack(side="left", padx=(0,6))

        # ── Main layout: sidebar RIGHT, content LEFT ──
        main_area = tk.Frame(self, bg=_BG)
        main_area.pack(fill="both", expand=True)

        # 1. sidebar — packed FIRST to claim right side
        sidebar = tk.Frame(main_area, bg="#0a0a0a", width=160)
        sidebar.pack(side="right", fill="y")
        sidebar.pack_propagate(False)

        # 2. thin divider
        tk.Frame(main_area, bg="#1a1a1a", width=1).pack(side="right", fill="y")

        # 3. content — gets ALL remaining space on the left
        self._content = tk.Frame(main_area, bg="#0b0b0b")
        self._content.pack(side="left", fill="both", expand=True)

        # sidebar header
        tk.Frame(sidebar, bg="#0a0a0a", height=10).pack(fill="x")
        tk.Label(sidebar, text="MODULES",
                 fg="#2a2a2a", bg="#0a0a0a",
                 font=("Courier New", 7, "bold")).pack(fill="x", padx=12)
        tk.Frame(sidebar, bg="#1a1a1a", height=1).pack(fill="x", padx=8, pady=(4,2))

        for tool in TOOLS_DEF:
            tid   = tool["id"]
            color = tool.get("color", _MUTED)

            # separator before row 2 tools
            if tid == "mdt_color_editor":
                tk.Frame(sidebar, bg="#1a1a1a", height=1).pack(fill="x", padx=8, pady=5)

            # separator before Scripts section
            if tid == "scripts":
                tk.Frame(sidebar, bg="#1a1a1a", height=1).pack(fill="x", padx=8, pady=5)

            # colored left indicator bar + button in a row
            btn_frame = tk.Frame(sidebar, bg="#0a0a0a")
            btn_frame.pack(fill="x")

            indicator = tk.Frame(btn_frame, bg="#0a0a0a", width=3)
            indicator.pack(side="left", fill="y")

            btn = tk.Button(btn_frame,
                            text=tool["label"],
                            font=("Courier New", 9, "bold"),
                            fg="#5a5a5a", bg="#0a0a0a",
                            activeforeground=color,
                            activebackground="#111",
                            relief="flat", bd=0,
                            cursor="hand2",
                            anchor="w",
                            justify="left",
                            padx=10, pady=8,
                            command=lambda t=tid: self._switch_tool(t))
            btn.pack(fill="x", expand=True)

            # hover animation
            def _on_enter(e, b=btn, ind=indicator, c=color):
                b.configure(fg=c)
                ind.configure(bg=c)
            def _on_leave(e, b=btn, ind=indicator):
                # keep color if active
                if getattr(b, "_active", False):
                    return
                b.configure(fg="#2e2e2e")
                ind.configure(bg="#0a0a0a")

            btn.bind("<Enter>", _on_enter)
            btn.bind("<Leave>", _on_leave)
            btn._active   = False
            btn._color    = color
            btn._indicator = indicator

            self._nav_btns[tid] = btn

        tk.Frame(sidebar, bg="#0a0a0a").pack(fill="both", expand=True)

        # sidebar footer
        tk.Frame(sidebar, bg="#1a1a1a", height=1).pack(fill="x", padx=8, pady=(0,4))
        tk.Label(sidebar, text="by YEMENI",
                 fg="#1a1a1a", bg="#0a0a0a",
                 font=("Courier New", 7)).pack(pady=(0,8))

        # content is already created inside main_area above

        self._welcome = WelcomePanel(self._content)
        self._welcome.place(relx=0, rely=0, relwidth=1, relheight=1)

        for tool in TOOLS_DEF:
            tid   = tool["id"]
            label = tool["label"]
            lock  = tool.get("lock")
            if tid == "code_manager":
                panel = CodeManagerPanel(self._content, self)
            elif tid == "cns_editor":
                panel = CNSEditorPanel(self._content, self)
            elif tid == "mdt_color_editor":
                panel = MDTColorPanel(self._content, self)
            elif tid == "aev_editor":
                panel = AEVOptionPanel(self._content, self)
            elif tid == "avl_editor":
                panel = LockAEVPanel(self._content, self)
            elif tid == "osd_editor":
                panel = OSDEditorPanel(self._content, self)
            elif tid == "room_init_editor":
                panel = RoomInitPanel(self._content, self)
            elif tid == "scripts":
                panel = ScriptsPanel(self._content, self)
            else:
                panel = ComingSoonPanel(self._content, label)
            panel.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._panels[tid] = panel

        # status bar
        tk.Frame(self, bg="#111", height=1).pack(fill="x")
        sbar = tk.Frame(self, bg="#0d0d0d")
        sbar.pack(fill="x")
        self._status_var = tk.StringVar(value="")
        tk.Label(sbar, textvariable=self._status_var,
                 fg="#444", bg="#0d0d0d",
                 font=("Courier New", 7)).pack(side="left", padx=12, pady=3)
        tk.Label(sbar, text="by YEMENI",
                 fg="#333", bg="#0d0d0d",
                 font=("Courier New", 7)).pack(side="right", padx=12, pady=3)

    def _reload_master_ui(self):
        """Rebuild the entire Master Editor UI in-place (no process restart)."""
        # Hide window during rebuild to avoid flicker
        self.withdraw()

        # Destroy all child widgets
        for w in self.winfo_children():
            w.destroy()

        # Rebuild
        self._build_ui()
        self._show_welcome()

        # Show again
        self.deiconify()

    def _show_credit(self):
        dlg = tk.Toplevel(self)
        dlg.title(t("المطورين","Credit"))
        dlg.geometry("480x300")
        dlg.resizable(False, False)
        dlg.configure(bg="#0b0b0b")
        dlg.grab_set()

        tk.Label(dlg, text="RE4 MASTER EDITOR",
                 fg="#c8a035", bg="#0b0b0b",
                 font=("Courier New", 12, "bold")).pack(pady=(20, 4))

        credit_text = (
            t(
                "الأداة بواسطة : اليمني\n\n"
                "محرر تهيئة الغرف ومحرر الصوت\n"
                "ومحرر الأسلحة والعناصر بواسطة : Player7z\n\n"
                "الكود مكتوب بواسطة : Claude AI\n\n"
                "ملاحظة لمحرر الأسلحة والعناصر:\n"
                "الكود المصدري تمت مشاركته بشكل خاص.\n"
                "لن تجد هذا القسم على GitHub\n"
                "لأن Player7z اختار عدم نشره بشكل عام.\n"
                "شكر خاص لـ Player7z.",
                "Tool by : YEMENI\n\n"
                "Room Init Editor And Snd Editor\n"
                "And Weapon And Items Editor by : Player7z\n\n"
                "Code Written By : Claude AI\n\n"
                "Note for Weapons and Items Editor:\n"
                "The source code was shared privately.\n"
                "You won't find this section on GitHub\n"
                "because Player7z chose not to publish it publicly.\n"
                "Special thanks to Player7z."
            )
        )

        tk.Label(dlg, text=credit_text,
                 fg="#aaaaaa", bg="#0b0b0b",
                 font=("Courier New", 9),
                 justify="center").pack(padx=20, pady=8)

        tk.Frame(dlg, bg="#c8a035", height=1).pack(fill="x", padx=20, pady=8)

        tk.Button(dlg, text=t("إغلاق","Close"),
                  font=("Courier New", 9),
                  fg="#888", bg="#1a1a1a",
                  activeforeground="#aaa", activebackground="#222",
                  relief="flat", bd=0, cursor="hand2",
                  padx=16, pady=5,
                  command=dlg.destroy).pack(pady=(0, 16))

    def _show_info(self):
        win = tk.Toplevel(self)
        win.title("Info")
        win.geometry("900x640")
        win.configure(bg="#0b0b0b")
        win.transient(self)

        # lang from app settings — no toggle needed
        _lang_val = MASTER_SETTINGS.get("lang", APP_SETTINGS.get("lang", "en"))

        topbar = tk.Frame(win, bg="#0e0e0e")
        topbar.pack(fill="x")
        tk.Label(topbar, text="INFO", fg="#c8a035", bg="#0e0e0e",
                 font=("Courier New", 12, "bold")).pack(side="left", padx=16, pady=8)

        _content_frame = [None]
        _active_key    = ["Code Manager"]

        def _render(key):
            if _content_frame[0]:
                _content_frame[0].destroy()
            data = (_INFO_DATA_AR if _lang_val=="ar" else _INFO_DATA_EN)
            title, color, text = data[key]
            cf = tk.Frame(content_area, bg="#0b0b0b")
            cf.pack(fill="both", expand=True)
            _content_frame[0] = cf
            tk.Frame(cf, bg=color, height=2).pack(fill="x")
            outer = tk.Frame(cf, bg="#0b0b0b")
            outer.pack(fill="both", expand=True)
            canvas = tk.Canvas(outer, bg="#0b0b0b", highlightthickness=0)
            sb = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
            canvas.configure(yscrollcommand=sb.set)
            canvas.pack(side="left", fill="both", expand=True)
            sb.pack(side="right", fill="y")
            inner = tk.Frame(canvas, bg="#0b0b0b")
            cw = canvas.create_window((0,0), window=inner, anchor="nw")
            inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.bind("<Configure>", lambda e: canvas.itemconfig(cw, width=e.width))
            canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)),"units"))
            is_ar = (_lang_val == "ar")
            tk.Label(inner, text=title, fg=color, bg="#0b0b0b",
                     font=("Courier New", 15, "bold"), anchor="e" if is_ar else "w"
                     ).pack(anchor="e" if is_ar else "w", padx=28, pady=(24,4))
            tk.Frame(inner, bg="#1e1e1e", height=1).pack(fill="x", padx=28, pady=(0,16))
            for line in text.split("\n"):
                if line.startswith("##"):
                    tk.Label(inner, text=line[2:].strip(), fg=color, bg="#0b0b0b",
                             font=("Courier New", 10, "bold"),
                             anchor="e" if is_ar else "w"
                             ).pack(anchor="e" if is_ar else "w", padx=28, pady=(14,2))
                elif line.startswith("+"):
                    tk.Label(inner, text="  " + line[1:].strip(), fg="#777", bg="#0b0b0b",
                             font=("Courier New", 9),
                             anchor="e" if is_ar else "w"
                             ).pack(anchor="e" if is_ar else "w", padx=36, pady=1)
                elif line.strip() == "":
                    tk.Frame(inner, bg="#0b0b0b", height=5).pack()
                else:
                    tk.Label(inner, text=line, fg="#aaaaaa", bg="#0b0b0b",
                             font=("Courier New", 9),
                             anchor="e" if is_ar else "w",
                             justify="right" if is_ar else "left",
                             wraplength=580
                             ).pack(anchor="e" if is_ar else "w", padx=28, pady=1)

        def _switch(key):
            _active_key[0] = key
            data = (_INFO_DATA_AR if _lang_val=="ar" else _INFO_DATA_EN)
            for k,(b,i) in nav_btns.items():
                c = data[k][1]
                if k==key: b.configure(fg=c); i.configure(bg=c)
                else:       b.configure(fg="#3a3a3a"); i.configure(bg="#080808")
            _render(key)

        tk.Frame(win, bg="#c8a035", height=1).pack(fill="x")
        body = tk.Frame(win, bg="#0b0b0b")
        body.pack(fill="both", expand=True)
        sidebar = tk.Frame(body, bg="#080808", width=180)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Frame(sidebar, bg="#1a1a1a", height=1).pack(fill="x", pady=(8,2))
        content_area = tk.Frame(body, bg="#0b0b0b")
        content_area.pack(side="left", fill="both", expand=True)
        nav_btns = {}

        sections = list(_INFO_DATA_AR.keys())
        for key in sections:
            _, color, _ = _INFO_DATA_AR[key]
            bf = tk.Frame(sidebar, bg="#080808"); bf.pack(fill="x")
            ind = tk.Frame(bf, bg="#080808", width=3); ind.pack(side="left", fill="y")
            btn = tk.Button(bf, text=key, font=("Courier New", 8),
                            fg="#3a3a3a", bg="#080808",
                            activeforeground=color, activebackground="#111",
                            relief="flat", bd=0, anchor="w", padx=10, pady=6,
                            cursor="hand2", command=lambda k=key: _switch(k))
            btn.pack(fill="x", expand=True)
            btn.bind("<Enter>", lambda e,b=btn,i=ind,c=color: (b.configure(fg=c),i.configure(bg=c)))
            btn.bind("<Leave>", lambda e,b=btn,i=ind,k2=key,lv=_lang_val: (
                b.configure(fg=(_INFO_DATA_AR if lv=="ar" else _INFO_DATA_EN)[k2][1]
                            if _active_key[0]==k2 else "#3a3a3a"),
                i.configure(bg=(_INFO_DATA_AR if lv=="ar" else _INFO_DATA_EN)[k2][1]
                            if _active_key[0]==k2 else "#080808")
            ))
            nav_btns[key] = (btn, ind)

        _switch("Code Manager")
        win.after(50, lambda: (win.lift(), win.focus_force()))


    def _show_welcome(self):
        for p in self._panels.values():
            p.lower()
        self._welcome.lift()
        for tool in TOOLS_DEF:
            btn  = self._nav_btns.get(tool["id"])
            if btn:
                btn.configure(fg="#2e2e2e", bg="#0a0a0a")
                btn._active = False
                if hasattr(btn, "_indicator"):
                    btn._indicator.configure(bg="#0a0a0a", width=3)
        self._status_var.set("")

    def _switch_tool(self, tool_id):
        tool_def  = next((t for t in TOOLS_DEF if t["id"] == tool_id), None)
        lock      = tool_def.get("lock") if tool_def else None
        needs_exe = tool_def.get("needs_exe", False) if tool_def else False

        # Check exe requirement first
        if needs_exe and not (self.exe_path.get().strip() and
                              os.path.isfile(self.exe_path.get().strip())):
            messagebox.showwarning(
                "EXE Required" if CURRENT_LANG == "en" else "يلزم EXE",
                "Please select bio4.exe first using the Browse button at the top."
                if CURRENT_LANG == "en" else
                "اختر bio4.exe أولاً عبر زر Browse في الأعلى."
            )
            return

        if lock and lock[0] not in self._unlocked_codes:
            cm = self._cm_app
            if cm is None or not cm.scanned:
                messagebox.showwarning(
                    "Scan Required" if CURRENT_LANG == "en" else "يلزم مسح",
                    ("Please scan bio4.exe from RE4 CODE MANAGER first.\n"
                     "Go to RE4 CODE MANAGER  press SCAN EXE  return here.")
                    if CURRENT_LANG == "en" else
                    ("سوي Scan من RE4 CODE MANAGER أولاً.\n"
                     "روح RE4 CODE MANAGER  اضغط SCAN EXE  ارجع هنا.")
                )
            else:
                messagebox.showwarning(
                    "Module Locked" if CURRENT_LANG == "en" else "القسم مقفل",
                    f"This module requires [{lock[1]}] to be enabled in RE4 CODE MANAGER."
                    if CURRENT_LANG == "en" else
                    f"هذا القسم يتطلب تفعيل [{lock[1]}] في RE4 CODE MANAGER."
                )
            return

        self._welcome.lower()
        for tid, panel in self._panels.items():
            panel.lower()
            btn = self._nav_btns.get(tid)
            if btn:
                btn.configure(fg="#2e2e2e", bg="#0a0a0a")
                btn._active = False
                if hasattr(btn, "_indicator"):
                    btn._indicator.configure(bg="#0a0a0a", width=3)

        panel = self._panels.get(tool_id)
        if panel:
            panel.lift()
            panel.activate()
            panel.update_idletasks()

        btn = self._nav_btns.get(tool_id)
        if btn:
            tool_def_cur = next((t for t in TOOLS_DEF if t["id"] == tool_id), {})
            accent = tool_def_cur.get("color", _GOLD)
            btn.configure(fg=accent, bg="#111")
            btn._active = True
            if hasattr(btn, "_indicator"):
                btn._indicator.configure(bg=accent, width=3)

        label = next((t["label"] for t in TOOLS_DEF if t["id"] == tool_id), tool_id)
        self._status_var.set(label)

    def _add_paste_menu(self, entry):
        menu = tk.Menu(entry, tearoff=0, bg="#1a1a1a", fg="#ccc",
                       activebackground="#2a2a2a",
                       font=("Courier New", 8))
        menu.add_command(label="Paste", command=lambda: entry.event_generate("<<Paste>>"))
        menu.add_command(label="Copy",  command=lambda: entry.event_generate("<<Copy>>"))
        menu.add_command(label="Select All", command=lambda: entry.select_range(0,"end"))
        entry.bind("<Button-3>", lambda e: menu.tk_popup(e.x_root, e.y_root))

    def _create_backup(self):
        """Copy bio4.exe → BIO4_BACKUP.EXE next to the original."""
        exe = self.exe_path.get().strip()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("Error", "Select bio4.exe first.")
            return
        import shutil
        dst = os.path.join(os.path.dirname(exe), "BIO4_BACKUP.EXE")
        if os.path.isfile(dst):
            if not messagebox.askyesno("Overwrite?",
                f"BIO4_BACKUP.EXE already exists.\nOverwrite?"):
                return
        try:
            shutil.copy2(exe, dst)
            messagebox.showinfo("Done", f"Backup created:\n{dst}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def _browse_exe(self):
        p = _browse_open(
            title="Select bio4.exe",
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
            key="exe"
        )
        if p:
            self.exe_path.set(p)

    def _on_exe_change(self, *_):
        path = self.exe_path.get().strip()
        if path and os.path.isfile(path):
            if MASTER_SETTINGS.get("remember_exe", True):
                MASTER_SETTINGS["last_exe"] = path
                save_master_settings(MASTER_SETTINGS)
            # auto-scan: get CM app from panel if not set yet
            cm = self._cm_app
            if cm is None:
                cm_panel = self._panels.get("code_manager")
                if cm_panel:
                    cm = getattr(cm_panel, "_app", None)
            if cm and hasattr(cm, "_scan"):
                self.after(600, cm._scan)
            # auto-scan MDT colors (speech + custom)
            mdt = self._panels.get("mdt_color_editor")
            if mdt and getattr(mdt, "_built", False):
                try:
                    sp = getattr(mdt, "_speech_panel", None)
                    if sp and hasattr(sp, "_scan_exe_colors"):
                        sp._scan_exe_colors()
                    cp = getattr(mdt, "_custom_panel", None)
                    if cp and hasattr(cp, "_reload"):
                        cp._reload()
                except Exception:
                    pass
                try:
                    cp = getattr(mdt, "_custom_panel", None)
                    if cp and hasattr(cp, "_reload"):
                        cp._reload()
                except Exception:
                    pass

    def _check_locked_panels(self):
        cm = self._cm_app
        if not cm:
            return
        for tool in TOOLS_DEF:
            lock = tool.get("lock")
            if not lock:
                continue
            code_id = lock[0]
            tid     = tool["id"]
            if cm.applied.get(code_id, False) or cm.detected.get(code_id, False):
                self._unlocked_codes.add(code_id)
            else:
                self._unlocked_codes.discard(code_id)
            # no visual color change for lock state

    def _open_settings(self):
        dlg = tk.Toplevel(self)
        dlg.title(t("الإعدادات","Settings"))
        dlg.geometry("300x280")
        dlg.resizable(False, False)
        dlg.configure(bg="#111")
        dlg.grab_set()

        tk.Label(dlg, text=t("الإعدادات","Settings"), fg=_GOLD, bg="#111",
                 font=("Courier New", 11, "bold")).pack(pady=(16,10))
        tk.Frame(dlg, bg="#333", height=1).pack(fill="x", padx=20, pady=4)
        tk.Label(dlg, text=t("اللغة","Language"), fg="#555", bg="#111",
                 font=("Courier New", 8)).pack()

        lang_var = tk.StringVar(value=MASTER_SETTINGS.get("lang", "en"))
        lf = tk.Frame(dlg, bg="#111")
        lf.pack(pady=4)
        for val, lbl in [("en", "English"), ("ar", "العربية")]:
            tk.Radiobutton(lf, text=lbl, variable=lang_var, value=val,
                           fg="#ccc", bg="#111",
                           activebackground="#111", selectcolor="#1a1a1a",
                           font=("Courier New", 9), relief="flat"
                           ).pack(side="left", padx=12)

        tk.Frame(dlg, bg="#333", height=1).pack(fill="x", padx=20, pady=4)
        rem_var = tk.BooleanVar(value=MASTER_SETTINGS.get("remember_exe", True))
        tk.Checkbutton(dlg, text=t("تذكر مسار EXE الأخير","Remember last EXE path"),
                       variable=rem_var, fg="#ccc", bg="#111",
                       activebackground="#111", selectcolor="#1a1a1a",
                       font=("Courier New", 9), relief="flat",
                       command=lambda: (
                           MASTER_SETTINGS.update({"remember_exe": rem_var.get()}),
                           save_master_settings(MASTER_SETTINGS)
                       )).pack(padx=24, anchor="w", pady=4)

        tk.Frame(dlg, bg="#333", height=1).pack(fill="x", padx=20, pady=4)

        # Check for Updates button
        def _manual_check():
            _check_for_update(self, manual=True)
            # Also reset "skip" if user manually checks
            if MASTER_SETTINGS.get("skip_update_notify", False):
                MASTER_SETTINGS["skip_update_notify"] = False
                save_master_settings(MASTER_SETTINGS)
            dlg.destroy()

        tk.Button(dlg,
                  text=t("التحقق من التحديثات", "Check for Updates"),
                  font=("Courier New", 9),
                  fg=_GOLD, bg="#1a1500",
                  activeforeground=_GOLD, activebackground="#2a2000",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground=_GOLD,
                  padx=12, pady=4,
                  command=_manual_check
                  ).pack(pady=6)

        tk.Frame(dlg, bg="#333", height=1).pack(fill="x", padx=20, pady=4)

        def apply_lang():
            global CURRENT_LANG
            new_lang = lang_var.get()
            if new_lang == CURRENT_LANG:
                dlg.destroy()
                return
            MASTER_SETTINGS["lang"] = new_lang
            APP_SETTINGS["lang"]    = new_lang
            save_master_settings(MASTER_SETTINGS)
            save_settings(APP_SETTINGS)
            CURRENT_LANG = new_lang
            dlg.destroy()
            self._reload_master_ui()

        tk.Button(dlg, text=t("تطبيق","Apply"), font=("Courier New", 9),
                  fg=_GREEN, bg="#1a2a0a",
                  activeforeground=_GREEN, activebackground="#2a4a1a",
                  relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground=_GREEN,
                  command=apply_lang, padx=12, pady=3
                  ).pack(pady=8)


# 
#  Entry point
# 

if __name__ == "__main__":
    is_first = MASTER_SETTINGS.get("first_run", True)

    app = RE4MasterEditor()

    if is_first:
        def _on_lang_chosen(lang):
            # Rebuild UI with chosen language — no process restart needed
            app.after(100, app._reload_master_ui)
        app.after(100, lambda: _show_first_run_setup(app, _on_lang_chosen))

    app.mainloop()