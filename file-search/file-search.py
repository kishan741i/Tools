# """
# Whole-Machine File & Folder Search
# ----------------------------------
# A simple desktop search bar (Tkinter, no extra installs needed) that looks
# for any file or folder name across every drive on your computer.

# Run:
#     python file_search.py
# """

# import os
# import platform
# import string
# import threading
# import subprocess
# import time
# import tkinter as tk
# from tkinter import ttk


# # --------------------------------------------------------------------------
# # Helpers
# # --------------------------------------------------------------------------

# def get_all_drives():
#     """Return a list of all available drive roots (Windows) or '/' (Linux/macOS)."""
#     system = platform.system()
#     if system == "Windows":
#         drives = []
#         for letter in string.ascii_uppercase:
#             drive = f"{letter}:\\"
#             if os.path.exists(drive):
#                 drives.append(drive)
#         return drives or ["C:\\"]
#     else:
#         return ["/"]


# def get_search_roots(selected_drive=None):
#     """Return the top-level folders to start scanning from.

#     If selected_drive is None or 'This PC', scan all drives.
#     Otherwise scan only the selected drive.
#     """
#     if selected_drive and selected_drive != "This PC":
#         return [selected_drive]
#     # This PC → all drives
#     return get_all_drives()


# SKIP_DIR_NAMES = {
#     # Windows noise
#     "$Recycle.Bin", "System Volume Information", "Windows.old",
#     # Linux/macOS virtual/system mounts, safe to skip for a name search
#     "proc", "sys", "dev", "run",
# }


# def human_size(num_bytes):
#     if num_bytes is None:
#         return ""
#     for unit in ["B", "KB", "MB", "GB", "TB"]:
#         if num_bytes < 1024:
#             return f"{num_bytes:.0f} {unit}" if unit == "B" else f"{num_bytes:.1f} {unit}"
#         num_bytes /= 1024
#     return f"{num_bytes:.1f} PB"


# def open_containing_folder(path):
#     folder = path if os.path.isdir(path) else os.path.dirname(path)
#     system = platform.system()
#     try:
#         if system == "Windows":
#             # Select the exact file/folder in Explorer when possible.
#             subprocess.run(["explorer", "/select,", path], check=False)
#         elif system == "Darwin":
#             subprocess.run(["open", "-R", path], check=False)
#         else:
#             subprocess.run(["xdg-open", folder], check=False)
#     except Exception:
#         pass


# # --------------------------------------------------------------------------
# # App
# # --------------------------------------------------------------------------

# class SearchApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Search My Machine")
#         self.root.geometry("760x520")
#         self.root.minsize(560, 380)

#         self.search_thread = None
#         self.stop_event = threading.Event()
#         self.result_count = 0
#         self.start_time = None

#         self._build_ui()

#     # ---- UI ----

#     def _build_ui(self):
#         pad = {"padx": 10, "pady": 6}

#         top = ttk.Frame(self.root)
#         top.pack(fill="x", **pad)

#         # ---- Drive dropdown (NEW) ----
#         ttk.Label(top, text="Location:").pack(side="left")

#         self.drive_var = tk.StringVar(value="This PC")
#         self.drive_combo = ttk.Combobox(
#             top,
#             textvariable=self.drive_var,
#             state="readonly",
#             width=12,
#             font=("Segoe UI", 10),
#         )
#         self._refresh_drive_list()
#         self.drive_combo.pack(side="left", padx=(6, 10))
#         # Refresh drive list every time dropdown is opened
#         self.drive_combo.bind("<<ComboboxSelected>>", lambda e: None)
#         self.drive_combo.bind("<Button-1>", self._on_drive_dropdown_open)

#         # ---- Search label + entry ----
#         ttk.Label(top, text="Search for:").pack(side="left")

#         self.query_var = tk.StringVar()
#         self.entry = ttk.Entry(top, textvariable=self.query_var, font=("Segoe UI", 11))
#         self.entry.pack(side="left", fill="x", expand=True, padx=(6, 6))
#         self.entry.bind("<Return>", lambda e: self.start_search())
#         self.entry.focus_set()

#         self.search_btn = ttk.Button(top, text="Search", command=self.start_search)
#         self.search_btn.pack(side="left", padx=(0, 4))

#         self.stop_btn = ttk.Button(top, text="Stop", command=self.stop_search, state="disabled")
#         self.stop_btn.pack(side="left")

#         # Options row
#         opts = ttk.Frame(self.root)
#         opts.pack(fill="x", padx=10, pady=(0, 6))

