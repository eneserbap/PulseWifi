import os
import time
import sys
from modules import engine, radar, strike

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'
    CYAN = '\033[96m'

def banner():
    # Burada os modülünü kullanıyoruz, o yüzden en tepede import os şart!
    os.system('clear') 
    print(f"{Colors.BLUE}{Colors.BOLD}")
    print(r"""
  _____  _    _ _       _____ ______  __          _______ ______ _____ 
 |  __ \| |  | | |     / ____|  ____| \ \        / /_   _|  ____|_   _|
 | |__) | |  | | |    | (___ | |__     \ \  /\  / /  | | | |__    | |  
 |  ___/| |  | | |     \___ \|  __|     \ \/  \/ /   | | |  __|   | |  
 | |    | |__| | |____ ____) | |____     \  /\  /   _| |_| |     _| |_ 
 |_|     \____/|______|_____/|______|     \/  \/   |_____|_|    |_____|""")
    print(f"{' ' * 51}{Colors.CYAN}by EnesErbap{Colors.END}")
    print(f"{Colors.BLUE}    " + "═" * 62 + f"{Colors.END}")

def menu_box(title, options):
    print(f"\n{Colors.BOLD}    ╔═══════════════ {title.upper()} ═══════════════╗{Colors.END}")
    print(f"    ║                                            ║")
    for opt in options:
        print(f"    ║  {opt} ║")
    print(f"    ║                                            ║")
    print(f"{Colors.BOLD}    ╚════════════════════════════════════════════╝{Colors.END}")

def select_interface():
    # Bu fonksiyon engine.py içindeki get_interfaces'i kullanır
    ifaces = engine.get_interfaces()
    
    if not ifaces:
        print(f"    {Colors.RED}[!] Hiç Wi-Fi kartı bulunamadı!{Colors.END}")
        input(f"\n    Devam etmek için Enter...")
        return None

    print(f"\n    {Colors.BOLD}[*] Mevcut Wi-Fi Kartları:{Colors.END}")
    for i, name in enumerate(ifaces):
        print(f"    {Colors.YELLOW}[{i}]{Colors.END} {name}")
    
    try:
        secim = int(input(f"\n    {Colors.CYAN}Pulse/Iface #{Colors.END} "))
        return ifaces[secim]
    except (ValueError, IndexError):
        print(f"    {Colors.RED}[!] Geçersiz seçim!{Colors.END}")
        time.sleep(1)
        return None

def engine_ui():
    while True:
        banner()
        opts = [
            f"{Colors.YELLOW}[1]{Colors.END} Monitor Modu AÇ                  ",
            f"{Colors.YELLOW}[2]{Colors.END} Monitor Modu KAPAT               ",
            f"{Colors.YELLOW}[0]{Colors.END} Geri                             "
        ]
        menu_box("ENGINE", opts)
        sub = input(f"\n    Pulse/Engine # ")
        if sub == "1":
            iface = select_interface()
            if iface:
                res, msg = engine.toggle_monitor(iface, "start")
                print(f"    {msg}")
                time.sleep(2)
        elif sub == "2":
            iface = select_interface()
            if iface:
                res, msg = engine.toggle_monitor(iface, "stop")
                print(f"    {msg}")
                time.sleep(2)
        elif sub == "0": break

def radar_ui():
    while True:
        banner()
        opts = [
            f"{Colors.YELLOW}[1]{Colors.END} Tüm Ağları Tara                  ",
            f"{Colors.YELLOW}[2]{Colors.END} Hedefe Kilitlen (Handshake)       ",
            f"{Colors.YELLOW}[0]{Colors.END} Geri                             "
        ]
        menu_box("RADAR", opts)
        sub = input(f"\n    {Colors.BOLD}Pulse/Radar #{Colors.END} ")
        
        if sub == "1":
            iface = select_interface() 
            if iface:
                radar.scan_all(iface)
            else:
                print(f"    {Colors.RED}[!] Kart seçilmedi!{Colors.END}")
                time.sleep(2)
        elif sub == "2":
            iface = select_interface()
            if iface:
                bssid = input("    BSSID: ")
                ch = input("    Kanal: ")
                name = input("    Dosya Adı: ")
                radar.target_lock(iface, bssid, ch, name)
        elif sub == "0": break

def strike_ui():
    while True:
        banner()
        opts = [
            f"{Colors.YELLOW}[1]{Colors.END} Pulse Kick (Deauth)              ",
            f"{Colors.YELLOW}[0]{Colors.END} Geri                             "
        ]
        menu_box("STRIKE", opts)
        sub = input(f"\n    Pulse/Strike # ")
        if sub == "1":
            iface = select_interface()
            if iface:
                bssid = input("    BSSID: ")
                client = input("    Cihaz MAC (Boş bırakılabilir): ")
                strike.pulse_kick(iface, bssid, client if client else None)
                input("\n    Devam etmek için Enter...")
        elif sub == "0": break

def main():
<    while True:
        banner()
        opts = [
            f"{Colors.YELLOW}[1]{Colors.END} RADAR  (Ağ Tarama)               ",
            f"{Colors.YELLOW}[2]{Colors.END} STRIKE (Saldırı Modu)            ",
            f"{Colors.YELLOW}[3]{Colors.END} ENGINE (Adaptör Ayarları)        ",
            f"{Colors.YELLOW}[0]{Colors.END} Çıkış                            "
        ]
        menu_box("KATEGORİLER", opts)
        choice = input(f"\n    {Colors.BOLD}Pulse #{Colors.END} ")

        if choice == "1":
            radar_ui()
        elif choice == "2":
            strike_ui()
        elif choice == "3":
            engine_ui()
        elif choice == "0":
            print(f"\n    {Colors.BLUE}[*] Pulse kesildi.{Colors.END}")
            break

if __name__ == "__main__":
    main()  