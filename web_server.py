from flask import Flask, render_template
from modules import engine # Bizim canavar modülü çağırıyoruz

app = Flask(__name__)

# Tarayıcıdan siteye girildiğinde çalışacak fonksiyon
@app.route('/')
def ana_sayfa():
    # Arkada kartları buluyoruz
    kartlar = engine.get_interfaces()
    
    # HTML dosyasına bu kartları gönderiyoruz
    return render_template('index.html', interfaces=kartlar)

if __name__ == '__main__':
    # Sunucuyu başlat (Herkes ağdan bağlanabilsin diye 0.0.0.0 yapıyoruz)
    app.run(host='0.0.0.0', port=5000, debug=True)