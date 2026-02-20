import geonamescache
import undetected_chromedriver as uc
import time

def tum_dunya_koordinat_sozlugu_olustur():
    """Tüm ülkelerin merkez koordinatlarını oluşturur."""
    gc = geonamescache.GeonamesCache()
    countries = gc.get_countries()
    global_coords = {}
    
    for code, info in countries.items():
        if 'lat' in info and 'lng' in info:
            if info['tld']:
                ext = "." + info['tld'].replace(".", "")
            else:
                ext = f".{code.lower()}"
            global_coords[ext] = {"lat": info['lat'], "lng": info['lng']}
            
    # Hata önleyici manuel eklemeler
    global_coords[".tr"] = {"lat": 38.9637, "lng": 35.2433} # Türkiye
    global_coords[".com"] = {"lat": 37.0902, "lng": -95.7129} # Global/US
    
    return global_coords

KOORDINAT_VERITABANI = tum_dunya_koordinat_sozlugu_olustur()

def valentin_simulasyonu_baslat(sorgu, ulke_kodu, dil_kodu, ulke_uzantisi):
    """Google Bot korumasını aşan hayalet tarayıcı ile GPS simülasyonu yapar."""
    
    print("👻 HAYALET MODU: Google anti-bot kalkanı aşılıyor...")
    
    # Standart Selenium yerine "undetected_chromedriver" kullanıyoruz
    options = uc.ChromeOptions()
    options.add_argument(f"--lang={dil_kodu}")
    
    # Tarayıcıyı başlat
    driver = uc.Chrome(options=options)
    
    # 1. Koordinatları al
    nokta = KOORDINAT_VERITABANI.get(ulke_uzantisi, {"lat": 38.9637, "lng": 35.2433})
    lat = float(nokta['lat'])
    lng = float(nokta['lng'])

    # 2. Tarayıcıyı o koordinata "Işınla" 
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
        "latitude": lat,
        "longitude": lng,
        "accuracy": 100
    })

    # 3. URL oluşturma (Sadece arama terimi ve bölge kodları)
    u_kodu = ulke_kodu.lower()
    google_url = f"https://www.google.com/search?q={sorgu}&gl={u_kodu}&hl={dil_kodu}"
    
    print(f"🌍 KONUM IŞINLAMASI BAŞARILI: {ulke_uzantisi.upper()} ({lat}, {lng})")
    
    # İnsan davranışı simülasyonu (hemen linke saldırmıyoruz)
    driver.get(google_url)
    time.sleep(2) 
    
    return driver