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
        '/usr/share/hwdata/oui.txt',
        '/usr/share/misc/oui.txt'
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
def auto_scan_and_select(iface, scan_time=15, interactive=True):
    """Arka planda tarar ve bulunan ağları bir liste olarak döner."""
    print(t("strike_scanning"))
    
    # YENİ EKLENEN: 5GHz ve 2.4GHz Tarama Seçeneği
    band_param = []
    if interactive:
        print("\n    \033[93m[1] Hızlı Tarama (Sadece 2.4GHz)\033[0m")
        print("    \033[96m[2] Derin Tarama (2.4GHz + 5GHz)\033[0m")
        secim = input("    Tarama Modu: ")
        if secim == "2":
            band_param = ["--band", "abg"]
    else:
        # Etkileşimsiz modda (Kaos Modu gibi) varsayılan olarak her yeri tara
        band_param = ["--band", "abg"]

    pid = os.getpid()
    prefix = f"/tmp/pulse_{pid}"
    
    import glob
    for f in glob.glob(f"{prefix}*"):
        try: os.remove(f)
        except: pass

    # airodump-ng komutuna band_param listesini dinamik olarak ekliyoruz
    cmd = ["sudo", "airodump-ng"] + band_param + ["--output-format", "csv", "-w", prefix, iface]
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
    
    time.sleep(1)
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for line in lines:
                if "," in line and len(line.split(",")) > 10:
                    parts = [p.strip() for p in line.split(",")]
                    if re.match(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", parts[0]):
                        bssid = parts[0]
                        ch = parts[3]
                        dbm = parts[8]
                        essid = parts[13] if len(parts) > 13 else "[Hidden]"
                        
                        if bssid not in [n['bssid'] for n in networks]:
                            # YENİ EKLENEN: Arayüz (UI) Frekans Renklendirmesi
                            try:
                                kanal_no = int(ch.strip())
                                if kanal_no > 14:
                                    freq_label = "\033[96m[5GHz]\033[0m"
                                else:
                                    freq_label = "\033[93m[2.4G]\033[0m"
                            except:
                                freq_label = "[???]"

                            networks.append({
                                'bssid': bssid,
                                'ch': ch,
                                'freq_label': freq_label, # pulse_main.py'da tablonu çizerken net['freq_label'] kullan!
                                'dbm': dbm,
                                'essid': clean_ssid(essid),
                                'vendor': get_vendor(bssid)
                            })
    except Exception as e:
        print(f"Tarama hatası: {e}")

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
    cmd = ["sudo", "airodump-ng", "--bssid", bssid, "-c", str(channel), "-w", file_name, iface]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print(t("strike_press_enter"))