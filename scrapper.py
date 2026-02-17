import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

def fetch_localized_results(oem, gtip, parca_ismi, country_code="us", extension=".com", adet=10):
    """
    Valentin.app mantığını simüle eder: Google'a 'ben bu konumdayım' der.
    oem, gtip ve parca_ismi verilerini birleştirerek nitelikli arama yapar.
    """
    # Döküman Madde 2: Sorgu oluşturma (OEM + GTIP + İSİM)
    keyword = f'"{oem}" {gtip} "{parca_ismi}" site:*{extension}'
    
    # Valentin.app'in arka planda kullandığı Google parametreleri:
    # gl: Ülke Kodu (ru, de, tr vb.)
    # hl: Dil Kodu
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Valentin Simülasyon URL'si
    url = f"https://www.google.com/search?q={keyword}&gl={country_code}&hl={country_code}"
    
    print(f"🚀 Valentin Simülasyonu Başlatıldı: {country_code.upper()} üzerinden aranıyor...")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        linkler = []
        # Google sonuçlarını ayıkla
        for g in soup.find_all('div', class_='tF2Cxc'):
            link = g.find('a')['href']
            title = g.find('h3').text if g.find('h3') else "Bilinmeyen Firma"
            
            if link not in [l['Web'] for l in linkler]:
                linkler.append({
                    "Firma": title,
                    "Web": link,
                    "Kaynak": f"Valentin ({country_code.upper()})",
                    "OEM": oem,
                    "GTIP": gtip,
                    "Ülke": country_code,
                    "Tarama Tarihi": datetime.now().strftime("%d/%m/%Y")
                })
        
        return linkler[:adet]
    
    except Exception as e:
        print(f"❌ Scraper Hatası: {e}")
        return []

def sonuclari_excele_aktar(veri_listesi, oem_no="Sorgu"):
    """
    Bulunan potansiyel müşterileri Excel olarak kaydeder.
    """
    if not veri_listesi:
        print("⚠️ Kaydedilecek veri bulunamadı.")
        return
    
    df = pd.DataFrame(veri_listesi)
    dosya_adi = f"B2B_Sorgu_{oem_no}.xlsx"
    
    # Excel dosyasını oluşturur
    df.to_excel(dosya_adi, index=False)
    print(f"✅ BAŞARILI: {dosya_adi} dosyası oluşturuldu.")

# --- TEST KISMI (GUI'den bağımsız çalıştırmak istersen) ---
if __name__ == "__main__":
    # Örnek bir pazar taraması
    test_verileri = fetch_localized_results(
        oem="260x85", 
        gtip="8708.99", 
        parca_ismi="Piston", 
        country_code="de", 
        extension=".de"
    )
    
    sonuclari_excele_aktar(test_verileri, "260x85")