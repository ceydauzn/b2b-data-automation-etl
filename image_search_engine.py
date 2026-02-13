import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time
from googlesearch import search
from serpapi import GoogleSearch 
from deep_translator import GoogleTranslator

# --- 1. MODÜL: TEKNİK TERİM DOĞRULAMA VE ÇEVİRİ ---
def teknik_terim_dogrula_ve_cevir(kelime, hedef_uzanti):
    """
    Döküman Madde 1-a & c: Kelimeyi seçilen ülkenin diline çevirir.
    """
    uzanti_dil_haritasi = {
        '.de': 'de', '.ru': 'ru', '.es': 'es', 
        '.fr': 'fr', '.it': 'it', '.com': 'en'
    }
    hedef_dil = uzanti_dil_haritasi.get(hedef_uzanti, 'en')
    try:
        print(f"🌐 '{kelime}' terimi {hedef_uzanti} pazarı için çevriliyor...")
        cevirilmis = GoogleTranslator(source='auto', target=hedef_dil).translate(kelime)
        print(f"✅ Teknik Karşılığı: {cevirilmis}")
        return cevirilmis
    except Exception as e:
        print(f"⚠️ Çeviri hatası: {e}. Orijinal kelime kullanılacak.")
        return kelime

# --- 2. MODÜL: B2B İLETİŞİM AYIKLAYICI ---
def b2b_iletisim_tara(url):
    """Web sitesinin içine girip e-postaları ayıklar."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    try:
        if not url.startswith("http"):
            url = "https://" + url
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            metin = soup.get_text()
            
            mail_deseni = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            mailler = list(set(re.findall(mail_deseni, metin)))
            
            oncelikli = "Bulunamadı"
            for m in mailler:
                if any(k in m.lower() for k in ['purchasing', 'sales', 'info', 'manager', 'buying', 'contact']):
                    oncelikli = m
                    break
            if oncelikli == "Bulunamadı" and mailler:
                oncelikli = mailler[0]
                
            return ", ".join(mailler), oncelikli
    except:
        return "Erişilemedi", "Erişilemedi"
    return "Bulunamadı", "Bulunamadı"

# --- 3. MODÜL: AKILLI ARAMA MOTORU ---
def google_canli_arama(oem_no, yerel_parca_ismi, ulke_uzantisi, adet=5):
    """Hem API hem de ücretsiz arama ile linkleri toplar."""
    linkler = []
    
    # --- SERPAPI ANAHTARI ---
    # Eğer API anahtarın varsa buraya yazabilirsin.
    SERP_API_KEY = "BURAYA_KENDI_API_ANAHTARINI_YAZ" 

    if SERP_API_KEY and SERP_API_KEY != "BURAYA_KENDI_API_ANAHTARINI_YAZ":
        print(f"🚀 SerpApi üzerinden '{yerel_parca_ismi}' olarak aranıyor...")
        try:
            params = {
                "q": f"{oem_no} {yerel_parca_ismi} site:*{ulke_uzantisi}",
                "location": "Global",
                "api_key": SERP_API_KEY
            }
            search_api = GoogleSearch(params)
            results = search_api.get_dict().get("organic_results", [])
            linkler = [r.get("link") for r in results[:adet]]
            if linkler: print(f"✅ API ile {len(linkler)} sonuç getirildi.")
        except Exception as e:
            print(f"⚠️ API Hatası: {e}. Ücretsiz yönteme geçiliyor.")

    # API başarısızsa veya yoksa ücretsiz yöntem
    if not linkler:
        print(f"🔍 Ücretsiz yöntem deneniyor: {yerel_parca_ismi}")
        sorgular = [
            f"{oem_no} {yerel_parca_ismi} {ulke_uzantisi}",
            f"{yerel_parca_ismi} supplier {ulke_uzantisi}"
        ]
        for sorgu in sorgular:
            if len(linkler) >= adet: break
            try:
                for j in search(sorgu, num_results=adet):
                    if j not in linkler:
                        linkler.append(j)
                    if len(linkler) >= adet: break
                if linkler: break
                time.sleep(2)
            except:
                continue
                
    return linkler

# --- 4. MODÜL: ANA İŞLEYİCİ (Global Pazar Taraması) ---
def global_pazar_taramasi(oem_no, parca_ismi, ulke_uzantisi):
    """
    Arayüz (GUI) tarafından çağrılan ana fonksiyon. 
    Tüm iş akışını yönetir.
    """
    print(f"\n🚀 {ulke_uzantisi} Pazarı Analiz Ediliyor...")
    
    # 1. Parça ismini hedef dile çevir
    yerel_isim = teknik_terim_dogrula_ve_cevir(parca_ismi, ulke_uzantisi)
    
    # 2. Google'dan linkleri topla
    bulunan_linkler = google_canli_arama(oem_no, yerel_isim, ulke_uzantisi)
    
    final_listesi = []
    if not bulunan_linkler:
        print("❌ Hiçbir sonuç bulunamadı.")
        return []

    # 3. Bulunan siteleri tek tek analiz et
    for url in bulunan_linkler:
        print(f"🔎 Veri çekiliyor: {url}")
        mailler, yetkili = b2b_iletisim_tara(url)
        
        final_listesi.append({
            "OEM No": oem_no,
            "Aranan Terim": parca_ismi,
            "Yerel Karşılık": yerel_isim,
            "Ülke": ulke_uzantisi,
            "Web Sitesi": url,
            "E-postalar": mailler,
            "Öncelikli Yetkili": yetkili,
            "Tarama Tarihi": datetime.now().strftime("%d/%m/%Y")
        })
        time.sleep(1) # Banlanma önleyici bekleme
        
    return final_listesi