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
        subprocess.run(f"sudo airodump-ng {iface} -M", shell=True)
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
    paths = ['/usr/share/macchanger/OUI.list', '/var/lib/ieee-data/oui.txt']
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
    
    # Dosya temizliği (shell=True yerine güvenli yöntem)
    import glob
    for f in glob.glob("/tmp/pulse_scan*"):
        try: os.remove(f)
        except: pass

    # airodump-ng'yi arka planda başlat (& yerine Popen)
    cmd = ["sudo", "airodump-ng", iface, "--output-format", "csv", "-w", "/tmp/pulse_scan"]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    try:
        time.sleep(scan_time)
    finally:
        # Süreci güvenli bir şekilde sonlandır (killall yerine terminate)
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
    networks = []
    file_path = '/tmp/pulse_scan-01.csv'
    if not os.path.exists(file_path):
        return networks
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.strip() == '' or 'Station MAC' in line:
                    continue
                parts = line.split(',')
                if len(parts) >= 14 and parts[0].strip() != 'BSSID':
                    bssid = parts[0].strip()
                    ch = parts[3].strip()
                    dbm = parts[8].strip()
                    essid = clean_ssid(parts[13])
                    if bssid and essid:
                        networks.append({
                            'bssid': bssid, 
                            'ch': ch, 
                            'dbm': dbm, 
                            'essid': essid,
                            'vendor': get_vendor(bssid) 
                        })
    except Exception:
        pass
    def sort_by_signal(net):
        try:
            val = int(net['dbm'].strip())
            if val == -1 or val == 0:
                return -100
            return val
        except:
            return -100
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
