# By XiEn New Era
import json
import re
import requests
import os
import time
import colorama
import sys
import subprocess
from colorama import Fore, Style
from datetime import datetime
colorama.init(autoreset=True)
aziz="XiEn"
try:
    from pystyle import Colorate, Colors
except Exception:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pystyle"])
        from pystyle import Colorate, Colors
    except Exception:
        Colorate = None
        Colors = None
# Emek var la değiştirme kodu he bide json dosyasını silersen her seferinde baştan ayar yapmak zorunda kalırsın 
ayarları_FILE = 'ayarlar.json'
LOG_FILE = 'log.txt'

def ayarları_yükle():
    if os.path.exists(ayarları_FILE):
        with open(ayarları_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'telegram_token': '', 'telegram_id': '', 'check_method': 'both', 'test_mode': False, 'mask_logs': True}

def ayarları_kaydet(ayarları):
    with open(ayarları_FILE, 'w', encoding='utf-8') as f:
        json.dump(ayarları, f, ensure_ascii=False, indent=2)

def log_maskelemesi(card):
    clean = card.replace(' ', '')
    if len(clean) <= 8:
        return clean
    return clean[:6] + '*' * (len(clean) - 10) + clean[-4:]
    # By XiEn New Era

def işlem_kayıt(raw, result, mask_logs=True):
    try:
        entry_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        def temizle(metin):
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            metin = ansi_escape.sub('', str(metin))
            return "".join(char for char in metin if char.isprintable())

        clean_raw = temizle(raw)
        clean_result = temizle(result)
        
        raw_display = clean_raw
        if mask_logs and '|' in clean_raw:
            parts = clean_raw.split('|')
            if len(parts) >= 1:
                parts[0] = log_maskelemesi(parts[0])
                raw_display = '|'.join(parts)
        
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{entry_time}] | Girdi: {raw_display} | Sonuç: {clean_result}\n")
    except Exception as e:
        print(f"Loglama hatası: {e}")


def kart_türü(card):
    card = card.replace(' ', '')
    if re.match(r'^9792[0-9]{12}$', card):
        return 'Troy'
    elif re.match(r'^4[0-9]{12}(?:[0-9]{3})?$', card):
        return 'Visa'
    elif re.match(r'^5[1-5][0-9]{14}$', card):
        return 'Mastercard'
    elif re.match(r'^3[47][0-9]{13}$', card):
        return 'American Express'
    else:
    # By XiEn New Era
        return 'Bilinmiyor'

def luhn_check(card):
    card = card.replace(' ', '')
    total = 0
    reverse_digits = card[::-1]
    for i, d in enumerate(reverse_digits):
        n = int(d)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0

def bin_check(card):
    bin_number = card.replace(' ', '')[:6]

    # By XiEn New Era
    try:
        with open('binlist_tr.json', 'r', encoding='utf-8') as f:
            turkish_bins = json.load(f)
        if bin_number in turkish_bins:
            bank_brand = turkish_bins[bin_number]
            if ' - ' in bank_brand:
                bank, brand = bank_brand.split(' - ', 1)
            else:
                bank = bank_brand
                brand = 'Bilinmiyor'
            return {
                'status': 'success',
                'bank': bank,
                'brand': brand,
                'kart_türü': brand,
                'is_business': False
            }
    except Exception:
        pass
    try:
        url = f'https://ppgpayment-test.birlesikodeme.com:20000/api/ppg/Payment/BinList/{bin_number}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and data:
                info = data[0]
                return {
                    'status': 'success',
                    'bank': info.get('bankName', 'Bilinmiyor'),
                    'brand': info.get('network', 'Bilinmiyor'),
                    'kart_türü': info.get('cardType', 'Bilinmiyor'),
                    'is_business': info.get('isBusinessCard', False)
                }
    except Exception:
        pass
    return {
        'status': 'unknown',
        'bank': 'Bilinmiyor',
        'brand': 'Bilinmiyor',
        'kart_türü': 'Bilinmiyor',
        'is_business': False,
        'message': 'Kart Turkiyedeki yaygin bankalara ait degil veya tanimlanamiyor'
    }

