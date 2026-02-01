import asyncio
import json
import csv
import os
import subprocess
from datetime import datetime
import time
import webbrowser
from portxcan.async_scanner import AsyncPortScanner
from portxcan.utils import expand_target


# ---------------------------
# ANSI Colors (Bluish Theme)
# ---------------------------
GREEN = "\033[38;5;39m"
BRIGHT = "\033[1m"
YELLOW = "\033[38;5;214m"
RED = "\033[38;5;196m"
BLUE = "\033[38;5;27m"
RESET = "\033[0m"

os.system("")


# ---------------------------
# Helpers
# ---------------------------
def clear():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input(YELLOW + "\nPress Enter to continue..." + RESET)


def banner():
    clear()

    logo = [
        "                                                    ",
        "                        ▄▄▄   ▄▄▄                   ",
        "                   ██   ████▄████                   ",
        "████▄ ▄███▄ ████▄ ▀██▀▀  ▀█████▀  ▄████  ▀▀█▄ ████▄ ",
        "██ ██ ██ ██ ██ ▀▀  ██   ▄███████▄ ██    ▄█▀██ ██ ██ ",
        "████▀ ▀███▀ ██     ██   ███▀ ▀███ ▀████ ▀█▄██ ██ ██ ",
        "██                                                  ",
        "▀▀                                                  ",
    ]

    gradient = [
        "\033[38;5;17m",  # deep navy
        "\033[38;5;18m",
        "\033[38;5;19m",
        "\033[38;5;20m",
        "\033[38;5;21m",
        "\033[38;5;27m",
        "\033[38;5;33m",
        "\033[1;97m",      # bright white
    ]

    for line, color in zip(logo, gradient):
        print(color + line + RESET)

    print("\n" + BLUE + BRIGHT + "Made with ❤️ by arxncodes | Advanced Network Port Scanner | V1.0" + RESET)
    print("\033[38;5;240m" + BRIGHT + "_" * 90 + RESET + "\n")


def get_port_range():
    try:
        start = int(input(GREEN + "Start port (default 1): " + RESET) or 1)
        end = int(input(GREEN + "End port (default 1024): " + RESET) or 1024)
        return start, end
    except ValueError:
        print(RED + "[ERROR] Invalid port range." + RESET)
        return get_port_range()


# ---------------------------
# Export Functions
# ---------------------------
def export_json(results):
    filename = f"portxcan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=4)
    print(GREEN + f"[+] Results saved to {filename}" + RESET)


def export_csv(results):
    filename = f"portxcan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["host", "port", "service", "banner"])
        for r in results:
            writer.writerow([r["host"], r["port"], r["service"], r["banner"]])
    print(GREEN + f"[+] Results saved to {filename}" + RESET)


# ---------------------------
# Post Scan Menu
# ---------------------------
def post_scan_menu(results):
    while True:
        print("\nScan completed.")
        print("1. View results")
        print("2. Export to JSON")
        print("3. Export to CSV")
        print("4. Return to Main Menu")

        choice = input("Select option: ").strip()

        if choice == "1":
            for r in results:
                print(
                    GREEN +
                    f"[OPEN] {r['host']}:{r['port']} | "
                    f"{r['service']} | {r['banner']}" +
                    RESET
                )
        elif choice == "2":
            export_json(results)
        elif choice == "3":
            export_csv(results)
        elif choice == "4":
            break
        else:
            print(RED + "Invalid choice." + RESET)


# ---------------------------
# Scan Logic
# ---------------------------
def run_scan(target):
    start, end = get_port_range()

    try:
        hosts = expand_target(target)
    except ValueError as e:
        print(RED + f"[ERROR] {e}" + RESET)
        return

    results = []

    print(GREEN + "\n[+] Scan started...\n" + RESET)

    for host in hosts:
        scanner = AsyncPortScanner(
            target=host,
            start_port=start,
            end_port=end,
            timeout=1
        )
        host_results = asyncio.run(scanner.run())

        if not host_results:
            print(YELLOW + f"[INFO] No open ports on {host}" + RESET)
        else:
            for r in host_results:
                r["host"] = host
                results.append(r)

    post_scan_menu(results)


# ---------------------------
# Main Menu (PRIMARY INTERFACE)
# ---------------------------
def menu():
    while True:
        banner()
        option_colors = [BLUE, BLUE, BLUE, BLUE]
        options = ["1. Single Host Scan", "2. CIDR Scan", "3. Launch Web UI (Optional)", "4. Exit"]
        for col, opt in zip(option_colors, options):
            print(col + opt + RESET)

        choice = input(BRIGHT + "\nSelect option: " + RESET).strip()

        if choice == "1":
            target = input(GREEN + "Enter IP / Hostname: " + RESET).strip()
            run_scan(target)
            pause()
        elif choice == "2":
            target = input(GREEN + "Enter CIDR (e.g. 192.168.1.0/24): " + RESET).strip()
            run_scan(target)
            pause()
        elif choice == "3":
            print(GREEN + "[+] Starting PortXcan Web UI..." + RESET)

            subprocess.Popen(
                ["uvicorn", "web.app:app"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # give uvicorn time to start
            time.sleep(2)

            # open browser to HOME page
            webbrowser.open("http://127.0.0.1:8000/")

            print(GREEN + "[+] Web UI opened in browser." + RESET)
            pause()
        elif choice == "4":
            print(GREEN + "Exiting PortXcan." + RESET)
            break
        else:
            print(RED + "Invalid option." + RESET)
            pause()


# ---------------------------
# Entry Point
# ---------------------------
if __name__ == "__main__":
    menu()
