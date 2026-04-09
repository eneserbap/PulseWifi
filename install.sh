#!/bin/bash
GREEN='\033[1;32m'
CYAN='\033[1;36m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
NC='\033[0m'

echo -e "${CYAN}[*] PulseWifi Kurulum Sihirbazı v1.2.1 Başlatılıyor...${NC}\n"

# Paket Yöneticisi Tespiti
if [ -x "$(command -v apt-get)" ]; then
    PKG_MGR="apt"
    INSTALL_CMD="sudo apt-get install -y -qq"
    UPDATE_CMD="sudo apt-get update -y -qq"
    PKG_LIST="aircrack-ng mdk3 macchanger hashcat hcxtools hostapd dnsmasq python3-pip python3-flask"
elif [ -x "$(command -v dnf)" ]; then
    PKG_MGR="dnf"
    INSTALL_CMD="sudo dnf install -y -q"
    UPDATE_CMD="sudo dnf check-update -q"
    PKG_LIST="aircrack-ng mdk3 macchanger hashcat hcxtools hostapd dnsmasq python3-pip python3-flask"
elif [ -x "$(command -v pacman)" ]; then
    PKG_MGR="pacman"
    INSTALL_CMD="sudo pacman -S --noconfirm --needed"
    UPDATE_CMD="sudo pacman -Sy"
    PKG_LIST="aircrack-ng mdk3 macchanger hashcat hcxtools hostapd dnsmasq python-pip python-flask"
else
    echo -e "${RED}[!] Desteklenen bir paket yöneticisi bulunamadı (apt, dnf, pacman).${NC}"
    echo -e "${YELLOW}[!] Lütfen bağımlılıkları manuel kurun: aircrack-ng, mdk3, macchanger, hashcat, hcxtools, hostapd, dnsmasq, python3-flask${NC}"
    exit 1
fi

echo -e "${YELLOW}[1/4] Paket yöneticisi algılandı: ${PKG_MGR^^}${NC}"
$UPDATE_CMD > /dev/null 2>&1

echo -e "${YELLOW}[2/4] Araçlar kuruluyor (Lütfen bekleyin)...${NC}"
$INSTALL_CMD $PKG_LIST > /dev/null 2>&1

# Hostapd/Dnsmasq maskesini kaldır (systemd varsa)
if [ -x "$(command -v systemctl)" ]; then
    sudo systemctl unmask hostapd > /dev/null 2>&1
    sudo systemctl unmask dnsmasq > /dev/null 2>&1
    sudo systemctl disable hostapd > /dev/null 2>&1
    sudo systemctl disable dnsmasq > /dev/null 2>&1
fi

echo -e "${YELLOW}[3/4] Python ek bağımlılıkları kontrol ediliyor...${NC}"
pip3 install flask -q > /dev/null 2>&1

echo -e "${YELLOW}[4/4] Çalıştırma izinleri tanımlanıyor...${NC}"
chmod +x pulse_main.py
chmod +x modules/*.py

echo -e "\n${GREEN}[✔] PulseWifi başarıyla kuruldu!${NC}"
echo -e "${CYAN}[*] Kullanım: sudo python3 pulse_main.py${NC}"
