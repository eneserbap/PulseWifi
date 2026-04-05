import subprocess
import os # EKSİKTİ, EKLENDİ!

def run_cmd(command):
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def toggle_monitor(interface, mode="start"):
    if mode == "start":
        cmd = f"sudo airmon-ng start {interface} && sudo airmon-ng check kill"
        msg = f"    [✔] {interface} Monitör moduna alındı ve çakışan süreçler temizlendi."
    else:
        cmd = f"sudo airmon-ng stop {interface} && sudo service network-manager restart"
        msg = "    [✔] Managed moda dönüldü, NetworkManager geri yüklendi."
    
    success = run_cmd(cmd)
    return success, msg

def get_interfaces():
    """Sistemdeki Wi-Fi arayüzlerini listeler."""
    interfaces = []
    try:
        # Windows'ta çalıştırıldığında çökmemesi için try-except içine alındı
        for iface in os.listdir('/sys/class/net'):
            if os.path.exists(f'/sys/class/net/{iface}/wireless'):
                interfaces.append(iface)
    except FileNotFoundError:
        pass
    return interfaces