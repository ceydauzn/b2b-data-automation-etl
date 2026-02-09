def get_complementary_data(main_keyword, gtip_code=None):
    """
    Belgedeki 15-17. maddelere göre bağlı sektörleri ve 
    yan GTİP verilerini analiz eder.
    """
    # Belgedeki örneklere göre oluşturulmuş bağlı sektör haritası
    # [cite: 15, 16, 17]
    sector_map = {
        "kaynak ekipmanları": ["hırdavat", "metal işleme"], # [cite: 15]
        "otomobil": ["oto yedek parça", "lastik", "servis ekipmanları"], # [cite: 16]
        "vinç": ["demir", "çelik", "inşaat ekipmanları"], # [cite: 17]
    }
    
    # GTİP bazlı tamamlayıcı çalışma [cite: 17]
    gtip_map = {
        "8708": ["8703", "4011"], # Yedek parça kodu girilirse araç kodunu da ekle
        "8426": ["7214", "7216"], # Vinç kodu girilirse demir-çelik kodlarını ekle
    }

    results = {
        "additional_keywords": [],
        "additional_gtips": []
    }

    # Anahtar kelime eşleşmesi kontrolü
    for key, values in sector_map.items():
        if key in main_keyword.lower():
            results["additional_keywords"].extend(values)

    # GTİP eşleşmesi kontrolü (İlk 4 hane üzerinden) [cite: 17]
    if gtip_code:
        prefix = str(gtip_code)[:4]
        results["additional_gtips"].extend(gtip_map.get(prefix, []))

    return results

# TEST ETMEK İÇİN:
if __name__ == "__main__":
    test_keyword = "kaynak ekipmanları"
    print(f"Bağlı Sektör Analizi: {get_complementary_data(test_keyword)}")