import requests
import pycountry

def tum_dunya_verilerini_hazirla():
    """Tüm ülkeleri, uzantılarını ve Google yerel kodlarını (GL/HL) hazırlar."""
    dunya_listesi = []
    # Genel uzantıları ekle
    dunya_listesi.append({"isim": "Global (.com)", "kod": "us", "uzanti": ".com", "dil": "en"})
    
    for country in pycountry.countries:
        try:
            dunya_listesi.append({
                "isim": f"{country.name} (.{country.alpha_2.lower()})",
                "kod": country.alpha_2.lower(),
              "uzanti": f".{country.alpha_2.lower()}",
                "dil": country.alpha_2.lower() # Varsayılan dil kodu
            })
        except: continue
    return sorted(dunya_listesi, key=lambda x: x["isim"])

# DURUM B: KULLANICI HAYIR DEDİ (IP Üzerinden Takip)
def ip_tabanli_firma_bul(ip_adresi):
    """
    Patronun 1-b maddesi: Kullanıcı konum izni vermezse çalışır.
    """
    try:
        url = f"http://ip-api.com/json/{ip_adresi}?fields=status,org,country,city,as"
        response = requests.get(url, timeout=5).json()
        
        if response.get("status") == "success":
            return {
                "Yöntem": "IP Sorgu (Gizli Takip)",
                "Firma": response.get("org"), # Şirket adı buradadır
                "Ülke": response.get("country"),
                "Detay": response.get("as")
            }
    except:
        return None

# DURUM A: KULLANICI EVET DEDİ (Konum Üzerinden Takip)
def koordinat_tabanli_firma_bul(lat, lon):
    """
    Patronun 1-a maddesi: Kullanıcı izin verirse nokta atışı yapar.
    """
    # Burada Google Maps Geocoding API kullanılır
    return {
        "Yöntem": "Konum Eşleşmesi (Doğrudan)",
        "Lokasyon": f"Enlem: {lat}, Boylam: {lon}",
        "Not": "Google Servisi ile firma ismi eşleştiriliyor..."
    }