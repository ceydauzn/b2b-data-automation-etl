import cv2
import numpy as np

def resim_karsilastir(referans_resim_yolu, hedef_resim_yolu):
    """
    Döküman Madde 2-e: Ürün resmiyle eşleşen siteleri bulmak için 
    iki resmi karşılaştırır ve benzerlik oranını döner.
    """
    # Resimleri oku
    img1 = cv2.imread(referans_resim_yolu, 0) # Bizim parça (deneme.jpg)
    img2 = cv2.imread(hedef_resim_yolu, 0)    # İnternetten bulunan parça

    if img1 is None or img2 is None:
        return 0

    # ORB Tanımlayıcı oluştur (Senin yazdığın Pylance güvenli yöntemi)
    try:
        orb = cv2.ORB_create()
    except:
        orb = getattr(cv2, 'ORB_create')()

    # Anahtar noktaları ve tanımlayıcıları bul
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    if des1 is None or des2 is None:
        return 0

    # Brute-Force Eşleştirici (BFMatcher) kullanarak noktaları kıyasla
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)

    # Mesafeye göre sırala (Daha kısa mesafe = daha çok benzerlik)
    matches = sorted(matches, key=lambda x: x.distance)

    # Benzerlik puanı hesapla (Eşleşen nokta sayısı / Toplam nokta sayısı)
    skor = len(matches) / max(len(kp1), len(kp2)) * 100
    return round(skor, 2)

if __name__ == "__main__":
    resim_adi = "deneme.jpg" 
    print(f"📸 {resim_adi} üzerinden karşılaştırma motoru aktif.")
    # Örnek kullanım:
    # benzerlik = resim_karsilastir("deneme.jpg", "bulunan_ilan.jpg")
    # print(f"Benzerlik Oranı: %{benzerlik}")