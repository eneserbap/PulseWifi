import subprocess
import os
import time

def scan_all(iface):
    print(f"\n    [*] {iface} ile canlı tarama başlatılıyor... (Durdurmak için CTRL+C)")
    try:
        subprocess.run(f"sudo airodump-ng {iface} -M", shell=True)
    except KeyboardInterrupt:
        pass

def get_signal_bar(dbm):
    """Sinyal gücünü dBm'den görsele çevirir."""
    try:
        dbm = int(dbm)
        if dbm == -1: return "[Bilinmiyor]"
        quality = max(0, min(100, 2 * (dbm + 100)))
        bars = int(quality / 10)
        return "[" + "#" * bars + "-" * (10 - bars) + "]"
    except:
        return "[Hata]"

def auto_scan_and_select(iface, scan_time=10):
    print(f"\n    [*] Hızlı keşif başlatıldı, {scan_time} saniye havayı dinliyorum...")
    # Eski dosyaları temizle ve arkaplanda airodump çalıştır
    os.system("rm -f /tmp/pulse_scan*")
    cmd = f"sudo airodump-ng {iface} --output-format csv -w /tmp/pulse_scan & sleep {scan_time}; sudo killall airodump-ng"
    subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    
    networks = []
    try:
        with open('/tmp/pulse_scan-01.csv', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.strip() == '' or 'Station MAC' in line: break
                parts = line.split(',')
                if len(parts) >= 14 and parts[0].strip() != 'BSSID':
                    bssid, ch, dbm, essid = parts[0].strip(), parts[3].strip(), parts[8].strip(), parts[13].strip()
                    if bssid and essid:
                        networks.append({'bssid': bssid, 'ch': ch, 'dbm': dbm, 'essid': essid})
    except:
        pass
    return networks

def target_lock(iface, bssid, channel, file_name):
    print(f"\n    [*] Hedefe kilitlenildi. Handshake bekleniyor... (CTRL+C ile durdur)")
    cmd = f"sudo airodump-ng --bssid {bssid} -c {channel} -w {file_name} {iface}"
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print(f"\n    [✔] Dinleme tamamlandı. {file_name} kaydedildi.")