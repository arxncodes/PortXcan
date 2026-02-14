import asyncio
import json
import csv
import os
import subprocess
import sys
from datetime import datetime
import time
import webbrowser

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import (
    Progress, SpinnerColumn, BarColumn,
    TextColumn, TimeElapsedColumn, MofNCompleteColumn,
)
from rich.text import Text
from rich.align import Align
from rich.rule import Rule
from rich.prompt import Prompt, IntPrompt
from rich import box

from portxcan.async_scanner import AsyncPortScanner
from portxcan.utils import expand_target

# ─── Globals ──────────────────────────────────────
console = Console()
WEB_PORT = 8000
_web_process = None
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

LOGO = r"""
                        ▄▄▄   ▄▄▄
                   ██   ████▄████
 ████▄ ▄███▄ ████▄ ▀██▀▀  ▀█████▀  ▄████  ▀▀█▄ ████▄
 ██ ██ ██ ██ ██ ▀▀  ██   ▄███████▄ ██    ▄█▀██ ██ ██
 ████▀ ▀███▀ ██     ██   ███▀ ▀███ ▀████ ▀█▄██ ██ ██
 ██
 ▀▀
"""


# ─── Web server ───────────────────────────────────
def start_web_server():
    """Start uvicorn in the background."""
    global _web_process
    if _web_process is not None and _web_process.poll() is None:
        return

    try:
        _web_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "web.app:app",
             "--host", "127.0.0.1", "--port", str(WEB_PORT)],
            cwd=PROJECT_ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        time.sleep(2)
        if _web_process.poll() is not None:
            err = _web_process.stderr.read().decode(errors="ignore").strip()
            console.print(f"[bold red]✗[/] Web server failed to start.")
            if err:
                console.print(f"[dim red]  {err}[/]")
            _web_process = None
    except Exception as e:
        console.print(f"[bold red]✗[/] Could not start Web UI: {e}")
        _web_process = None


# ─── Banner ───────────────────────────────────────
def banner():
    console.clear()
    logo_text = Text(LOGO)
    logo_text.stylize("bold bright_cyan")
    panel = Panel(
        Align.center(logo_text),
        title="[bold bright_blue]⚡ PortXcan[/]",
        subtitle="[dim]Advanced Network Port Scanner • v1.0 • by arxncodes[/]",
        border_style="bright_blue",
        box=box.DOUBLE_EDGE,
        padding=(0, 4),
    )
    console.print(panel)

    if _web_process and _web_process.poll() is None:
        console.print(
            Align.center(
                Text(f"🌐 Web UI running → http://127.0.0.1:{WEB_PORT}", style="dim green")
            )
        )
    console.print()


# ─── Menu display ─────────────────────────────────
def show_menu():
    items = [
        ("1", "Single Host Scan", "Scan a single IP or hostname"),
        ("2", "CIDR Range Scan",  "Scan an entire subnet"),
        ("3", "Open Web UI",      f"Launch browser → localhost:{WEB_PORT}"),
        ("4", "Exit",             "Quit PortXcan"),
    ]
    for num, title, desc in items:
        console.print(f"  [bold cyan]{num}[/]  ║  [bold white]{title}[/]  [dim]— {desc}[/]")
    console.print()


# ─── Input helpers ────────────────────────────────
def get_port_range():
    try:
        start = IntPrompt.ask("  [cyan]Start port[/]", default=1, console=console)
        end = IntPrompt.ask("  [cyan]End port[/]",   default=1024, console=console)
        if start < 1 or end > 65535 or start > end:
            console.print("[red]  ✗ Invalid range (1-65535, start ≤ end)[/]")
            return get_port_range()
        return start, end
    except ValueError:
        console.print("[red]  ✗ Enter valid numbers[/]")
        return get_port_range()


# ─── Service colour helper ────────────────────────
def svc_style(service: str) -> str:
    s = service.lower()
    if s in ("ssh", "ssh-alt", "telnet", "rdp", "vnc", "vnc-1", "vnc-2"):
        return "bright_cyan"
    if "http" in s:
        return "bright_green"
    if s in ("smb", "netbios-ssn", "netbios-ns", "msrpc", "nfs"):
        return "bright_red"
    if s in ("mysql", "postgresql", "mssql", "mongodb", "redis", "oracle", "cassandra"):
        return "bright_magenta"
    if s in ("smtp", "pop3", "imap", "smtps", "imaps", "pop3s"):
        return "bright_yellow"
    if s in ("ftp", "ftp-data", "sftp", "tftp"):
        return "cyan"
    if s in ("dns", "ldap", "ldaps", "kerberos"):
        return "bright_blue"
    return "dim"


# ─── Results table ────────────────────────────────
def show_results(results):
    if not results:
        console.print("[yellow]  No open ports detected.[/]")
        return

    hosts = {}
    for r in results:
        hosts.setdefault(r["host"], []).append(r)

    for host, entries in hosts.items():
        table = Table(
            title=f"[bold cyan]🖥️  {host}[/]",
            box=box.ROUNDED,
            border_style="bright_blue",
            header_style="bold bright_blue",
            show_lines=False,
            padding=(0, 2),
            expand=True,
        )
        table.add_column("Port",    style="cyan",  justify="right", width=8)
        table.add_column("Service", min_width=14)
        table.add_column("Banner",  style="dim",   ratio=1)

        for e in sorted(entries, key=lambda x: x["port"]):
            st = svc_style(e["service"])
            ban = e["banner"] if e["banner"] != "Not disclosed" else "—"
            table.add_row(str(e["port"]), f"[{st}]{e['service']}[/]", ban)

        console.print(table)
        console.print()


