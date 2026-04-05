from flask import Flask, render_template, jsonify, request
import os
from modules import engine, radar, strike

app = Flask(__name__)

# --- BÜTÜN ROTALAR (ROUTE) BURADA OLMALI ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/interfaces')
def get_interfaces():
    ifaces = engine.get_interfaces()
    return jsonify({"interfaces": ifaces})

@app.route('/api/toggle_monitor', methods=['POST'])
def toggle_monitor():
    data = request.json
    iface = data.get('iface')
    action = data.get('action')
    status, msg, new_iface = engine.toggle_monitor(iface, action)
    return jsonify({"status": status, "message": msg, "new_iface": new_iface})

@app.route('/api/scan') # <--- BU ARTIK YUKARIDA, YANİ KAYITLI
def start_scan():
    iface = request.args.get('iface')
    if not iface:
        return jsonify({"status": "error", "message": "Kart seçilmedi"}), 400
    try:
        print(f"[*] {iface} üzerinde tarama yapılıyor...")
        found_nets = radar.auto_scan_and_select(iface, scan_time=10)
        return jsonify({
            "status": "success", 
            "networks": found_nets if found_nets else []
        })
    except Exception as e:
        print(f"[!] Tarama hatası: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- SUNUCUYU BAŞLATAN KOMUT HER ZAMAN EN SONDA OLMALI ---

if __name__ == '__main__':
    if os.geteuid() != 0:
        print("[!] Lütfen web sunucusunu 'sudo' ile çalıştırın!")
    else:
        # Debug=True sayesinde kodda hata olursa terminalde detaylı görürsün
        app.run(host='0.0.0.0', port=5000, debug=True)