from modules import i18n
t = i18n.t
import subprocess
import os
import time

# --- COMMAND RUNNER (Komut Çalıştırıcı) ---
def run_cmd(command_list):
    """Komutları liste bazlı çalıştırarak kabuk (shell) açıklarını engeller."""
    try:
        if isinstance(command_list, str):
            import shlex
            command_list = shlex.split(command_list)
        process = subprocess.Popen(
            command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )
        stdout, stderr = process.communicate()
        if process.returncode == 0: return True, stdout
        else: return False, stderr
    except Exception as e: return False, str(e)


def get_service_manager():
    """Sistemin servis yöneticisini (systemd, openrc, sysvinit) tespit eder."""
    if os.path.exists("/usr/bin/systemctl"): return "systemd"
    if os.path.exists("/sbin/openrc"): return "openrc"
    if os.path.exists("/usr/sbin/service") or os.path.exists("/usr/sbin/invoke-rc.d"): return "sysvinit"
    return "unknown"


def manage_service(service, action):
    """Servisleri (başlat, durdur, yeniden başlat) evrensel şekilde yönetir."""
    mgr = get_service_manager()
    success = False
    if mgr == "systemd":
        success, _ = run_cmd(["sudo", "systemctl", action, service])
    elif mgr == "openrc":
        success, _ = run_cmd(["sudo", "rc-service", service, action])
    elif mgr == "sysvinit":
        success, _ = run_cmd(["sudo", "service", service, action])
    return success


def is_service_active(service):
    """Bir servisin aktif olup olmadığını kontrol eder."""
    mgr = get_service_manager()
    if mgr == "systemd":
        success, out = run_cmd(["sudo", "systemctl", "is-active", service])
        return success and out.strip() == "active"
    elif mgr == "openrc":
        success, out = run_cmd(["sudo", "rc-service", service, "status"])
        return success and "started" in out.lower()
    elif mgr == "sysvinit":
        success, out = run_cmd(["sudo", "service", service, "status"])
        return success and ("running" in out.lower() or "active" in out.lower())
    return False


def set_ipv6(iface, state):
    """Belirli bir arayüz için IPv6'yı etkinleştirir veya devre dışı bırakır."""
    val = "0" if state else "1"
    run_cmd(["sudo", "sysctl", "-w", f"net.ipv6.conf.{iface}.disable_ipv6={val}"])
    run_cmd(["sudo", "sysctl", "-w", f"net.ipv6.conf.all.disable_ipv6={val}"])
    run_cmd(["sudo", "sysctl", "-w", f"net.ipv6.conf.default.disable_ipv6={val}"])




def get_active_nm():
    """Sistemde aktif olan ağ yöneticisini (NetworkManager veya connman) bulur."""
    # Daha kesin sonuç için pgrep kullanımı
    success, _ = run_cmd(["pgrep", "-x", "NetworkManager"])
    if success: return "NetworkManager"
    
    success, _ = run_cmd(["pgrep", "-x", "connmand"])
    if success: return "connman"
    
    # Fallback: ps aux
    _, out = run_cmd(["ps", "aux"])
    if "NetworkManager" in out: return "NetworkManager"
    if "connmand" in out: return "connman"
    
    return "NetworkManager"



def is_monitor(iface):
    # Modern 'iw' komutu (Daha stabil ve yetki sorunu yaşatmaz)
    success, out = run_cmd(["sudo", "iw", "dev", iface, "info"])
    if success and "type monitor" in out.lower(): return True

    # Eski 'iwconfig' komutu (sudo eklendi, boşluklar silindi, küçük harfe çevrildi)
    success, out = run_cmd(["sudo", "iwconfig", iface])
    if success and "mode:monitor" in out.lower().replace(" ", ""): return True
    
    return False


def get_real_iface(iface):
    return iface


