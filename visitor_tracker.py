import requests

def ziyaretci_bilgisi_al(ip_adresi):
    """
    IP adresinden konum ve potansiyel firma ismini bulur.
    (Dökümandaki 1-b maddesi için IP tabanlı çözüm)
    """
    try:
        # IP Geolocation API servisini kullanıyoruz (ip-api gibi ücretsiz servisler)
        url = f"http://ip-api.com/json/{ip_adresi}?fields=status,message,country,city,isp,org,as"
        response = requests.get(url)
        data = response.json()
        
        if data['status'] == 'success':
            return {
                "Ülke": data.get('country'),
                "Şehir": data.get('city'),
                "Organizasyon/Firma": data.get('org') or data.get('isp'), # Firma ismini buradan yakalıyoruz
                "IP": ip_adresi
            }
    except Exception as e:
        return f"Hata: {e}"

# Örnek kullanım (Ziyaretçi geldiğinde tetiklenecek)
# print(ziyaretci_bilgisi_al("8.8.8.8"))