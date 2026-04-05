import subprocess
import os

def run_cmd(command):
    try:
        res = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, res.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def is_monitor(iface):
    """Kartın zaten monitör modunda olup olmadığını kontrol eder."""
    success, out = run_cmd(f"iwconfig {iface}")
    return "Mode:Monitor" in out

def toggle_monitor(iface, mode="start"):
    if mode == "start":
        if not is_monitor(iface):
            run_cmd("sudo airmon-ng check kill")
            run_cmd(f"sudo airmon-ng start {iface}")
            return True, f"    [✔] {iface} otomatik olarak Monitör moduna alındı."
        return True, f"    [*] {iface} zaten Monitör modunda."
    else:
        run_cmd(f"sudo airmon-ng stop {iface}")
        run_cmd("sudo service network-manager restart")
        return True, f"    [✔] Ağ servisleri geri yüklendi (Clean Exit)."

def change_mac(iface):
    """Gizlilik için MAC adresini rastgele değiştirir."""
    run_cmd(f"sudo ifconfig {iface} down")
    success, _ = run_cmd(f"sudo macchanger -r {iface}")
    run_cmd(f"sudo ifconfig {iface} up")
    if success:
        print(f"    [✔] {iface} için MAC adresi başarıyla gizlendi.")
    else:
        print(f"    [✘] MAC değiştirilemedi (macchanger kurulu mu?).")

def get_interfaces():
    interfaces = []
    try:
        for iface in os.listdir('/sys/class/net'):
            if os.path.exists(f'/sys/class/net/{iface}/wireless'):
                interfaces.append(iface)
    except FileNotFoundError:
        pass
    return interfaces