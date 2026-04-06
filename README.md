<div align="center">

# 📡 PulseWifi 
### Advanced Wi-Fi Security & Penetration Suite

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?style=for-the-badge&logo=python)
![OS](https://img.shields.io/badge/Sistem-Kali%20Linux-orange.svg?style=for-the-badge&logo=kali-linux)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen.svg?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-red.svg?style=for-the-badge)

**[English](#-english) | [Türkçe](#-türkçe)**

PulseWifi is a modular, high-performance TUI (Text User Interface) tool designed to automate complex Wi-Fi security auditing processes. It bridges the gap between raw command-line tools and a seamless user experience.

> [!CAUTION]
> **Legal Disclaimer:** This tool is strictly for educational purposes and authorized penetration testing. Misuse of this software can lead to criminal charges. Always obtain explicit permission before testing any network!

</div>

---

## 🇬🇧 English

PulseWifi is built on top of industry-standard tools, providing a unified interface for reconnaissance, attack, and decryption. It handles adapter states and network configurations automatically to ensure your environment stays stable.

### 🚀 Core Modules

| Module | Description |
| :--- | :--- |
| 🛡 **Engine** | High-level adapter management. Enable/Disable Monitor mode and activate the **Privacy Shield** (MAC Randomization). |
| 📡 **Radar** | Passive and active reconnaissance. Offline OUI database for vendor detection and signal-based target prioritizing. |
| ⚡ **Strike** | Automated attacks. Includes Targeted Deauth, Mass Deauth, Beacon Spamming (Chaos Mode), and Evil Twin setups. |
| 🔓 **Decrypt** | Dual-mode cracking. CPU-based Aircrack-ng or high-speed GPU-based Hashcat (converts .cap to .hc22000 automatically). |

### 🛠 Technology Stack
* **Language:** Python 3.8+
* **System Utilities:** `aircrack-ng`, `mdk3`, `macchanger`, `hashcat`, `hcxtools`, `hostapd`, `dnsmasq`
* **Web Portal:** Flask (for Evil Twin Captive Portals)

### 📥 Installation & Usage
```bash
# Clone the repository
git clone https://github.com/eneserbap/PulseWifi.git
cd PulseWifi

# Run installer (Installs all dependencies)
chmod +x install.sh
sudo ./install.sh

# Run PulseWifi
sudo python3 pulse_main.py
```

### 🗺 Roadmap
- [ ] WPS Attack Module (Reaver/Bully integration)
- [ ] Bluetooth Reconnaissance Module
- [ ] Custom Captive Portal Templates
- [ ] Detailed PDF Report Generation

---

## 🇹🇷 Türkçe

PulseWifi, karmaşık Wi-Fi güvenlik denetleme süreçlerini tek bir merkezden yönetmenizi sağlayan, modüler ve yüksek performanslı bir TUI aracıdır. Ham komut satırı araçlarını profesyonel bir kullanıcı deneyimi ile birleştirir.

### 🚀 Temel Modüller

*   🛡 **Engine:** Adaptör yönetimi. Monitör modunu açıp kapatır ve **Gizlilik Kalkanı** (MAC Adresi Rastgeleleştirme) sağlar.
*   📡 **Radar:** Pasif ve aktif keşif. Marka tespiti için çevrimdışı OUI veritabanı ve sinyal gücüne göre hedef sıralama yardımı sağlar.
*   ⚡ **Strike:** Otomasyonlu saldırılar. Hedefli/Genel Deauth, Beacon Spam (Kaos Modu) ve Evil Twin (Şeytani İkiz) kurulumlarını kapsar.
*   🔓 **Decrypt:** Çift modlu şifre kırma. CPU tabanlı Aircrack-ng veya yüksek hızlı GPU tabanlı Hashcat desteği (.cap dosyalarını otomatik .hc22000'e çevirir).

### 🛠 Teknik Altyapı
*   **Dil:** Python 3.8+
*   **Sistem Araçları:** `aircrack-ng`, `mdk3`, `macchanger`, `hashcat`, `hcxtools`, `hostapd`, `dnsmasq`
*   **Web Portal:** Flask (Evil Twin için sahte giriş sayfaları)

### 📥 Kurulum ve Kullanım
```bash
# Depoyu klonlayın
git clone https://github.com/eneserbap/PulseWifi.git
cd PulseWifi

# Kurulumu başlatın (Tüm bağımlılıkları yükler)
chmod +x install.sh
sudo ./install.sh

# Çalıştırın
sudo python3 pulse_main.py
```

### 📅 Gelecek Planları
- [ ] WPS Saldırı Modülü (Reaver/Bully entegrasyonu)
- [ ] Bluetooth Keşif Modülü
- [ ] Özel Captive Portal Temaları
- [ ] Detaylı PDF Rapor Oluşturma

---

<div align="center">
  <p><b>Handcrafted with passion for the Cybersecurity community.</b></p>
  <sub>By EnesErbap</sub>
</div>
