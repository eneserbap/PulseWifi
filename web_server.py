import os
import sys
import threading
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from modules import engine, radar, strike

if os.name == 'posix' and os.geteuid() != 0:
    print("    [*] Linux tespit edildi. Root (sudo) yetkisine otomatik geçiliyor...")
    os.execvp("sudo", ["sudo", sys.executable] + sys.argv)

# Flask uygulamasını, ana klasörü (index.html'in bulunduğu yer) statik olarak sunacak şekilde yapılandırıyoruz
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

print("[*] PulseWifi Backend Başlatılıyor...")

def get_default_iface():
    """Mevcut adaptörlerden birini (tercihen monitor modunda olanı) döndürür."""
    ifaces = engine.get_interfaces()
    if ifaces:
        for iface in ifaces:
            if "mon" in iface:
                return iface
        return ifaces[0]
    return "wlan0"

@app.route('/')
def serve_index():
    return send_file('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    ifaces = engine.get_interfaces()
    current_iface = get_default_iface()
    is_monitor = "mon" in current_iface
    return jsonify({
        "status": "success",
        "interface": current_iface,
        "is_monitor": is_monitor,
        "mac": "Spoofed"  # Mock veya gerçek MAC eklenebilir
    })

@app.route('/api/monitor', methods=['POST'])
def toggle_monitor():
    data = request.json or {}
    action = data.get('action', 'start') # 'start' or 'stop'
    current_iface = data.get('interface')
    
    if not current_iface:
        current_iface = get_default_iface()
        
    status, msg, new_iface = engine.toggle_monitor(current_iface, action)
    is_monitor = "mon" in new_iface
    return jsonify({
        "status": "success" if status else "error",
        "message": msg,
        "interface": new_iface,
        "is_monitor": is_monitor
    })

@app.route('/api/scan', methods=['POST'])
def scan_network():
    current_iface = get_default_iface()
    
    if "mon" not in current_iface:
        # Tarama için Monitor Modu zorunlu
        status, msg, current_iface = engine.toggle_monitor(current_iface, "start")

    data = request.json or {}
    scan_time = data.get('scan_time', 15)  # Varsayılan 15 saniye tarama
    
    try:
        # Airodump-ng'yi arka planda başlatıp parse eden mevcut fonksiyon
        found_nets = radar.auto_scan_and_select(current_iface, scan_time)
        return jsonify({
            "status": "success",
            "networks": found_nets,
            "interface": current_iface
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/attack', methods=['POST'])
def launch_attack():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Gönderilen veri bulunamadı."}), 400

    target_bssid = data.get('bssid')
    attack_type = data.get('type')
    duration = int(data.get('duration', 60))
    target_client = data.get('client_mac', None)
    
    current_iface = get_default_iface()
    if "mon" not in current_iface:
        _, _, current_iface = engine.toggle_monitor(current_iface, "start")

    def run_attack():
        print(f"[*] Arka planda saldırı tetiklendi: {attack_type} BSSID: {target_bssid}")
        try:
            if 'Deauth' in attack_type:
                # Target client None ise broadcast atar (modules/strike.py içindeki gibi)
                strike.pulse_kick(current_iface, target_bssid, target_client, duration)
            elif 'Beacon Flood' in attack_type:
                strike.beacon_spam(current_iface)
            else:
                print(f"[!] Henüz web arayüzüne bağlanmamış saldırı tipi: {attack_type}")
        except Exception as e:
            print(f"[!] Saldırı yürütülürken hata oluştu: {e}")

    # Saldırının web paneli dondurmaması için (airodump/aireplay blocking olabilir), Thread ile asenkron çalıştırıyoruz.
    t = threading.Thread(target=run_attack)
    t.start()
    
    return jsonify({
        "status": "success",
        "message": f"{attack_type} saldırısı başlatıldı!",
        "target": target_bssid,
        "duration": duration
    })

from modules import decrypt

@app.route('/api/system/interfaces', methods=['GET'])
def get_interfaces():
    ifaces = engine.get_interfaces()
    return jsonify({
        "status": "success",
        "interfaces": ifaces
    })

@app.route('/api/engine/mac', methods=['POST'])
def spoof_mac():
    data = request.json or {}
    action = data.get('action', 'random') # 'random' or 'reset'
    
    current_iface = get_default_iface()
    try:
        engine.change_mac(current_iface, action)
        msg = "Gerçek kimliğe geri dönüldü." if action == "reset" else "Rastgele sahte kimlik atandı (Spoofed)."
        return jsonify({"status": "success", "message": msg})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/decrypt', methods=['POST'])
def start_decrypt():
    data = request.json or {}
    engine_type = data.get('engine', 'cpu') # 'cpu' (aircrack) or 'gpu' (hashcat) or 'brute'
    cap_file = data.get('cap_file', '')
    
    if not cap_file:
        return jsonify({"status": "error", "message": ".cap dosyası belirtilmedi."}), 400

    def run_decrypt():
        print(f"[*] Arka planda şifre kılıcı tetiklendi: {engine_type}")
        try:
            if engine_type == 'cpu':
                wordlist = data.get('wordlist', '/usr/share/wordlists/rockyou.txt')
                decrypt.wordlist_attack(cap_file, wordlist)
            elif engine_type == 'gpu':
                wordlist = data.get('wordlist', '/usr/share/wordlists/rockyou.txt')
                decrypt.hashcat_attack(cap_file, wordlist)
            elif engine_type == 'brute':
                essid = data.get('essid', 'unknown')
                charset = data.get('charset', '0123456789')
                length = int(data.get('length', 8))
                decrypt.brute_force(cap_file, essid, charset, length)
        except Exception as e:
            print(f"[!] Kırma işlemi başarısız: {e}")

    t = threading.Thread(target=run_decrypt)
    t.start()
    
    return jsonify({
        "status": "success",
        "message": f"Şifre kırma motoru ({engine_type}) başlatıldı."
    })

if __name__ == '__main__':
    # 0.0.0.0 sayesinde sadece localhost değil ağdaki diğer cihazlardan da panele erişebilirsiniz.
    app.run(host='0.0.0.0', port=5000)
