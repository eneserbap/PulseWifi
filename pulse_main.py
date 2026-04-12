import os
import time
import sys
import re
import subprocess
from modules import engine, radar, strike, decrypt, eviltwin, i18n
t = i18n.t
if os.name == 'posix' and os.geteuid() != 0:
    print(t("root_escalation"))
    os.execvp("sudo", ["sudo", sys.executable] + sys.argv)
class Colors:
    BLUE, GREEN, YELLOW, RED, BOLD, END, CYAN = '\033[94m', '\033[92m', '\033[93m', '\033[91m', '\033[1m', '\033[0m', '\033[96m'

USED_IFACES = set()


# --- BANNER/UI ELEMENTS (Arayüz Elemanları) ---
def banner():
    try:
        if os.name == 'posix': subprocess.run(["clear"])
        else: subprocess.run(["cls"], shell=True) 
    except: pass
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


# --- NETWORK INTERFACE CHOOSER (Ağ Kartı Seçici) ---
def select_interface():
    ifaces = engine.get_interfaces()
    if not ifaces:
        print(f"    {Colors.RED}{t('no_wifi_card').strip()}{Colors.END}"); time.sleep(2); return None
    print(f"\n    {Colors.BOLD}{t('existing_wifi_cards').strip()}{Colors.END}")
    for i, name in enumerate(ifaces): print(f"    {Colors.YELLOW}[{i}]{Colors.END} {name}")
    try: 
        sel = ifaces[int(input(f"\n    {Colors.CYAN}{t('iface_prompt').strip()}{Colors.END} "))]
        USED_IFACES.add(sel)
        return sel
    except (ValueError, IndexError): return None


# --- ENGINE MENU (Motor Menüsü) ---
def engine_ui():
    while True:
        banner()
        opts = [
            f"{Colors.YELLOW}[1]{Colors.END} {t('menu_engine_opt1').replace('[1] ', '')}",
            f"{Colors.YELLOW}[2]{Colors.END} {t('menu_engine_opt2').replace('[2] ', '')}",
            f"{Colors.YELLOW}[3]{Colors.END} {t('menu_engine_opt3').replace('[3] ', '')}",
            f"{Colors.YELLOW}[4]{Colors.END} {t('menu_engine_opt4').replace('[4] ', '')}",
            f"{Colors.YELLOW}[0]{Colors.END} {t('menu_return').replace('[0] ', '')}"
        ]
        menu_box(t("menu_engine_title"), opts)
        sub = input(f"\n    {Colors.BOLD}{t('engine_prompt').strip()}{Colors.END} ")
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
                print(t("mac_fake_success")); time.sleep(2)
            elif sub == "4":
                engine.change_mac(iface, "reset")
                print(t("mac_original_success")); time.sleep(2)
        elif sub == "0": break


# --- RADAR MENU (Keşif Menüsü) ---
def radar_ui():
    while True:
        banner()
        opts = [
            f"{Colors.YELLOW}[1]{Colors.END} {t('menu_radar_opt1').replace('[1] ', '')}",
            f"{Colors.YELLOW}[2]{Colors.END} {t('menu_radar_opt2').replace('[2] ', '')}",
            f"{Colors.YELLOW}[0]{Colors.END} {t('menu_radar_opt0').replace('[0] ', '')}"
        ]
        menu_box(t("menu_radar_title"), opts)
        sub = input(f"\n    {Colors.BOLD}{t('radar_prompt').strip()}{Colors.END} ")
        if sub == "1":
            iface = select_interface()
            if iface:
                success, msg, iface = engine.toggle_monitor(iface, "start")
                if not success:
                    print(f"    {Colors.RED}{msg}{Colors.END}")
                    time.sleep(3)
                    continue
                found_nets = radar.auto_scan_and_select(iface) 
                if not found_nets: print(f"    {Colors.RED}{t('radar_no_nets')}{Colors.END}"); time.sleep(2); continue
                print(f"\n    {Colors.CYAN}{t('radar_table_header')}{Colors.END}")
                print("    " + "-"*84)
                for i, net in enumerate(found_nets):
                    bar = radar.get_signal_bar(net['dbm'])
                    freq = net.get('freq_label', '')
                    print(f"    {Colors.YELLOW}[{i}]{Colors.END} {bar:<15} {net['essid'][:18]:<20} {freq:<18} {net['vendor']:<12} {net['bssid']:<18} Ch:{net['ch']}")
                secim = input(t("radar_target_prompt", max_id=len(found_nets)-1))
                if secim.isdigit() and int(secim) < len(found_nets):
                    target = found_nets[int(secim)]
                    print(t("radar_target_selected", essid=target['essid'], vendor=target['vendor']))
                    dosya_adi = input(t("radar_save_prompt")).strip()
                    if not dosya_adi: dosya_adi = f"scan_{target['bssid'].replace(':', '')}"
                    radar.target_lock(iface, target['bssid'], target['ch'], dosya_adi)
                else: print(t("radar_invalid_selection")); time.sleep(1.5)
        elif sub == "2":
            iface = select_interface()
            if iface:
                success, msg, iface = engine.toggle_monitor(iface, "start")
                if not success:
                    print(f"    {Colors.RED}{msg}{Colors.END}")
                    time.sleep(3)
                    continue
                radar.scan_all(iface)
        elif sub == "0": break


