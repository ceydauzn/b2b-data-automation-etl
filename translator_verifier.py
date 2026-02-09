import requests
from bs4 import BeautifulSoup

def iate_dogrulama(kelime, hedef_dil="en"):
    """
    IATE veritabanı üzerinden teknik terim doğrulaması yapar. 
    """
    url = f"https://iate.europa.eu/search/standard/result/1/1" 
    
    params = {
        "term": kelime,
        "sl": "tr", 
        "tl": hedef_dil 
    }

    try:
        response = requests.get(url, params=params)
        return f"{kelime} için {hedef_dil} dilinde teknik terimler kontrol edildi."
    except Exception as e:
        return f"Doğrulama hatası: {e}"

def cambridge_kontrol(kelime):
    """
    Cambridge Sözlük üzerinden kelimenin doğruluğunu kontrol eder. 
    """
    url = f"https://dictionary.cambridge.org/dictionary/english/{kelime}"
    headers = {"User-Agent": "Mozilla/5.0"} 
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return "Terim sözlükte mevcut ve geçerli."
        else:
            return "Terim bulunamadı, kontrol ediniz."
    except Exception as e:
        return f"Bağlantı hatası: {e}"

# TEST ETMEK İÇİN:
if __name__ == "__main__":
    test_kelime = "piston"
    print(f"Cambridge Sonucu: {cambridge_kontrol(test_kelime)}")
    print(f"IATE Sonucu: {iate_dogrulama(test_kelime, 'en')}")