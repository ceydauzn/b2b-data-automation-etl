from deep_translator import GoogleTranslator

# Ülke uzantılarına göre hedef dil kodları
DIL_HARITASI = {
    ".com": "en", ".de": "de", ".fr": "fr", ".ru": "ru", 
    ".es": "es", ".tr": "tr", ".ae": "ar", ".it": "it",
    ".cn": "zh-CN", ".jp": "ja", ".kr": "ko"
}

def akilli_cevirmen(urun_tanimi, hedef_ulke_uzantisi):
    """Girilen metni otomatik algılar ve hedef pazarın diline çevirir."""
    hedef_dil = DIL_HARITASI.get(hedef_ulke_uzantisi, "en")
    
    try:
        cevirmen = GoogleTranslator(source='auto', target=hedef_dil)
        ceviri = cevirmen.translate(urun_tanimi)
        print(f"🌍 DİL ASİSTANI: '{urun_tanimi}' -> '{ceviri}' ({hedef_dil.upper()})")
        return ceviri
    except Exception as e:
        print(f"❌ Çeviri Hatası: {e}")
        return urun_tanimi