def exxen_check(card, expiry, cvv):
    # By XiEn New Era
    try:
        if int(card[-1]) % 2 == 0:
            return {
                'status': 'approved',
                'message': 'Exxen: 1 TL işlem başarılı (simülasyon)'
            }
        else:
            return {
                'status': 'declined',
                'message': 'Exxen: 1 TL işlem başarısız (simülasyon)'
            }
    except Exception as e:
        return {'status': 'error', 'message': f'Exxen: {str(e)}'}

def send_telegram(token, chat_id, message):
    if not token or not chat_id:
        return False, 'Telegram ayarları eksik.'
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {'chat_id': chat_id, 'text': message}
    try:
        r = requests.post(url, data=data, timeout=10)
        if r.status_code == 200:
            return True, 'Gönderildi.'
        else:
            return False, f'Hata: {r.text}'
    except Exception as e:
        return False, str(e)
    # By XiEn New Era

def telegram_ayarları():
    ayarları = ayarları_yükle()
    print(Colorate.Horizontal(Colors.white_to_red, "\nTelegram Ayarları"))
    print(f"{Fore.LIGHTWHITE_EX}Mevcut Token: {ayarları.get('telegram_token', 'Ayarlanmamış')}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTWHITE_EX}Mevcut Chat ID: {ayarları.get('telegram_id', 'Ayarlanmamış')}{Style.RESET_ALL}")
    token = input(f"{Fore.LIGHTWHITE_EX}Yeni Bot Token (boş bırakınca değişmez): {Style.RESET_ALL}").strip()
    chat_id = input(f"{Fore.LIGHTWHITE_EX}Yeni Chat ID (boş bırakınca değişmez): {Style.RESET_ALL}").strip()
    if token:
        ayarları['telegram_token'] = token
    if chat_id:
        ayarları['telegram_id'] = chat_id
    ayarları_kaydet(ayarları)
    print(Colorate.Horizontal(Colors.white_to_green, "Ayarlar kaydedildi!"))


def check_ayarları():
    ayarları = ayarları_yükle()
    print(Colorate.Horizontal(Colors.white_to_red, "\nCheck Ayarları"))
    print(f"{Fore.LIGHTWHITE_EX}Mevcut Check Yöntemi: {ayarları.get('check_method', 'both')}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTWHITE_EX}Test Modu: {'Açık' if ayarları.get('test_mode', False) else 'Kapalı'}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTWHITE_EX}Loglarda maskeleme: {'Açık' if ayarları.get('mask_logs', True) else 'Kapalı'}{Style.RESET_ALL}")
    print(Colorate.Horizontal(Colors.white_to_red, "\nCheck Yöntemleri:"))
    print(f"{Fore.LIGHTWHITE_EX}1. Sadece BIN Checkü{Style.RESET_ALL}")
    print(f"{Fore.LIGHTWHITE_EX}2. Sadece Exxen Checkü{Style.RESET_ALL}")
    print(f"{Fore.LIGHTWHITE_EX}3. Her İkisi (Önerilen){Style.RESET_ALL}")
    method = input(f"{Fore.LIGHTWHITE_EX}Yeni Check yöntemi (1-3, boş bırakınca değişmez): {Style.RESET_ALL}").strip()
    if method == '1':
        ayarları['check_method'] = 'bin_only'
    elif method == '2':
        ayarları['check_method'] = 'exxen_only'
    elif method == '3':
        ayarları['check_method'] = 'both'
    test_mode = input(f"{Fore.LIGHTWHITE_EX}Test modu açılsın mı? y/n (Boş Bırakınca Değişmez): {Style.RESET_ALL}").strip().lower()
    if test_mode == 'y':
        ayarları['test_mode'] = True
    elif test_mode == 'n':
        ayarları['test_mode'] = False
    mask_mode = input(f"{Fore.LIGHTWHITE_EX}Loglarda kart numarası maskelensin mi? y/n (Boş bırakınca değişmez): {Style.RESET_ALL}").strip().lower()
    if mask_mode == 'y':
        ayarları['mask_logs'] = True
    elif mask_mode == 'n':
        ayarları['mask_logs'] = False
    ayarları_kaydet(ayarları)
    print(Colorate.Horizontal(Colors.white_to_green, "Başarıyla Kaydedildi :D"))


