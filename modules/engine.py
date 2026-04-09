from modules import i18n
t = i18n.t
import subprocess
import os


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
    if mgr == "systemd":
        run_cmd(["sudo", "systemctl", action, service])
    elif mgr == "openrc":
        run_cmd(["sudo", "rc-service", service, action])
    elif mgr == "sysvinit":
        run_cmd(["sudo", "service", service, action])


def get_active_nm():
    """Sistemde aktif olan ağ yöneticisini (NetworkManager veya connman) bulur."""
    _, out = run_cmd(["ps", "aux"])
    if "NetworkManager" in out: return "NetworkManager"
    if "connmand" in out: return "connman"
    return "NetworkManager" # Varsayılan


def is_monitor(iface):

    success, out = run_cmd(["iwconfig", iface])
    if success and "Mode:Monitor" in out: return True
    return False


def get_real_iface(iface):
    if os.path.exists('/sys/class/net/' + iface + 'mon'):
        return iface + 'mon'
    return iface


# --- MONITOR MODE TOGGLE (Monitör Modu Anahtarı) ---
def toggle_monitor(iface, mode="start"):
    if mode == "start":
        if not is_monitor(iface):
            print(t("engine_monitor_prep", iface=iface))
            run_cmd(["sudo", "airmon-ng", "check", "kill"])
            run_cmd(["sudo", "airmon-ng", "start", iface])
        yeni_isim = get_real_iface(iface)
        if is_monitor(yeni_isim):
            return True, t("engine_monitor_start_success", yeni_isim=yeni_isim), yeni_isim
        else:
            return False, t("engine_monitor_start_fail"), yeni_isim
    else:
        print(t("engine_monitor_stop"))
        run_cmd(["sudo", "airmon-ng", "stop", iface])
        
        nm_service = get_active_nm()
        manage_service(nm_service, "restart")
        manage_service("wpa_supplicant", "restart")
        
        eski_isim = iface.replace('mon', '')
        return True, t("engine_monitor_stop_success"), eski_isim



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
    nm_service = get_active_nm()
    manage_service(nm_service, "restart")
    manage_service("wpa_supplicant", "restart")
    
    # nmcli varsa networking on yap (NetworkManager için)
    if os.path.exists("/usr/bin/nmcli"):
        subprocess.run(["sudo", "nmcli", "networking", "on"], capture_output=True)
    return True

