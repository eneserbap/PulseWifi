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
        return jsonify({"status": "error", "message": "Kart seçilmedi"}), 400
    
    try:
        # ÖNEMLİ: engine modülünde kartın monitör modunda olduğundan emin olmalıyız
        # Eğer kart monitör modunda değilse hata verebilir
        print(f"[*] {iface} üzerinde tarama yapılıyor...")
        
        # Senin radar modülündeki fonksiyonu çağırıyoruz
        found_nets = radar.auto_scan_and_select(iface, scan_time=10)
        
        # Eğer liste boş dönerse bile JSON formatında boş liste gönderiyoruz
        return jsonify({
            "status": "success", 
            "networks": found_nets if found_nets else []
        })
    except Exception as e:
        print(f"[!] Tarama hatası: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500