# ─── Export ───────────────────────────────────────
def export_json(results):
    name = f"portxcan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(name, "w") as f:
        json.dump(results, f, indent=4)
    console.print(f"  [green]✓[/] Saved → [cyan]{name}[/]")


def export_csv(results):
    name = f"portxcan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(name, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["host", "port", "service", "banner"])
        for r in results:
            writer.writerow([r["host"], r["port"], r["service"], r["banner"]])
    console.print(f"  [green]✓[/] Saved → [cyan]{name}[/]")


# ─── Post-scan menu ──────────────────────────────
def post_scan_menu(results):
    while True:
        console.print()
        console.print(Rule("[bold]Post-Scan Options[/]", style="blue"))
        console.print("  [cyan]1[/]  ║  View results table")
        console.print("  [cyan]2[/]  ║  Export to JSON")
        console.print("  [cyan]3[/]  ║  Export to CSV")
        console.print("  [cyan]4[/]  ║  Return to main menu")
        console.print()

        choice = Prompt.ask("  [bold]Select[/]", choices=["1", "2", "3", "4"],
                            default="4", console=console)

        if choice == "1":
            show_results(results)
        elif choice == "2":
            export_json(results)
        elif choice == "3":
            export_csv(results)
        elif choice == "4":
            break


# ─── Scan logic ───────────────────────────────────
def run_scan(target):
    start, end = get_port_range()

    try:
        hosts = expand_target(target)
    except ValueError as e:
        console.print(f"[bold red]  ✗ Error:[/] {e}")
        return

    console.print()
    total_ports = len(hosts) * (end - start + 1)
    results = []
    t0 = time.time()

    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40, complete_style="bright_cyan", finished_style="green"),
        MofNCompleteColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:
        for host in hosts:
            task = progress.add_task(f"[cyan]{host}[/]", total=end - start + 1)

            def make_cb(t):
                def _cb(scanned, total):
                    progress.advance(t)
                return _cb

            scanner = AsyncPortScanner(
                target=host,
                start_port=start,
                end_port=end,
                timeout=1,
                progress_cb=make_cb(task),
            )
            host_results = asyncio.run(scanner.run())
            for r in host_results:
                r["host"] = host
                results.append(r)

    elapsed = time.time() - t0
    speed = total_ports / elapsed if elapsed > 0 else 0

    # ── Summary ──
    console.print()
    summary = Table(box=box.SIMPLE_HEAD, show_header=False, border_style="blue",
                    padding=(0, 2), expand=True)
    summary.add_column(ratio=1)
    summary.add_column(ratio=1)
    summary.add_column(ratio=1)
    summary.add_column(ratio=1)
    summary.add_column(ratio=1)
    summary.add_row(
        f"[bold]Hosts[/]  [cyan]{len(hosts)}[/]",
        f"[bold]Ports[/]  [cyan]{start}–{end}[/]",
        f"[bold]Open[/]   [green]{len(results)}[/]",
        f"[bold]Time[/]   [yellow]{elapsed:.1f}s[/]",
        f"[bold]Speed[/]  [dim]{speed:.0f} p/s[/]",
    )
    console.print(Panel(summary, title="[bold]Scan Summary[/]", border_style="blue",
                        box=box.ROUNDED))

    if results:
        console.print()
        show_results(results)

    post_scan_menu(results)


# ─── Main menu ────────────────────────────────────
def menu():
    start_web_server()

    while True:
        banner()
        show_menu()

        choice = Prompt.ask("  [bold bright_blue]Select option[/]",
                            choices=["1", "2", "3", "4"], console=console)

        if choice == "1":
            target = Prompt.ask("  [cyan]Enter IP / Hostname[/]", console=console)
            run_scan(target.strip())

        elif choice == "2":
            target = Prompt.ask("  [cyan]Enter CIDR (e.g. 192.168.1.0/24)[/]",
                                console=console)
            run_scan(target.strip())

        elif choice == "3":
            if _web_process is None or _web_process.poll() is not None:
                console.print("  [yellow]⟳ Restarting web server...[/]")
                start_web_server()
                time.sleep(1)

            if _web_process and _web_process.poll() is None:
                webbrowser.open(f"http://127.0.0.1:{WEB_PORT}/")
                console.print("  [green]✓[/] Web UI opened in browser")
            else:
                console.print("  [red]✗ Web server failed to start[/]")
            Prompt.ask("\n  [dim]Press Enter to continue[/]", default="", console=console)

        elif choice == "4":
            if _web_process and _web_process.poll() is None:
                _web_process.terminate()
            console.print()
            console.print(Panel(
                Align.center(Text("Thanks for using PortXcan ⚡", style="bold bright_cyan")),
                border_style="blue", box=box.ROUNDED
            ))
            break


# ─── Entry ────────────────────────────────────────
if __name__ == "__main__":
    menu()
