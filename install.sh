#!/bin/bash

# Renk kodları (Koyu Mavi yerine Parlak Cyan kullandık)
GREEN='\033[1;32m'
CYAN='\033[1;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${CYAN}[*] PulseWifi Kurulum Sihirbazı Başlatılıyor...${NC}\n"

# ==========================================
# SESSİZ KURULUM AYARLARI
# ==========================================
echo "macchanger macchanger/auto boolean false" | sudo debconf-set-selections

# 1. Sistem Güncelleme
# -qq ve > /dev/null 2>&1 komutları ekrandaki tüm o çirkin logları yok eder
echo -e "${YELLOW}[1/4] Sistem paket listeleri güncelleniyor... (Lütfen bekleyin)${NC}"
sudo apt-get update -y -qq > /dev/null 2>&1

# 2. Temel Siber Güvenlik Araçları (Hashcat ve Hcxtools eklendi)
echo -e "${YELLOW}[2/4] Kablosuz ağ araçları kuruluyor (Aircrack-ng, MDK3, MacChanger, Hashcat, Hcxtools)...${NC}"
sudo DEBIAN_FRONTEND=noninteractive apt-get install aircrack-ng mdk3 macchanger hashcat hcxtools python3-pip -y -qq > /dev/null 2>&1

# 3. Python Kütüphaneleri
echo -e "${YELLOW}[3/4] Python bağımlılıkları yükleniyor...${NC}"
sudo apt-get install python3-flask -y -qq > /dev/null 2>&1 || pip3 install flask -q > /dev/null 2>&1

# 4. Dosya İzinlerini Ayarlama
echo -e "${YELLOW}[4/4] Çalıştırma izinleri tanımlanıyor...${NC}"
chmod +x pulse_main.py
chmod +x modules/*.py

echo -e "\n${GREEN}[✔] PulseWifi başarıyla kuruldu!${NC}"
echo -e "${CYAN}[*] Kullanım: sudo python3 pulse_main.py${NC}"