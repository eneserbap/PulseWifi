import subprocess
import os

def run_cmd(command):
    try:
        # Popen, Python'ın en eski sürümlerinden beri olan en temel komut çalıştırma yoludur
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True # 'text=True' yerine bu kullanılır
        )
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            return True, stdout
        else:
            return False, stderr
    except Exception as e:
        return False, str(e)

def is_monitor(iface):
    success, out = run_cmd("iwconfig " + iface)
    if success and "Mode:Monitor" in out:
        return True
    return False

def toggle_monitor(iface, mode="start"):
    if mode == "start":
        if not is_monitor(iface):
            print("    [*] Hazırlanıyor: " + iface)
            # Çakışan servisleri temizle
            run_cmd("sudo airmon-ng check kill")
            # Monitör modunu başlat
            success, err = run_cmd("sudo airmon-ng start " + iface)
            if success:
                return True, "    [✔] " + iface + " Monitör moduna geçti."
            else:
                return False, "    [✘] Mod değiştirme başarısız: " + str(err)
        return True, "    [*] " + iface + " zaten Monitör modunda."
    else:
        print("    [*] Monitör modu kapatılıyor...")
        run_cmd("sudo airmon-ng stop " + iface)
        # İnternet servislerini canlandır
        run_cmd("sudo systemctl restart NetworkManager")
        run_cmd("sudo systemctl restart wpa_supplicant")
        return True, "    [✔] İnternet servisleri geri yüklendi."

def get_interfaces():
    interfaces = []
    try:
        # Linux dizininden Wi-Fi kartlarını bulur
        for iface in os.listdir('/sys/class/net'):
            if os.path.exists('/sys/class/net/' + iface + '/wireless'):
                interfaces.append(iface)
    except:
        pass
    return interfaces