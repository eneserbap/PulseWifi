from flask import Flask, render_template, jsonify, request
from flask_cors import CORS  # Yeni ekledik
import os
import sys
from modules import engine, radar, strike

app = Flask(__name__)
CORS(app) # Tüm tarayıcı isteklerine izin ver

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/interfaces')
def get_interfaces():
    try:
        ifaces = engine.get_interfaces()
        return jsonify({"interfaces": ifaces})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/scan')
def start_scan():
    iface = request.args.get('iface')
    if not iface:
        return jsonify({"status": "error", "message": "Kart seçilmedi"}), 400
    
    try:
        print(f"[*] {iface} üzerinde tarama başlatılıyor... Lütfen bekleyin.")
        # Radar taramasını yapıyoruz
        found_nets = radar.auto_scan_and_select(iface, scan_time=10)
        
        print(f"[*] Tarama bitti, {len(found_nets)} ağ bulundu.")
        return jsonify({
            "status": "success", 
            "networks": found_nets
        })
    except Exception as e:
        print(f"[!] KRİTİK HATA: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# API: Monitör Modu Kontrol
@app.route('/api/toggle_monitor', methods=['POST'])
def toggle_monitor():
    data = request.json
    iface = data.get('iface')
    action = data.get('action')
    status, msg, new_iface = engine.toggle_monitor(iface, action)
    return jsonify({"status": status, "message": msg, "new_iface": new_iface})

if __name__ == '__main__':
    if os.geteuid() != 0:
        print("\n[!] HATA: Lütfen 'sudo python3 web_server.py' olarak çalıştırın!\n")
    else:
        # Host 0.0.0.0 önemli, yoksa dışarıdan (telefondan) bağlanamazsın
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)