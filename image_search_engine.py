import pandas as pd
import re
from datetime import datetime
import time
import random
from deep_translator import GoogleTranslator

# Selenium Araçları
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- 1. MODÜL: TEKNİK TERİM DOĞRULAMA VE ÇEVİRİ ---
def teknik_terim_dogrula_ve_cevir(kelime, hedef_uzanti):
    # Kapsamlı uzantı-dil haritası (Azerbaycan ve diğerleri eklendi)
    uzanti_dil_haritasi = {
        '.tr': 'tr', '.de': 'de', '.ru': 'ru', '.fr': 'fr', 
        '.it': 'it', '.es': 'es', '.jp': 'ja', '.cn': 'zh-CN',
        '.az': 'az', # Azerbaycan Türkçesi eklendi
        '.pl': 'pl', '.nl': 'nl', '.gr': 'el', '.bg': 'bg'
    }
    
    # Eğer uzantı listede yoksa, pycountry veya basit mantıkla dili tahmin et
    hedef_dil = uzanti_dil_haritasi.get(hedef_uzanti)
    
    if not hedef_dil:
        # Uzantıdan (örn: .az -> az) dili tahmin etmeye çalış
        hedef_dil = hedef_uzanti.replace(".", "")
    
    try:
        # Otomatik algılama ile hedef dile çevir
        cevirilmis = GoogleTranslator(source='auto', target=hedef_dil).translate(kelime)
        print(f"✅ Çeviri Yapıldı: {kelime} -> {cevirilmis} ({hedef_dil.upper()})")
        return cevirilmis
    except Exception as e:
        print(f"⚠️ Çeviri Hatası: {e}. Orijinal terim kullanılıyor.")
        return kelime
# --- 2. MODÜL: AKILLI ARAMA MOTORU (ÜLKE VE DİL MANİPÜLASYONU) ---
def google_canli_arama(oem_no, gtip_no, yerel_parca_ismi, ulke_uzantisi, adet=10):
    """
    Seçilen ülkeye göre Google'ın yerel versiyonunu ve dil ayarlarını kullanır.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Arka plan modu
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # --- VALENTIN MANTIĞI: DİNAMİK URL OLUŞTURMA ---
    # Uzantıyı temizle (örn: .de -> de)
    u_kodu = ulke_uzantisi.replace(".", "")
    if u_kodu == "com": u_kodu = "us" # Global için ABD varsayılan
    
    # Yerel Google alan adını belirle (google.de, google.fr vb.)
    google_domain = f"google.{u_kodu}" if u_kodu != "us" else "google.com"
    
    # Sorgu ve Parametreler (gl=konum, hl=dil)
    sorgu = f"{oem_no} {yerel_parca_ismi} supplier"
    url = f"https://www.{google_domain}/search?q={sorgu}&gl={u_kodu}&hl={u_kodu}"
    
    print(f"🌍 Valentin Simülasyonu: {google_domain} üzerinden {u_kodu.upper()} konumuyla aranıyor...")
    
    linkler = []
    try:
        driver.get(url)
        time.sleep(random.uniform(5, 8)) # Sayfa yüklenmesi için insansı bekleme
        
        # Sonuçları topla
        search_results = driver.find_elements(By.CSS_SELECTOR, "div.yuRUbf a")
        for res in search_results:
            link = res.get_attribute("href")
            if link and "google.com" not in link and link.startswith("http"):
                if link not in linkler:
                    linkler.append(link)
            if len(linkler) >= adet: break
            
    except Exception as e:
        print(f"⚠️ Arama Hatası: {e}")
    finally:
        driver.quit()
    
    return linkler

# --- 3. MODÜL: ANA İŞLEYİCİ ---
def global_pazar_taramasi(oem_no, parca_ismi, ulke_uzantisi, gtip_no=""):
    # 1. Çeviriyi hedef ülkeye göre yap
    yerel_isim = teknik_terim_dogrula_ve_cevir(parca_ismi, ulke_uzantisi)
    print(f"🔎 Aranan Terim: {yerel_isim} ({ulke_uzantisi})")
    
    # 2. Google engelini Selenium ve Yerel Parametrelerle aş
    bulunan_linkler = google_canli_arama(oem_no, gtip_no, yerel_isim, ulke_uzantisi)
    
    final_listesi = []
    if not bulunan_linkler:
        return []

    # 3. İletişim bilgilerini topla (Scraper fonksiyonun burada çalışır)
    for url in bulunan_linkler:
        from maps_scraper import b2b_iletisim_tara # Eğer fonksiyon oradaysa
        mailler, yetkili = b2b_iletisim_tara(url)
        
        final_listesi.append({
            "OEM No": oem_no,
            "GTIP No": gtip_no,
            "Web Sitesi": url,
            "E-postalar": mailler,
            "Ülke": ulke_uzantisi,
            "Tarama Tarihi": datetime.now().strftime("%d/%m/%Y")
        })
    return final_listesi