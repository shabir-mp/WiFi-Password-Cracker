<p align="center">
<img src="https://github.com/user-attachments/assets/17c844bd-9ad8-480c-8732-84460bb0a31e" width="500" />
<h1 align="center">WiFi Security & Router Diagnostics v2.0.0</h1>
<h3 align="center"> - Updated Version of WiFi Password Cracker -</h3>
   
</p>

WiFi Security & Router Diagnostics is a cross-platform Python script that retrieves saved WiFi profiles and their details including passwords, authentication type, encryption, and radio band on Windows, Linux, and macOS. It uses platform-native tools (`netsh` on Windows, NetworkManager on Linux, and Keychain on macOS) to access and display this information. The script includes an interactive menu for filtering, searching, and exporting results, as well as user consent via Terms and Conditions before any data is retrieved.

## About
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](https://github.com/shabir-mp/Image-Background-Remover/blob/main/LICENSE)

- **Developer:** Shabir Mahfudz Prahono - @shabir-mp
- **Application creation date:** 18 June 2024
- **Last updated:** 17 March 2026

## Features

- Cross-platform support: Windows, Linux, and macOS.
- Retrieves all saved WiFi profiles on the device.
- Displays WiFi name, password, authentication type, encryption cipher, and radio band.
- Colorized terminal output — green for profiles with a password, red for those without.
- Interactive menu with options to browse, search, filter, and export data.
- Search profiles by name keyword.
- Filter to show only profiles that have a saved password.
- Export results to CSV, TXT, or JSON (auto-timestamped filenames).
- Re-scan profiles without restarting the program.
- Auto-installs `colorama` if not already present.

## Requirements

- Python 3.x
- `colorama` (auto-installed on first run)
- **Windows:** No additional requirements
- **Linux:** NetworkManager (`/etc/NetworkManager/system-connections/`) — requires root for password access
- **macOS:** `networksetup` and `security` CLI tools (built-in)

## Installation

1. Clone this repository or download the script directly.
   ```sh
   git clone https://github.com/shabir-mp/WiFi-Password-Cracker.git
   cd WiFi-Password-Cracker
   ```
2. Ensure you have Python 3.x installed. You can download it from [python.org](https://www.python.org/).

## Usage

1. Open a terminal or command prompt.
2. Navigate to the directory where `main.py` is located.
3. Run the script:
   ```sh
   python main.py
   ```
   > **Linux/macOS:** If profiles are not found, run with elevated permissions:
   > ```sh
   > sudo python main.py
   > ```
4. Read and agree to the Terms and Conditions by typing `Y`.
5. Use the interactive menu to navigate:

   | Option | Description |
   |--------|-------------|
   | `[1]` Show All Profiles | Display all scanned WiFi profiles |
   | `[2]` Search by Name | Filter profiles by a keyword |
   | `[3]` Show Only With Password | Display only profiles that have a saved password |
   | `[4]` Export Results | Save current view to CSV, TXT, or JSON |
   | `[5]` Re-Scan | Refresh the profile list from the system |
   | `[0]` Exit | Exit the program |

## Code Explanation

### Dependency Check

```python
def check_dependencies():
    try:
        import colorama
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
```

Automatically installs `colorama` if it is not found, so no manual `pip install` is needed before running the script.

### Platform Detection

```python
OS = platform.system()  # "Windows", "Linux", "Darwin"
```

Detects the current operating system and routes all profile retrieval functions accordingly.

### Platform-Specific Parsers

#### Windows : `get_profiles_windows()` / `get_profile_details_windows()`

Uses `netsh wlan show profiles` to list all profiles and `netsh wlan show profile <name> key=clear` to retrieve password, authentication, cipher, and radio band for each profile.

#### Linux : `get_profiles_linux()` / `get_profile_details_linux()`

Reads `.nmconnection` files from `/etc/NetworkManager/system-connections/`. Extracts `psk` (password), `key-mgmt` (auth), `pairwise` (encryption), and `band` fields. Raises a `[Permission Denied]` note if root access is required.

#### macOS : `get_profiles_macos()` / `get_profile_details_macos()`

Uses `networksetup -listpreferredwirelessnetworks en0` to list profiles and `security find-generic-password -wa <name>` to retrieve passwords from the system Keychain.

### Unified Scanner

```python
def scan_all_profiles():
```

Calls the appropriate platform-specific parser and returns a unified list of profile dictionaries with the keys: `name`, `password`, `auth`, `encryption`, `band`.

### Display

```python
def print_table(profiles):
```

Prints results as a formatted, colorized table. Rows are shown in **green** if a password is found, and **red** if no password is stored.

### Filter / Search

```python
def filter_profiles(profiles, keyword=None, with_password_only=False):
```

Filters the profile list by a case-insensitive name keyword and/or by password presence. Used by menu options `[2]` and `[3]`.

### Export

```python
def export_profiles(profiles, fmt):
```

Exports the current profile view to a file. The filename is auto-generated with a timestamp, e.g. `fisard_wifi_export_20260315_143022.csv`. Supports three formats:

- **CSV** — spreadsheet-compatible, one row per profile
- **TXT** — human-readable, one block per profile
- **JSON** — structured data, array of profile objects

### Interactive Menu

```python
def show_menu():
```

Displays a box-styled menu using Unicode border characters. Returns the user's choice as a string for the main loop to process.

## Disclaimer

This script is intended for educational and personal use only. Unauthorized access to networks or devices you do not own is illegal and unethical. Use this script responsibly and only on devices you own or have explicit permission to access.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

-----------------------------------------------------------------------------------------
![Github Footer](https://github.com/shabir-mp/Kereta-Api-Indonesia-Booking-System/assets/133546000/c1833fe4-f470-494f-99e7-d583421625be)