#         self.match_files = tk.BooleanVar(value=True)
#         self.match_folders = tk.BooleanVar(value=True)
#         self.case_sensitive = tk.BooleanVar(value=False)
#         self.exact_match = tk.BooleanVar(value=False)

#         ttk.Checkbutton(opts, text="Files", variable=self.match_files).pack(side="left")
#         ttk.Checkbutton(opts, text="Folders", variable=self.match_folders).pack(side="left", padx=(10, 0))
#         ttk.Checkbutton(opts, text="Case sensitive", variable=self.case_sensitive).pack(side="left", padx=(10, 0))
#         ttk.Checkbutton(opts, text="Exact name (not just contains)", variable=self.exact_match).pack(side="left", padx=(10, 0))

#         # Status row
#         self.status_var = tk.StringVar(value="Type a name and press Search.")
#         status_label = ttk.Label(self.root, textvariable=self.status_var, foreground="#555")
#         status_label.pack(fill="x", padx=10)

#         self.progress = ttk.Progressbar(self.root, mode="indeterminate")
#         self.progress.pack(fill="x", padx=10, pady=(2, 8))

#         # Results list
#         list_frame = ttk.Frame(self.root)
#         list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

#         columns = ("path", "type", "size")
#         self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
#         self.tree.heading("path", text="Full path")
#         self.tree.heading("type", text="Type")
#         self.tree.heading("size", text="Size")
#         self.tree.column("path", width=520, anchor="w")
#         self.tree.column("type", width=70, anchor="center")
#         self.tree.column("size", width=90, anchor="e")

#         vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
#         self.tree.configure(yscrollcommand=vsb.set)
#         self.tree.pack(side="left", fill="both", expand=True)
#         vsb.pack(side="right", fill="y")

#         self.tree.bind("<Double-1>", self._on_result_double_click)

#         hint = ttk.Label(
#             self.root,
#             text="Double-click a result to open its folder. Scanning the whole machine can take a few minutes.",
#             foreground="#777",
#         )
#         hint.pack(fill="x", padx=10, pady=(0, 8))

#     # ---- Drive dropdown helpers (NEW) ----

#     def _refresh_drive_list(self):
#         """Rebuild the dropdown values: 'This PC' + all available drives."""
#         drives = get_all_drives()
#         values = ["This PC"] + drives
#         self.drive_combo["values"] = values
#         # Keep current selection if still valid, otherwise default to "This PC"
#         if self.drive_var.get() not in values:
#             self.drive_var.set("This PC")

#     def _on_drive_dropdown_open(self, event):
#         """Refresh drive list just before the dropdown opens (so USB drives etc. show up)."""
#         self._refresh_drive_list()

#     # ---- Search control ----

#     def start_search(self):
#         query = self.query_var.get().strip()
#         if not query:
#             self.status_var.set("Please type a name to search for.")
#             return
#         if self.search_thread and self.search_thread.is_alive():
#             return  # a search is already running

#         for row in self.tree.get_children():
#             self.tree.delete(row)
#         self.result_count = 0
#         self.stop_event.clear()
#         self.start_time = time.time()

#         self.search_btn.config(state="disabled")
#         self.stop_btn.config(state="normal")
#         self.progress.start(12)

#         selected = self.drive_var.get()
#         if selected == "This PC":
#             self.status_var.set("Searching on all drives...")
#         else:
#             self.status_var.set(f"Searching on {selected} ...")

#         self.search_thread = threading.Thread(
#             target=self._run_search,
#             args=(query, self.match_files.get(), self.match_folders.get(),
#                   self.case_sensitive.get(), self.exact_match.get(),
#                   selected),
#             daemon=True,
#         )
#         self.search_thread.start()
#         self.root.after(150, self._poll_thread)

#     def stop_search(self):
#         self.stop_event.set()
#         self.status_var.set("Stopping...")
#         self.stop_btn.config(state="disabled")

#     def _poll_thread(self):
#         if self.search_thread and self.search_thread.is_alive():
#             self.root.after(150, self._poll_thread)
#         else:
#             self._search_finished()

#     def _search_finished(self):
#         self.progress.stop()
#         self.search_btn.config(state="normal")
#         self.stop_btn.config(state="disabled")
#         elapsed = time.time() - self.start_time if self.start_time else 0
#         if self.stop_event.is_set():
#             self.status_var.set(f"Stopped — {self.result_count} result(s) found in {elapsed:.1f}s.")
#         else:
#             self.status_var.set(f"Done — {self.result_count} result(s) found in {elapsed:.1f}s.")

