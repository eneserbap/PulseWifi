import subprocess

def scan_all(interface):
    print(f"\n    [*] Tarama yapılıyor... Durdurmak için [CTRL+C]")
    try:
        # -M üretici ismini gösterir, daha profesyonel durur
        subprocess.run(f"sudo airodump-ng {interface} -M", shell=True)
    except KeyboardInterrupt:
        print(f"\n    [!] Tarama bitti.")

def target_lock(interface, bssid, channel, file_name):
    print(f"\n    [*] {bssid} hedefine kilitlenildi. Handshake bekleniyor...")
    # Yakalanan paketleri dosyaya yazar
    cmd = f"sudo airodump-ng --bssid {bssid} -c {channel} -w {file_name} {interface}"
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print(f"\n    [!] Dinleme durduruldu. Dosyalar kaydedildi.")