# --- MONITOR MODE TOGGLE (Monitör Modu Anahtarı) ---
def toggle_monitor(iface, mode="start"):
    if mode == "start":
        if not is_monitor(iface):
            print(t("engine_monitor_prep", iface=iface))
            
            # 1. NetworkManager'dan ayır
            run_cmd(["sudo", "nmcli", "device", "set", iface, "managed", "no"])
            run_cmd(["sudo", "rfkill", "unblock", "wifi"])
            time.sleep(1) # Sistemin bunu algılaması için bekle
            
            # 2. Kartı kapat ve üzerindeki IP adreslerini zorla temizle (Kilit nokta!)
            run_cmd(["sudo", "ip", "link", "set", iface, "down"])
            run_cmd(["sudo", "ip", "addr", "flush", "dev", iface])
            time.sleep(1) # Kartın tamamen kapanıp boşa çıkması için bekle
            
            # 3. Önce güncel yöntem (iw) ile monitör moda almayı dene
            success, _ = run_cmd(["sudo", "iw", "dev", iface, "set", "type", "monitor"])
            
            # 4. Eğer 'iw' başarısız olursa, eski yöntem (iwconfig) ile zorla
            if not success:
                run_cmd(["sudo", "iwconfig", iface, "mode", "monitor"])
                
            time.sleep(1) # Modun oturmasını bekle
            
            # 5. Kartı tekrar ayağa kaldır
            run_cmd(["sudo", "ip", "link", "set", iface, "up"])
            
            # 6. TxPower (Sinyal Gücü) Kilidini Kır (Bolivya Bölgesi + 30 dBm)
            run_cmd(["sudo", "iw", "reg", "set", "BO"])
            time.sleep(0.5)
            run_cmd(["sudo", "iwconfig", iface, "txpower", "30"])
        
        if is_monitor(iface):
            return True, t("engine_monitor_start_success", yeni_isim=iface), iface
        else:
            return False, f"[!] HATA: {iface} monitör moda geçemedi. Terminale 'sudo dmesg | tail' yazarak asıl sorunu görebilirsin.", iface
    else:
        print(t("engine_monitor_stop"))
        
        # 1. Kartı kapat ve IP temizle
        run_cmd(["sudo", "ip", "link", "set", iface, "down"])
        run_cmd(["sudo", "ip", "addr", "flush", "dev", iface])
        time.sleep(1)
        
        # 2. Normal (Managed) moda döndür
        success, _ = run_cmd(["sudo", "iw", "dev", iface, "set", "type", "managed"])
        if not success:
            run_cmd(["sudo", "iwconfig", iface, "mode", "managed"])
            
        time.sleep(1)
        
        # 3. Kartı ayağa kaldır ve NetworkManager'a geri ver
        run_cmd(["sudo", "ip", "link", "set", iface, "up"])
        run_cmd(["sudo", "nmcli", "device", "set", iface, "managed", "yes"])
        
        return True, t("engine_monitor_stop_success"), iface


def get_interfaces():
    interfaces = []
    try:
        for iface in os.listdir('/sys/class/net'):
            if os.path.exists('/sys/class/net/' + iface + '/wireless'):
                interfaces.append(iface)
    except: pass
    return interfaces


# --- MAC SPOOFING (MAC Sahtekarlığı) ---
def change_mac(iface, mode="random"):
    print(t("engine_mac_down", iface=iface))
    run_cmd(["sudo", "ip", "link", "set", iface, "down"])
    if mode == "random":
        print(t("engine_mac_random"))
        run_cmd(["sudo", "macchanger", "-r", iface])
    elif mode == "reset":
        print(t("engine_mac_reset"))
        run_cmd(["sudo", "macchanger", "-p", iface])
    print(t("engine_mac_up"))
    run_cmd(["sudo", "ip", "link", "set", iface, "up"])
    return True


# --- CLEANUP (Temizlik) ---
def cleanup():
    # Programdan çıkarken TÜM Wi-Fi kartlarını donanımsal olarak serbest bırak
    ifaces = get_interfaces()
    if os.path.exists("/usr/bin/nmcli"):
        for iface in ifaces:
            # Tüm kartları zorla NetworkManager'a geri ver
            subprocess.Popen(["sudo", "nmcli", "device", "set", iface, "managed", "yes"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Kartı ayağa kaldır
            subprocess.Popen(["sudo", "ip", "link", "set", iface, "up"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    return True