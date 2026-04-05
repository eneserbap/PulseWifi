import subprocess
import os

def run_cmd(command):
    try:
        # stderr'i de yakalıyoruz ki hata varsa görelim
        res = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, res.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def is_monitor(iface):
    success, out = run_cmd(f"iwconfig {iface}")
    return "Mode:Monitor" in out

def toggle_monitor(iface, mode="start"):
    if mode == "start":
        if not is_monitor(iface):
            print(f"    [*] Süreçler temizleniyor ve {iface} mod değiştiriyor...")
            run_cmd("sudo airmon-ng check kill")
            success, err = run_cmd(f"sudo airmon-ng start {iface}")
            if success:
                return True, f"    [✔] {iface} Monitör moduna alındı."
            return False, f"    [✘] Hata: {err}"
        return True, f"    [*] {iface} zaten Monitör modunda."
    else:
        # KAPATMA HATASI ÇÖZÜMÜ: airmon-ng bazen kart ismini bulamazsa hata verir
        print(f"    [*] Monitör modu kapatılıyor...")
        success, err = run_cmd(f"sudo airmon-ng stop {iface}")
        
        # İnternet servislerini her durumda ayağa kaldır
        run_cmd("sudo systemctl restart NetworkManager") 
        run_cmd("sudo systemctl restart wpa_supplicant")
        
        if success:
            return True, "    [✔] Managed moda dönüldü, internet servisleri canlandırıldı."
        else:
            return False, f"    [!] Uyarı: {err} (Ancak servisler yine de sıfırlandı)."

def get_interfaces():
    interfaces = []
    try:
        for iface in os.listdir('/sys/class/net'):
            if os.path.exists(f'/sys/class/net/{iface}/wireless'):
                interfaces.append(iface)
    except:
        pass
    return interfaces