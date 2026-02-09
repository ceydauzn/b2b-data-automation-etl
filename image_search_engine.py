import pandas as pd
# Önceki yazdığımız modülleri buraya çağırıyoruz
from image_processor import resim_analiz_et
from scrapper import sonuclari_excele_aktar

def gorselle_web_sitesi_bul(resim_yolu):
    """
    1. Resmi analiz eder.
    2. Resmi internette arar (Reverse Image Search).
    3. Bulunan siteleri listeler.
    """
    
    # 1. Önce resmin sağlam olup olmadığını ve özelliklerini kontrol et
    analiz_sonucu = resim_analiz_et(resim_yolu)
    print(f"Sistem Mesajı: {analiz_sonucu}")
    
    if "Hata" in analiz_sonucu:
        return []

    print(f"--- {resim_yolu} için internet taraması başlatılıyor ---")
    
    # NOT: Gerçek bir Google Lens araması için 'SerpApi' veya 'Google Vision API' gerekir.
    # Şimdilik proje prototipi olduğu için, arama motorunun bulacağı "Örnek Sonuçları" simüle ediyoruz.
    # (Buraya daha sonra gerçek API kodunu entegre edebilirsin)
    
    bulunan_siteler = [
        # Bu veriler normalde Google'dan dönecek
        {"Firma": "Bulunan Firma A (Rusya)", "Web": "www.russia-parts.ru", "Kaynak": "Görsel Eşleşme", "Eşleşme Oranı": "%95"},
        {"Firma": "Bulunan Firma B (Almanya)", "Web": "www.germany-auto.de", "Kaynak": "Görsel Eşleşme", "Eşleşme Oranı": "%88"},
        {"Firma": "Yan Sanayi C", "Web": "www.yansanayi.com", "Kaynak": "Benzer Görsel", "Eşleşme Oranı": "%70"}
    ]
    
    return bulunan_siteler

# --- ANA ÇALIŞTIRMA BLOĞU ---
if __name__ == "__main__":
    resim = "deneme.jpg" # Klasöründeki resmin adı
    
    # 1. Aramayı Yap
    sonuclar = gorselle_web_sitesi_bul(resim)
    
    # 2. Sonuçları Ekrana Yaz
    print(f"\nToplam {len(sonuclar)} web sitesi bulundu.")
    
    # 3. Sonuçları Excel'e Kaydet (Scrapper modülündeki fonksiyonu kullanıyoruz)
    if sonuclar:
        sonuclari_excele_aktar(sonuclar, "gorsel_arama_sonuclari.xlsx")