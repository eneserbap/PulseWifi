import subprocess

def run_cmd(command):
    try:
        # Hataları yakalamak için capture_output kullanıyoruz
        subprocess.run(command, shell=True, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def toggle_monitor(interface, mode="start"):
    if mode == "start":
        # check kill eklemek bağlantı hatalarını önler
        cmd = f"sudo airmon-ng start {interface} && sudo airmon-ng check kill"
        msg = f"{interface} Monitör moduna alındı."
    else:
        cmd = f"sudo airmon-ng stop {interface} && sudo service network-manager restart"
        msg = "Managed moda dönüldü, internet servisleri geri yüklendi."
    
    success = run_cmd(cmd)
    return success, msg

def get_interfaces():
    """Sistemdeki Wi-Fi arayüzlerini listeler."""
    interfaces = []
    # /sys/class/net dizini sistemdeki tüm ağ kartlarını tutar
    for iface in os.listdir('/sys/class/net'):
        # Kablosuz kartların içinde genellikle 'wireless' klasörü olur
        if os.path.exists(f'/sys/class/net/{iface}/wireless'):
            interfaces.append(iface)
    return interfaces