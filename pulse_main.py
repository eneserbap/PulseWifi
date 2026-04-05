import os
import time
import sys
import re
from modules import engine, radar, strike, decrypt, eviltwin

if os.name == 'posix' and os.geteuid() != 0:
    print("    [*] Linux tespit edildi. Root (sudo) yetkisine otomatik geçiliyor...")
    os.execvp("sudo", ["sudo", sys.executable] + sys.argv)

class Colors:
    BLUE, GREEN, YELLOW, RED, BOLD, END, CYAN = '\033[94m', '\033[92m', '\033[93m', '\033[91m', '\033[1m', '\033[0m', '\033[96m'

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

def strip_colors(text):
    return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)

def menu_box(title, options):
    width = 62 
    clean_title = strip_colors(title)
    pad_l = (width - len(clean_title) - 2) // 2
    pad_r = width - len(clean_title) - 2 - pad_l
    
    print(f"\n{Colors.BOLD}    ╔{'═' * pad_l} {title} {'═' * pad_r}╗{Colors.END}")
    print(f"    ║{' ' * width}║")
    for opt in options:
        clean_opt = strip_colors(opt)
        spaces = width - len(clean_opt) - 2
        print(f"    ║ {opt}{' ' * spaces} ║")
    print(f"    ║{' ' * width}║")
    print(f"{Colors.BOLD}    ╚{'═' * width}╝{Colors.END}")

def select_interface():
    ifaces = engine.get_interfaces()
    if not ifaces:
        print(f"    {Colors.RED}[!] Wi-Fi kartı bulunamadı!{Colors.END}"); time.sleep(2); return None
    print(f"\n    {Colors.BOLD}[*] Mevcut Wi-Fi Kartları:{Colors.END}")
    for i, name in enumerate(ifaces): print(f"    {Colors.YELLOW}[{i}]{Colors.END} {name}")
    try: return ifaces[int(input(f"\n    {Colors.CYAN}Pulse/Iface #{Colors.END} "))]
    except (ValueError, IndexError): return None

def engine_ui():
    while True:
        banner()
        opts = [
            f"{Colors.YELLOW}[1]{Colors.END} Monitör Modunu AÇ (Saldırı Hazırlığı)",
            f"{Colors.YELLOW}[2]{Colors.END} Monitör Modunu KAPAT (İnterneti Geri Al)",
            f"{Colors.YELLOW}[3]{Colors.END} Gizlilik Kalkanı AÇ (Rastgele MAC Al)",
            f"{Colors.YELLOW}[4]{Colors.END} Gizlilik Kalkanı KAPAT (Orijinal MAC Dön)",
            f"{Colors.YELLOW}[0]{Colors.END} Ana Menüye Dön"
        ]
        menu_box("ENGINE - ADAPTÖR & GİZLİLİK YÖNETİMİ", opts)
        sub = input(f"\n    {Colors.BOLD}Pulse/Engine #{Colors.END} ")
        
        if sub in ["1", "2", "3", "4"]:
            iface = select_interface()
            if not iface: continue
            
            if sub == "1":
                status, msg, iface = engine.toggle_monitor(iface, "start")
                print(msg); time.sleep(2)
            elif sub == "2":
                success, msg, iface = engine.toggle_monitor(iface, "stop")
                print(msg); time.sleep(2)
            elif sub == "3":
                engine.change_mac(iface, "random")
                print(f"    {Colors.GREEN}[✔] Sahte kimlik başarıyla atandı!{Colors.END}"); time.sleep(2)
            elif sub == "4":
                engine.change_mac(iface, "reset")
                print(f"    {Colors.GREEN}[✔] Orijinal kimliğe geri dönüldü!{Colors.END}"); time.sleep(2)
                
        elif sub == "0": break

