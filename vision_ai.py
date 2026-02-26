import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import threading
from PIL import Image
import torch # ⚡ HIZLANDIRMA İÇİN EKLENDİ

_classifier = None 
_yukleniyor = False 

# --- 🛠️ ÇOKTAN SEÇMELİ SANAYİ TESTİ (SIFIR-ATAR MANTIĞI) ---
OTOMOTIV_PARCALARI = [
    "steering wheel", "disk brake", "car engine", "car bumper", 
    "radiator", "car battery", "headlight", "car mirror", 
    "seat belt", "windshield wiper", "spark plug", "car tire", 
    "suspension", "exhaust pipe", "car wheel"
]

def modeli_arka_planda_yukle():
    """Ücretsiz ve yerel CLIP modelini arka planda sessizce yükler."""
    global _classifier, _yukleniyor
    if _classifier is None and not _yukleniyor:
        _yukleniyor = True
        print("🧠 ÜCRETSİZ Yerel Zeka (Hugging Face CLIP) Yükleniyor...")
        
        from transformers import pipeline
        
        # ⚡ OPTİMİZASYON 1: Ekran Kartı (GPU) Taraması
        # Sisteminde uyumlu bir GPU varsa onu kullanır, yoksa en verimli şekilde CPU'da çalışır
        cihaz_id = 0 if torch.cuda.is_available() else -1
        
        _classifier = pipeline("zero-shot-image-classification", 
                               model="openai/clip-vit-base-patch32", 
                               device=cihaz_id)
        
        # ⚡ OPTİMİZASYON 2: Isınma Turu (Warm-up)
        # Modelin "ilk fotoğrafı yavaş işleme" huyunu kırmak için arka planda beyaz bir resimle motoru ısıtıyoruz
        print("⚙️ Model motoru ısıtılıyor (Warm-up)...")
        sahte_resim = Image.new('RGB', (224, 224), color='white')
        _classifier(sahte_resim, candidate_labels=["test"])
        
        print("✅ Yerel Zeka Motoru Kuruldu, Isındı ve Fişek Gibi Hazır!")
        _yukleniyor = False

threading.Thread(target=modeli_arka_planda_yukle, daemon=True).start()

def resmi_analiz_et(resim_yolu):
    """
    Sıfır-Atar (Zero-Shot) mantığıyla fotoğrafı sadece otomotiv sözlüğüyle karşılaştırır.
    """
    global _classifier
    try:
        while _classifier is None:
            import time
            print("⏳ Yapay zeka motoru hazırlanıyor, lütfen bekleyin...")
            time.sleep(1) # Bekleme süresi 2'den 1'e düşürüldü
            
        print("🔍 CLIP Zekası görseli Sektör Sözlüğüyle eşleştiriyor...")
        
        # ⚡ OPTİMİZASYON 3: Resim Küçültme (Thumbnail)
        # Orijinal resmi bozmadan, sadece yapay zekanın inceleyeceği kopyayı ufalttık
        image = Image.open(resim_yolu).convert('RGB')
        image.thumbnail((300, 300)) 
        
        sonuclar = _classifier(image, candidate_labels=OTOMOTIV_PARCALARI)
        
        en_iyi_sonuc = sonuclar[0]['label']
        
        print("\n📊 ÇOKTAN SEÇMELİ TEST SONUÇLARI (İLK 3):")
        for i in range(3):
            print(f"  {i+1}. %{round(sonuclar[i]['score']*100, 2):05.2f} ihtimalle : {sonuclar[i]['label'].upper()}")
        print("-" * 40)
        
        return en_iyi_sonuc
        
    except Exception as e:
        print(f"❌ Resim Analiz Hatası: {e}")
        return None