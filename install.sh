#!/bin/bash
GREEN='\033[1;32m'
CYAN='\033[1;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color
echo -e "${CYAN}[*] PulseWifi Kurulum Sihirbazı Başlatılıyor...${NC}\n"
echo "macchanger macchanger/auto boolean false" | sudo debconf-set-selections
echo -e "${YELLOW}[1/4] Sistem paket listeleri güncelleniyor... (Lütfen bekleyin)${NC}"
sudo apt-get update -y -qq > /dev/null 2>&1
echo -e "${YELLOW}[2/4] Kablosuz ağ araçları kuruluyor (Aircrack-ng, MDK3, MacChanger, Hashcat, Hcxtools, Hostapd, Dnsmasq)...${NC}"
sudo DEBIAN_FRONTEND=noninteractive apt-get install aircrack-ng mdk3 macchanger hashcat hcxtools hostapd dnsmasq python3-pip -y -qq > /dev/null 2>&1
sudo systemctl unmask hostapd > /dev/null 2>&1
sudo systemctl unmask dnsmasq > /dev/null 2>&1
sudo systemctl disable hostapd > /dev/null 2>&1
sudo systemctl disable dnsmasq > /dev/null 2>&1
echo -e "${YELLOW}[3/4] Python bağımlılıkları yükleniyor...${NC}"
sudo apt-get install python3-pip python3-flask -y -qq > /dev/null 2>&1 || pip3 install flask -q > /dev/null 2>&1
echo -e "${YELLOW}[4/4] Çalıştırma izinleri tanımlanıyor...${NC}"
chmod +x pulse_main.py
chmod +x modules/*.py
echo -e "\n${GREEN}[✔] PulseWifi başarıyla kuruldu!${NC}"
echo -e "${CYAN}[*] Terminal Kullanımı: sudo python3 pulse_main.py${NC}"
