import cv2
import numpy as np

def resim_analiz_et(resim_yolu):
    image = cv2.imread(resim_yolu)
    if image is None:
        return "Hata: Resim dosyası bulunamadı."

    # Gri tonlamaya çevirme (Analiz hızı için şart)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Pylance hatasını aşmak için alternatif yöntem:
    try:
        # Önce standart yöntemi dene
        orb = cv2.ORB_create()
    except (AttributeError, Exception):
        # Eğer tanımazsa direkt kütüphaneden zorlayarak çağır
        orb = getattr(cv2, 'ORB_create')()
        
    keypoints, descriptors = orb.detectAndCompute(gray, None)
    return f"Resim analiz edildi. {len(keypoints)} adet ayırt edici nokta bulundu."
# --- BU KISIM DOSYANIN EN ALTINDA OLMALI ---
if __name__ == "__main__":
    # Klasördeki resmin adını buraya tam doğru yazmalısın
    resim_adi = "deneme.jpg" 
    
    print(f"{resim_adi} analizi başlıyor...")
    sonuc = resim_analiz_et(resim_adi)
    print("SONUÇ:", sonuc)