def radar_ui():
    while True:
        banner()
        opts = [
            f"{Colors.YELLOW}[1]{Colors.END} Otomatik Hedef Seç (Tavsiye)",
            f"{Colors.YELLOW}[2]{Colors.END} Canlı İzleme (Manuel)",
            f"{Colors.YELLOW}[0]{Colors.END} Geri"
        ]
        menu_box("RADAR / KEŞİF", opts)
        sub = input(f"\n    {Colors.BOLD}Pulse/Radar #{Colors.END} ")

        if sub == "1":
            iface = select_interface()
            if iface:
                _, _, iface = engine.toggle_monitor(iface, "start")
                found_nets = radar.auto_scan_and_select(iface) 
                if not found_nets: print(f"    {Colors.RED}[!] Hiç ağ bulunamadı.{Colors.END}"); time.sleep(2); continue
                
                print(f"\n    {Colors.CYAN}{'ID':<3} {'SİNYAL':<15} {'SSID':<20} {'MARKA':<12} {'BSSID':<18} {'CH'}{Colors.END}")
                print("    " + "-"*76)
                for i, net in enumerate(found_nets):
                    bar = radar.get_signal_bar(net['dbm'])
                    print(f"    {Colors.YELLOW}[{i}]{Colors.END} {bar:<15} {net['essid'][:18]:<20} {net['vendor']:<12} {net['bssid']:<18} {net['ch']}")
                
                secim = input(f"\n    Hangi hedef? (0 ile {len(found_nets)-1} arası bir ID girin): ")
                if secim.isdigit() and int(secim) < len(found_nets):
                    target = found_nets[int(secim)]
                    print(f"    [✔] Seçilen: {target['essid']} ({target['vendor']})")
                    dosya_adi = input("    Kaydedilecek dosya adı (Şu anki klasöre '.cap' olarak kaydedilecek, örn: 'hedef1'): ")
                    radar.target_lock(iface, target['bssid'], target['ch'], dosya_adi)
                else: print("    [!] Geçersiz seçim. Lütfen listedeki numaralardan birini girin."); time.sleep(1.5)
        elif sub == "2":
            iface = select_interface()
            if iface: _, _, iface = engine.toggle_monitor(iface, "start"); radar.scan_all(iface)
        elif sub == "0": break

def strike_ui():
    while True:
        banner()
        opts = [
            f"{Colors.YELLOW}[1]{Colors.END} Ağdaki Herkesi Düşür (Broadcast)",
            f"{Colors.YELLOW}[2]{Colors.END} Spesifik Cihazı Düşür (Targeted)",
            f"{Colors.YELLOW}[3]{Colors.END} Beacon Spam (Etrafa Sahte Ağlar Yay)",
            f"{Colors.YELLOW}[4]{Colors.END} Chaos Modu (Tam Otomatik Kitle İmha)",
            f"{Colors.YELLOW}[5]{Colors.END} Evil Twin (Rogue AP & Captive Portal)",
            f"{Colors.YELLOW}[0]{Colors.END} Geri"
        ]
        menu_box("STRIKE - DEAUTH SALDIRISI", opts)
        sub = input(f"\n    {Colors.BOLD}Pulse/Strike #{Colors.END} ")
        
        if sub in ["1", "2", "5"]:
            iface = select_interface()
            if not iface: continue
            
            if sub == "5" and iface.endswith("mon"):
                print(f"    {Colors.RED}[!] Evil Twin için adaptör Manage modunda (ör: wlan0) olmalıdır, 'mon' değil.{Colors.END}")
                print(f"    {Colors.YELLOW}[*] 'Engine' menüsünden Monitör Modunu kapatıp tekrar gelin.{Colors.END}"); time.sleep(3); continue

            if sub in ["1", "2"]:
                _, _, iface = engine.toggle_monitor(iface, "start")

            print(f"\n    {Colors.CYAN}[*] Hedef seçimi için etraf taranıyor...{Colors.END}")
            if sub == "5":
                # Evil Twin için geçici monitör aç-kapat izleme yapalım
                _, _, mon_iface = engine.toggle_monitor(iface, "start")
                found_nets = radar.auto_scan_and_select(mon_iface)
                engine.toggle_monitor(mon_iface, "stop")
            else:
                found_nets = radar.auto_scan_and_select(iface) 
                
            if not found_nets: continue
            
            print(f"\n    {Colors.CYAN}{'ID':<3} {'SİNYAL':<15} {'SSID':<25} {'BSSID':<20} {'CH'}{Colors.END}")
            for i, net in enumerate(found_nets):
                bar = radar.get_signal_bar(net['dbm'])
                print(f"    {Colors.YELLOW}[{i}]{Colors.END} {bar:<15} {net['essid'][:23]:<25} {net['bssid']:<20} {net['ch']}")
            
            secim = input(f"\n    Hedef ağ (ID): ")
            if secim.isdigit() and int(secim) < len(found_nets):
                target = found_nets[int(secim)]
                if sub in ["1", "2"]:
                    engine.run_cmd(f"sudo iwconfig {iface} channel {target['ch']}")
                    client = input("    Düşürülecek Cihaz MAC (Boş bırakırsan ağdaki herkes düşer): ") if sub == "2" else None
                    timer = input("    Saldırı Süresi (Saniye, sınırsız için 0 veya Enter'a bas): ")
                    timer = int(timer) if timer.isdigit() else 0
                    strike.pulse_kick(iface, target['bssid'], client, timer)
                    input("\n    Devam etmek için Enter...")
                elif sub == "5":
                    eviltwin.start_evil_twin(iface, target['essid'], target['ch'])
                    input("\n    Devam etmek için Enter...")
            else:
                print("    [!] Geçersiz seçim. Lütfen listedeki numaralardan birini girin."); time.sleep(1.5)
        
        elif sub == "3":
            iface = select_interface()
            if iface:
                _, _, iface = engine.toggle_monitor(iface, "start")
                strike.beacon_spam(iface)
                input("\n    Devam etmek için Enter...")
                
        elif sub == "4":
            iface = select_interface()
            if iface:
                _, _, iface = engine.toggle_monitor(iface, "start")
                strike.chaos_mode(iface)
                input("\n    Devam etmek için Enter...")
                
        elif sub == "0": break

