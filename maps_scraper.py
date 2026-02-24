import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import geonamescache

try:
    from image_search_engine import teknik_terim_dogrula_ve_cevir
except ImportError:
    print("Uyarı: Gerekli modüller bulunamadı.")

# --- AKILLI KOORDİNAT SİSTEMİ ---
def akilli_koordinat_bul(ulke_uzantisi):
    """
    Hedef pazarın uzantısına göre en doğru enlem ve boylamı verir.
    """
    garanti_koordinatlar = {
        ".com": {"lat": 37.0902, "lng": -95.7129},  
        ".tr": {"lat": 38.9637, "lng": 35.2433},    
        ".jp": {"lat": 36.2048, "lng": 138.2529},   
        ".de": {"lat": 51.1657, "lng": 10.4515},    
        ".fr": {"lat": 46.2276, "lng": 2.2137},     
        ".es": {"lat": 40.4637, "lng": -3.7492},    
        ".it": {"lat": 41.8719, "lng": 12.5674},    
        ".ru": {"lat": 61.5240, "lng": 105.3188},   
        ".ae": {"lat": 23.4241, "lng": 53.8478},    
        ".cn": {"lat": 35.8617, "lng": 104.1954},   
        ".kr": {"lat": 35.9078, "lng": 127.7669},   
        ".uk": {"lat": 55.3781, "lng": -3.4360}     
    }
    
    if ulke_uzantisi in garanti_koordinatlar:
        return garanti_koordinatlar[ulke_uzantisi]
        
    try:
        gc = geonamescache.GeonamesCache()
        for code, info in gc.get_countries().items():
            if info.get('tld') == ulke_uzantisi.replace(".", "") or f".{code.lower()}" == ulke_uzantisi:
                 return {"lat": info['lat'], "lng": info['lng']}
    except Exception as e:
        print(f"Koordinat kütüphanesi hatası: {e}")
             
    return {"lat": 37.0902, "lng": -95.7129}

# --- ANA HARİTA TARAMA FONKSİYONU ---
def google_maps_tara(sector, country_ext, limit=15):
    """
    Hayalet tarayıcı ile Google Maps engellerini aşarak veri çeker.
    """
    
    # 1. ADIM: Sektör Çevirisi
    try:
        yerel_arama_terimi = teknik_terim_dogrula_ve_cevir(sector, country_ext)
    except:
        yerel_arama_terimi = sector

    # --- İŞTE YENİ HAYALET TARAYICI (UNDETECTED CHROMEDRIVER) ---
    print("👻 HAYALET MODU AKTİF: Google Maps anti-bot kalkanı aşılıyor...")
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    
    lang_code = "en" if country_ext == ".com" else country_ext.replace('.','')
    options.add_argument(f"--lang={lang_code}") 
    
    driver = uc.Chrome(options=options)
    
    try:
        target_url = ""
        
        # 2. ADIM: URL ve Konum Ayarlama
        if country_ext == ".com":
            print(f"🌐 GLOBAL MOD SEÇİLDİ: Konum kısıtlaması kaldırılıyor...")
            target_url = f"https://www.google.com/maps/search/{yerel_arama_terimi.replace(' ', '+')}"
            
        else:
            nokta = akilli_koordinat_bul(country_ext)
            lat = float(nokta['lat'])
            lng = float(nokta['lng'])
            
            print(f"📍 {country_ext} MODU: {lat}, {lng} koordinatlarına ışınlanılıyor.")

            driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
                "latitude": lat,
                "longitude": lng,
                "accuracy": 100
            })

            domain = f"google.{country_ext.replace('.','')}"
            if country_ext == ".jp" or country_ext == ".uk":
                domain = f"google.co{country_ext}" 

            target_url = f"https://www.{domain}/maps/search/{yerel_arama_terimi.replace(' ', '+')}/@{lat},{lng},10z"

        # 3. ADIM: Tarayıcıyı Başlat
        print(f"🚀 Tarayıcı Açılıyor: {target_url}")
        driver.get(target_url)

        wait = WebDriverWait(driver, 15)
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hfpxzc")))
        except:
            print(f"⚠️ Sonuç bulunamadı veya geç yüklendi.")
            return []

        # 4. ADIM: Scroll
        scroll_count = 5 if country_ext == ".com" else 2
        try:
            scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
            for i in range(scroll_count):
                driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
                time.sleep(2)
        except:
            pass

        # 5. ADIM: Verileri Topla
        results = []
        items = driver.find_elements(By.CLASS_NAME, "hfpxzc") 
        
        for item in items[:limit]:
            try:
                name = item.get_attribute("aria-label")
                link = item.get_attribute("href")
                if name:
                    results.append({"Firma": name, "Link": link})
                    print(f"✅ Firma Yakalandı: {name}")
            except:
                continue
        
        return results

    except Exception as e:
        print(f"❌ Hata: {e}")
        return []
    finally:
        driver.quit()