import requests
from bs4 import BeautifulSoup
import time

def valentin_gibi_ara(yerel_arama_terimi, ulke_uzantisi):
    """
    Valentin.app mantığıyla Google'ı kandırarak o ülkeden arama yapıyormuş gibi davranır.
    """
    # Google'ın bölge (gl) ve dil (hl) kodlarını ayarlıyoruz
    ulke_kodu = ulke_uzantisi.replace(".", "").upper() if ulke_uzantisi != ".com" else "US"
    dil_kodu = ulke_uzantisi.replace(".", "").lower() if ulke_uzantisi != ".com" else "en"
    
    print(f"🕵️ Valentin Bot: {ulke_kodu} pazarında '{yerel_arama_terimi}' aranıyor...")

    # Valentin'in taklit ettiği arama URL'si mantığı
    url = f"https://www.google.com/search?q={yerel_arama_terimi}&gl={ulke_kodu}&hl={dil_kodu}"
    
    # Gerçek bir insanmışız gibi tarayıcı başlıkları (User-Agent) ekliyoruz
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    sonuclar = []
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Google organik arama sonuçlarının kutularını bul
            siteler = soup.find_all("div", class_="tF2Cxc")
            
            for site in siteler:
                baslik = site.find("h3").text if site.find("h3") else "Başlıksız"
                link = site.find("a")["href"] if site.find("a") else ""
                
                # Potansiyel B2B veya e-ticaret sitelerini yakala
                if link and "google.com" not in link:
                    sonuclar.append({"Firma_Basligi": baslik, "Web_Sitesi": link})
                    print(f"✅ Potansiyel Alıcı Bulundu: {baslik}")
        else:
            print(f"⚠️ Google aramayı engelledi. Durum Kodu: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Valentin Bot Hatası: {e}")

    time.sleep(2) # Banlanmamak için kısa bir bekleme
    return sonuclar