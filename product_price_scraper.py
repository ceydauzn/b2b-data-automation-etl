import requests
from bs4 import BeautifulSoup

# Test ettiğin linki buraya yaz (tırnak içinde):
url = "www.yansanayi.com/urun/piston-segmenti"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers)
    print(f"Bağlantı Durumu: {response.status_code}") # 200 ise başarılı, 403 ise engellendik demektir.

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        # Sayfanın başlığını yazdıralım ki doğru yerde miyiz görelim
        print(f"Sayfa Başlığı: {soup.title.text.strip()}")
        
        # Fiyatı bulmaya çalış (Burası siteye göre değişecek)
        # Şimdilik sadece tüm metni çekip içinde 'TL' var mı bakalım
        if "TL" in soup.text:
            print("Sayfada TL ibaresi var, fiyat çekilebilir.")
        else:
            print("Sayfada TL bulunamadı, muhtemelen dinamik yükleniyor.")
            
    else:
        print("Siteye giriş engellendi (403/503 Hatası).")

except Exception as e:
    print(f"Hata: {e}")