#     # ---- Search worker (runs in a background thread) ----

#     def _run_search(self, query, want_files, want_folders, case_sensitive, exact, selected_drive):
#         needle = query if case_sensitive else query.lower()

#         def matches(name):
#             candidate = name if case_sensitive else name.lower()
#             return candidate == needle if exact else needle in candidate

#         for root_path in get_search_roots(selected_drive):
#             if self.stop_event.is_set():
#                 return
#             for current_dir, dirnames, filenames in os.walk(root_path, topdown=True, onerror=lambda e: None):
#                 if self.stop_event.is_set():
#                     return

#                 # Prune noisy/virtual directories in place so os.walk skips them.
#                 dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]

#                 self._set_status_safe(f"Scanning: {current_dir}")

#                 if want_folders:
#                     for d in dirnames:
#                         if self.stop_event.is_set():
#                             return
#                         if matches(d):
#                             full = os.path.join(current_dir, d)
#                             self._add_result_safe(full, "Folder", None)

#                 if want_files:
#                     for f in filenames:
#                         if self.stop_event.is_set():
#                             return
#                         if matches(f):
#                             full = os.path.join(current_dir, f)
#                             size = None
#                             try:
#                                 size = os.path.getsize(full)
#                             except OSError:
#                                 pass
#                             self._add_result_safe(full, "File", size)

#     # ---- Thread-safe UI updates ----

#     def _add_result_safe(self, full_path, kind, size):
#         self.result_count += 1

#         def update():
#             self.tree.insert("", "end", values=(full_path, kind, human_size(size)))
#         self.root.after(0, update)

#     def _set_status_safe(self, text):
#         def update():
#             # Don't spam the status line if a search just stopped/finished.
#             if self.search_thread and self.search_thread.is_alive():
#                 self.status_var.set(text if len(text) < 100 else text[:97] + "...")
#         self.root.after(0, update)

#     def _on_result_double_click(self, event):
#         selection = self.tree.selection()
#         if not selection:
#             return
#         values = self.tree.item(selection[0], "values")
#         if values:
#             open_containing_folder(values[0])


# if __name__ == "__main__":
#     root = tk.Tk()
#     app = SearchApp(root)
#     root.mainloop()

"""
Whole-Machine File & Folder Search
----------------------------------
A simple desktop search bar (Tkinter, no extra installs needed) that looks
for any file or folder name across every drive on your computer.

Run:
    python file_search.py
"""

import os
import platform
import string
import threading
import subprocess
import time
import tkinter as tk
from tkinter import ttk


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def get_all_drives():
    """Return a list of all available drive roots (Windows) or '/' (Linux/macOS)."""
    system = platform.system()
    if system == "Windows":
        drives = []
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                drives.append(drive)
        return drives or ["C:\\"]
    else:
        return ["/"]


def get_search_roots(selected_drive=None):
    """Return the top-level folders to start scanning from.

    If selected_drive is None or 'This PC', scan all drives.
    Otherwise scan only the selected drive.
    """
    if selected_drive and selected_drive != "This PC":
        return [selected_drive]
    return get_all_drives()


SKIP_DIR_NAMES = {
    # Windows noise
    "$Recycle.Bin", "System Volume Information", "Windows.old",
    # Linux/macOS virtual/system mounts, safe to skip for a name search
    "proc", "sys", "dev", "run",
}


# --------------------------------------------------------------------------
# File type filters (NEW)
# --------------------------------------------------------------------------
# Each entry: Display name -> set of extensions (lowercase, with dot)
# "All Types" means no extension filter at all.
TYPE_FILTERS = {
    "All Types":      None,
    "Documents":      {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt",
                       ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".md"},
    "Images":         {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff",
                       ".webp", ".svg", ".ico", ".heic"},
    "Videos":         {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv",
                       ".webm", ".m4v", ".mpg", ".mpeg", ".3gp"},
    "Audio":          {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a",
                       ".wma", ".opus", ".aiff"},
    "Archives":       {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2",
                       ".xz", ".iso", ".cab"},
    "Programs":       {".exe", ".msi", ".bat", ".cmd", ".sh", ".app",
                       ".apk", ".deb", ".rpm"},
    "Code":           {".py", ".js", ".ts", ".java", ".c", ".cpp", ".h",
                       ".cs", ".php", ".html", ".css", ".json", ".xml",
                       ".sql", ".rb", ".go", ".rs"},
    "Folders only":   "__FOLDER__",   # special marker
}


