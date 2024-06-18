import subprocess

def process_wifi():
    data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8').split('\n')
    profiles = [i.split(":")[1][1:-1] for i in data if "All User Profile" in i]

    for i in profiles:
        results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', i, 'key=clear']).decode('utf-8').split('\n')
        results = [b.split(":")[1][1:-1] for b in results if "Key Content" in b]
        try:
            print("{:<30} | {:<}".format(i, results[0]))
        except IndexError:
            print("{:<30} | {:<}".format(i, ""))

print("""
░░     ░░ ░░ ░░░░░░░ ░░      ░░░░░░ ░░░░░░   ░░░░░   ░░░░░░ ░░   ░░ ░░░░░░░ ░░░░░░  
▒▒     ▒▒ ▒▒ ▒▒      ▒▒     ▒▒      ▒▒   ▒▒ ▒▒   ▒▒ ▒▒      ▒▒  ▒▒  ▒▒      ▒▒   ▒▒ 
▒▒  ▒  ▒▒ ▒▒ ▒▒▒▒▒   ▒▒     ▒▒      ▒▒▒▒▒▒  ▒▒▒▒▒▒▒ ▒▒      ▒▒▒▒▒   ▒▒▒▒▒   ▒▒▒▒▒▒  
▓▓ ▓▓▓ ▓▓ ▓▓ ▓▓      ▓▓     ▓▓      ▓▓   ▓▓ ▓▓   ▓▓ ▓▓      ▓▓  ▓▓  ▓▓      ▓▓   ▓▓ 
 ███ ███  ██ ██      ██      ██████ ██   ██ ██   ██  ██████ ██   ██ ███████ ██   ██ 

""")
print("Wifi Password Cracker")
print("Copyright 2024 - Shabir Mahfudz Prahono")
print()
terms = input("Agree Terms and Conditions ? (Y/n) ")
if terms.lower() == 'y':
    print("-"*70)
    print("WiFi Name                      | WiFi Password")
    process_wifi()
else:
    print("Program End")
    exit()
