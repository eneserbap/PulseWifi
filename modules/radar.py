import subprocess
import os
import time
import re
from modules import i18n
t = i18n.t


# --- UTILS (Yardımcı Araçlar) ---
def clean_ssid(ssid):
    """SSID karakterlerini temizler, gizli karakterleri siler ve 32 karakterle sınırlar."""
    if not ssid: return ""
    
    cleaned = "".join(filter(lambda x: x.isprintable(), ssid))
 
    return cleaned.strip()[:32]


# --- LIVE SCANNING (Canlı Tarama) ---
def scan_all(iface):
    """Ekranda canlı tarama yapar, sadece izleme içindir."""
    print(t("strike_scanning"))
    try:
        subprocess.run(["sudo", "airodump-ng", iface, "-M"])
    except KeyboardInterrupt:
        pass

def get_signal_bar(dbm):
    """dBm değerini görsel bir bara çevirir: [####------]"""
    try:
        dbm = int(dbm.strip())
        if dbm == -1 or dbm == 0: return "[Bilinmiyor]"
        quality = max(0, min(100, 2 * (dbm + 100)))
        bars = int(quality / 10)
        return "[" + "#" * bars + "-" * (10 - bars) + "]"
    except:
        return "[--Hata---]"


# --- VENDOR DETECTION (Marka Tespiti) ---
def get_vendor(mac):
    """MAC adresinin ilk 6 hanesinden cihaz markasını çevrimdışı (offline) bulur."""
    prefix = mac.upper().replace(':', '')[:6]
    paths = [
        '/usr/share/macchanger/OUI.list', 
        '/var/lib/ieee-data/oui.txt',
        '/usr/share/hwdata/oui.txt', # Fedora/Arch path
        '/usr/share/misc/oui.txt'    # Alternative path
    ]
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        if prefix in line:
                            parts = line.strip().split(maxsplit=1)
                            if len(parts) > 1:
                                marka = parts[1].replace(',', '').split()[0]
                                return marka[:12] 
            except:
                continue
    return t("radar_unknown_vendor")


# --- AUTO TARGET SELECT (Otomatik Hedef Seçimi) ---
def auto_scan_and_select(iface, scan_time=15):
    """Arka planda tarar ve bulunan ağları bir liste olarak döner."""
    print(t("strike_scanning"))
    
    pid = os.getpid()
    prefix = f"/tmp/pulse_{pid}"
    
    # Eski kalıntıları temizle
    import glob
    for f in glob.glob(f"{prefix}*"):
        try: os.remove(f)
        except: pass

    cmd = ["sudo", "airodump-ng", iface, "--output-format", "csv", "-w", prefix]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    try:
        time.sleep(scan_time)
    finally:
        proc.terminate()
        try: proc.wait(timeout=2)
        except: proc.kill()

    networks = []
    file_path = f'{prefix}-01.csv'
    if not os.path.exists(file_path):
        return networks
    
    try:
        import csv
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # AP'ler ve Station'lar arasındaki boşluktan böl
            parts = content.split('\n\n')
            if not parts: return []
            
            # CSV okuyucu ile parse et (virgüllü SSID'ler için kritik)
            lines = parts[0].strip().splitlines()
            if not lines: return []
            
            reader = csv.reader(lines)
            headers = [h.strip() for h in next(reader)]
            
            for row in reader:
                if len(row) < len(headers): continue
                # Header'lara göre index bul
                try:
                    res = {headers[i]: row[i].strip() for i in range(len(headers))}
                    bssid = res.get('BSSID')
                    essid = clean_ssid(res.get('ESSID'))
                    if bssid and essid:
                        networks.append({
                            'bssid': bssid, 
                            'ch': res.get('channel', '0'), 
                            'dbm': res.get('Power', '-100'), 
                            'essid': essid,
                            'vendor': get_vendor(bssid) 
                        })
                except: continue
    except Exception:
        pass

    def sort_by_signal(net):
        try:
            val = int(str(net['dbm']).strip())
            return val if val != -1 and val != 0 else -100
        except: return -100

    networks.sort(key=sort_by_signal, reverse=True)
    return networks



# --- TARGET LOCK (Hedefe Kilitlenme) ---
def target_lock(iface, bssid, channel, file_name):
    """Seçilen hedefe kilitlenip Handshake yakalamaya çalışır."""
    print(t("strike_handshake_check", cap_file=f"{bssid} (Ch: {channel})"))
    cmd = ["sudo", "airodump-ng", "--bssid", bssid, "-c", channel, "-w", file_name, iface]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print(t("strike_press_enter"))