# --- STRIKE MENU (Saldırı Menüsü) ---
def strike_ui():
    while True:
        banner()
        opts = [
            f"{Colors.YELLOW}[1]{Colors.END} {t('menu_strike_opt1').replace('[1] ', '')}",
            f"{Colors.YELLOW}[2]{Colors.END} {t('menu_strike_opt2').replace('[2] ', '')}",
            f"{Colors.YELLOW}[3]{Colors.END} {t('menu_strike_opt3').replace('[3] ', '')}",
            f"{Colors.YELLOW}[4]{Colors.END} {t('menu_strike_opt4').replace('[4] ', '')}",
            f"{Colors.YELLOW}[5]{Colors.END} {t('menu_strike_opt5').replace('[5] ', '')}",
            f"{Colors.YELLOW}[6]{Colors.END} {t('menu_strike_opt6').replace('[6] ', '')}",
            f"{Colors.YELLOW}[0]{Colors.END} {t('menu_radar_opt0').replace('[0] ', '')}"
        ]
        menu_box(t("menu_strike_title"), opts)
        sub = input(f"\n    {Colors.BOLD}{t('strike_prompt').strip()}{Colors.END} ")
        if sub in ["1", "2", "5", "6"]:
            iface = select_interface()
            if not iface: continue
            if sub == "5" and engine.is_monitor(iface):
                print(f"    {Colors.RED}{t('strike_evil_twin_error')}{Colors.END}")
                print(f"    {Colors.YELLOW}{t('strike_evil_twin_hint')}{Colors.END}"); time.sleep(3); continue
            if sub in ["1", "2"]:
                success, msg, iface = engine.toggle_monitor(iface, "start")
                if not success:
                    print(f"    {Colors.RED}{msg}{Colors.END}")
                    time.sleep(3)
                    continue
            print(f"\n    {Colors.CYAN}[*] Hedef seçimi için etraf taranıyor...{Colors.END}")
            if sub == "5":
                success, msg, iface = engine.toggle_monitor(iface, "start")
                if not success:
                    print(f"    {Colors.RED}{msg}{Colors.END}")
                    time.sleep(3)
                    continue
                USED_IFACES.add(iface)
                print(f"    {Colors.CYAN}[*] Fedora için derin tarama yapılıyor (20sn)...{Colors.END}")
                found_nets = radar.auto_scan_and_select(iface, scan_time=20)
                
                if not found_nets:
                    print(f"    {Colors.RED}[!] Hiçbir ağ bulunamadı! Kartın kapsama alanında olduğundan emin ol.{Colors.END}")
                    time.sleep(3)
                    continue
                # DÜZELTME: Kart taramadan sonra kapanmalı değil, Evil Twin modülü yönetecek
            else:
                found_nets = radar.auto_scan_and_select(iface) 
            if not found_nets: continue
            print(f"\n    {Colors.CYAN}{t('strike_table_header')}{Colors.END}")
            print("    " + "-"*84)
            for i, net in enumerate(found_nets):
                bar = radar.get_signal_bar(net['dbm'])
                freq = net.get('freq_label', '')
                print(f"    {Colors.YELLOW}[{i}]{Colors.END} {bar:<15} {net['essid'][:18]:<20} {freq:<18} {net['bssid']:<20} Ch:{net['ch']}")
            secim = input(t("strike_target_prompt")).strip()
            if secim.isdigit() and int(secim) < len(found_nets):
                target = found_nets[int(secim)]
                if sub in ["1", "2"]:
                    client = input(t("strike_client_prompt")).strip() if sub == "2" else None
                    if not client: client = None
                    timer_input = input(t("strike_timer_prompt")).strip()
                    timer = int(timer_input) if timer_input.isdigit() else 0
                    strike.pulse_kick(iface, target['bssid'], client, timer, channel=target['ch'])
                    input(t("strike_press_enter"))
                elif sub == "5":
                    eviltwin.start_evil_twin(iface, target['essid'], target['ch'])
                    input(t("strike_press_enter"))
                elif sub == "6":
                    strike.mesh_strike(iface, target['essid'], channel=target['ch'])
                    input(t("strike_press_enter"))
            else:
                if sub == "6":
                    ssid = input(t("strike_mesh_prompt")).strip()
                    if ssid:
                        strike.mesh_strike(iface, ssid)
                        input(t("strike_press_enter"))
                    else:
                        print(f"    {Colors.RED}{t('radar_invalid_selection')}{Colors.END}"); time.sleep(1.5)
                else:
                    print(t("radar_invalid_selection")); time.sleep(1.5)
        elif sub == "3":
            iface = select_interface()
            if iface:
                success, msg, iface = engine.toggle_monitor(iface, "start")
                if not success:
                    print(f"    {Colors.RED}{msg}{Colors.END}")
                    time.sleep(3)
                    continue
                strike.beacon_spam(iface)
                input(t("strike_press_enter"))
        elif sub == "4":
            iface = select_interface()
            if iface:
                success, msg, iface = engine.toggle_monitor(iface, "start")
                if not success:
                    print(f"    {Colors.RED}{msg}{Colors.END}")
                    time.sleep(3)
                    continue
                strike.chaos_mode(iface)
                input(t("strike_press_enter"))
        elif sub == "0": break


