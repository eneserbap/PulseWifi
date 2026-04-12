#!/bin/bash
GREEN='\033[1;32m'
CYAN='\033[1;36m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
NC='\033[0m'

echo -e "${CYAN}[*] PulseWifi Kurulum Sihirbazı v1.2 Başlatılıyor...${NC}\n"

# Paket Yöneticisi Tespiti
if [ -x "$(command -v dnf)" ]; then
    PKG_MGR="dnf"
    INSTALL_CMD="sudo dnf install -y -q"
    UPDATE_CMD="sudo dnf check-update -q"
    PKG_LIST="aircrack-ng mdk4 macchanger hashcat hcxtools hostapd dnsmasq psmisc nftables wireless-tools iw python3-flask python3-pip crunch lsof rfkill curl"
elif [ -x "$(command -v pacman)" ]; then
    PKG_MGR="pacman"
    INSTALL_CMD="sudo pacman -S --noconfirm --needed"
    UPDATE_CMD="sudo pacman -Sy"
    PKG_LIST="aircrack-ng mdk4 macchanger hashcat hcxtools hostapd dnsmasq psmisc nftables wireless_tools iw python-flask python-pip crunch lsof rfkill curl"
elif [ -x "$(command -v apt-get)" ]; then
    PKG_MGR="apt"
    INSTALL_CMD="sudo apt-get install -y -qq"
    UPDATE_CMD="sudo apt-get update -y -qq"
    PKG_LIST="aircrack-ng mdk4 macchanger hashcat hcxtools hostapd dnsmasq psmisc nftables wireless-tools iw python3-flask python3-pip crunch lsof rfkill curl"

else
    echo -e "${RED}[!] Desteklenen bir paket yöneticisi bulunamadı (apt, dnf, pacman).${NC}"
    echo -e "${YELLOW}[!] Lütfen bağımlılıkları manuel kurun: aircrack-ng, mdk4, macchanger, hashcat, hcxtools, hostapd, dnsmasq, wireless-tools, iw, python3-flask${NC}"
    exit 1
fi

echo -e "${YELLOW}[1/5] Paket yöneticisi algılandı: ${PKG_MGR^^}${NC}"
$UPDATE_CMD > /dev/null 2>&1

echo -e "${YELLOW}[2/5] Araçlar kuruluyor (Lütfen bekleyin)...${NC}"
$INSTALL_CMD $PKG_LIST > /dev/null 2>&1

if ! command -v mdk4 &> /dev/null; then
    echo -e "${YELLOW}[*] mdk4 kurulamadı (depolarda yok), kaynaktan derleniyor...${NC}"
    if [ "$PKG_MGR" = "dnf" ]; then
        sudo dnf install -y -q libpcap-devel libnl3-devel gcc make git pkgconf > /dev/null 2>&1
    elif [ "$PKG_MGR" = "apt" ]; then
        sudo apt-get install -y -qq libpcap-dev libnl-3-dev libnl-genl-3-dev pkg-config gcc make git > /dev/null 2>&1
    elif [ "$PKG_MGR" = "pacman" ]; then
        sudo pacman -S --noconfirm --needed libpcap libnl pkgconf gcc make git > /dev/null 2>&1
    fi
    git clone https://github.com/aircrack-ng/mdk4.git /tmp/mdk4 > /dev/null 2>&1 || { echo -e "${RED}[!] mdk4 kaynak kodu indirilemedi!${NC}"; exit 1; }
    cd /tmp/mdk4 || exit
    make > /dev/null 2>&1 || { echo -e "${RED}[!] mdk4 derlenirken hata oluştu! Eksik kütüphane olabilir.${NC}"; exit 1; }
    sudo make install > /dev/null 2>&1 || { echo -e "${RED}[!] mdk4 kurulamadı!${NC}"; exit 1; }
    cd - > /dev/null 2>&1
    rm -rf /tmp/mdk4
fi

# Hostapd/Dnsmasq maskesini kaldır (systemd varsa)
if [ -x "$(command -v systemctl)" ]; then
    sudo systemctl unmask hostapd > /dev/null 2>&1
    sudo systemctl unmask dnsmasq > /dev/null 2>&1
    sudo systemctl disable hostapd > /dev/null 2>&1
    sudo systemctl disable dnsmasq > /dev/null 2>&1
fi

# Python ek bağımlılıkları kontrol ediliyor...
echo -e "${YELLOW}[3/5] Python ek bağımlılıkları kontrol ediliyor...${NC}"
if ! python3 -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}[*] Flask modülü sistem paketlerinden kurulamadı, pip fallback uygulanıyor...${NC}"
    # Fedora/Ubuntu gibi PEP 668 uygulayan modern sistemlerde pip hata verebilir, break-system-packages kullanılır.
    pip3 install flask --break-system-packages > /dev/null 2>&1 || pip3 install flask > /dev/null 2>&1
fi

echo -e "${YELLOW}[4/5] Çalıştırma izinleri tanımlanıyor...${NC}"
chmod +x pulse_main.py
chmod +x modules/*.py

echo -e "${YELLOW}[5/5] Varsayılan wordlist (rockyou.txt) kontrol ediliyor...${NC}"
WORDLIST_DIR="/usr/share/wordlists"
if [ ! -f "$WORDLIST_DIR/rockyou.txt" ]; then
    echo -e "${CYAN}[*] rockyou.txt bulunamadı. İndiriliyor... (Biraz sürebilir)${NC}"
    sudo mkdir -p "$WORDLIST_DIR"
    sudo curl -L -o "$WORDLIST_DIR/rockyou.txt" "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        sudo chmod 644 "$WORDLIST_DIR/rockyou.txt"
        echo -e "${GREEN}[✔] rockyou.txt başarıyla yüklendi! ($WORDLIST_DIR)${NC}"
    else
        echo -e "${RED}[!] rockyou.txt indirilemedi. Lütfen manuel indirip $WORDLIST_DIR/rockyou.txt yoluna koyun.${NC}"
    fi
else
    echo -e "${GREEN}[✔] rockyou.txt mevcut.${NC}"
fi

echo -e "\n${GREEN}[✔] PulseWifi başarıyla kuruldu!${NC}"
echo -e "${CYAN}[*] Kullanım: sudo python3 pulse_main.py${NC}"
