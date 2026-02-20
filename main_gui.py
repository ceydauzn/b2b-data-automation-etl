import os 
# Diğer importlarının (import vision_ai vb.) yanına bunları da ekle:
from bs4 import BeautifulSoup
import translator_bot
import valentineapp

# --- TensorFlow Kırmızı Yazıları Gizle ---
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# --- 1. GRUP: Temel Kütüphaneler (ctk BURADA) ---
import customtkinter as ctk  # <--- HATA BUNUN EKSİKLİĞİNDEN KAYNAKLANIYOR
from tkinter import messagebox, filedialog
import threading
import time
import pandas as pd
import pycountry
from PIL import Image


# --- TASARIM AYARLARI ---
ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("blue") 

# ... Kodun geri kalanı (class ModernB2BApp...) buradan devam etsin ...

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
    import visitor_tracker
except ImportError:
    print("Uyarı: Bazı modül dosyaları bulunamadı. Lütfen tüm .py dosyalarının aynı klasörde olduğunu kontrol edin.")

# --- TASARIM AYARLARI ---
ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("blue") 

class ModernB2BApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Ayarları
        self.title("Global B2B Hunter Enterprise v2.0")
        self.geometry("1100x850")
        
        # Değişkenler
        self.ulke_listesi = dunya_verilerini_hazirla()
        self.secili_resim_yolu = None

        # Grid Yapılandırması
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SOL PANEL (SIDEBAR) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="HUNTER CORE", 
                                       font=ctk.CTkFont(family="Inter", size=22, weight="bold"),
                                       text_color="#38bdf8")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 40))

        self.home_btn = ctk.CTkButton(self.sidebar_frame, text="🔍 Ana Terminal", 
                                      command=self.show_main_terminal, height=40)
        self.home_btn.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.vision_btn = ctk.CTkButton(self.sidebar_frame, text="📷 Resim Analiz", 
                                        fg_color="#a855f7", hover_color="#9333ea",
                                        command=self.show_vision_panel, height=40)
        self.vision_btn.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.map_btn_sidebar = ctk.CTkButton(self.sidebar_frame, text="📍 Harita Modülü", 
                                             command=self.run_map_process, height=40)
        self.map_btn_sidebar.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.appearance_label = ctk.CTkLabel(self.sidebar_frame, text="Görünüm Modu:", font=ctk.CTkFont(size=12))
        self.appearance_label.grid(row=5, column=0, padx=20, pady=(350, 0))
        
        self.appearance_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light"], 
                                                        command=self.change_appearance_mode)
        self.appearance_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 20))

        # --- ANA İÇERİK ALANI ---
        self.main_container = ctk.CTkFrame(self, corner_radius=20, fg_color="transparent")
        self.main_container.grid(row=0, column=1, padx=25, pady=25, sticky="nsew")
        
        self.show_main_terminal()

    def clear_main_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def show_main_terminal(self):
        self.clear_main_container()
        
        header = ctk.CTkLabel(self.main_container, text="İHRACAT İSTİHBARAT TERMİNALİ", 
                              font=ctk.CTkFont(family="Inter", size=26, weight="bold"))
        header.pack(pady=(20, 10))

        # --- MODÜL: ERİŞİM PANELİ ---
        self.visitor_panel = ctk.CTkFrame(self.main_container, corner_radius=15, border_width=1)
        self.visitor_panel.pack(pady=15, padx=30, fill="x")

        self.v_label = ctk.CTkLabel(self.visitor_panel, 
                                    text="Size daha iyi hizmet verebilmemiz için lütfen konum bilgisini paylaşın.", 
                                    font=ctk.CTkFont(size=13, weight="bold"), text_color="#38bdf8")
        self.v_label.pack(pady=(20, 10))

        self.btn_frame = ctk.CTkFrame(self.visitor_panel, fg_color="transparent")
        self.btn_frame.pack(pady=(0, 20))

        self.yes_btn = ctk.CTkButton(self.btn_frame, text="ERİŞİME İZİN VER", width=160, fg_color="#059669", 
                                     command=lambda: self.ziyaretci_karar_simule_et("Evet"))
        self.yes_btn.grid(row=0, column=0, padx=15)

        self.no_btn = ctk.CTkButton(self.btn_frame, text="ERİŞİMİ REDDET", width=160, fg_color="#dc2626", 
                                    command=lambda: self.ziyaretci_karar_simule_et("Hayır"))
        self.no_btn.grid(row=0, column=1, padx=15)

        # --- MODÜL: ARAMA TERMİNALİ ---
        self.search_frame = ctk.CTkFrame(self.main_container, corner_radius=15)
        self.search_frame.pack(pady=10, padx=30, fill="both", expand=True)

        self.oem_entry = ctk.CTkEntry(self.search_frame, placeholder_text="OEM NUMARASI", width=420, height=45)
        self.oem_entry.pack(pady=10)

        self.gtip_entry = ctk.CTkEntry(self.search_frame, placeholder_text="GTIP KODU", width=420, height=45)
        self.gtip_entry.pack(pady=10)

        self.name_entry = ctk.CTkEntry(self.search_frame, placeholder_text="ÜRÜN TANIMI (Örn: Brake Pad)", width=420, height=45)
        self.name_entry.pack(pady=10)

        ulke_isimleri = [u["display"] for u in self.ulke_listesi]
        self.country_combo = ctk.CTkComboBox(self.search_frame, values=ulke_isimleri, width=420, height=45)
        self.country_combo.pack(pady=10)
        self.country_combo.set("Global (.com)")

        self.run_button = ctk.CTkButton(self.search_frame, text="KÜRESEL ANALİZİ BAŞLAT", 
                                        font=ctk.CTkFont(size=15, weight="bold"), 
                                        width=350, height=55, corner_radius=30,
                                        command=self.start_web_search_thread)
        self.run_button.pack(pady=20)

        self.progress_bar = ctk.CTkProgressBar(self.search_frame, width=500)
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self.search_frame, text="SİSTEM DURUMU: BEKLEMEDE")
        self.status_label.pack(pady=5)

    def show_vision_panel(self):
        self.clear_main_container()
        header = ctk.CTkLabel(self.main_container, text="📷 GÖRSEL ÜRÜN ANALİZ TERMİNALİ", 
                              font=ctk.CTkFont(size=24, weight="bold"), text_color="#a855f7")
        header.pack(pady=20)

        self.vision_frame = ctk.CTkFrame(self.main_container, width=600, height=350, corner_radius=15, border_width=2, border_color="#a855f7")
        self.vision_frame.pack(pady=20, padx=40)
        self.vision_frame.pack_propagate(False)

        self.upload_btn = ctk.CTkButton(self.vision_frame, text="FOTOĞRAF YÜKLE", fg_color="#a855f7", command=self.action_upload_image)
        self.upload_btn.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.main_container, text="HEDEF PAZAR SEÇİN:").pack(pady=5)
        ulke_isimleri = [u["display"] for u in self.ulke_listesi]
        self.vision_country_combo = ctk.CTkComboBox(self.main_container, values=ulke_isimleri, width=400, height=40)
        self.vision_country_combo.pack(pady=10)

        self.vision_run_btn = ctk.CTkButton(self.main_container, text="GÖRSEL ANALİZİ BAŞLAT", width=400, height=50, corner_radius=25,
                                            command=self.start_vision_search_thread)
        self.vision_run_btn.pack(pady=20)

    def action_upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Resim Dosyaları", "*.jpg *.jpeg *.png")])
        if file_path:
            self.secili_resim_yolu = file_path
            for widget in self.vision_frame.winfo_children(): widget.destroy()
            img = Image.open(file_path)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(300, 200))
            ctk.CTkLabel(self.vision_frame, image=ctk_img, text="").pack(pady=20)
            ctk.CTkLabel(self.vision_frame, text=os.path.basename(file_path)).pack()

    def ziyaretci_karar_simule_et(self, karar):
        data = visitor_tracker.gercek_ip_ve_firma_analiz_et()
        if karar == "Evet":
            self.v_label.configure(text="✅ Gerçek konumunuz doğrulandı.", text_color="#10b981")
            msg = f"🛡️ ADMİN RAPORU\nFirma: {data['Firma']}\nŞehir: {data['Sehir']}\nIP: {data['IP']}"
            messagebox.showinfo("Yönetici Paneli", msg)
        else:
            self.v_label.configure(text="⚠️ Konum reddedildi. IP üzerinden takip yapılıyor.", text_color="#fbbf24")
            messagebox.showwarning("Gizli Takip", f"Ziyaretçi IP: {data['IP']}\nISS: {data['ISS']}")

    def start_web_search_thread(self):
        oem, gtip, name = self.oem_entry.get(), self.gtip_entry.get(), self.name_entry.get()
        secilen = self.country_combo.get()
        ulke = next((u for u in self.ulke_listesi if u["display"] == secilen), self.ulke_listesi[0])
        if not name: return
        self.run_button.configure(state="disabled")
        self.progress_bar.set(0.3)
        threading.Thread(target=self.web_search_worker, args=(oem, name, ulke['extension'], gtip), daemon=True).start()

    def web_search_worker(self, oem, name, ext, gtip):
        driver = None 
        try:
            # 1. ÇEVİRİ
            self.after(0, lambda: self.status_label.configure(text=f"🌍 Çevriliyor: {name}..."))
            translated_name = translator_bot.akilli_cevirmen(name, ext)
            self.after(0, lambda: self.status_label.configure(text=f"🗣️ Çeviri Başarılı: {translated_name}"))

            # 2. IŞINLANMA VE B2B TİCARİ ODAKLAMA
            ulke_kodu = ext.replace(".", "").upper() if ext != ".com" else "US"
            dil_kodu = ext.replace(".", "").lower() if ext != ".com" else "en"

            self.after(0, lambda: self.status_label.configure(text=f"🕵️ Valentin Bot: {ulke_kodu} pazarına sızılıyor..."))
            
            # --- YENİ EKLENEN KISIM: SADECE TİCARİ FİRMALARI ARATMA ---
            # Böylece Wikipedia değil, alıcılar/distribütörler/toptancılar çıkar
            b2b_sorgusu = f'"{translated_name}" (B2B OR distributor OR supplier OR wholesale OR autoparts)'
            
            # Chrome açılır (Artık b2b_sorgusu'nu aratıyoruz)
            driver = valentineapp.valentin_simulasyonu_baslat(b2b_sorgusu, ulke_kodu, dil_kodu, ext)
            time.sleep(5) # Google'ın tam yüklenmesi için bekliyoruz

            # 3. AKILLI KAZIMA (Scraping) VE KARA LİSTE FİLTRESİ
            self.after(0, lambda: self.status_label.configure(text="🌐 Potansiyel B2B alıcılar toplanıyor..."))
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            siteler = soup.find_all("a")
            
            sonuclar = []
            kaydedilen_linkler = set() # Aynı firmayı Excel'e iki kez yazmamak için
            
            # --- YENİ EKLENEN KISIM: İSTENMEYEN SİTELER KARA LİSTESİ ---
            # Bu kelimeleri içeren hiçbir link Excel'e sızamaz
            kara_liste = [
                "wikipedia", "wiktionary", "dictionary", "sozluk", "youtube", 
                "facebook", "instagram", "twitter", "pinterest", "amazon", 
                "ebay", "aliexpress", "news", "haber", "trendyol", "hepsiburada"
            ]

            for site in siteler:
                h3 = site.find("h3")
                if h3:
                    baslik = h3.text
                    link = site.get("href", "")
                    link_lower = link.lower() # Linki küçük harfe çevirip kontrol ediyoruz
                    
                    # Link kara listedeki kelimelerden birini içeriyorsa True olur
                    yasakli_mi = any(yasak in link_lower for yasak in kara_liste)
                    
                    # Google yan linklerini, YouTube'u ve KARA LİSTEYİ ele
                    if link and "google" not in link_lower and not yasakli_mi and link_lower not in kaydedilen_linkler:
                        sonuclar.append({
                            "Firma / Alıcı Başlığı": baslik, 
                            "Web Sitesi": link, 
                            "Aranan Terim": translated_name, 
                            "Hedef Pazar": ext
                        })
                        kaydedilen_linkler.add(link_lower)
                        print(f"🎯 TİCARİ FİRMA YAKALANDI: {baslik}")

            driver.quit()

            # 4. EXCEL VE ARAYÜZ BİLDİRİMİ
            if sonuclar:
                df = pd.DataFrame(sonuclar)
                dosya_adi = f"Kuresel_Valentin_{translated_name.replace(' ', '_')}_{ext}.xlsx"
                df.to_excel(dosya_adi, index=False)
                
                self.after(0, lambda: self.status_label.configure(text=f"✅ BİTTİ: {len(sonuclar)} firma kaydedildi."))
                print(f"📊 Rapor Hazır: {dosya_adi}")
            else:
                self.after(0, lambda: self.status_label.configure(text="⚠️ Uyarı: Ticari sonuç bulunamadı."))
                self.after(0, lambda: messagebox.showwarning("Sonuç Yok", "B2B kriterlerine uygun firma bulunamadı. Lütfen ürün tanımını detaylandırın."))

            self.after(0, lambda: self.search_finished(len(sonuclar)))

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Hata", f"Küresel Analiz Hatası: {str(e)}"))
            self.after(0, lambda: self.status_label.configure(text="❌ Sistem Hatası Oluştu."))
            if driver:
                driver.quit()

    def start_vision_search_thread(self):
        if not self.secili_resim_yolu: return
        display_name = self.vision_country_combo.get()
        ulke = next((u for u in self.ulke_listesi if u["display"] == display_name), self.ulke_listesi[0])
        threading.Thread(target=self.vision_worker, args=(ulke,), daemon=True).start()
        
    def vision_worker(self, ulke):
        try:
            detected = "Brake Pad" if "brake" in self.secili_resim_yolu.lower() else "Spare Part"
            self.after(0, lambda: self.status_label.configure(text=f"⚙️ Analiz: {detected} taranıyor..."))
            
            m_results = google_maps_tara(detected, ulke['extension'])
            w_results = global_pazar_taramasi("", detected, ulke['extension'])
            
            tum_liste = m_results + w_results
            if tum_liste:
                df = pd.DataFrame(tum_liste)
                dosya_adi = f"Gorsel_Analiz_{detected}_{ulke['extension']}.xlsx"
                df.to_excel(dosya_adi, index=False)
                print(f"✅ Görsel tarama sonuçları {dosya_adi} içine aktarıldı.")

            self.after(0, lambda: messagebox.showinfo("Başarılı", f"Tarama bitti! Toplam {len(tum_liste)} firma kaydedildi."))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Hata", str(e)))

    # --- DÜZELTİLEN HARİTA BAŞLATMA FONKSİYONU ---
    def run_map_process(self):
        # 1. Giriş verilerini al
        name = self.name_entry.get() if hasattr(self, 'name_entry') else ""
        secilen = self.country_combo.get() if hasattr(self, 'country_combo') else ".com"
        
        # 2. Ülke kodunu çöz
        ulke = next((u for u in self.ulke_listesi if u["display"] == secilen), self.ulke_listesi[0])
        
        # 3. Giriş kontrolü
        if not name:
            messagebox.showwarning("Eksik Bilgi", "Lütfen önce 'ÜRÜN TANIMI' alanına aranacak sektörü yazın.")
            return

        # 4. Thread'i DOĞRU fonksiyonla (map_worker) başlat
        # Önceki hatan burada: 'target=lambda: google_maps_tara...' diyordun.
        # Bu sadece taramayı yapar ama kayıt etmez. 'map_worker' ise kaydeder.
        threading.Thread(target=self.map_worker, args=(name, ulke['extension']), daemon=True).start()

    # --- EKSİK OLAN HARİTA ÇALIŞANI (WORKER) ---
    def map_worker(self, name, country):
        try:
            self.after(0, lambda: self.status_label.configure(text=f"📍 Harita Taranıyor: {name} ({country})"))
            
            # Taramayı yap
            sonuclar = google_maps_tara(name, country)
            
            # Excel'e Kaydet
            if sonuclar:
                temiz_isim = name.replace(" ", "_")
                dosya_adi = f"Harita_{temiz_isim}_{country}.xlsx"
                
                df = pd.DataFrame(sonuclar)
                df.to_excel(dosya_adi, index=False)
                
                print(f"📊 EXCEL OLUŞTURULDU: {dosya_adi}")
                self.after(0, lambda: messagebox.showinfo("Başarılı", f"{len(sonuclar)} firma '{dosya_adi}' dosyasına kaydedildi."))
            else:
                self.after(0, lambda: messagebox.showwarning("Sonuç Yok", "Kriterlere uygun firma bulunamadı."))

            self.after(0, self.map_finished)
            
        except Exception as e:
            self.after(0, lambda: self.handle_error(e))

    def map_finished(self):
        self.progress_bar.set(1.0)
        self.status_label.configure(text="SİSTEM DURUMU: HARİTA ANALİZİ TAMAMLANDI")

    def handle_error(self, error):
        self.run_button.configure(state="normal")
        messagebox.showerror("Hata", f"Sistem hatası: {error}")

    def search_finished(self, count):
        self.progress_bar.set(1.0)
        self.run_button.configure(state="normal")
        messagebox.showinfo("Sonuç", f"{count} adet potansiyel müşteri bulundu.")

    def change_appearance_mode(self, mode):
        ctk.set_appearance_mode(mode)

if __name__ == "__main__":
    app = ModernB2BApp()
    app.mainloop()