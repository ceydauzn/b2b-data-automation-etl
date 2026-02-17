from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# --- ENTEGRASYON BÖLÜMÜ ---
try:
    from image_search_engine import teknik_terim_dogrula_ve_cevir
    # Valentineapp'teki devasa koordinat veritabanını çekiyoruz
    from valentineapp import KOORDINAT_VERITABANI 
except ImportError:
    print("Uyarı: Gerekli modüller (valentineapp veya image_search_engine) bulunamadı.")
    KOORDINAT_VERITABANI = {}

def google_maps_tara(sector, country_ext, limit=10):
    """
    Valentineapp koordinat veritabanını kullanarak tüm dünyada 
    nokta atışı harita taraması yapar.
    """
    # 1. ADIM: Sektör Çevirisi (Yerelleştirme)
    try:
        yerel_arama_terimi = teknik_terim_dogrula_ve_cevir(sector, country_ext)
    except:
        yerel_arama_terimi = sector

    # 2. ADIM: Koordinat Çekme (Valentineapp Entegrasyonu)
    # Veritabanından o ülkenin GPS verisini alıyoruz
    nokta = KOORDINAT_VERITABANI.get(country_ext, {"lat": 38.9637, "lng": 35.2433})
    selected_coord = f"{nokta['lat']},{nokta['lng']}"
    
    print(f"🛰️ {country_ext} Koordinatları Bağlandı: {selected_coord}")

    chrome_options = Options()
    # Harita sonuçlarını daha iyi yakalamak için pencereyi geniş tutuyoruz
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(f"--lang={country_ext.replace('.','')}") 
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Alan adı ve arama terimi hazırlığı
        domain = f"google.{country_ext.replace('.','')}" if country_ext != ".com" else "google.com"
        search_query = yerel_arama_terimi.replace(" ", "+")
        
        # URL'e koordinatları enjekte ediyoruz (@ koordinatı)
        target_url = f"https://www.{domain}/maps/search/{search_query}/@{selected_coord},12z"
        
        print(f"🚀 Küresel Harita Taraması Başladı: {target_url}")
        driver.get(target_url)

        # 3. ADIM: Dinamik Yükleme Beklemesi
        wait = WebDriverWait(driver, 15)
        try:
            # Google Maps'teki işletme kartlarının güncel sınıfı: hfpxzc
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hfpxzc")))
        except:
            print(f"⚠️ {country_ext} bölgesinde '{yerel_arama_terimi}' için sonuç bulunamadı.")
            return []

        # 4. ADIM: Lazy Loading Tetikleme (Scroll)
        # Daha fazla sonuç çekmek için harita listesini aşağı kaydırır
        try:
            # Harita yan panelindeki kaydırılabilir alanı bul
            scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
            for _ in range(2):
                driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
                time.sleep(2)
        except:
            pass # Scroll alanı bulunamazsa devam et

        # 5. ADIM: Veri Ayıklama
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
        print(f"❌ Harita Modülünde Hata: {e}")
        return []
    finally:
        driver.quit()