def check_alanı(raw, ayarları):
    raw_stripped = raw.strip()

    if '|' not in raw_stripped:
        result = Colorate.Horizontal(Colors.white_to_red, "Hatalı format! Doğru format: Numara|Ay|Yıl|CVV")
        işlem_kayıt(raw_stripped, result, mask_logs=ayarları.get('mask_logs', True))
        return result

    parts = raw_stripped.split('|')
    if len(parts) != 4:
        result = Colorate.Horizontal(Colors.white_to_red, "Hatalı format! Dört parça gerekli.")
        işlem_kayıt(raw_stripped, result, mask_logs=ayarları.get('mask_logs', True))
        return result

    card, ay, yil, cvv = [p.strip() for p in parts]

    if not card.isdigit() or len(card) < 13 or len(card) > 19:
        result = Colorate.Horizontal(Colors.white_to_red, "Hatalı kart numarası!")
        işlem_kayıt(raw_stripped, result, mask_logs=ayarları.get('mask_logs', True))
        return result

    if not ay.isdigit() or int(ay) < 1 or int(ay) > 12:
        result = Colorate.Horizontal(Colors.white_to_red, "Hatalı ay!")
        işlem_kayıt(raw_stripped, result, mask_logs=ayarları.get('mask_logs', True))
        return result

    if not yil.isdigit():
        result = Colorate.Horizontal(Colors.white_to_red, "Hatalı yıl!")
        işlem_kayıt(raw_stripped, result, mask_logs=ayarları.get('mask_logs', True))
        return result

    if len(yil) == 2:
        yil = '20' + yil
    elif len(yil) == 4:
        pass
    else:
        result = Colorate.Horizontal(Colors.white_to_red, "Hatalı yıl formatı! (2 veya 4 haneli olmalı)")
        işlem_kayıt(raw_stripped, result, mask_logs=ayarları.get('mask_logs', True))
        return result

    if not cvv.isdigit() or len(cvv) < 3 or len(cvv) > 4:
        result = Colorate.Horizontal(Colors.white_to_red, "Hatalı CVV!")
        işlem_kayıt(raw_stripped, result, mask_logs=ayarları.get('mask_logs', True))
        return result

    ctype = kart_türü(card)
    if ctype == 'Bilinmiyor':
        result = Colorate.Horizontal(Colors.white_to_red, "Desteklenmeyen kart tipi! Troy, Visa, Mastercard veya Amex olmalı.")
        işlem_kayıt(raw_stripped, result, mask_logs=ayarları.get('mask_logs', True))
        return result

    if not luhn_check(card):
        result = Colorate.Horizontal(Colors.white_to_red, "Hatalı kart numarası (Luhn algoritması hatası)!")
        işlem_kayıt(raw_stripped, result, mask_logs=ayarları.get('mask_logs', True))
        return result

    if ayarları.get('test_mode', False):
        result = Colorate.Horizontal(Colors.white_to_green, f"TEST MODU - Kart: {log_maskelemesi(card) if ayarları.get('mask_logs', True) else card} Tip: {ctype} (Test sonucu)")
        işlem_kayıt(raw_stripped, result, mask_logs=ayarları.get('mask_logs', True))
        return result

    check_method = ayarları.get('check_method', 'both')
    results = []

    if check_method in ['bin_only', 'both']:
        bin_result = bin_check(card)
        if bin_result['status'] == 'success':
            results.append(f"BIN: {bin_result['bank']} - {bin_result['brand']}")
        elif bin_result['status'] == 'unknown':
            results.append(f"BIN: {bin_result['message']}")
        else:
            results.append(f"BIN: {bin_result.get('message', 'Bilinmeyen durum')}")

    if check_method in ['exxen_only', 'both']:
        exxen_result = exxen_check(card, f'{ay}/{yil}', cvv)
        if exxen_result['status'] == 'approved':
            results.append(f"Exxen: {exxen_result['message']}")
        elif exxen_result['status'] == 'declined':
            results.append(f"Exxen: {exxen_result['message']}")
        else:
            results.append(f"Exxen: {exxen_result.get('message', 'Hata')}")

    final_status = 'Belirsiz'
    if any('başarılı' in r.lower() or 'approved' in r.lower() for r in results):
        final_status = Colorate.Horizontal(Colors.white_to_green, "ONaylandı")
    elif any('başarısız' in r.lower() or 'declined' in r.lower() for r in results):
        final_status = Colorate.Horizontal(Colors.white_to_red, "Reddedildi")

    has_3d = "3D Secure Var" if ctype in ['Visa', 'Mastercard'] else "3D Secure Yok"

    msg = f"{final_status} | Kart: {log_maskelemesi(card) if ayarları.get('mask_logs', True) else card} | Tip: {ctype} | {has_3d} | {' | '.join(results)}"

    işlem_kayıt(raw_stripped, msg, mask_logs=ayarları.get('mask_logs', True))

    token = ayarları.get('telegram_token', '')
    chat_id = ayarları.get('telegram_id', '')
    if token and chat_id and "Onaylandı" in final_status:
        try:
            telegram_msg = f"LIVE KART\n\n{log_maskelemesi(card)}|{ay}|{yil}|{cvv}\n\n{final_status}\nTip: {ctype}\n{has_3d}\n\n{' | '.join(results)}"
            ok, tmsg = send_telegram(token, chat_id, telegram_msg)
            msg += f" | Telegram: {tmsg}"
            işlem_kayıt(raw_stripped, f"Telegram sonucu: {tmsg}", mask_logs=ayarları.get('mask_logs', True))
        except Exception as e:
            işlem_kayıt(raw_stripped, f"Telegram gönderim hatası: {e}", mask_logs=ayarları.get('mask_logs', True))

    return msg
