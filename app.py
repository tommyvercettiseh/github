from __future__ import annotations

import json
import logging
import os
import queue
import subprocess
import threading
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tkinter import Tk, StringVar, BooleanVar, filedialog, messagebox
from tkinter import ttk

APP_NAME = "Turbo GitHub Hub"
APP_VERSION = "0.1.0"
CONFIG_DIR = Path(os.getenv("APPDATA", Path.home())) / "TurboGitHubHub"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_FILE = LOG_DIR / "github-hub.log"

BG = "#0b1118"
PANEL = "#111923"
PANEL_2 = "#151f2b"
BORDER = "#273445"
TEXT = "#f4f7fb"
MUTED = "#93a4b8"
BLUE = "#2f80ed"
GREEN = "#24c875"
ORANGE = "#f5a524"
RED = "#ef5350"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


@dataclass
class RepoState:
    name: str
    path: Path
    branch: str = "-"
    remote_url: str = ""
    status: str = "Niet gecontroleerd"
    detail: str = ""
    ahead: int = 0
    behind: int = 0
    dirty: bool = False
    last_commit: str = ""
    preview: Path | None = None
    manifest: dict | None = None
    error: str = ""

    @property
    def can_pull(self) -> bool:
        return (
            self.behind > 0
            and self.ahead == 0
            and not self.dirty
            and not self.error
        )


def run_git(repo: Path, *args: str, timeout: int = 45) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )


def normalize_github_url(url: str) -> str:
    value = url.strip()
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value.split(":", 1)[1]
    if value.endswith(".git"):
        value = value[:-4]
    return value


