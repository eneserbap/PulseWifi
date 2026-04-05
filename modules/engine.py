import subprocess
import os

def run_cmd(command):
    try:
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )
        stdout, stderr = process.communicate()
        if process.returncode == 0: return True, stdout
        else: return False, stderr
    except Exception as e: return False, str(e)

def is_monitor(iface):
    success, out = run_cmd("iwconfig " + iface)
    if success and "Mode:Monitor" in out: return True
    return False

def get_real_iface(iface):
    if os.path.exists('/sys/class/net/' + iface + 'mon'):
        return iface + 'mon'
    return iface

def toggle_monitor(iface, mode="start"):
    if mode == "start":
        if not is_monitor(iface):
            print("    [*] Hazırlanıyor: " + iface)
            run_cmd("sudo airmon-ng check kill")
            run_cmd("sudo airmon-ng start " + iface)
        
        yeni_isim = get_real_iface(iface)
        
        if is_monitor(yeni_isim):
            return True, "    [✔] " + yeni_isim + " Monitör modunda.", yeni_isim
        else:
            return False, "    [✘] Mod değiştirilemedi.", yeni_isim
    else:
        print("    [*] Monitör modu kapatılıyor...")
        run_cmd("sudo airmon-ng stop " + iface)
        run_cmd("sudo systemctl restart NetworkManager")
        run_cmd("sudo systemctl restart wpa_supplicant")
        
        eski_isim = iface.replace('mon', '')
        return True, "    [✔] İnternet servisleri geri yüklendi.", eski_isim

def get_interfaces():
    interfaces = []
    try:
        for iface in os.listdir('/sys/class/net'):
            if os.path.exists('/sys/class/net/' + iface + '/wireless'):
                interfaces.append(iface)
    except: pass
    return interfaces

# ==========================================
# YENİ: GİZLİLİK KALKANI (MAC SPOOFING)
# ==========================================
def change_mac(iface, mode="random"):
    print(f"\n    [*] Ağ kartı ({iface}) geçici olarak kapatılıyor...")
    run_cmd(f"sudo ip link set {iface} down")
    
    if mode == "random":
        print("    [*] Gizlilik Kalkanı Aktif: Rastgele sahte bir MAC adresi üretiliyor...")
        run_cmd(f"sudo macchanger -r {iface}")
    elif mode == "reset":
        print("    [*] Kalkan Kapatılıyor: Orijinal fabrika MAC adresine dönülüyor...")
        run_cmd(f"sudo macchanger -p {iface}")
        
    print(f"    [*] Ağ kartı tekrar ayağa kaldırılıyor...")
    run_cmd(f"sudo ip link set {iface} up")
    return True