from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
import sys
from modules import engine, radar, strike

app = Flask(__name__)
# CORS desteği: Tarayıcının "Network Error" vermesini engeller
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 1. Dashboard Ana Sayfası
@app.route('/')
def index():
    return render_template('index.html')

# 2. API: Kartları Listele
@app.route('/api/interfaces')
def get_interfaces():
    try:
        ifaces = engine.get_interfaces()
        return jsonify({"interfaces": ifaces})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 3. API: Radar Taramasını Başlat
@app.route('/api/scan')
def start_scan():
    iface = request.args.get('iface')
    if not iface:
        return jsonify({"status": "error", "message": "Kart seçilmedi!"}), 400
    
    try:
        print(f"[*] {iface} üzerinde tarama başlatılıyor... Lütfen 10 saniye bekleyin.")
        # Senin radar modülündeki tarama fonksiyonunu çağırıyoruz
        found_nets = radar.auto_scan_and_select(iface, scan_time=10)
        
        print(f"[*] Tarama bitti, {len(found_nets)} ağ bulundu.")
        return jsonify({
            "status": "success", 
            "networks": found_nets
        })
    except Exception as e:
        print(f"[!] Tarama Hatası: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# 4. API: Monitör Modu & MAC Kontrol
@app.route('/api/toggle_monitor', methods=['POST'])
def toggle_monitor():
    try:
        data = request.json
        iface = data.get('iface')
        action = data.get('action') # "start" veya "stop"
        status, msg, new_iface = engine.toggle_monitor(iface, action)
        return jsonify({"status": status, "message": msg, "new_iface": new_iface})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 5. SUNUCUYU BAŞLAT (Her zaman en sonda olmalı!)
if __name__ == '__main__':
    # sudo kontrolü
    if os.geteuid() != 0:
        print("\n" + "="*50)
        print("[!] HATA: Lütfen 'sudo python3 web_server.py' olarak çalıştırın!")
        print("="*50 + "\n")
    else:
        print("\n[*] PulseWifi Web Sunucusu Başlatılıyor...")
        print("[*] Adres: http://localhost:5000")
        print("[*] Durdurmak için: CTRL+C\n")
        
        # use_reloader=False ve debug=True çakışmaları önlemek için idealdir
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)