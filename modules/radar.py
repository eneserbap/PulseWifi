import subprocess

def scan_all(interface):
    print(f"\n    [*] {interface} üzerinden geniş çaplı tarama başlatılıyor...")
    print(f"    [*] Durdurmak için [CTRL+C] tuşlarına basın.\n")
    try:
        subprocess.run(f"sudo airodump-ng {interface} -M", shell=True)
    except KeyboardInterrupt:
        print(f"\n    [!] Tarama kullanıcı tarafından durduruldu.")

def target_lock(interface, bssid, channel, file_name):
    print(f"\n    [*] Hedef BSSID: {bssid} | Kanal: {channel}")
    print(f"    [*] Handshake bekleniyor... (Dosya: {file_name}.cap)")
    cmd = f"sudo airodump-ng --bssid {bssid} -c {channel} -w {file_name} {interface}"
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print(f"\n    [✔] Dinleme tamamlandı. '{file_name}' kaydedildi.")