# XiEn New Era

def tek_kart_check(ayarları):
    print(Colorate.Horizontal(Colors.white_to_red, "\nTek Kart Check"))
    raw = input(f"{Fore.LIGHTWHITE_EX}Kart bilgisi (Numara|Ay|Yıl|CVV): {Style.RESET_ALL}").strip()
    if not raw:
        print(Colorate.Horizontal(Colors.white_to_red, "Kart bilgisi girilmedi"))
        return
    print(Colorate.Horizontal(Colors.white_to_red, "\nCheck ediliyor"))
    result = check_alanı(raw, ayarları)
    print(Colorate.Horizontal(Colors.white_to_green, f"\nSonuç: {result}"))

def çoklu_kart_check(ayarları):
    print(Colorate.Horizontal(Colors.white_to_red, "\nDosyadan Kart Check"))
    file_path = input(f"{Fore.LIGHTWHITE_EX}Dosya yolu: {Style.RESET_ALL}").strip()
    if not file_path:
        print(Colorate.Horizontal(Colors.white_to_red, "Dosya yolu girilmedi"))
        return
    if not os.path.exists(file_path):
        print(Colorate.Horizontal(Colors.white_to_red, "Dosya bulunamadı"))
        return
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [ln.strip() for ln in f if ln.strip()]
    except Exception as e:
        print(Colorate.Horizontal(Colors.white_to_red, f"Dosya okunamadı: {str(e)}"))
        return
    print(Colorate.Horizontal(Colors.white_to_red, f"\n{len(lines)} kart Check ediliyor"))
    approved_count = 0
    declined_count = 0
    error_count = 0
    for idx, line in enumerate(lines, 1):
        result = check_alanı(line, ayarları)
        print(f"{Fore.LIGHTWHITE_EX}{idx:3d}. {result}{Style.RESET_ALL}")
        if result.startswith('ONaylandı') or '| ONaylandı' in result or 'ONaylandı' in result:
            approved_count += 1
        elif result.startswith('Reddedildi') or '| Reddedildi' in result or 'Reddedildi' in result:
            declined_count += 1
        else:
            error_count += 1
        time.sleep(0.2)
    print(Colorate.Horizontal(Colors.white_to_red, "ÖZET:"))
    print(Colorate.Horizontal(Colors.white_to_green, f"    Onay Verilen: {approved_count}"))
    print(Colorate.Horizontal(Colors.white_to_red, f"    Red Yiyen: {declined_count}"))
    print(Colorate.Horizontal(Colors.white_to_red, f"    Hatalı/Belirsiz: {error_count}"))
    print(f"{Fore.LIGHTWHITE_EX}    Total: {len(lines)}{Style.RESET_ALL}")