def decrypt_ui():
    while True:
        banner()
        opts = [
            f"{Colors.YELLOW}[1]{Colors.END} Aircrack İle Kır (CPU - Standart)",
            f"{Colors.YELLOW}[2]{Colors.END} Smart Brute (Sadece Rakamlar vb.)",
            f"{Colors.YELLOW}[3]{Colors.END} Hashcat İle Kır (GPU - Ultra Hızlı)",
            f"{Colors.YELLOW}[4]{Colors.END} Handshake Doğrula",
            f"{Colors.YELLOW}[0]{Colors.END} Geri"
        ]
        menu_box("DECRYPT / ŞİFRE KIRMA", opts)
        sub = input(f"\n    {Colors.BOLD}Pulse/Decrypt #{Colors.END} ")
        if sub in ["1", "2", "3", "4"]:
            cap = input("    .cap Dosyasının Yolu (Örn: hedef1-01.cap): ")
            
            if sub == "1": 
                wl = input("    Wordlist Yolu (Enter'a basarsan varsayılan '/usr/share/wordlists/rockyou.txt' kullanılır): ") or "/usr/share/wordlists/rockyou.txt"
                decrypt.wordlist_attack(cap, wl)
                
            elif sub == "2": 
                essid = input("    Hedef Ağın Adı (ESSID): ")
                charset = input("    Karakter Seti (Enter'a basarsan varsayılan '0123456789' kullanılır): ") or "0123456789"
                length_str = input("    Şifre Uzunluğu (Enter'a basarsan varsayılan 8 kullanılır): ") or "8"
                decrypt.brute_force(cap, essid, charset, int(length_str))
                
            elif sub == "3": 
                wl = input("    Wordlist Yolu (Enter'a basarsan varsayılan '/usr/share/wordlists/rockyou.txt' kullanılır): ") or "/usr/share/wordlists/rockyou.txt"
                decrypt.hashcat_attack(cap, wl)
                
            elif sub == "4": 
                strike.verify_handshake(cap)
                
            input("\n    Devam etmek için Enter...")
        elif sub == "0": break

def main():
    try:
        while True:
            banner()
            opts = [
                f"{Colors.YELLOW}[1]{Colors.END} ENGINE  (Sistem & Gizlilik)",
                f"{Colors.YELLOW}[2]{Colors.END} RADAR   (Keşif & Hedef Seçimi)",
                f"{Colors.YELLOW}[3]{Colors.END} STRIKE  (Saldırı & Deauth)",
                f"{Colors.YELLOW}[4]{Colors.END} DECRYPT (Şifre Kırma & Analiz)",
                f"{Colors.YELLOW}[0]{Colors.END} Çıkış"
            ]
            menu_box("KATEGORİLER (Önerilen Akış Sırası)", opts)
            choice = input(f"\n    {Colors.BOLD}Pulse #{Colors.END} ")
            if choice == "1": engine_ui()
            elif choice == "2": radar_ui()
            elif choice == "3": strike_ui()
            elif choice == "4": decrypt_ui()
            elif choice == "0": print(f"\n    {Colors.BLUE}[*] Pulse kesiliyor... Ağ ayarları onarılıyor...{Colors.END}"); break
    except KeyboardInterrupt: print(f"\n    {Colors.RED}[!] Acil çıkış yapıldı! Ağ ayarları kurtarılıyor...{Colors.END}")
    finally:
        ifaces = engine.get_interfaces()
        if ifaces: 
            gercek_isim = ifaces[0].replace('mon', '')
            engine.toggle_monitor(ifaces[0], "stop")
            print(f"    {Colors.BLUE}[*] Orijinal kimliğe (MAC) dönülüyor...{Colors.END}")
            engine.change_mac(gercek_isim, "reset")

if __name__ == "__main__":
    main()