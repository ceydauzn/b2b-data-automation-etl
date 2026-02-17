import customtkinter as ctk
from tkinter import messagebox
import threading
import time
import pandas as pd
import pycountry

# --- YARDIMCI FONKSİYONLAR ---
def dunya_verilerini_hazirla():
    """Tüm ülkeleri alfabetik ve düzenli bir liste haline getirir."""
    data = []
    data.append({"display": "Global (.com)", "code": "us", "extension": ".com"})
    sorted_countries = sorted(pycountry.countries, key=lambda x: x.name)
    for country in sorted_countries:
        try:
            data.append({
                "display": f"{country.name} (.{country.alpha_2.lower()})",
                "code": country.alpha_2.lower(),
                "extension": f".{country.alpha_2.lower()}"
            })
        except: continue
    return data

# Modül içe aktarmaları
try:
    from image_search_engine import global_pazar_taramasi
    from maps_scraper import google_maps_tara
    from visitor_tracker import ip_tabanli_firma_bul, koordinat_tabanli_firma_bul
except ImportError:
    print("Uyarı: Bazı modül dosyaları bulunamadı.")

# --- TASARIM AYARLARI ---
ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("blue") 

class ModernB2BApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Ayarları
        self.title("Global B2B Hunter Enterprise v2.0")
        self.geometry("950x800")
        
        # Ülke veritabanı
        self.ulke_listesi = dunya_verilerini_hazirla()

        # Grid Yapılandırması
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SOL PANEL (SIDEBAR) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="HUNTER CORE", 
                                       font=ctk.CTkFont(family="Inter", size=22, weight="bold"),
                                       text_color="#38bdf8")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 40))

        self.map_btn = ctk.CTkButton(self.sidebar_frame, text="📍 Harita Modülü", 
                                     font=ctk.CTkFont(size=14, weight="bold"),
                                     height=40,
                                     command=self.run_map_process)
        self.map_btn.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.appearance_label = ctk.CTkLabel(self.sidebar_frame, text="Görünüm Modu:", font=ctk.CTkFont(size=12))
        self.appearance_label.grid(row=5, column=0, padx=20, pady=(400, 0))
        
        self.appearance_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light"], 
                                                        command=self.change_appearance_mode)
        self.appearance_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 20))
        self.appearance_optionemenu.set("Dark")

        # --- ANA PANEL ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=20)
        self.main_frame.grid(row=0, column=1, padx=25, pady=25, sticky="nsew")

        self.header_label = ctk.CTkLabel(self.main_frame, text="İHRACAT İSTİHBARAT TERMİNALİ", 
                                         font=ctk.CTkFont(family="Inter", size=26, weight="bold"))
        self.header_label.pack(pady=(20, 10))

        # --- MODÜL 1: ERİŞİM PANELİ ---
        self.visitor_panel = ctk.CTkFrame(self.main_frame, corner_radius=15, border_width=1)
        self.visitor_panel.pack(pady=15, padx=30, fill="x")

        self.v_label = ctk.CTkLabel(self.visitor_panel, 
                                    text="Size daha iyi hizmet verebilmemiz için lütfen konum bilgisini bizimle paylaşın.", 
                                    font=ctk.CTkFont(size=13, weight="bold"), text_color="#38bdf8")
        self.v_label.pack(pady=(20, 10))

        self.btn_frame = ctk.CTkFrame(self.visitor_panel, fg_color="transparent")
        self.btn_frame.pack(pady=(0, 20))

        self.yes_btn = ctk.CTkButton(self.btn_frame, text="ERİŞİME İZİN VER", width=160, height=35,
                                     fg_color="#059669", hover_color="#10b981", 
                                     command=lambda: self.ziyaretci_karar_simule_et("Evet"))
        self.yes_btn.grid(row=0, column=0, padx=15)

        self.no_btn = ctk.CTkButton(self.btn_frame, text="ERİŞİMİ REDDET", width=160, height=35,
                                    fg_color="#dc2626", hover_color="#ef4444", 
                                    command=lambda: self.ziyaretci_karar_simule_et("Hayır"))
        self.no_btn.grid(row=0, column=1, padx=15)

        # --- MODÜL 2: ARAMA TERMİNALİ ---
        self.search_frame = ctk.CTkFrame(self.main_frame, corner_radius=15, fg_color="transparent")
        self.search_frame.pack(pady=10, padx=30, fill="both", expand=True)

        self.s_title = ctk.CTkLabel(self.search_frame, text="🔍 PAZAR TARAMA KRİTERLERİ", 
                                    font=ctk.CTkFont(size=15, weight="bold"))
        self.s_title.pack(pady=(10, 15))

        self.entry_row = ctk.CTkFrame(self.search_frame, fg_color="transparent")
        self.entry_row.pack(pady=5)

        self.oem_entry = ctk.CTkEntry(self.entry_row, placeholder_text="OEM NUMARASI", width=200, height=45)
        self.oem_entry.grid(row=0, column=0, padx=10)

        self.gtip_entry = ctk.CTkEntry(self.entry_row, placeholder_text="GTIP KODU", width=200, height=45)
        self.gtip_entry.grid(row=0, column=1, padx=10)

        self.name_entry = ctk.CTkEntry(self.search_frame, placeholder_text="ÜRÜN TANIMI (İngilizce veya Yerel Dil)", 
                                       width=420, height=45)
        self.name_entry.pack(pady=15)

        self.country_label = ctk.CTkLabel(self.search_frame, text="HEDEF PAZAR / ÜLKE:", font=ctk.CTkFont(size=12, weight="bold"))
        self.country_label.pack(pady=(5, 0))
        
        ulke_isimleri = [u["display"] for u in self.ulke_listesi]

        self.country_combo = ctk.CTkComboBox(
            self.search_frame, 
            values=ulke_isimleri, 
            width=420, 
            height=45,
            justify="center"
        )
        self.country_combo.pack(pady=10)
        self.country_combo.set("Global (.com)")

        self.run_button = ctk.CTkButton(self.search_frame, text="KÜRESEL ANALİZİ BAŞLAT", 
                                        font=ctk.CTkFont(size=15, weight="bold"), 
                                        width=350, height=55, corner_radius=30, 
                                        fg_color="#0284c7", hover_color="#0369a1",
                                        command=self.start_web_search_thread)
        self.run_button.pack(pady=25)

        self.progress_bar = ctk.CTkProgressBar(self.search_frame, width=500, height=12)
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self.search_frame, text="SİSTEM DURUMU: BEKLEMEDE", 
                                         font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=10)

    # --- TEKNİK FONKSİYONLAR ---
    def change_appearance_mode(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)

    def ziyaretci_karar_simule_et(self, karar):
        """
        Döküman Madde 1-a (Gerçek Konum) ve 1-b (IP Takip) Entegrasyonu:
        Ziyaretçiden bilgiyi gizler, Admin'e SİZİN GERÇEK verilerinizi sunar.
        """
        import visitor_tracker # Gerçek verileri çekmek için

        if karar == "Evet":
            # 1-a: GERÇEK VERİLERİ ÇEK (Statik Berlin verisi silindi)
            data = visitor_tracker.gercek_ip_ve_firma_analiz_et()
            
            # Ekranda ziyaretçinin gördüğü (Hassas bilgi içermez)
            self.v_label.configure(text="✅ Konum eşleşti. Yerel pazar verileri optimize ediliyor.", text_color="#10b981")
            
            # SADECE ADMİNİN (SİZİN) GÖRECEĞİ GERÇEK RAPOR
            admin_mesaj = (
                f"🛡️ YÖNETİCİ İSTİHBARAT RAPORU (CANLI)\n"
                f"----------------------------------\n"
                f"🏢 TESPİT EDİLEN AĞ/FİRMA: {data['Firma']}\n"
                f"🌍 LOKASYON: {data['Sehir']}, {data['Ulke']}\n"
                f"📍 KOORDİNAT: {data['Lat']}, {data['Lon']}\n"
                f"🔢 GERÇEK IP: {data['IP']}\n"
                f"🔍 DURUM: Nokta atışı konum doğrulandı."
            )
            messagebox.showinfo("Admin Özel Panel", admin_mesaj)
            
        else:
            # 1-b: IP üzerinden kısıtlı takip
            data = visitor_tracker.gercek_ip_ve_firma_analiz_et()
            
            # Ekranda ziyaretçinin gördüğü
            self.v_label.configure(text="⚠️ Konum reddedildi. Standart güvenlik moduna geçildi.", text_color="#fbbf24")
            
            # SADECE ADMİNİN GÖRECEĞİ IP RAPORU
            admin_ip_mesaj = (
                f"🕵️ YÖNETİCİ IP ANALİZ RAPORU\n"
                f"----------------------------------\n"
                f"🔢 ZİYARETÇİ IP: {data['IP']}\n"
                f"📡 SERVİS SAĞLAYICI: {data['ISS']}\n"
                f"⚙️ DURUM: Konum izni yok, sadece ağ verisi çekildi."
            )
            messagebox.showwarning("Admin Gizli IP Takibi", admin_ip_mesaj)
    def start_web_search_thread(self):
        oem = self.oem_entry.get()
        gtip = self.gtip_entry.get()
        name = self.name_entry.get()
        secilen_display = self.country_combo.get() 
        ulke_verisi = next((u for u in self.ulke_listesi if u["display"] == secilen_display), 
                           {"extension": ".com", "code": "us", "display": "Global (.com)"})
        if not name:
            messagebox.showwarning("Giriş Hatası", "Ürün Tanımı girmelisiniz.")
            return
        self.run_button.configure(state="disabled", text="ANALİZ YAPILIYOR...")
        self.status_label.configure(text=f"BOT DURUMU: {ulke_verisi['display']} taranıyor...")
        self.progress_bar.set(0.3)
        threading.Thread(target=self.web_search_worker, 
                         args=(oem, name, ulke_verisi['extension'], gtip, ulke_verisi['code']), 
                         daemon=True).start()

    def web_search_worker(self, oem, name, extension, gtip, country_code):
        try:
            sonuclar = global_pazar_taramasi(oem, name, extension, gtip_no=gtip)
            self.after(0, lambda: self.search_finished(len(sonuclar), oem))
        except Exception as e:
            self.after(0, lambda: self.handle_error(e))

    def run_map_process(self):
        name = self.name_entry.get()
        secilen_display = self.country_combo.get()
        ulke_verisi = next((u for u in self.ulke_listesi if u["display"] == secilen_display), self.ulke_listesi[0])
        if not name:
            messagebox.showwarning("Eksik Veri", "Sektör ismi girin.")
            return
        self.map_btn.configure(state="disabled")
        threading.Thread(target=self.map_worker, args=(name, ulke_verisi['extension']), daemon=True).start()

    def map_worker(self, name, country):
        try:
            sonuclar = google_maps_tara(name, country)
            if sonuclar:
                df = pd.DataFrame(sonuclar)
                df.to_excel(f"Maps_{name.replace(' ', '_')}_{country}.xlsx", index=False)
                self.after(0, lambda: messagebox.showinfo("Başarılı", "Veriler kaydedildi."))
            self.after(0, self.map_finished)
        except Exception as e:
            self.after(0, lambda: self.handle_error(e))

    def map_finished(self):
        self.map_btn.configure(state="normal")
        self.status_label.configure(text="SİSTEM DURUMU: HARİTA ANALİZİ TAMAMLANDI")
        self.progress_bar.set(1.0)

    def search_finished(self, count, oem):
        self.progress_bar.set(1.0)
        self.run_button.configure(state="normal", text="KÜRESEL ANALİZİ BAŞLAT")
        messagebox.showinfo("Analiz Tamamlandı", f"{count} adet potansiyel müşteri bulundu.")

    def handle_error(self, error):
        self.run_button.configure(state="normal", text="YENİDEN DENE")
        messagebox.showerror("Hata", f"Sistem hatası: {error}")

if __name__ == "__main__":
    app = ModernB2BApp()
    app.mainloop()