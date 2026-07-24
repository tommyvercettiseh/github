from __future__ import annotations

import json
import os
import subprocess
import threading
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from tkinter import Canvas, Frame, Label, Button, Entry, StringVar, Tk, filedialog, messagebox

APP_NAME = "GitHub Hub"
APP_VERSION = "0.2.0"
APP_DIR = Path(__file__).resolve().parent
CONFIG_DIR = Path(os.getenv("APPDATA", Path.home())) / "TurboGitHubHub"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_DIR = APP_DIR / "logs"

BG = "#f7f8fb"
CARD = "#ffffff"
TEXT = "#16181d"
MUTED = "#697386"
BORDER = "#e2e5ec"
PURPLE = "#6847f5"
GREEN = "#22a866"
ORANGE = "#ef8b17"
RED = "#e34a4a"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class Repo:
    name: str
    description: str
    url: str
    clone_url: str
    branch: str
    private: bool
    local_path: Path | None = None
    status: str = "Online"
    detail: str = "Nog niet lokaal gedownload"
    can_pull: bool = False
    dirty: bool = False


def run(command: list[str], cwd: Path | None = None, timeout: int = 90) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=timeout,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"projects_root": str(Path.home() / "GitHub")}


def save_config(data: dict) -> None:
    CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def gh_available() -> bool:
    try:
        return run(["gh", "--version"], timeout=10).returncode == 0
    except FileNotFoundError:
        return False


def gh_logged_in() -> bool:
    if not gh_available():
        return False
    return run(["gh", "auth", "status"], timeout=20).returncode == 0


def inspect_local(repo: Repo) -> Repo:
    path = repo.local_path
    if not path:
        return repo
    try:
        fetch = run(["git", "fetch", "--prune"], cwd=path)
        if fetch.returncode != 0:
            repo.status = "Controle mislukt"
            repo.detail = fetch.stderr.strip() or "Git fetch mislukt"
            return repo

        dirty = run(["git", "status", "--porcelain"], cwd=path)
        repo.dirty = bool(dirty.stdout.strip())

        upstream = run(["git", "rev-parse", "--abbrev-ref", "@{u}"], cwd=path)
        if upstream.returncode != 0:
            repo.status = "Geen upstream"
            repo.detail = "Lokale branch is niet aan GitHub gekoppeld"
            return repo

        counts = run(["git", "rev-list", "--left-right", "--count", "HEAD...@{u}"], cwd=path)
        ahead, behind = (0, 0)
        if counts.returncode == 0:
            parts = counts.stdout.strip().split()
            if len(parts) == 2:
                ahead, behind = map(int, parts)

        if repo.dirty:
            repo.status = "Lokale wijzigingen"
            repo.detail = "Pull geblokkeerd om je werk te beschermen"
        elif ahead and behind:
            repo.status = "Branches verschillen"
            repo.detail = f"{ahead} lokaal vooruit, {behind} online vooruit"
        elif behind:
            repo.status = "Update beschikbaar"
            repo.detail = f"{behind} commit(s) achter"
            repo.can_pull = True
        elif ahead:
            repo.status = "Lokale commits"
            repo.detail = f"{ahead} commit(s) nog niet gepusht"
        else:
            repo.status = "Up-to-date"
            repo.detail = "Gelijk aan de laatste GitHub-commit"
    except Exception as exc:
        repo.status = "Fout"
        repo.detail = str(exc)
    return repo


