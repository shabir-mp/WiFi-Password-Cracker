"""
FISARD - WiFi Security & Router Diagnostics
Cross-platform WiFi profile scanner with export, filter, and network details.
Author: Shabir Mahfudz Prahono
"""

import subprocess
import platform
import sys
import os
import csv
import json
import re
from datetime import datetime

# ──────────────────────────────────────────────
# Dependency Check
# ──────────────────────────────────────────────

def check_dependencies():
    try:
        import colorama
    except ImportError:
        print("[!] 'colorama' not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
        print("[+] colorama installed successfully.\n")

check_dependencies()

from colorama import init, Fore, Style
init(autoreset=True)

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────

OS = platform.system()  # "Windows", "Linux", "Darwin"

BANNER = r"""
      XXXXXXXXXX   XX    XXXXXXXXX     $$$$$$$$    $$$$$$$$$$   $$$$$$$$$        
      XX           XX   XX           $$$$    $$$  $$$      $$$  $$$     $$$      
      XX X XXX$    XX   XX$X        $$$      $$$  $$$      $$$  $$$      $$$     
      XX XXXXXX    XX    $XXXXXXXX$ $$$      $$$  $$$$$$$$$$$   $$$      $$$     
      XX           XX            XX $$$$$$$$$$$$  $$$  $$$$     $$$      $$      
      XX           XX   XXXXXXXXXX  $$$      $$$  $$$    $$$$   $$$$$$$$$$  
"""

# ──────────────────────────────────────────────
# Platform-specific Parsers
# ──────────────────────────────────────────────

def get_profiles_windows():
    """Return list of saved WiFi profile names on Windows."""
    try:
        raw = subprocess.check_output(
            ["netsh", "wlan", "show", "profiles"],
            stderr=subprocess.DEVNULL
        ).decode("utf-8", errors="replace")
    except subprocess.CalledProcessError:
        return []
    return [
        line.split(":")[1].strip()
        for line in raw.splitlines()
        if "All User Profile" in line
    ]

def get_profile_details_windows(profile_name):
    """Return dict with password, encryption, band info for a Windows WiFi profile."""
    try:
        raw = subprocess.check_output(
            ["netsh", "wlan", "show", "profile", profile_name, "key=clear"],
            stderr=subprocess.DEVNULL
        ).decode("utf-8", errors="replace")
    except subprocess.CalledProcessError:
        return {"password": "", "encryption": "N/A", "auth": "N/A", "band": "N/A"}

    details = {"password": "", "encryption": "N/A", "auth": "N/A", "band": "N/A"}
    for line in raw.splitlines():
        if "Key Content" in line:
            details["password"] = line.split(":", 1)[1].strip()
        elif "Cipher" in line:
            details["encryption"] = line.split(":", 1)[1].strip()
        elif "Authentication" in line:
            details["auth"] = line.split(":", 1)[1].strip()
        elif "Radio type" in line:
            val = line.split(":", 1)[1].strip()
            details["band"] = val if val else "N/A"
    return details

def get_profiles_linux():
    """Return list of saved WiFi profile names on Linux (NetworkManager)."""
    nm_dir = "/etc/NetworkManager/system-connections/"
    if not os.path.exists(nm_dir):
        return []
    return [
        f.replace(".nmconnection", "")
        for f in os.listdir(nm_dir)
        if f.endswith(".nmconnection") or "." not in f
    ]

def get_profile_details_linux(profile_name):
    """Return dict with password and encryption info for a Linux WiFi profile."""
    nm_dir = "/etc/NetworkManager/system-connections/"
    details = {"password": "", "encryption": "N/A", "auth": "N/A", "band": "N/A"}

    # Try both with and without .nmconnection extension
    candidates = [
        os.path.join(nm_dir, profile_name),
        os.path.join(nm_dir, profile_name + ".nmconnection"),
    ]
    filepath = next((c for c in candidates if os.path.exists(c)), None)
    if not filepath:
        return details

    try:
        with open(filepath, "r") as f:
            content = f.read()
        for line in content.splitlines():
            if line.startswith("psk="):
                details["password"] = line.split("=", 1)[1].strip()
            elif line.startswith("key-mgmt="):
                details["auth"] = line.split("=", 1)[1].strip().upper()
            elif line.startswith("pairwise="):
                details["encryption"] = line.split("=", 1)[1].strip().upper()
            elif line.startswith("band="):
                val = line.split("=", 1)[1].strip()
                details["band"] = "5 GHz" if val == "a" else "2.4 GHz" if val == "bg" else val
    except PermissionError:
        details["password"] = "[Permission Denied - run as root]"
    return details

def get_profiles_macos():
    """Return list of saved WiFi profile names on macOS."""
    try:
        raw = subprocess.check_output(
            ["networksetup", "-listpreferredwirelessnetworks", "en0"],
            stderr=subprocess.DEVNULL
        ).decode("utf-8", errors="replace")
        return [
            line.strip()
            for line in raw.splitlines()
            if line.strip() and "Preferred networks" not in line
        ]
    except subprocess.CalledProcessError:
        return []

def get_profile_details_macos(profile_name):
    """Return dict with password for a macOS WiFi profile via Keychain."""
    details = {"password": "", "encryption": "N/A", "auth": "N/A", "band": "N/A"}
    try:
        raw = subprocess.check_output(
            ["security", "find-generic-password", "-wa", profile_name],
            stderr=subprocess.DEVNULL
        ).decode("utf-8", errors="replace").strip()
        details["password"] = raw
    except subprocess.CalledProcessError:
        details["password"] = ""
    return details

# ──────────────────────────────────────────────
# Unified Scanner
# ──────────────────────────────────────────────

def scan_all_profiles():
    """Scan all saved WiFi profiles and return list of dicts."""
    results = []

    if OS == "Windows":
        profiles = get_profiles_windows()
        for name in profiles:
            details = get_profile_details_windows(name)
            results.append({"name": name, **details})

    elif OS == "Linux":
        profiles = get_profiles_linux()
        for name in profiles:
            details = get_profile_details_linux(name)
            results.append({"name": name, **details})

    elif OS == "Darwin":
        profiles = get_profiles_macos()
        for name in profiles:
            details = get_profile_details_macos(name)
            results.append({"name": name, **details})

    else:
        print(Fore.RED + f"[!] Unsupported OS: {OS}")

    return results

# ──────────────────────────────────────────────
# Display
# ──────────────────────────────────────────────

def print_table(profiles):
    """Print results in a colorized table."""
    if not profiles:
        print(Fore.YELLOW + "\n  No profiles to display.\n")
        return

    col_w = [30, 22, 10, 10, 8]
    header = (
        f"{'WiFi Name':<{col_w[0]}} | "
        f"{'Password':<{col_w[1]}} | "
        f"{'Auth':<{col_w[2]}} | "
        f"{'Encryption':<{col_w[3]}} | "
        f"{'Band':<{col_w[4]}}"
    )
    sep = "-" * len(header)

    print(Fore.CYAN + Style.BRIGHT + "\n" + sep)
    print(Fore.CYAN + Style.BRIGHT + header)
    print(Fore.CYAN + Style.BRIGHT + sep)

    for p in profiles:
        name = p["name"][:col_w[0]]
        pwd  = p["password"][:col_w[1]] if p["password"] else ""
        auth = p["auth"][:col_w[2]]
        enc  = p["encryption"][:col_w[3]]
        band = p["band"][:col_w[4]]

        color = Fore.GREEN if pwd else Fore.RED
        print(
            color +
            f"{name:<{col_w[0]}} | "
            f"{pwd:<{col_w[1]}} | "
            f"{auth:<{col_w[2]}} | "
            f"{enc:<{col_w[3]}} | "
            f"{band:<{col_w[4]}}"
        )

    print(Fore.CYAN + sep)
    print(Fore.WHITE + f"\n  Total: {len(profiles)} profile(s) | "
          + Fore.GREEN + f"{sum(1 for p in profiles if p['password'])} with password "
          + Fore.RED + f"| {sum(1 for p in profiles if not p['password'])} without\n")

# ──────────────────────────────────────────────
# Filter / Search
# ──────────────────────────────────────────────

def filter_profiles(profiles, keyword=None, with_password_only=False):
    """Filter profiles by keyword and/or password presence."""
    result = profiles
    if keyword:
        kw = keyword.lower()
        result = [p for p in result if kw in p["name"].lower()]
    if with_password_only:
        result = [p for p in result if p["password"]]
    return result

# ──────────────────────────────────────────────
# Export
# ──────────────────────────────────────────────

def export_profiles(profiles, fmt):
    """Export profiles to CSV, TXT, or JSON."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"fisard_wifi_export_{timestamp}.{fmt}"

    if fmt == "csv":
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "password", "auth", "encryption", "band"])
            writer.writeheader()
            writer.writerows(profiles)

    elif fmt == "txt":
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"FISARD WiFi Export — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n")
            for p in profiles:
                f.write(f"Name       : {p['name']}\n")
                f.write(f"Password   : {p['password'] or '(none)'}\n")
                f.write(f"Auth       : {p['auth']}\n")
                f.write(f"Encryption : {p['encryption']}\n")
                f.write(f"Band       : {p['band']}\n")
                f.write("-" * 40 + "\n")

    elif fmt == "json":
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(profiles, f, indent=2, ensure_ascii=False)

    else:
        print(Fore.RED + f"[!] Unknown format: {fmt}")
        return

    print(Fore.GREEN + f"\n[+] Exported {len(profiles)} profile(s) to {Fore.YELLOW + filename}\n")

# ──────────────────────────────────────────────
# Interactive Menu
# ──────────────────────────────────────────────

def show_menu():
    print(Fore.CYAN + Style.BRIGHT + "\n  ╔══════════════════════════════╗")
    print(Fore.CYAN + Style.BRIGHT +   "  ║        MAIN MENU             ║")
    print(Fore.CYAN + Style.BRIGHT +   "  ╠══════════════════════════════╣")
    print(Fore.WHITE +                 "  ║  [1] Show All Profiles       ║")
    print(Fore.WHITE +                 "  ║  [2] Search by Name          ║")
    print(Fore.WHITE +                 "  ║  [3] Show Only With Password ║")
    print(Fore.WHITE +                 "  ║  [4] Export Results          ║")
    print(Fore.WHITE +                 "  ║  [5] Re-Scan                 ║")
    print(Fore.RED +                   "  ║  [0] Exit                    ║")
    print(Fore.CYAN + Style.BRIGHT +   "  ╚══════════════════════════════╝")
    return input(Fore.YELLOW + "\n  Choose option: ").strip()

def export_menu(profiles):
    print(Fore.CYAN + "\n  Export format:")
    print("  [1] CSV")
    print("  [2] TXT")
    print("  [3] JSON")
    choice = input(Fore.YELLOW + "  Choose: ").strip()
    fmt_map = {"1": "csv", "2": "txt", "3": "json"}
    fmt = fmt_map.get(choice)
    if fmt:
        export_profiles(profiles, fmt)
    else:
        print(Fore.RED + "  [!] Invalid choice.")

# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    # Banner
    print(Fore.CYAN + Style.BRIGHT + BANNER)
    print(Fore.WHITE + Style.BRIGHT + "  WiFi Security & Router Diagnostics v2.0.0")
    print(Fore.WHITE + f"  Platform  : {Fore.YELLOW}{OS}")
    print(Fore.WHITE + f"  Timestamp : {Fore.YELLOW}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(Fore.WHITE + "  Copyright 2026 - " + Fore.YELLOW + "Shabir Mahfudz Prahono on GitHub")
    print()

    # Terms
    print(Fore.YELLOW + "  This tool reads locally saved WiFi credentials on your own device.")
    print(Fore.YELLOW + Style.BRIGHT + "\n  ╔══════════════════════════════════════════════════════════╗")
    print(Fore.YELLOW + Style.BRIGHT +   "  ║              TERMS AND CONDITIONS                        ║")
    print(Fore.YELLOW + Style.BRIGHT +   "  ╠══════════════════════════════════════════════════════════╣")
    print(Fore.WHITE +                   "  ║  1. This tool is intended for PERSONAL USE ONLY.         ║")
    print(Fore.WHITE +                   "  ║  2. Only use this on devices you OWN or have explicit    ║")
    print(Fore.WHITE +                   "  ║     permission to access.                                ║")
    print(Fore.WHITE +                   "  ║  3. Unauthorized access to others' credentials is        ║")
    print(Fore.WHITE +                   "  ║     ILLEGAL and violates privacy laws.                   ║")
    print(Fore.WHITE +                   "  ║  4. The author holds NO responsibility for any misuse    ║")
    print(Fore.WHITE +                   "  ║     or damage caused by this tool.                       ║")
    print(Fore.WHITE +                   "  ║  5. By continuing, you confirm that you are authorized   ║")
    print(Fore.WHITE +                   "  ║     to retrieve credentials on this device.              ║")
    print(Fore.YELLOW + Style.BRIGHT +   "  ╚══════════════════════════════════════════════════════════╝")
    terms = input(Fore.WHITE + "  Agree to Terms and Conditions? (Y/n): ").strip().lower()
    if terms != "y":
        print(Fore.RED + "\n  Program terminated.\n")
        sys.exit(0)

    # Initial scan
    print(Fore.CYAN + "\n  [*] Scanning WiFi profiles...")
    all_profiles = scan_all_profiles()

    if not all_profiles:
        print(Fore.RED + "  [!] No WiFi profiles found or insufficient permissions.\n")
        sys.exit(1)

    print(Fore.GREEN + f"  [+] Found {len(all_profiles)} profile(s).\n")

    current_view = all_profiles

    # Main loop
    while True:
        choice = show_menu()

        if choice == "1":
            current_view = all_profiles
            print_table(current_view)

        elif choice == "2":
            kw = input(Fore.YELLOW + "\n  Enter keyword to search: ").strip()
            current_view = filter_profiles(all_profiles, keyword=kw)
            if current_view:
                print_table(current_view)
            else:
                print(Fore.RED + f"\n  [!] No profiles matching '{kw}'.\n")

        elif choice == "3":
            current_view = filter_profiles(all_profiles, with_password_only=True)
            if current_view:
                print_table(current_view)
            else:
                print(Fore.RED + "\n  [!] No profiles with a saved password found.\n")

        elif choice == "4":
            if not current_view:
                print(Fore.RED + "\n  [!] No data to export. Show profiles first.\n")
            else:
                export_menu(current_view)

        elif choice == "5":
            print(Fore.CYAN + "\n  [*] Re-scanning...")
            all_profiles = scan_all_profiles()
            current_view = all_profiles
            print(Fore.GREEN + f"  [+] Found {len(all_profiles)} profile(s).\n")

        elif choice == "0":
            print(Fore.CYAN + "\n  Thankyou, Goodbye! \n")
            break

        else:
            print(Fore.RED + "\n  [!] Invalid option. Try again.\n")


if __name__ == "__main__":
    main()
