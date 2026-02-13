import customtkinter as ctk
from tkinter import messagebox
import threading
import time
import pandas as pd

# Yazdığımız modülleri içe aktarıyoruz
try:
    from image_search_engine import global_pazar_taramasi
    from maps_scraper import google_maps_tara
except ImportError:
    print("Uyarı: Bazı modül dosyaları bulunamadı. Lütfen image_search_engine.py ve maps_scraper.py dosyalarını kontrol edin.")

# Görünüm ayarları
ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("blue") 

class ModernB2BApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Global B2B Hunter v2.0")
        self.geometry("700x550")

        # Grid yapısı
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- YAN MENÜ ---
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="B2B HUNTER", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Harita Modülü Butonu
        self.map_btn = ctk.CTkButton(self.sidebar_frame, text="Harita Modülü", command=self.run_map_process)
        self.map_btn.grid(row=1, column=0, padx=20, pady=10)

        self.appearance_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light"], command=self.change_appearance_mode)
        self.appearance_optionemenu.grid(row=6, column=0, padx=20, pady=(250, 20))

        # --- ANA PANEL ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.title_label = ctk.CTkLabel(self.main_frame, text="İhracat İstihbarat Robotu", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=20)

        self.oem_entry = ctk.CTkEntry(self.main_frame, placeholder_text="OEM / Parça No (Örn: 260x85)", width=350, height=45)
        self.oem_entry.pack(pady=10)

        self.name_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Parça İsmi (Örn: Piston)", width=350, height=45)
        self.name_entry.pack(pady=10)

        self.country_menu = ctk.CTkOptionMenu(self.main_frame, values=[".com", ".de", ".ru", ".fr", ".it"], width=350, height=45)
        self.country_menu.pack(pady=10)
        self.country_menu.set(".de")

        self.run_button = ctk.CTkButton(self.main_frame, text="TARAMAYI BAŞLAT", font=ctk.CTkFont(size=14, weight="bold"), 
                                        width=250, height=50, corner_radius=25, command=self.start_web_search_thread)
        self.run_button.pack(pady=20)

        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=400)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self.main_frame, text="Sistem Hazır", font=("Arial", 12))
        self.status_label.pack(pady=5)

    def change_appearance_mode(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)

    # --- WEB TARAMA THREAD YÖNETİMİ ---
    def start_web_search_thread(self):
        oem = self.oem_entry.get()
        name = self.name_entry.get()
        country = self.country_menu.get()

        if not name: # OEM zorunlu değil ama isim şart
            messagebox.showwarning("Eksik Veri", "Lütfen bir Parça İsmi giriniz.")
            return

        self.run_button.configure(state="disabled", text="Aranıyor...")
        self.status_label.configure(text=f"{country} pazarı taranıyor...", text_color="orange")
        self.progress_bar.set(0.3)
        
        # Arka planda çalıştır
        threading.Thread(target=self.web_search_worker, args=(oem, name, country), daemon=True).start()

    def web_search_worker(self, oem, name, country):
        try:
            # image_search_engine.py içindeki ana fonksiyonu çağırır
            sonuclar = global_pazar_taramasi(oem, name, country)
            self.after(0, lambda: self.search_finished(len(sonuclar), oem))
        except Exception as e:
            self.after(0, lambda: self.handle_error(e))

    # --- HARİTA TARAMA THREAD YÖNETİMİ ---
    def run_map_process(self):
        """
        Döküman Madde 2: Harita üzerinden dükkan avlama modülünü tetikler.
        """
        name = self.name_entry.get()
        country = self.country_menu.get()
        
        if not name:
            messagebox.showwarning("Eksik Veri", "Harita taraması için bir sektör/parça ismi girin.")
            return

        self.map_btn.configure(state="disabled", text="Taranıyor...")
        self.status_label.configure(text="Google Maps dükkanları taranıyor (Selenium)...", text_color="cyan")
        self.progress_bar.set(0.5)
        
        # Arayüzün donmaması için Selenium'u ayrı bir thread'de başlatıyoruz
        threading.Thread(target=self.map_worker, args=(name, country), daemon=True).start()

    def map_worker(self, name, country):
        try:
            # maps_scraper.py içindeki fonksiyonu çağırıyoruz
            sonuclar = google_maps_tara(name, country)
            
            # İşlem bitince Excel'e kaydedelim (maps_scraper içinde yapılmadıysa)
            if sonuclar:
                df = pd.DataFrame(sonuclar)
                dosya_adi = f"Maps_{name.replace(' ', '_')}_{country}.xlsx"
                df.to_excel(dosya_adi, index=False)
                
                self.after(0, lambda: messagebox.showinfo("Başarılı", f"{len(sonuclar)} dükkan bulundu!\n{dosya_adi} kaydedildi."))
            else:
                self.after(0, lambda: messagebox.showwarning("Sonuç Yok", "Haritalarda bu kriterde dükkan bulunamadı."))
            
            self.after(0, self.map_finished)
        except Exception as e:
            self.after(0, lambda: self.handle_error(e))

    def map_finished(self):
        self.map_btn.configure(state="normal", text="Harita Modülü")
        self.status_label.configure(text="Harita taraması bitti.", text_color="green")
        self.progress_bar.set(1.0)

    # --- ORTAK YARDIMCI FONKSİYONLAR ---
    def search_finished(self, count, oem):
        self.progress_bar.set(1.0)
        self.run_button.configure(state="normal", text="TARAMAYI BAŞLAT")
        self.status_label.configure(text="İşlem Başarıyla Tamamlandı", text_color="green")
        messagebox.showinfo("B2B Hunter", f"Tarama Bitti!\n{count} firma analiz edildi.\nB2B_Sorgu_{oem}.xlsx oluşturuldu.")

    def handle_error(self, error):
        self.run_button.configure(state="normal", text="TARAMAYI BAŞLAT")
        self.map_btn.configure(state="normal", text="Harita Modülü")
        self.status_label.configure(text="Hata oluştu!", text_color="red")
        messagebox.showerror("Sistem Hatası", f"Bir hata meydana geldi:\n{error}")

if __name__ == "__main__":
    app = ModernB2BApp()
    app.mainloop()