import os
import time
from modules import engine, radar, strike

# Renkler (Her dosyada kullanabilirsin)
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'
    CYAN = '\033[96m'

def banner():
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

def main_menu():
    while True: # İŞTE BURASI: Programın kapanmasını engelleyen ana döngü
        banner()
        print(f"\n{Colors.BOLD}    ╔═══════════════════ ANA MENÜ ═══════════════════╗{Colors.END}")
        print(f"    ║                                            ║")
        print(f"    ║  {Colors.YELLOW}[1]{Colors.END} RADAR  (Ağ Tarama & Keşif)          ║")
        print(f"    ║  {Colors.YELLOW}[2]{Colors.END} STRIKE (Saldırı & Paket Yakalama)    ║")
        print(f"    ║  {Colors.YELLOW}[3]{Colors.END} ENGINE (Adaptör & Monitör Modu)     ║")
        print(f"    ║  {Colors.YELLOW}[0]{Colors.END} Çıkış                              ║")
        print(f"    ║                                            ║")
        print(f"{Colors.BOLD}    ╚════════════════════════════════════════════╝{Colors.END}")
        
        choice = input(f"\n    {Colors.BOLD}Pulse #{Colors.END} ")

        if choice == "1":
            radar_submenu() # Radar menüsüne dallan
        elif choice == "2":
            strike_submenu() # Strike menüsüne dallan
        elif choice == "3":
            engine_submenu() # Engine menüsüne dallan
        elif choice == "0":
            print(f"\n    {Colors.BLUE}[*] Pulse kesiliyor... Güle güle!{Colors.END}")
            break # Döngüden çık ve programı kapat
        else:
            print(f"    {Colors.RED}[!] Geçersiz seçim!{Colors.END}")
            time.sleep(1)

# Alt Menü Örneği (Diğerleri için de benzerini yapabilirsin)
def engine_submenu():
    while True:
        banner()
        print(f"    {Colors.CYAN}Kategori: ENGINE (Sistem){Colors.END}")
        print(f"\n    ╔════════════════════════════════════════════╗")
        print(f"    ║  {Colors.YELLOW}[1]{Colors.END} Monitor Modu AÇ                   ║")
        print(f"    ║  {Colors.YELLOW}[2]{Colors.END} Monitor Modu KAPAT                ║")
        print(f"    ║  {Colors.YELLOW}[0]{Colors.END} Ana Menüye Dön                    ║")
        print(f"    ╚════════════════════════════════════════════╝")
        
        sub_choice = input(f"\n    {Colors.BOLD}Pulse/Engine #{Colors.END} ")
        
        if sub_choice == "1":
            iface = input("    Kart: ")
            engine.toggle_monitor(iface, mode="start")
        elif sub_choice == "2":
            iface = input("    Kart: ")
            engine.toggle_monitor(iface, mode="stop")
        elif sub_choice == "0":
            break

if __name__ == "__main__":
    main_menu()