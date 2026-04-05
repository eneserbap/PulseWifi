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