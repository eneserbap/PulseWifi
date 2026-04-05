#!/bin/bash

# Renk kodları (Görsellik önemli)
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}[*] PulseWifi Kurulum Sihirbazı Başlatılıyor...${NC}"

# 1. Sistem Güncelleme
echo -e "${YELLOW}[1/4] Sistem paket listeleri güncelleniyor...${NC}"
sudo apt update -y

# 2. Temel Siber Güvenlik Araçları
echo -e "${YELLOW}[2/4] Kablosuz ağ araçları kuruluyor (Aircrack-ng, MDK3, MacChanger)...${NC}"
# macchanger-gtk kurmuyoruz ki terminalde kalsın, mdk3 beacon spam için şart
sudo apt install aircrack-ng mdk3 macchanger python3-pip -y

# 3. Python Kütüphaneleri
echo -e "${YELLOW}[3/4] Python bağımlılıkları yükleniyor...${NC}"
# Flask'ı sildik dedin ama kurulumda olması zarar vermez, ileride açınca hazır olur
sudo apt install python3-flask -y 2>/dev/null || pip3 install flask

# 4. Dosya İzinlerini Ayarlama
echo -e "${YELLOW}[4/4] Çalıştırma izinleri tanımlanıyor...${NC}"
chmod +x pulse_main.py
chmod +x modules/*.py

echo -e "${GREEN}[✔] PulseWifi başarıyla kuruldu!${NC}"
echo -e "${BLUE}[*] Kullanım: sudo python3 pulse_main.py${NC}"