def main():
    ayarları = ayarları_yükle()

ASCII1 = r"""                                                 
                                                                     ,                                          
                                                                     Et                                         
                          L.                       L.                E#t              .                        
             t    L       EW:        ,ft           EW:        ,ft    E##t            ,W                        
             Ej   #K:     E##;       t#E           E##;       t#E    E#W#t          i##                        
  :KW,      LE#,  :K#t    E###t      t#E        jt E###t      t#E    E#tfL.        f###      ,##############Wf.
   ,#W:   ,KGE#t    L#G.  E#fE#f     t#E       G#t E#fE#f     t#E    E#t          G####       ........jW##Wt   
    ;#W. jWi E#t     t#W, E#t D#G    t#E       E#t E#t D#G    t#E ,ffW#Dffj.    .K#Ki##             tW##Kt     
     i#KED.  E#t  .jffD##fE#t  f#E.  t#E       E#t E#t  f#E.  t#E  ;LW#ELLLf.  ,W#D.,##           tW##E;       
      L#W.   E#t .fLLLD##LE#t   t#K: t#E       E#t E#t   t#K: t#E    E#t      i##E,,i##,        tW##E;         
    .GKj#K.  E#t     ;W#i E#t    ;#W,t#E       E#t E#t    ;#W,t#E    E#t     ;DDDDDDE##DGi   .fW##D,           
   iWf  i#K. E#t    j#E.  E#t     :K#D#E       E#t E#t     :K#D#E    E#t            ,##    .f###D,             
  LK:    t#E E#t  .D#f    E#t      .E##E       E#t E#t      .E##E    E#t            ,##  .f####Gfffffffffff;   
  i       tDjE#t  KW,     **         G#E       tf, ..         G#E    E#t            .E# .fLLLLLLLLLLLLLLLLLi   
             ,;.  G.                  fE                       fE    ;#t              t                        
                                       '                        '     :;                                       
                                             By. XiEn     #newera
                                                                                                               """

ASCII2 = r""" 
   ,o888888o.        ,o888888o.                  ,o888888o.    8 8888        8 8 8888888888       ,o888888o.    8 8888     ,88' 8 8888888888   8 888888888o.   
   8888     `88.     8888     `88.               8888     `88.  8 8888        8 8 8888            8888     `88.  8 8888    ,88'  8 8888         8 8888    `88.  
,8 8888       `8. ,8 8888       `8.           ,8 8888       `8. 8 8888        8 8 8888         ,8 8888       `8. 8 8888   ,88'   8 8888         8 8888     `88  
88 8888           88 8888                     88 8888           8 8888        8 8 8888         88 8888           8 8888  ,88'    8 8888         8 8888     ,88  
88 8888           88 8888                     88 8888           8 8888        8 8 888888888888 88 8888           8 8888 ,88'     8 888888888888 8 8888.   ,88'  
88 8888           88 8888                     88 8888           8 8888        8 8 8888         88 8888           8 8888 88'      8 8888         8 888888888P'   
88 8888           88 8888                     88 8888           8 8888888888888 8 8888         88 8888           8 888888<       8 8888         8 8888`8b       
`8 8888       .8' `8 8888       .8'           `8 8888       .8' 8 8888        8 8 8888         `8 8888       .8' 8 8888 `Y8.     8 8888         8 8888 `8b.     
   8888     ,88'     8888     ,88'               8888     ,88'  8 8888        8 8 8888            8888     ,88'  8 8888   `Y8.   8 8888         8 8888   `8b.   
    `8888888P'        `8888888P'                  `8888888P'    8 8888        8 8 888888888888     `8888888P'    8 8888     `Y8. 8 888888888888 8 8888     `88.  
    
                                                                    By. XiEn     #newera
                                                                                                                                                                               """
def cls():
    os.system("cls" if os.name == "nt" else "clear")

