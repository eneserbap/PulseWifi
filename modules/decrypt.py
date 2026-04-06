import subprocess
import os
import time


from modules import i18n
t = i18n.t


# --- AIRCRACK CPU BRUTEFORCE (CPU ile Kaba Kuvvet) ---
def wordlist_attack(cap_file, wordlist):
    print(t("decrypt_start_cpu"))
    cmd = ["sudo", "aircrack-ng", cap_file, "-w", wordlist]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print(t("decrypt_cancel"))


def brute_force(cap_file, essid, charset="0123456789", length=8):
    print(t("decrypt_start_brute", length=length, charset=charset))
    try:
        p1 = subprocess.Popen(["crunch", str(length), str(length), charset], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["sudo", "aircrack-ng", cap_file, "-e", essid, "-w", "-"], stdin=p1.stdout)
        p1.stdout.close()
        p2.communicate()
    except KeyboardInterrupt:
        print(t("decrypt_cancel"))


# --- HASHCAT GPU CRACKING (GPU ile Şifre Kırma) ---
def hashcat_attack(cap_file, wordlist):
    print(t("decrypt_hashcat_prep"))
    base_name = cap_file.replace('.cap', '')
    hc_file = f"{base_name}.hc22000"
    print(t("decrypt_convert_format"))
    
    
    conv_cmd = ["hcxpcapngtool", "-o", hc_file, cap_file]
    subprocess.run(conv_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if not os.path.exists(hc_file) or os.path.getsize(hc_file) == 0:
        print(t("decrypt_convert_fail"))
        return
    print(t("decrypt_convert_success"))
    time.sleep(1)
    
    cmd = ["hashcat", "-m", "22000", hc_file, wordlist]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print(t("decrypt_cancel"))
