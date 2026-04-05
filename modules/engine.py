import subprocess
import os

def run_cmd(command):
    try:
        # capture_output yerine eski/garanti yöntem olan PIPE kullanıyoruz
        res = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        return True, res.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except Exception as e:
        return False, str(e)

def is_monitor(iface):
    success, out = run_cmd(f"iwconfig {iface}")
    if success and "Mode:Monitor" in out:
        return True
    return False

def toggle_monitor(iface, mode="start"):
    if mode == "start":
        if not is_monitor(iface):
            print(f"    [*] Hazırlanıyor: {iface}")
            # Önce çakışan servisleri durdur
            run_cmd("sudo airmon-ng check kill")
            # Modu başlat
            success, err = run_cmd(f"sudo airmon-ng start {iface}")
            if success:
                return True, f"    [✔] {iface} Monitör moduna geçti."
            else:
                return False, f"    [✘] Mod değiştirme başarısız: {err}"
        return True, f"    [*] {iface} zaten Monitör modunda."
    else:
        print(f"    [*] Monitör modu kapatılıyor...")
        # airmon-ng stop komutu bazen isme takılır, o yüzden en garanti yol
        run_cmd(f"sudo airmon-ng stop {iface}")
        # Servisleri canlandır
        run_cmd("sudo systemctl restart NetworkManager")
        run_cmd("sudo systemctl restart wpa_supplicant")
        return True, "    [✔] İnternet servisleri geri yüklendi."

def get_interfaces():
    interfaces = []
    try:
        # Linux dizininden kartları çekiyoruz
        for iface in os.listdir('/sys/class/net'):
            if os.path.exists(f'/sys/class/net/{iface}/wireless'):
                interfaces.append(iface)
    except:
        pass
    return interfaces