def human_size(num_bytes):
    if num_bytes is None:
        return ""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.0f} {unit}" if unit == "B" else f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"


def open_containing_folder(path):
    folder = path if os.path.isdir(path) else os.path.dirname(path)
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.run(["explorer", "/select,", path], check=False)
        elif system == "Darwin":
            subprocess.run(["open", "-R", path], check=False)
        else:
            subprocess.run(["xdg-open", folder], check=False)
    except Exception:
        pass


# --------------------------------------------------------------------------
# App
# --------------------------------------------------------------------------

class SearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Search My Machine")
        self.root.geometry("820x540")
        self.root.minsize(620, 400)

        self.search_thread = None
        self.stop_event = threading.Event()
        self.result_count = 0
        self.start_time = None

        self._build_ui()

    # ---- UI ----

    def _build_ui(self):
        pad = {"padx": 10, "pady": 6}

        # ============ Row 1: Location + Type + Query + Buttons ============
        top = ttk.Frame(self.root)
        top.pack(fill="x", **pad)

        # ---- Location dropdown ----
        ttk.Label(top, text="Location:").pack(side="left")

        self.drive_var = tk.StringVar(value="This PC")
        self.drive_combo = ttk.Combobox(
            top,
            textvariable=self.drive_var,
            state="readonly",
            width=10,
            font=("Segoe UI", 10),
        )
        self._refresh_drive_list()
        self.drive_combo.pack(side="left", padx=(6, 10))
        self.drive_combo.bind("<Button-1>", self._on_drive_dropdown_open)

        # ---- Type dropdown (NEW) ----
        ttk.Label(top, text="Type:").pack(side="left")

        self.type_var = tk.StringVar(value="All Types")
        self.type_combo = ttk.Combobox(
            top,
            textvariable=self.type_var,
            state="readonly",
            width=13,
            font=("Segoe UI", 10),
            values=list(TYPE_FILTERS.keys()),
        )
        self.type_combo.pack(side="left", padx=(6, 10))

        # ---- Search label + entry ----
        ttk.Label(top, text="Search for:").pack(side="left")

        self.query_var = tk.StringVar()
        self.entry = ttk.Entry(top, textvariable=self.query_var, font=("Segoe UI", 11))
        self.entry.pack(side="left", fill="x", expand=True, padx=(6, 6))
        self.entry.bind("<Return>", lambda e: self.start_search())
        self.entry.focus_set()

        self.search_btn = ttk.Button(top, text="Search", command=self.start_search)
        self.search_btn.pack(side="left", padx=(0, 4))

        self.stop_btn = ttk.Button(top, text="Stop", command=self.stop_search, state="disabled")
        self.stop_btn.pack(side="left")

        # Options row
        opts = ttk.Frame(self.root)
        opts.pack(fill="x", padx=10, pady=(0, 6))

        self.match_files = tk.BooleanVar(value=True)
        self.match_folders = tk.BooleanVar(value=True)
        self.case_sensitive = tk.BooleanVar(value=False)
        self.exact_match = tk.BooleanVar(value=False)

        ttk.Checkbutton(opts, text="Files", variable=self.match_files).pack(side="left")
        ttk.Checkbutton(opts, text="Folders", variable=self.match_folders).pack(side="left", padx=(10, 0))
        ttk.Checkbutton(opts, text="Case sensitive", variable=self.case_sensitive).pack(side="left", padx=(10, 0))
        ttk.Checkbutton(opts, text="Exact name (not just contains)", variable=self.exact_match).pack(side="left", padx=(10, 0))

        # Status row
        self.status_var = tk.StringVar(value="Type a name and press Search.")
        status_label = ttk.Label(self.root, textvariable=self.status_var, foreground="#555")
        status_label.pack(fill="x", padx=10)

        self.progress = ttk.Progressbar(self.root, mode="indeterminate")
        self.progress.pack(fill="x", padx=10, pady=(2, 8))

        # Results list
        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("path", "type", "size")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("path", text="Full path")
        self.tree.heading("type", text="Type")
        self.tree.heading("size", text="Size")
        self.tree.column("path", width=580, anchor="w")
        self.tree.column("type", width=70, anchor="center")
        self.tree.column("size", width=90, anchor="e")

        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", self._on_result_double_click)

        hint = ttk.Label(
            self.root,
            text="Double-click a result to open its folder. Scanning the whole machine can take a few minutes.",
            foreground="#777",
        )
        hint.pack(fill="x", padx=10, pady=(0, 8))

    # ---- Drive dropdown helpers ----

    def _refresh_drive_list(self):
        drives = get_all_drives()
        values = ["This PC"] + drives
        self.drive_combo["values"] = values
        if self.drive_var.get() not in values:
            self.drive_var.set("This PC")

    def _on_drive_dropdown_open(self, event):
        self._refresh_drive_list()

    # ---- Search control ----

    def start_search(self):
        query = self.query_var.get().strip()
        if not query:
            self.status_var.set("Please type a name to search for.")
            return
        if self.search_thread and self.search_thread.is_alive():
            return

        for row in self.tree.get_children():
            self.tree.delete(row)
        self.result_count = 0
        self.stop_event.clear()
        self.start_time = time.time()

        self.search_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.progress.start(12)

        selected_drive = self.drive_var.get()
        selected_type = self.type_var.get()

        location_text = "all drives" if selected_drive == "This PC" else selected_drive
        self.status_var.set(f"Searching on {location_text}  ({selected_type}) ...")

        self.search_thread = threading.Thread(
            target=self._run_search,
            args=(query,
                  self.match_files.get(),
                  self.match_folders.get(),
                  self.case_sensitive.get(),
                  self.exact_match.get(),
                  selected_drive,
                  selected_type),
            daemon=True,
        )
        self.search_thread.start()
        self.root.after(150, self._poll_thread)

    def stop_search(self):
        self.stop_event.set()
        self.status_var.set("Stopping...")
        self.stop_btn.config(state="disabled")

    def _poll_thread(self):
        if self.search_thread and self.search_thread.is_alive():
            self.root.after(150, self._poll_thread)
        else:
            self._search_finished()

    def _search_finished(self):
        self.progress.stop()
        self.search_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        elapsed = time.time() - self.start_time if self.start_time else 0
        if self.stop_event.is_set():
            self.status_var.set(f"Stopped — {self.result_count} result(s) found in {elapsed:.1f}s.")
        else:
            self.status_var.set(f"Done — {self.result_count} result(s) found in {elapsed:.1f}s.")

    # ---- Search worker ----

    def _run_search(self, query, want_files, want_folders,
                    case_sensitive, exact, selected_drive, selected_type):
        needle = query if case_sensitive else query.lower()

        def matches(name):
            candidate = name if case_sensitive else name.lower()
            return candidate == needle if exact else needle in candidate

        # Resolve type filter
        ext_filter = TYPE_FILTERS.get(selected_type, None)
        folders_only = (ext_filter == "__FOLDER__")

        # If "Folders only" type selected, force file search off
        if folders_only:
            want_files = False
            want_folders = True
        # If a specific extension type is chosen, disable folder results
        elif ext_filter is not None:
            want_folders = False

        for root_path in get_search_roots(selected_drive):
            if self.stop_event.is_set():
                return
            for current_dir, dirnames, filenames in os.walk(root_path, topdown=True, onerror=lambda e: None):
                if self.stop_event.is_set():
                    return

                dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]

                self._set_status_safe(f"Scanning: {current_dir}")

                # Folder matches
                if want_folders:
                    for d in dirnames:
                        if self.stop_event.is_set():
                            return
                        if matches(d):
                            full = os.path.join(current_dir, d)
                            self._add_result_safe(full, "Folder", None)

                # File matches
                if want_files:
                    for f in filenames:
                        if self.stop_event.is_set():
                            return

                        # Extension filter check
                        if ext_filter is not None:
                            ext = os.path.splitext(f)[1].lower()
                            if ext not in ext_filter:
                                continue

                        if matches(f):
                            full = os.path.join(current_dir, f)
                            size = None
                            try:
                                size = os.path.getsize(full)
                            except OSError:
                                pass
                            self._add_result_safe(full, "File", size)

    # ---- Thread-safe UI updates ----

    def _add_result_safe(self, full_path, kind, size):
        self.result_count += 1

        def update():
            self.tree.insert("", "end", values=(full_path, kind, human_size(size)))
        self.root.after(0, update)

    def _set_status_safe(self, text):
        def update():
            if self.search_thread and self.search_thread.is_alive():
                self.status_var.set(text if len(text) < 100 else text[:97] + "...")
        self.root.after(0, update)

    def _on_result_double_click(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0], "values")
        if values:
            open_containing_folder(values[0])


if __name__ == "__main__":
    root = tk.Tk()
    app = SearchApp(root)
    root.mainloop()