def find_preview(repo: Path, manifest: dict | None) -> Path | None:
    candidates: list[Path] = []
    if manifest and manifest.get("preview"):
        candidates.append(repo / str(manifest["preview"]))
    candidates.extend(
        [
            repo / "docs" / "previews" / "latest.png",
            repo / "docs" / "previews" / "latest.jpg",
            repo / "docs" / "previews" / "latest.gif",
            repo / "preview.png",
        ]
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def read_manifest(repo: Path) -> dict | None:
    path = repo / "turbo-project.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.warning("Manifest ongeldig voor %s: %s", repo, exc)
        return None


def inspect_repo(repo: Path, do_fetch: bool = True) -> RepoState:
    state = RepoState(name=repo.name, path=repo)
    try:
        if do_fetch:
            fetched = run_git(repo, "fetch", "--prune")
            if fetched.returncode != 0:
                state.detail = fetched.stderr.strip() or "Fetch kon niet worden uitgevoerd"

        branch = run_git(repo, "branch", "--show-current")
        state.branch = branch.stdout.strip() or "detached"

        remote = run_git(repo, "remote", "get-url", "origin")
        if remote.returncode == 0:
            state.remote_url = normalize_github_url(remote.stdout)

        dirty = run_git(repo, "status", "--porcelain")
        state.dirty = bool(dirty.stdout.strip())

        last = run_git(repo, "log", "-1", "--format=%cr · %h · %s")
        state.last_commit = last.stdout.strip()

        upstream = run_git(repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
        if upstream.returncode != 0:
            state.status = "Geen upstream"
            state.detail = "Koppel de lokale branch eerst aan origin"
        else:
            counts = run_git(repo, "rev-list", "--left-right", "--count", "HEAD...@{u}")
            if counts.returncode == 0:
                parts = counts.stdout.strip().split()
                if len(parts) == 2:
                    state.ahead, state.behind = map(int, parts)

            if state.dirty:
                state.status = "Lokale wijzigingen"
                state.detail = "Pull geblokkeerd om je lokale werk te beschermen"
            elif state.ahead and state.behind:
                state.status = "Branches verschillen"
                state.detail = f"{state.ahead} lokaal vooruit, {state.behind} online vooruit"
            elif state.behind:
                state.status = "Update beschikbaar"
                state.detail = f"{state.behind} commit(s) achter"
            elif state.ahead:
                state.status = "Lokale commits"
                state.detail = f"{state.ahead} commit(s) nog niet gepusht"
            else:
                state.status = "Up-to-date"
                state.detail = "Lokaal is gelijk aan GitHub"

        state.manifest = read_manifest(repo)
        if state.manifest and state.manifest.get("name"):
            state.name = str(state.manifest["name"])
        state.preview = find_preview(repo, state.manifest)
    except FileNotFoundError:
        state.error = "Git is niet geïnstalleerd of niet vindbaar"
        state.status = "Git ontbreekt"
    except subprocess.TimeoutExpired:
        state.error = "Git-opdracht duurde te lang"
        state.status = "Timeout"
    except Exception as exc:
        state.error = str(exc)
        state.status = "Fout"
        logging.exception("Inspectie mislukt voor %s", repo)
    return state


def discover_repositories(root: Path) -> list[Path]:
    if not root.exists():
        return []
    found: list[Path] = []
    if (root / ".git").exists():
        found.append(root)
    for child in root.iterdir():
        if child.is_dir() and (child / ".git").exists():
            found.append(child)
    return sorted(found, key=lambda p: p.name.lower())


class TurboGitHubHub(Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("1450x860")
        self.minsize(1100, 680)
        self.configure(bg=BG)

        self.root_path = StringVar(value=self.load_root())
        self.search_text = StringVar()
        self.auto_fetch = BooleanVar(value=True)
        self.status_text = StringVar(value="Klaar")
        self.repo_states: list[RepoState] = []
        self.filtered_states: list[RepoState] = []
        self.selected: RepoState | None = None
        self.result_queue: queue.Queue = queue.Queue()

        self.configure_styles()
        self.build_ui()
        self.search_text.trace_add("write", lambda *_: self.apply_filter())
        self.after(200, self.poll_queue)
        self.after(400, self.refresh_all)

    def configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("Panel2.TFrame", background=PANEL_2)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=BG, foreground=MUTED)
        style.configure("Panel.TLabel", background=PANEL, foreground=TEXT)
        style.configure("PanelMuted.TLabel", background=PANEL, foreground=MUTED)
        style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Segoe UI Semibold", 22))
        style.configure("Header.TLabel", background=PANEL, foreground=TEXT, font=("Segoe UI Semibold", 13))
        style.configure("TButton", background=PANEL_2, foreground=TEXT, padding=(14, 9), borderwidth=0)
        style.map("TButton", background=[("active", "#203045"), ("disabled", "#18212c")], foreground=[("disabled", "#617084")])
        style.configure("Primary.TButton", background=BLUE, foreground="white", padding=(16, 10))
        style.map("Primary.TButton", background=[("active", "#4694f5"), ("disabled", "#244a77")])
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT, rowheight=58, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=PANEL_2, foreground=MUTED, borderwidth=0, font=("Segoe UI Semibold", 9))
        style.map("Treeview", background=[("selected", "#17365d")], foreground=[("selected", "white")])
        style.configure("TEntry", fieldbackground=PANEL, foreground=TEXT, insertcolor=TEXT, bordercolor=BORDER, padding=9)
        style.configure("TCheckbutton", background=BG, foreground=MUTED)

    def build_ui(self) -> None:
        outer = ttk.Frame(self)
        outer.pack(fill="both", expand=True, padx=22, pady=20)

        header = ttk.Frame(outer)
        header.pack(fill="x", pady=(0, 16))
        ttk.Label(header, text="Turbo GitHub Hub", style="Title.TLabel").pack(side="left")
        ttk.Label(header, textvariable=self.status_text, style="Muted.TLabel").pack(side="right", padx=(12, 0))
        ttk.Button(header, text="↻ Alles verversen", style="Primary.TButton", command=self.refresh_all).pack(side="right")

        controls = ttk.Frame(outer)
        controls.pack(fill="x", pady=(0, 14))
        ttk.Entry(controls, textvariable=self.root_path, width=64).pack(side="left", fill="x", expand=True)
        ttk.Button(controls, text="Kies projectmap", command=self.choose_root).pack(side="left", padx=8)
        ttk.Entry(controls, textvariable=self.search_text, width=28).pack(side="left", padx=(8, 0))

        body = ttk.Frame(outer)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        left = ttk.Frame(body, style="Panel.TFrame", padding=1)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        right = ttk.Frame(body, style="Panel.TFrame", padding=20)
        right.grid(row=0, column=1, sticky="nsew")

        columns = ("repository", "branch", "status", "updated")
        self.tree = ttk.Treeview(left, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("repository", text="REPOSITORY")
        self.tree.heading("branch", text="BRANCH")
        self.tree.heading("status", text="STATUS")
        self.tree.heading("updated", text="LAATSTE COMMIT")
        self.tree.column("repository", width=270, anchor="w")
        self.tree.column("branch", width=100, anchor="w")
        self.tree.column("status", width=180, anchor="w")
        self.tree.column("updated", width=250, anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.detail_title = StringVar(value="Selecteer een repository")
        self.detail_path = StringVar(value="")
        self.detail_status = StringVar(value="")
        self.detail_text = StringVar(value="")
        self.detail_meta = StringVar(value="")
        self.preview_text = StringVar(value="Preview verschijnt hier wanneer docs/previews/latest.png bestaat.")

        ttk.Label(right, textvariable=self.detail_title, style="Header.TLabel").pack(anchor="w")
        ttk.Label(right, textvariable=self.detail_path, style="PanelMuted.TLabel", wraplength=480).pack(anchor="w", pady=(3, 18))
        ttk.Separator(right).pack(fill="x", pady=(0, 18))

        ttk.Label(right, text="Status", style="PanelMuted.TLabel").pack(anchor="w")
        ttk.Label(right, textvariable=self.detail_status, style="Header.TLabel").pack(anchor="w", pady=(4, 2))
        ttk.Label(right, textvariable=self.detail_text, style="PanelMuted.TLabel", wraplength=480).pack(anchor="w", pady=(0, 16))
        ttk.Label(right, textvariable=self.detail_meta, style="PanelMuted.TLabel", wraplength=480).pack(anchor="w", pady=(0, 18))

        self.pull_button = ttk.Button(right, text="↓ Veilig pullen", style="Primary.TButton", command=self.pull_selected, state="disabled")
        self.pull_button.pack(fill="x", pady=(0, 8))
        ttk.Button(right, text="Open in Visual Studio Code", command=self.open_vscode).pack(fill="x", pady=4)
        ttk.Button(right, text="Open lokale map", command=self.open_folder).pack(fill="x", pady=4)
        ttk.Button(right, text="Open in GitHub", command=self.open_github).pack(fill="x", pady=4)
        ttk.Button(right, text="Open preview", command=self.open_preview).pack(fill="x", pady=4)

        ttk.Separator(right).pack(fill="x", pady=18)
        ttk.Label(right, text="Projectpreview", style="PanelMuted.TLabel").pack(anchor="w")
        preview_box = ttk.Frame(right, style="Panel2.TFrame", padding=18)
        preview_box.pack(fill="both", expand=True, pady=(8, 0))
        ttk.Label(preview_box, textvariable=self.preview_text, style="Panel.TLabel", wraplength=430, justify="center").pack(expand=True)

        footer = ttk.Frame(outer)
        footer.pack(fill="x", pady=(12, 0))
        ttk.Label(footer, text=f"Logbestand: {LOG_FILE}", style="Muted.TLabel").pack(side="left")
        ttk.Label(footer, text="Pull wordt geblokkeerd bij lokale wijzigingen of diverged branches.", style="Muted.TLabel").pack(side="right")

    def load_root(self) -> str:
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return str(data.get("projects_root", Path.home() / "Projects"))
        except Exception:
            return str(Path.home() / "Projects")

    def save_root(self) -> None:
        CONFIG_FILE.write_text(json.dumps({"projects_root": self.root_path.get()}, indent=2), encoding="utf-8")

    def choose_root(self) -> None:
        chosen = filedialog.askdirectory(initialdir=self.root_path.get() or str(Path.home()))
        if chosen:
            self.root_path.set(chosen)
            self.save_root()
            self.refresh_all()

    def refresh_all(self) -> None:
        root = Path(self.root_path.get()).expanduser()
        if not root.exists():
            self.status_text.set("Kies eerst een geldige projectmap")
            return
        self.save_root()
        self.status_text.set("Repositories controleren…")
        self.tree.delete(*self.tree.get_children())
        self.repo_states = []
        threading.Thread(target=self.refresh_worker, args=(root,), daemon=True).start()

    def refresh_worker(self, root: Path) -> None:
        repos = discover_repositories(root)
        results = [inspect_repo(repo, do_fetch=self.auto_fetch.get()) for repo in repos]
        self.result_queue.put(("refresh_complete", results))

    def poll_queue(self) -> None:
        try:
            while True:
                action, payload = self.result_queue.get_nowait()
                if action == "refresh_complete":
                    self.repo_states = payload
                    self.apply_filter()
                    self.status_text.set(f"{len(payload)} repositories gecontroleerd · {datetime.now():%H:%M}")
                elif action == "pull_complete":
                    ok, message = payload
                    if ok:
                        messagebox.showinfo(APP_NAME, message)
                    else:
                        messagebox.showerror(APP_NAME, message)
                    self.refresh_all()
        except queue.Empty:
            pass
        self.after(200, self.poll_queue)

    def apply_filter(self) -> None:
        query = self.search_text.get().strip().lower()
        self.filtered_states = [
            state for state in self.repo_states
            if not query or query in state.name.lower() or query in state.path.name.lower() or query in state.status.lower()
        ]
        self.tree.delete(*self.tree.get_children())
        for index, state in enumerate(self.filtered_states):
            icon = self.status_icon(state)
            self.tree.insert("", "end", iid=str(index), values=(state.name, state.branch, f"{icon}  {state.status}", state.last_commit or "-"))
        if self.filtered_states:
            self.tree.selection_set("0")
            self.tree.focus("0")
            self.show_state(self.filtered_states[0])
        else:
            self.clear_detail()

    @staticmethod
    def status_icon(state: RepoState) -> str:
        if state.status == "Up-to-date":
            return "●"
        if state.status == "Update beschikbaar":
            return "↓"
        if state.status in {"Lokale wijzigingen", "Branches verschillen"}:
            return "!"
        if state.status == "Lokale commits":
            return "↑"
        return "○"

    def on_select(self, _event=None) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        index = int(selected[0])
        if 0 <= index < len(self.filtered_states):
            self.show_state(self.filtered_states[index])

    def show_state(self, state: RepoState) -> None:
        self.selected = state
        self.detail_title.set(state.name)
        self.detail_path.set(str(state.path))
        self.detail_status.set(state.status)
        self.detail_text.set(state.error or state.detail)
        version = (state.manifest or {}).get("version", "onbekend")
        description = (state.manifest or {}).get("description", "Geen turbo-project.json gevonden")
        self.detail_meta.set(f"Branch: {state.branch}   Versie: {version}\n{description}")
        if state.preview:
            self.preview_text.set(f"Preview gevonden:\n{state.preview}\n\nKlik op ‘Open preview’ om hem volledig te bekijken.")
        else:
            self.preview_text.set("Geen preview gevonden. Voeg docs/previews/latest.png toe aan deze repository.")
        self.pull_button.configure(state="normal" if state.can_pull else "disabled")

    def clear_detail(self) -> None:
        self.selected = None
        self.detail_title.set("Geen repository gevonden")
        self.detail_path.set("")
        self.detail_status.set("")
        self.detail_text.set("")
        self.detail_meta.set("")
        self.pull_button.configure(state="disabled")

    def pull_selected(self) -> None:
        state = self.selected
        if not state or not state.can_pull:
            messagebox.showwarning(APP_NAME, "Veilig pullen is voor deze repository geblokkeerd.")
            return
        self.status_text.set(f"{state.name} pullen…")
        threading.Thread(target=self.pull_worker, args=(state,), daemon=True).start()

    def pull_worker(self, state: RepoState) -> None:
        logging.info("Pull gestart voor %s", state.path)
        result = run_git(state.path, "pull", "--ff-only", timeout=120)
        if result.returncode == 0:
            self.result_queue.put(("pull_complete", (True, f"{state.name} is bijgewerkt.\n\n{result.stdout.strip()}")))
        else:
            logging.error("Pull mislukt voor %s: %s", state.path, result.stderr)
            self.result_queue.put(("pull_complete", (False, f"Pull mislukt:\n\n{result.stderr.strip()}")))

    def open_vscode(self) -> None:
        if not self.selected:
            return
        try:
            subprocess.Popen(["code", str(self.selected.path)], creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        except FileNotFoundError:
            messagebox.showerror(APP_NAME, "Visual Studio Code of het commando ‘code’ is niet gevonden.")

    def open_folder(self) -> None:
        if not self.selected:
            return
        if os.name == "nt":
            os.startfile(self.selected.path)  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", str(self.selected.path)])

    def open_github(self) -> None:
        if self.selected and self.selected.remote_url:
            webbrowser.open(self.selected.remote_url)
        else:
            messagebox.showwarning(APP_NAME, "Geen GitHub origin gevonden.")

    def open_preview(self) -> None:
        if self.selected and self.selected.preview:
            if os.name == "nt":
                os.startfile(self.selected.preview)  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["xdg-open", str(self.selected.preview)])
        else:
            messagebox.showwarning(APP_NAME, "Deze repository heeft nog geen preview.")


if __name__ == "__main__":
    TurboGitHubHub().mainloop()
