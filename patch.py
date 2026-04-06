import json
import os

with open('locales/tr.json', 'r', encoding='utf-8') as f:
    tr_dict = json.load(f)

# Hardcoded replacement logic for pulse_main.py
with open('pulse_main.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'from modules import i18n' not in content:
    content = content.replace('from modules import engine, radar, strike, decrypt, eviltwin', 'from modules import engine, radar, strike, decrypt, eviltwin, i18n\nt = i18n.t')

replacements = {
    '\"    [*] Linux tespit edildi. Root (sudo) yetkisine otomatik geçiliyor...\"': 't(\"root_escalation\")',
    'f\"    {Colors.RED}[!] Wi-Fi kartı bulunamadı!{Colors.END}\"': 'f\"    {Colors.RED}{t(\'no_wifi_card\').strip()}{Colors.END}\"',
    'f\"\\n    {Colors.BOLD}[*] Mevcut Wi-Fi Kartları:{Colors.END}\"': 'f\"\\n    {Colors.BOLD}{t(\'existing_wifi_cards\').strip()}{Colors.END}\"',
    'f\"\\n    {Colors.CYAN}Pulse/Iface #{Colors.END} \"': 'f\"\\n    {Colors.CYAN}{t(\'iface_prompt\').strip()}{Colors.END} \"',
    '\"ENGINE - ADAPTÖR & GİZLİLİK YÖNETİMİ\"': 't(\"menu_engine_title\")',
    'f\"{Colors.YELLOW}[1]{Colors.END} Monitör Modunu AÇ (Saldırı Hazırlığı)\"': 'f\"{Colors.YELLOW}[1]{Colors.END} {t(\'menu_engine_opt1\').replace(\'[1] \', \'\')}\"',
    'f\"{Colors.YELLOW}[2]{Colors.END} Monitör Modunu KAPAT (İnterneti Geri Al)\"': 'f\"{Colors.YELLOW}[2]{Colors.END} {t(\'menu_engine_opt2\').replace(\'[2] \', \'\')}\"',
    'f\"{Colors.YELLOW}[3]{Colors.END} Gizlilik Kalkanı AÇ (Rastgele MAC Al)\"': 'f\"{Colors.YELLOW}[3]{Colors.END} {t(\'menu_engine_opt3\').replace(\'[3] \', \'\')}\"',
    'f\"{Colors.YELLOW}[4]{Colors.END} Gizlilik Kalkanı KAPAT (Orijinal MAC Dön)\"': 'f\"{Colors.YELLOW}[4]{Colors.END} {t(\'menu_engine_opt4\').replace(\'[4] \', \'\')}\"',
    'f\"{Colors.YELLOW}[0]{Colors.END} Ana Menüye Dön\"': 'f\"{Colors.YELLOW}[0]{Colors.END} {t(\'menu_return\').replace(\'[0] \', \'\')}\"',
    'f\"\\n    {Colors.BOLD}Pulse/Engine #{Colors.END} \"': 'f\"\\n    {Colors.BOLD}{t(\'engine_prompt\').strip()}{Colors.END} \"',
    
    '\"RADAR / KEŞİF\"': 't(\"menu_radar_title\")',
    'f\"{Colors.YELLOW}[1]{Colors.END} Otomatik Hedef Seç (Tavsiye)\"': 'f\"{Colors.YELLOW}[1]{Colors.END} {t(\'menu_radar_opt1\').replace(\'[1] \', \'\')}\"',
    'f\"{Colors.YELLOW}[2]{Colors.END} Canlı İzleme (Manuel)\"': 'f\"{Colors.YELLOW}[2]{Colors.END} {t(\'menu_radar_opt2\').replace(\'[2] \', \'\')}\"',
    'f\"{Colors.YELLOW}[0]{Colors.END} Geri\"': 'f\"{Colors.YELLOW}[0]{Colors.END} {t(\'menu_radar_opt0\').replace(\'[0] \', \'\')}\"',
    'f\"\\n    {Colors.BOLD}Pulse/Radar #{Colors.END} \"': 'f\"\\n    {Colors.BOLD}{t(\'radar_prompt\').strip()}{Colors.END} \"',
    
    '\"STRIKE - DEAUTH SALDIRISI\"': 't(\"menu_strike_title\")',
    'f\"{Colors.YELLOW}[1]{Colors.END} Ağdaki Herkesi Düşür (Broadcast)\"': 'f\"{Colors.YELLOW}[1]{Colors.END} {t(\'menu_strike_opt1\').replace(\'[1] \', \'\')}\"',
    'f\"{Colors.YELLOW}[2]{Colors.END} Spesifik Cihazı Düşür (Targeted)\"': 'f\"{Colors.YELLOW}[2]{Colors.END} {t(\'menu_strike_opt2\').replace(\'[2] \', \'\')}\"',
    'f\"{Colors.YELLOW}[3]{Colors.END} Beacon Spam (Etrafa Sahte Ağlar Yay)\"': 'f\"{Colors.YELLOW}[3]{Colors.END} {t(\'menu_strike_opt3\').replace(\'[3] \', \'\')}\"',
    'f\"{Colors.YELLOW}[4]{Colors.END} Chaos Modu (Tam Otomatik Kitle İmha)\"': 'f\"{Colors.YELLOW}[4]{Colors.END} {t(\'menu_strike_opt4\').replace(\'[4] \', \'\')}\"',
    'f\"{Colors.YELLOW}[5]{Colors.END} Evil Twin (Rogue AP & Captive Portal)\"': 'f\"{Colors.YELLOW}[5]{Colors.END} {t(\'menu_strike_opt5\').replace(\'[5] \', \'\')}\"',
    'f\"\\n    {Colors.BOLD}Pulse/Strike #{Colors.END} \"': 'f\"\\n    {Colors.BOLD}{t(\'strike_prompt\').strip()}{Colors.END} \"',
    
    '\"DECRYPT / ŞİFRE KIRMA\"': 't(\"menu_decrypt_title\")',
    'f\"{Colors.YELLOW}[1]{Colors.END} Aircrack İle Kır (CPU - Standart)\"': 'f\"{Colors.YELLOW}[1]{Colors.END} {t(\'menu_decrypt_opt1\').replace(\'[1] \', \'\')}\"',
    'f\"{Colors.YELLOW}[2]{Colors.END} Smart Brute (Sadece Rakamlar vb.)\"': 'f\"{Colors.YELLOW}[2]{Colors.END} {t(\'menu_decrypt_opt2\').replace(\'[2] \', \'\')}\"',
    'f\"{Colors.YELLOW}[3]{Colors.END} Hashcat İle Kır (GPU - Ultra Hızlı)\"': 'f\"{Colors.YELLOW}[3]{Colors.END} {t(\'menu_decrypt_opt3\').replace(\'[3] \', \'\')}\"',
    'f\"{Colors.YELLOW}[4]{Colors.END} Handshake Doğrula\"': 'f\"{Colors.YELLOW}[4]{Colors.END} {t(\'menu_decrypt_opt4\').replace(\'[4] \', \'\')}\"',
    'f\"\\n    {Colors.BOLD}Pulse/Decrypt #{Colors.END} \"': 'f\"\\n    {Colors.BOLD}{t(\'decrypt_prompt\').strip()}{Colors.END} \"',
    
    '\"KATEGORİLER (Önerilen Akış Sırası)\"': 't(\"menu_main_title\")',
    'f\"{Colors.YELLOW}[1]{Colors.END} ENGINE  (Sistem & Gizlilik)\"': 'f\"{Colors.YELLOW}[1]{Colors.END} {t(\'menu_main_opt1\').replace(\'[1] \', \'\')}\"',
    'f\"{Colors.YELLOW}[2]{Colors.END} RADAR   (Keşif & Hedef Seçimi)\"': 'f\"{Colors.YELLOW}[2]{Colors.END} {t(\'menu_main_opt2\').replace(\'[2] \', \'\')}\"',
    'f\"{Colors.YELLOW}[3]{Colors.END} STRIKE  (Saldırı & Deauth)\"': 'f\"{Colors.YELLOW}[3]{Colors.END} {t(\'menu_main_opt3\').replace(\'[3] \', \'\')}\"',
    'f\"{Colors.YELLOW}[4]{Colors.END} DECRYPT (Şifre Kırma & Analiz)\"': 'f\"{Colors.YELLOW}[4]{Colors.END} {t(\'menu_main_opt4\').replace(\'[4] \', \'\')}\"',
    'f\"{Colors.YELLOW}[0]{Colors.END} Çıkış\"': 'f\"{Colors.YELLOW}[0]{Colors.END} {t(\'menu_main_opt0\').replace(\'[0] \', \'\')}\"',
    'f\"\\n    {Colors.BOLD}Pulse #{Colors.END} \"': 'f\"\\n    {Colors.BOLD}{t(\'main_prompt\').strip()}{Colors.END} \"',
    'f\"\\n    {Colors.BLUE}[*] Pulse kesiliyor... Ağ ayarları onarılıyor...{Colors.END}\"': 'f\"{Colors.BLUE}{t(\'main_exit\')}{Colors.END}\"',
    'f\"\\n    {Colors.RED}[!] Acil çıkış yapıldı! Ağ ayarları kurtarılıyor...{Colors.END}\"': 'f\"{Colors.RED}{t(\'main_emergency_exit\')}{Colors.END}\"',
    'f\"    {Colors.BLUE}[*] Orijinal kimliğe (MAC) dönülüyor...{Colors.END}\"': 'f\"{Colors.BLUE}{t(\'main_restore_mac\')}{Colors.END}\"',
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open('pulse_main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated pulse_main.py safely.")

# Also engine.py
with open('modules/engine.py', 'r', encoding='utf-8') as f:
    engine_content = f.read()

if 'from modules import i18n' not in engine_content:
    engine_content = 'from modules import i18n\nt = i18n.t\n' + engine_content

engine_replacements = {
    'print("    [*] Hazırlanıyor: " + iface)': 'print(t("engine_monitor_prep", iface=iface))',
    'return True, "    [✔] " + yeni_isim + " Monitör modunda.", yeni_isim': 'return True, t("engine_monitor_start_success", yeni_isim=yeni_isim), yeni_isim',
    'return False, "    [✘] Mod değiştirilemedi.", yeni_isim': 'return False, t("engine_monitor_start_fail"), yeni_isim',
    'print("    [*] Monitör modu kapatılıyor...")': 'print(t("engine_monitor_stop"))',
    'return True, "    [✔] İnternet servisleri geri yüklendi.", eski_isim': 'return True, t("engine_monitor_stop_success"), eski_isim',
    'print(f"\\n    [*] Ağ kartı ({iface}) geçici olarak kapatılıyor...")': 'print(t("engine_mac_down", iface=iface))',
    'print("    [*] Gizlilik Kalkanı Aktif: Rastgele sahte bir MAC adresi üretiliyor...")': 'print(t("engine_mac_random"))',
    'print("    [*] Kalkan Kapatılıyor: Orijinal fabrika MAC adresine dönülüyor...")': 'print(t("engine_mac_reset"))',
    'print(f"    [*] Ağ kartı tekrar ayağa kaldırılıyor...")': 'print(t("engine_mac_up"))'
}

for old, new in engine_replacements.items():
    engine_content = engine_content.replace(old, new)

with open('modules/engine.py', 'w', encoding='utf-8') as f:
    f.write(engine_content)
print("Updated modules/engine.py safely.")
