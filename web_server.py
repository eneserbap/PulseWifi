from flask import Flask, render_template, jsonify, request
import os
from modules import engine, radar, strike

app = Flask(__name__)

# Dashboard Ana Sayfası
@app.route('/')
def index():
    return render_template('index.html')

# API: Kartları Listele
@app.route('/api/interfaces')
def get_interfaces():
    ifaces = engine.get_interfaces()
    return jsonify({"interfaces": ifaces})

# API: Monitör Modu Kontrol
@app.route('/api/toggle_monitor', methods=['POST'])
def toggle_monitor():
    data = request.json
    iface = data.get('iface')
    action = data.get('action') # "start" veya "stop"
    status, msg, new_iface = engine.toggle_monitor(iface, action)
    return jsonify({"status": status, "message": msg, "new_iface": new_iface})

if __name__ == '__main__':
    # sudo ile çalışması gerektiği için yetki kontrolü
    if os.geteuid() != 0:
        print("[!] Lütfen web sunucusunu 'sudo' ile çalıştırın!")
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)

@app.route('/api/scan')
def start_scan():
    iface = request.args.get('iface')
    if not iface:
        return jsonify({"status": "error", "message": "Önce bir kart seçmelisin!"})
    
    # Senin radar modülündeki otomatik taramayı çağırıyoruz
    print(f"[*] {iface} üzerinde web üzerinden tarama başlatıldı...")
    found_nets = radar.auto_scan_and_select(iface, scan_time=10) # 10 saniye tara
    
    return jsonify({"status": "success", "networks": found_nets})