import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import re # E-posta ayıklamak için gerekli

# --- EXCEL KAYIT FONKSİYONU ---
def excel_kaydet(urun_adi, fiyat, tum_mailler, oncelikli_mail, link):
    dosya_adi = "B2B_Pazar_Analizi.xlsx"
    tarih = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # Yeni veri satırı (İletişim sütunları eklendi)
    yeni_veri = pd.DataFrame({
        "Tarih": [tarih],
        "Ürün/Firma Adı": [urun_adi],
        "Fiyat": [fiyat],
        "Bulunan E-postalar": [tum_mailler],
        "Potansiyel Yetkili": [oncelikli_mail],
        "Site Linki": [link]
    })

    if os.path.exists(dosya_adi):
        eski_df = pd.read_excel(dosya_adi)
        df_final = pd.concat([eski_df, yeni_veri], ignore_index=True)
    else:
        df_final = yeni_veri

    df_final.to_excel(dosya_adi, index=False)
    print(f"--> B2B Verisi Kaydedildi: {dosya_adi}")

# --- İLETİŞİM BİLGİSİ AYIKLAMA FONKSİYONU ---
def mail_ayikla(soup):
    sayfa_metni = soup.get_text()
    # E-posta yakalama deseni
    mail_deseni = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    mailler = list(set(re.findall(mail_deseni, sayfa_metni)))
    
    oncelikli = "Bulunamadı"
    # Satın alma veya yönetici maillerini filtrele (B2B için kritik)
    for m in mailler:
        if any(kelime in m.lower() for kelime in ['purchasing', 'sales', 'manager', 'info', 'buying']):
            oncelikli = m
            break
            
    return ", ".join(mailler), oncelikli

# --- ANA SCRAPER KODU ---
url = "https://www.trendyol.com/badem10/plastik-jantli-siboplu-260x85-mm-el-arabasi-tekeri-burclu-ic-lastikli-sisme-havali-tasima-arabalari-p-940922526" 

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Bağlantı Durumu: {response.status_code}")

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        sayfa_basligi = soup.title.text.strip()
        print(f"Sayfa Başlığı: {sayfa_basligi}")
        
        # 1. ADIM: Fiyatı Bul
        fiyat = "Bulunamadı"
        seciciler = [
            "span.prc-dsc", "div.product-price", "span.fiyat-deger", 
            "span.price", ".product-price-new", "span[id='fiyat']", ".current-price"
        ]

        for secici in seciciler:
            element = soup.select_one(secici)
            if element:
                fiyat = element.text.strip()
                print(f"Fiyat Bulundu: {fiyat}")
                break
        
        if fiyat == "Bulunamadı":
            for tag in soup.find_all(["span", "div", "b"]):
                metin = tag.text.strip()
                if "TL" in metin and 1 < len(metin) < 15:
                    fiyat = metin
                    break

        # 2. ADIM: B2B İletişim Bilgilerini Bul
        tum_mailler, yetkili_mail = mail_ayikla(soup)
        print(f"E-postalar: {tum_mailler}")
        
        # 3. ADIM: Excel'e Her Şeyi Kaydet
        excel_kaydet(sayfa_basligi, fiyat, tum_mailler, yetkili_mail, url)
            
    else:
        print(f"Siteye giriş engellendi. Hata kodu: {response.status_code}")

except Exception as e:
    print(f"Hata oluştu: {e}")