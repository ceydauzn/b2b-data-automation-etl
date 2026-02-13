from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
# Çeviri modülünü içe aktarıyoruz
try:
    from image_search_engine import teknik_terim_dogrula_ve_cevir
except ImportError:
    print("Uyarı: image_search_engine.py bulunamadı, çeviri yapılamayacak.")

def google_maps_tara(sector, country_ext, limit=5):
    """
    Hem koordinat kilidi hem de otomatik yerel dil çevirisi ile 
    nokta atışı dükkan bulur.
    """
    # 1. ADIM: Sektör ismini o ülkenin diline çevir (KRİTİK ADIM)
    try:
        yerel_arama_terimi = teknik_terim_dogrula_ve_cevir(sector, country_ext)
        print(f"🌍 Çeviri Yapıldı: {sector} -> {yerel_arama_terimi}")
    except:
        yerel_arama_terimi = sector

    # 2. ADIM: Koordinat Merkezleri
    merkezler = {
        ".de": "52.5200,13.4050", # Berlin
        ".ru": "55.7558,37.6173", # Moskova
        ".fr": "48.8566,2.3522",  # Paris
        ".it": "41.9028,12.4964", # Roma
        ".com": "40.7128,-74.0060" # New York
    }
    selected_coord = merkezler.get(country_ext, "52.5200,13.4050")
    
    chrome_options = Options()
    chrome_options.add_argument("--lang=en-US") 
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        domain = f"google{country_ext}" if country_ext != ".com" else "google.com"
        # URL'de artık yerel dildeki terimi kullanıyoruz
        search_query = yerel_arama_terimi.replace(" ", "+")
        
        target_url = f"https://www.{domain}/maps/search/{search_query}/@{selected_coord},12z"
        
        print(f"🚀 {country_ext} pazarına yerel dilde ışınlanılıyor: {target_url}")
        driver.get(target_url)
        time.sleep(7)

        results = []
        # Kartları tara
        items = driver.find_elements(By.CSS_SELECTOR, "div.Nv2Ybe, div.m67Bv, a.hfpx6") 
        
        for item in items[:limit]:
            try:
                name = item.get_attribute("aria-label")
                link = item.get_attribute("href")
                if name:
                    results.append({"Firma": name, "Link": link})
                    print(f"✅ Yerel Firma Bulundu: {name}")
            except:
                continue
        
        return results

    except Exception as e:
        print(f"❌ Hata: {e}")
        return []
    finally:
        driver.quit()