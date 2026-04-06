<div align="center">

# 📡 PulseWifi - Ultimate Wi-Fi Penetration Suite

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OS](https://img.shields.io/badge/OS-Kali%20Linux%20%7C%20Parrot%20%7C%20Ubuntu-orange.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-red.svg)

**[English](#english) | [Türkçe](#türkçe)**

PulseWifi is an advanced, automated, and modular TUI (Text User Interface) tool designed for Wi-Fi security auditing, penetration testing, and vulnerability analysis.

> ⚠️ **Disclaimer:** This tool is strictly for educational purposes and ethical hacking. The authors are not responsible for any misuse or legal actions. Always have permission before testing any network!

<br>
</div>

---

<h2 id="english">🇬🇧 English Readme</h2>

PulseWifi combines the power of tools like `aircrack-ng`, `mdk3`, `hashcat`, and `macchanger` down to a single, interactive, and aesthetic dashboard. It automatically manages your adapters, cleans up residual configurations, and prevents connectivity loss after your tasks are done.

<img width="970" height="559" alt="image" src="https://github.com/user-attachments/assets/469cad02-d455-49de-960e-059fc7d6c434" />


### 🌟 Key Features
* 🛡 **Engine:** Auto-manage monitor mode and randomize your MAC Address (Privacy Shield).
* 📡 **Radar:** Find the closest targets, determine vendor device info offline, and lock on APs automatically.
* ⚡ **Strike:** Targeted Deauth, Mass Deauth, Beacon Spam (Troll & Chaos Modes), and automated Evil Twin (Captive Portal DNS hijacking).
* 🔓 **Decrypt:** Integrates Aircrack-ng for CPU-based cracking and Hashcat (hcxtools) for ultra-fast GPU processing.

### 🚀 Installation
```bash
git clone https://github.com/eneserbap/PulseWifi.git
cd PulseWifi
chmod +x install.sh
sudo ./install.sh
```

### 🎮 Usage
You must run PulseWifi as Root (Sudo).
```bash
sudo python3 pulse_main.py
```
> **Multi-Language:** PulseWifi auto-detects your system language. You can manually change it via the generated `config.json`!

---

<h2 id="türkçe">🇹🇷 Türkçe Readme</h2>

PulseWifi; `aircrack-ng`, `mdk3`, `hashcat` ve `macchanger` gibi endüstri standardı araçları tek bir ekranda toplayan profesyonel ve TUI (Metin Tabanlı Arayüz) destekli bir siber güvenlik Wi-Fi otomasyon aracıdır.

Saldırı veya dinleme işleminden sonra ağ ayarlarınızı, servislerinizi (NetworkManager vb.) ve MAC adresinizi otomatik olarak orijinal haline getirerek geride iz bırakmamanızı sağlar.
<img width="945" height="563" alt="image" src="https://github.com/user-attachments/assets/2f8ee900-23e1-4abb-9c59-e225a6ee3bac" />

### 🌟 Temel Özellikler
* 🛡 **Engine (Motor):** Ağ kartını otomatik Monitör porta çeker, veya "Gizlilik Kalkanı" başlatarak MAC adresinizi değiştirir.
* 📡 **Radar (Keşif):** Çevreyi tarar, hedefleri sinyal gücüne göre listeler ve cihaz markalarını (Offline OUI veritabanı ile) analiz eder.
* ⚡ **Strike (Saldırı):** İster tek hedefe, ister herkese deauth (düşürme) atın. Dilerseniz Chaos Mode ile tüm mahalleyi kilitleyin veya Evil Twin (Şeytani İkiz) oluşturup kullanıcıların şifresini Captive Portal ile yakalayın.
* 🔓 **Decrypt (Kırma):** Sadece Aircrack ile kalmaz, `.cap` dosyalarını `.hc22000`'e çevirerek Ekran Kartı (GPU) destekli ultra hızlı *Hashcat* kırımına olanak tanır.

### 🚀 Kurulum
```bash
git clone https://github.com/eneserbap/PulseWifi.git
cd PulseWifi
chmod +x install.sh
sudo ./install.sh
```

### 🎮 Kullanım
Dosyayı doğrudan çalıştırdığınızda (eğer root değilseniz) sizden Root şifresi isteyerek yetkiyi devralacaktır.
```bash
sudo python3 pulse_main.py
```
> **Çoklu Dil Desteği:** PulseWifi dilinizi otomatik algılar. Dilerseniz oluşan `config.json` dosyası içinden menü dilini `tr` veya `en` olarak manuel biçimde ayarlayabilirsiniz!

---

<div align="center">
<i>Developed entirely with passion by <b>EnesErbap</b></i>
</div>
