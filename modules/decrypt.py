import subprocess

def wordlist_attack(cap_file, wordlist):
    print(f"\n    [*] Şifre kırma motoru başlatılıyor...")
    cmd = f"sudo aircrack-ng {cap_file} -w {wordlist}"
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print("\n    [!] Kırma işlemi iptal edildi.")

def brute_force(cap_file, essid, charset="0123456789", length=8):
    print(f"\n    [*] Smart Brute başlatılıyor... (Şablon: {length} hane | Karakter: {charset})")
    # crunch ile şifre üretip anında aircrack'e boruluyoruz (pipe)
    cmd = f"crunch {length} {length} {charset} | sudo aircrack-ng {cap_file} -e {essid} -w -"
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print("\n    [!] Kırma işlemi iptal edildi.")