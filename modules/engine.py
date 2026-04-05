import subprocess

def run_cmd(command):
    """Komutu çalıştırır ve çıktıları gizler (Temiz ekran için)."""
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True)
        return True
    except:
        return False

def toggle_monitor(interface, mode="start"):
    """Modu 'start' (Monitör) veya 'stop' (Managed) yapar."""
    if mode == "start":
        # airmon-ng ile kartı aç ve çakışan süreçleri öldür
        cmd = f"sudo airmon-ng start {interface} && sudo airmon-ng check kill"
    else:
        # Kartı kapat ve internet servislerini geri getir
        cmd = f"sudo airmon-ng stop {interface} && sudo service network-manager restart"
    
    return run_cmd(cmd)

def list_interfaces():
    """Sistemdeki kartları bulur."""
    cmd = "iwconfig"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    # Burada basitçe çıktıyı dönebiliriz, ileride regex ile güzelleştiririz
    return result.stdout