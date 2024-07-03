<p align="center">
<img src="https://github.com/shabir-mp/WiFi-Password-Cracker/assets/133546000/520a2994-7e4d-4c8b-a426-37ae89955e0a" width="150" />
<h1 align="center">WiFi Password Cracker v1.0.0</h1>
</p>


WiFi Password Cracker is a Python script that retrieves saved WiFi profiles and their passwords on a Windows machine. It uses the `netsh` command to access and display this information. The script uses the 'netsh' command-line tool to retrieve and display saved WiFi profiles and their passwords on a Windows machine. It includes user interaction to ensure consent before proceeding with the password retrieval. The process_wifi function handles the main logic of extracting and displaying the WiFi names and passwords.

## About
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](https://github.com/shabir-mp/Image-Background-Remover/blob/main/LICENSE)

- **Developer:** Shabir Mahfudz Prahono - @shabir-mp
- **Application creation date:** 18 June 2024

## Features

- Retrieves all saved WiFi profiles on a Windows machine.
- Displays the WiFi name and its corresponding password.

## Requirements

- Windows Operating System
- Python 3.x

## Installation

1. Clone this repository or download the script directly.
   ```sh
   git clone https://github.com/yourusername/wifi-password-cracker.git
   cd wifi-password-cracker
2. Ensure you have Python installed on your machine. You can download it from python.org.

## Usage
1. Open a command prompt or terminal.
2. Navigate to the directory where the script is located.
3. Run the script using Python: `python main.py`
4. The script will prompt you to agree to the terms and conditions. Type Y to proceed.
5. The script will display the WiFi names and their corresponding passwords.

## Code Explanations

### Importing the Required Module
```python
import subprocess
```
- **subprocess**: This module allows you to spawn new processes, connect to their input/output/error pipes, and obtain their return codes. It is used here to execute system commands.

### Defining the `process_wifi` Function
The `process_wifi` function retrieves and displays the names and passwords of all saved WiFi profiles on a Windows machine.

```python
def process_wifi():
    data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8').split('\n')
```
1. **Fetching WiFi Profiles**:
    - `subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'])`: Executes the `netsh wlan show profiles` command, which lists all the WiFi profiles saved on the system.
    - `.decode('utf-8')`: Converts the command output from bytes to a string.
    - `.split('\n')`: Splits the output string into a list of lines.

```python
    profiles = [i.split(":")[1][1:-1] for i in data if "All User Profile" in i]
```
2. **Extracting Profile Names**:
    - The list comprehension iterates through each line in `data`.
    - `if "All User Profile" in i`: Checks if the line contains "All User Profile", which indicates a WiFi profile.
    - `i.split(":")[1][1:-1]`: Splits the line at the colon, takes the second part (the profile name), and removes leading/trailing spaces and quotes.

```python
    for i in profiles:
        results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', i, 'key=clear']).decode('utf-8').split('\n')
```
3. **Fetching WiFi Passwords**:
    - The loop iterates over each profile name in `profiles`.
    - `subprocess.check_output(['netsh', 'wlan', 'show', 'profile', i, 'key=clear'])`: Executes the `netsh wlan show profile <profile_name> key=clear` command for each profile, which retrieves the details of the profile including the clear text key (password).
    - `.decode('utf-8').split('\n')`: Decodes and splits the output into lines.

```python
        results = [b.split(":")[1][1:-1] for b in results if "Key Content" in b]
```
4. **Extracting Passwords**:
    - Another list comprehension filters lines that contain "Key Content", indicating the presence of the password.
    - `b.split(":")[1][1:-1]`: Splits the line at the colon, takes the second part (the password), and removes leading/trailing spaces and quotes.

```python
        try:
            print("{:<30} | {:<}".format(i, results[0]))
        except IndexError:
            print("{:<30} | {:<}".format(i, ""))
```
5. **Displaying Results**:
    - `print("{:<30} | {:<}".format(i, results[0]))`: Prints the profile name and password in a formatted manner.
    - `except IndexError`: If no password is found, catches the exception and prints the profile name with an empty password field.

### Main Program Execution
The main part of the script handles user interaction and calls the `process_wifi` function if the user agrees to the terms and conditions.

```python
print("""
░░     ░░ ░░ ░░░░░░░ ░░      ░░░░░░ ░░░░░░   ░░░░░   ░░░░░░ ░░   ░░ ░░░░░░░ ░░░░░░  
▒▒     ▒▒ ▒▒ ▒▒      ▒▒     ▒▒      ▒▒   ▒▒ ▒▒   ▒▒ ▒▒      ▒▒  ▒▒  ▒▒      ▒▒   ▒▒ 
▒▒  ▒  ▒▒ ▒▒ ▒▒▒▒▒   ▒▒     ▒▒      ▒▒▒▒▒▒  ▒▒▒▒▒▒▒ ▒▒      ▒▒▒▒▒   ▒▒▒▒▒   ▒▒▒▒▒▒  
▓▓ ▓▓▓ ▓▓ ▓▓ ▓▓      ▓▓     ▓▓      ▓▓   ▓▓ ▓▓   ▓▓ ▓▓      ▓▓  ▓▓  ▓▓      ▓▓   ▓▓ 
 ███ ███  ██ ██      ██      ██████ ██   ██ ██   ██  ██████ ██   ██ ███████ ██   ██ 

""")
```
- This prints a stylized ASCII art title.

```python
print("Wifi Password Cracker")
print("Copyright 2024 - Shabir Mahfudz Prahono")
print()
terms = input("Agree Terms and Conditions ? (Y/n) ")
```
- Displays the program title and copyright notice.
- Prompts the user to agree to the terms and conditions.

```python
if terms.lower() == 'y':
    print("-"*70)
    print("WiFi Name                      | WiFi Password")
    process_wifi()
else:
    print("Program End")
    exit()
```
- If the user agrees (`terms.lower() == 'y'`), it prints a header line and calls the `process_wifi` function.
- If the user does not agree, it prints "Program End" and exits.

### Summary
The script uses the `netsh` command-line tool to retrieve and display saved WiFi profiles and their passwords on a Windows machine. It includes user interaction to ensure consent before proceeding with the password retrieval. The `process_wifi` function handles the main logic of extracting and displaying the WiFi names and passwords.

## Disclaimer
This script is intended for educational purposes only. Unauthorized access to networks is illegal and unethical. Use this script responsibly and only on networks you own or have permission to access.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

-----------------------------------------------------------------------------------------
![Github Footer](https://github.com/shabir-mp/Kereta-Api-Indonesia-Booking-System/assets/133546000/c1833fe4-f470-494f-99e7-d583421625be)
