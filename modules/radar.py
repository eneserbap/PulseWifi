import subprocess
import os
import time

def scan_all(iface):
    """Ekranda canlı tarama yapar, sadece izleme içindir."""
    print(f"\n    [*] {iface} ile canlı tarama başlatılıyor... (Durdurmak için CTRL+C)")
    try:
        # -M üretici ismini gösterir
        subprocess.run(f"sudo airodump-ng {iface} -M", shell=True)
    except KeyboardInterrupt:
        pass

def get_signal_bar(dbm):
    """dBm değerini görsel bir bara çevirir: [####------]"""
    try:
        dbm = int(dbm.strip())
        if dbm == -1 or dbm == 0: return "[Bilinmiyor]"
        # dBm genelde -100 ile 0 arasındadır. -30 süper, -90 çok zayıf.
        quality = max(0, min(100, 2 * (dbm + 100)))
        bars = int(quality / 10)
        return "[" + "#" * bars + "-" * (10 - bars) + "]"
    except:
        return "[--Hata---]"

def auto_scan_and_select(iface, scan_time=15):
    """Arka planda tarar ve bulunan ağları bir liste olarak döner."""
    print(f"\n    [*] Hızlı keşif başlatıldı, {scan_time} saniye çevre dinleniyor...")
    
    # Eski geçici dosyaları temizleyelim
    os.system("rm -f /tmp/pulse_scan*")
    
    # Arka planda çalıştırıp scan_time kadar bekleyip öldürüyoruz
    cmd = (f"sudo airodump-ng {iface} --output-format csv -w /tmp/pulse_scan & "
           f"sleep {scan_time}; sudo killall airodump-ng")
    
    subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    
    networks = []
    file_path = '/tmp/pulse_scan-01.csv'
    
    if not os.path.exists(file_path):
        print(f"    [!] Hata: Tarama dosyası oluşturulamadı.")
        return networks

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                # Boş satırları veya cihaz (station) listesine geçişi kontrol et
                if line.strip() == '' or 'Station MAC' in line:
                    continue
                
                parts = line.split(',')
                # CSV formatında BSSID ilk sütun, ESSID sonlardadır.
                if len(parts) >= 14 and parts[0].strip() != 'BSSID':
                    bssid = parts[0].strip()
                    ch = parts[3].strip()
                    dbm = parts[8].strip()
                    essid = parts[13].strip()
                    
                    # Gizli ağları (adı olmayanlar) süzebiliriz veya ekleyebiliriz
                    if bssid and essid:
                        networks.append({
                            'bssid': bssid, 
                            'ch': ch, 
                            'dbm': dbm, 
                            'essid': essid
                        })
    except Exception as e:
        print(f"    [!] Veri işlenirken hata oluştu: {e}")
        
    return networks

def target_lock(iface, bssid, channel, file_name):
    """Seçilen hedefe kilitlenip Handshake yakalamaya çalışır."""
    print(f"\n    [*] Hedefe kilitlenildi: {bssid} (Kanal: {channel})")
    print(f"    [*] Handshake bekleniyor... (Durdurmak için CTRL+C)")
    
    # -w ile dosyaya yazar, -c ile kanalı sabitler
    cmd = f"sudo airodump-ng --bssid {bssid} -c {channel} -w {file_name} {iface}"
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print(f"\n    [✔] Dinleme bitti. '{file_name}' dosyaları hazır.")