import geonamescache
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def tum_dunya_koordinat_sozlugu_olustur():
    """
    Dünyadaki tüm ülkelerin merkez koordinatlarını güvenli bir şekilde döndürür.
    Eksik veri (lat/lng) olan ülkeleri hata vermeden atlar.
    """
    gc = geonamescache.GeonamesCache()
    countries = gc.get_countries()
    global_coords = {}
    
    for code, info in countries.items():
        # HATA DÜZELTME: Veri var mı kontrol et (KeyError: 'lat' önleyici)
        if 'lat' in info and 'lng' in info:
            # Uzantıyı belirle (.tr, .az vb.)
            if info['tld']:
                ext = "." + info['tld'].replace(".", "")
            else:
                ext = f".{code.lower()}"
                
            global_coords[ext] = {"lat": info['lat'], "lng": info['lng']}
            
    return global_coords
# Koordinat veritabanını oluştur
KOORDINAT_VERITABANI = tum_dunya_koordinat_sozlugu_olustur()

def valentin_simulasyonu_baslat(sorgu, ulke_kodu, dil_kodu, ulke_uzantisi):
    """
    Tarayıcının GPS konumunu değiştirerek Berlin takılmasını çözer.
    """
    options = Options()
    # Gerçek bir kullanıcı gibi davranmak için dilleri de ekleyelim
    options.add_argument(f"--lang={dil_kodu}")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # 1. Koordinatları al
    nokta = KOORDINAT_VERITABANI.get(ulke_uzantisi, {"lat": 37.0902, "lng": -95.7129})
    lat = float(nokta['lat'])
    lng = float(nokta['lng'])

    # 2. KRİTİK ADIM: Tarayıcıyı o koordinata "Işınla" (Berlin'i unutturur)
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
        "latitude": lat,
        "longitude": lng,
        "accuracy": 100
    })

    # 3. URL oluşturma (Google Maps kancası eklenmiş)
    u_kodu = ulke_kodu.lower()
    # Harita sonuçlarını tetiklemek için sorgu sonuna ülke ekliyoruz
    google_url = f"https://www.google.com/search?q={sorgu}+{ulke_kodu}&gl={u_kodu}&hl={dil_kodu}&tbm=lcl"
    
    print(f"🌍 KONUM BAŞARIYLA DEĞİŞTİRİLDİ: {ulke_uzantisi.upper()} ({lat}, {lng})")
    
    driver.get(google_url)
    return driver