class GitHubHub(Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("1280x820")
        self.minsize(900, 620)
        self.configure(bg=BG)

        self.config_data = load_config()
        self.projects_root = Path(self.config_data["projects_root"])
        self.search = StringVar()
        self.account_text = StringVar(value="Niet ingelogd")
        self.status_text = StringVar(value="Klaar")
        self.repos: list[Repo] = []

        self.build_ui()
        self.search.trace_add("write", lambda *_: self.render_cards())
        self.after(250, self.startup)

    def build_ui(self) -> None:
        top = Frame(self, bg=BG)
        top.pack(fill="x", padx=28, pady=(24, 18))

        Label(top, text="GitHub Hub", bg=BG, fg=TEXT, font=("Segoe UI Semibold", 24)).pack(side="left")
        Label(top, textvariable=self.status_text, bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(side="right", padx=(12, 0))
        Button(top, text="↻", command=self.refresh, bg=CARD, fg=TEXT, relief="flat", bd=0, font=("Segoe UI", 14), padx=14, pady=7).pack(side="right")

        account = Frame(self, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        account.pack(fill="x", padx=28, pady=(0, 16))
        Label(account, textvariable=self.account_text, bg=CARD, fg=TEXT, font=("Segoe UI Semibold", 11)).pack(side="left", padx=18, pady=14)
        Button(account, text="Projectmap", command=self.choose_root, bg=CARD, fg=MUTED, relief="flat", bd=0, font=("Segoe UI", 10)).pack(side="right", padx=8)
        self.login_button = Button(account, text="Login met GitHub", command=self.login, bg=PURPLE, fg="white", activebackground="#5737e3", activeforeground="white", relief="flat", bd=0, font=("Segoe UI Semibold", 10), padx=18, pady=9)
        self.login_button.pack(side="right", padx=12, pady=9)

        search_wrap = Frame(self, bg=BG)
        search_wrap.pack(fill="x", padx=28, pady=(0, 14))
        Entry(search_wrap, textvariable=self.search, bg=CARD, fg=TEXT, insertbackground=TEXT, relief="flat", highlightbackground=BORDER, highlightthickness=1, font=("Segoe UI", 11)).pack(fill="x", ipady=10)

        container = Frame(self, bg=BG)
        container.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        self.canvas = Canvas(container, bg=BG, highlightthickness=0)
        self.scrollbar = __import__("tkinter").Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.cards = Frame(self.canvas, bg=BG)
        self.cards.bind("<Configure>", lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.canvas_window, width=e.width))
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-e.delta / 120), "units"))

    def startup(self) -> None:
        if gh_logged_in():
            self.refresh()
        else:
            self.account_text.set("Log in om je repositories te bekijken")
            if not gh_available():
                self.login_button.configure(text="Installeer GitHub CLI")

    def choose_root(self) -> None:
        selected = filedialog.askdirectory(initialdir=str(self.projects_root), title="Kies de map voor je GitHub-projecten")
        if selected:
            self.projects_root = Path(selected)
            self.config_data["projects_root"] = selected
            save_config(self.config_data)
            self.refresh()

    def login(self) -> None:
        if not gh_available():
            webbrowser.open("https://cli.github.com/")
            messagebox.showinfo("GitHub CLI nodig", "Installeer GitHub CLI en start deze launcher daarna opnieuw.")
            return

        self.status_text.set("GitHub-login openen...")
        threading.Thread(target=self._login_worker, daemon=True).start()

    def _login_worker(self) -> None:
        subprocess.run(["gh", "auth", "login", "--web", "--git-protocol", "https"])
        self.after(0, self.refresh)

    def refresh(self) -> None:
        if not gh_logged_in():
            self.account_text.set("Log in om je repositories te bekijken")
            return
        self.status_text.set("Repositories laden...")
        threading.Thread(target=self._refresh_worker, daemon=True).start()

    def _refresh_worker(self) -> None:
        result = run([
            "gh", "repo", "list", "--limit", "500",
            "--json", "name,description,url,sshUrl,defaultBranchRef,isPrivate,owner"
        ], timeout=120)
        if result.returncode != 0:
            self.after(0, lambda: messagebox.showerror("GitHub fout", result.stderr.strip() or "Repositories ophalen mislukt"))
            self.after(0, lambda: self.status_text.set("Ophalen mislukt"))
            return

        profile = run(["gh", "api", "user", "--jq", ".login"], timeout=30)
        username = profile.stdout.strip() or "GitHub-account"
        raw = json.loads(result.stdout or "[]")
        repos: list[Repo] = []
        self.projects_root.mkdir(parents=True, exist_ok=True)

        for item in raw:
            branch_data = item.get("defaultBranchRef") or {}
            name = item["name"]
            local = self.projects_root / name
            repo = Repo(
                name=name,
                description=item.get("description") or "Geen omschrijving",
                url=item.get("url") or "",
                clone_url=item.get("url", "") + ".git",
                branch=branch_data.get("name") or "main",
                private=bool(item.get("isPrivate")),
                local_path=local if (local / ".git").exists() else None,
            )
            if repo.local_path:
                repo = inspect_local(repo)
            repos.append(repo)

        repos.sort(key=lambda r: (r.local_path is None, r.name.lower()))
        self.repos = repos
        self.after(0, lambda: self.account_text.set(f"Ingelogd als {username}  •  {len(repos)} repositories"))
        self.after(0, self.render_cards)
        self.after(0, lambda: self.status_text.set("Bijgewerkt"))

    def render_cards(self) -> None:
        for child in self.cards.winfo_children():
            child.destroy()

        needle = self.search.get().strip().lower()
        shown = [r for r in self.repos if not needle or needle in r.name.lower() or needle in r.description.lower()]
        if not shown:
            Label(self.cards, text="Geen repositories gevonden", bg=BG, fg=MUTED, font=("Segoe UI", 12)).pack(pady=50)
            return

        for index, repo in enumerate(shown):
            card = Frame(self.cards, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
            card.grid(row=index // 3, column=index % 3, sticky="nsew", padx=7, pady=7)
            self.cards.grid_columnconfigure(index % 3, weight=1, uniform="cards")

            head = Frame(card, bg=CARD)
            head.pack(fill="x", padx=18, pady=(17, 6))
            Label(head, text=repo.name, bg=CARD, fg=TEXT, font=("Segoe UI Semibold", 13), anchor="w").pack(side="left")
            Label(head, text="Private" if repo.private else "Public", bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(side="right")

            Label(card, text=repo.description, bg=CARD, fg=MUTED, font=("Segoe UI", 9), anchor="w", justify="left", wraplength=320).pack(fill="x", padx=18)

            color = GREEN if repo.status == "Up-to-date" else ORANGE if repo.status in {"Update beschikbaar", "Online"} else RED
            Label(card, text=f"●  {repo.status}", bg=CARD, fg=color, font=("Segoe UI Semibold", 10), anchor="w").pack(fill="x", padx=18, pady=(18, 2))
            Label(card, text=repo.detail, bg=CARD, fg=MUTED, font=("Segoe UI", 9), anchor="w", wraplength=320).pack(fill="x", padx=18)
            Label(card, text=f"⑂  {repo.branch}", bg=CARD, fg=MUTED, font=("Segoe UI", 9), anchor="w").pack(fill="x", padx=18, pady=(8, 12))

            actions = Frame(card, bg=CARD)
            actions.pack(fill="x", padx=14, pady=(0, 14))
            if repo.local_path is None:
                Button(actions, text="Download", command=lambda r=repo: self.clone_repo(r), bg=PURPLE, fg="white", relief="flat", bd=0, padx=13, pady=8).pack(side="left", padx=4)
            elif repo.can_pull:
                Button(actions, text="Pull", command=lambda r=repo: self.pull_repo(r), bg=PURPLE, fg="white", relief="flat", bd=0, padx=16, pady=8).pack(side="left", padx=4)
            Button(actions, text="Open", command=lambda r=repo: self.open_repo(r), bg=BG, fg=TEXT, relief="flat", bd=0, padx=16, pady=8).pack(side="left", padx=4)
            Button(actions, text="GitHub", command=lambda r=repo: webbrowser.open(r.url), bg=BG, fg=TEXT, relief="flat", bd=0, padx=14, pady=8).pack(side="left", padx=4)

    def clone_repo(self, repo: Repo) -> None:
        target = self.projects_root / repo.name
        self.status_text.set(f"{repo.name} downloaden...")
        threading.Thread(target=self._clone_worker, args=(repo, target), daemon=True).start()

    def _clone_worker(self, repo: Repo, target: Path) -> None:
        result = run(["gh", "repo", "clone", repo.url, str(target)], timeout=300)
        if result.returncode != 0:
            self.after(0, lambda: messagebox.showerror("Download mislukt", result.stderr.strip()))
        self.after(0, self.refresh)

    def pull_repo(self, repo: Repo) -> None:
        if not repo.local_path:
            return
        self.status_text.set(f"{repo.name} pullen...")
        threading.Thread(target=self._pull_worker, args=(repo,), daemon=True).start()

    def _pull_worker(self, repo: Repo) -> None:
        result = run(["git", "pull", "--ff-only"], cwd=repo.local_path, timeout=180)
        if result.returncode != 0:
            self.after(0, lambda: messagebox.showerror("Pull mislukt", result.stderr.strip() or result.stdout.strip()))
        self.after(0, self.refresh)

    def open_repo(self, repo: Repo) -> None:
        if repo.local_path:
            try:
                subprocess.Popen(["code", str(repo.local_path)])
            except FileNotFoundError:
                os.startfile(repo.local_path) if os.name == "nt" else None
        else:
            webbrowser.open(repo.url)


if __name__ == "__main__":
    GitHubHub().mainloop()