def pprint_lines(text, colorscheme, delay=0.01):
    if Colorate is None:
        for line in text.splitlines():
            print(line)
            time.sleep(delay)
        return
    for line in text.splitlines():
        try:
            print(Colorate.Horizontal(colorscheme, line))
        except Exception:
            print(line)
        time.sleep(delay)

def k3y():
    cls()
    print()
    pprint_lines(ASCII1, Colors.white_to_red, delay=0.005)
    print()
    if Colorate is not None:
        try:
            print(Colorate.Horizontal(Colors.white_to_red, "Lütfen K3y Giriniz:"))
        except Exception:
            print(Colorate.Horizontal(Colors.black_to_white, "Lütfen K3y Giriniz:"))
    else:
        print(Colorate.Horizontal(Colors.black_to_white, "Lütfen K3y Giriniz:"))
    key = input(Colorate.Horizontal(Colors.black_to_white, " > ")).strip()
    if key == aziz:
        print(Colorate.Horizontal(Colors.green_to_white, "\nŞifre Doğrulandı! Yönlendiriliyorsunuz..."))
        time.sleep(1)
        menu_after_login()
    else:
        print(Colorate.Horizontal(Colors.red_to_white, "\nYanlış şifre! Tekrar deneyiniz.\n"))
        time.sleep(0.8)
        k3y()

def menu_after_login():
    cls()
    pprint_lines(ASCII2, Colors.red_to_white, delay=0.004)
    print(f"{Fore.LIGHTWHITE_EX}1 ~ Tool'a Git{Style.RESET_ALL}")
    print(Colorate.Horizontal(Colors.white_to_red, "2 ~ Programdan Çık"))
    secim = input(Colorate.Horizontal(Colors.green_to_white, "Seçiminiz: ")).strip()
    if secim == "1":
        pprint_lines(ASCII2, Colors.red_to_white, delay=0.002)
        main_menu()
    elif secim == "2":
        print(Colorate.Horizontal(Colors.red_to_white, "Çıkış yapılıyor..."))
        time.sleep(0.6)
        sys.exit(0)
    else:
        print(Colorate.Horizontal(Colors.red_to_white, "Geçersiz seçim!"))
        time.sleep(0.6)
        menu_after_login()

def main_menu():
    while True:
        cls()
        pprint_lines(ASCII2, Colors.red_to_white, delay=0.002)
        print(Colorate.Horizontal(Colors.white_to_red, "1 ~ Tek Kart Check"))
        print(Colorate.Horizontal(Colors.white_to_red, "2 ~ Dosyadan Check"))
        print(Colorate.Horizontal(Colors.white_to_red, "3 ~ Telegram Ayarları"))
        print(Colorate.Horizontal(Colors.white_to_red, "4 ~ Check Ayarları"))
        print(Colorate.Horizontal(Colors.white_to_red, "5 ~ Tool'u Terk Et"))

        ayarları = ayarları_yükle()
        print(f"{Fore.LIGHTWHITE_EX}Mevcut Ayarlar: {ayarları.get('check_method','both')} | Test: {'Açık' if ayarları.get('test_mode',False) else 'Kapalı'} | Log Mask: {'Açık' if ayarları.get('mask_logs',True) else 'Kapalı'}{Style.RESET_ALL}")

        secim = input(Colorate.Horizontal(Colors.green_to_white, "Seçiminiz (1-5): ")).strip()

        if secim == "1":
            tek_kart_check(ayarları)
        elif secim == "2":
            çoklu_kart_check(ayarları)
        elif secim == "3":
            telegram_ayarları()
        elif secim == "4":
            check_ayarları()
        elif secim == "5":
            print(Colorate.Horizontal(Colors.green_to_white, "Uygulama kapatılıyor"))
            time.sleep(0.8)
            break
        else:
            print(Colorate.Horizontal(Colors.red_to_white, "Geçersiz seçim, lütfen 1-5 arasında bir değer girin."))
            time.sleep(0.8)

if __name__ == "__main__":
    k3y()
    # XiEn New Era
    















































































































































































































































































































































































































































































































    # Elifi cuk sebiyom