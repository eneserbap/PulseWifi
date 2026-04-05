import subprocess
import os

def scan_all_networks(interface):
    """Etraftaki tüm ağları canlı olarak tarar."""
    print(f"\n    [*] Tarama başlatılıyor... Durdurmak için [CTRL+C]")
    try:
        # -M seçeneği üretici isimlerini de gösterir
        cmd = f"sudo airodump-ng {interface} -M"
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print(f"\n    [!] Tarama durduruldu.")

def target_scan(interface, bssid, channel, output_name):
    """Sadece seçilen bir ağa odaklanır ve handshake bekler."""
    print(f"\n    [*] {bssid} hedefine kilitlenildi (Kanal: {channel})")
    # -w ile yakalanan paketleri dosyaya kaydederiz
    cmd = f"sudo airodump-ng --bssid {bssid} -c {channel} -w {output_name} {interface}"
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print(f"\n    [!] Dinleme modu kapatıldı.")