# --- DECRYPT MENU (Şifre Kırma Menüsü) ---
def decrypt_ui():
    while True:
        banner()
        opts = [
            f"{Colors.YELLOW}[1]{Colors.END} {t('menu_decrypt_opt1').replace('[1] ', '')}",
            f"{Colors.YELLOW}[2]{Colors.END} {t('menu_decrypt_opt2').replace('[2] ', '')}",
            f"{Colors.YELLOW}[3]{Colors.END} {t('menu_decrypt_opt3').replace('[3] ', '')}",
            f"{Colors.YELLOW}[4]{Colors.END} {t('menu_decrypt_opt4').replace('[4] ', '')}",
            f"{Colors.YELLOW}[0]{Colors.END} {t('menu_radar_opt0').replace('[0] ', '')}"
        ]
        menu_box(t("menu_decrypt_title"), opts)
        sub = input(f"\n    {Colors.BOLD}{t('decrypt_prompt').strip()}{Colors.END} ")
        if sub in ["1", "2", "3", "4"]:
            cap = input(t("decrypt_cap_prompt")).strip()
            if not cap: continue
            if sub == "1": 
                wl = input(t("decrypt_wl_prompt")) or "/usr/share/wordlists/rockyou.txt"
                decrypt.wordlist_attack(cap, wl)
            elif sub == "2": 
                essid = input(t("decrypt_essid_prompt"))
                charset = input(t("decrypt_charset_prompt")) or "0123456789"
                length_str = input(t("decrypt_length_prompt")) or "8"
                decrypt.brute_force(cap, essid, charset, int(length_str))
            elif sub == "3": 
                wl = input(t("decrypt_wl_prompt")) or "/usr/share/wordlists/rockyou.txt"
                decrypt.hashcat_attack(cap, wl)
            elif sub == "4": 
                strike.verify_handshake(cap)
            input(t("strike_press_enter"))
        elif sub == "0": break


# --- MAIN EXECUTION (Ana Yürütme) ---
def main():
    try:
        while True:
            banner()
            opts = [
                f"{Colors.YELLOW}[1]{Colors.END} {t('menu_main_opt1').replace('[1] ', '')}",
                f"{Colors.YELLOW}[2]{Colors.END} {t('menu_main_opt2').replace('[2] ', '')}",
                f"{Colors.YELLOW}[3]{Colors.END} {t('menu_main_opt3').replace('[3] ', '')}",
                f"{Colors.YELLOW}[4]{Colors.END} {t('menu_main_opt4').replace('[4] ', '')}",
                f"{Colors.YELLOW}[0]{Colors.END} {t('menu_main_opt0').replace('[0] ', '')}"
            ]
            menu_box(t("menu_main_title"), opts)
            choice = input(f"\n    {Colors.BOLD}{t('main_prompt').strip()}{Colors.END} ")
            if choice == "1": engine_ui()
            elif choice == "2": radar_ui()
            elif choice == "3": strike_ui()
            elif choice == "4": decrypt_ui()
            elif choice == "0": print(f"{Colors.BLUE}{t('main_exit')}{Colors.END}"); break
    except KeyboardInterrupt: print(f"{Colors.RED}{t('main_emergency_exit')}{Colors.END}")
    finally:
        ifaces = engine.get_interfaces()
        for iface in ifaces:
            base_name = iface.replace("mon", "")
            if iface in USED_IFACES or base_name in USED_IFACES or (base_name+"mon") in USED_IFACES:
                if engine.is_monitor(iface):
                    engine.toggle_monitor(iface, "stop")
                engine.change_mac(iface, "reset")
        
        print(f"{Colors.BLUE}{t('main_restore_mac')}{Colors.END}")
        engine.cleanup()

if __name__ == "__main__":
    main()
