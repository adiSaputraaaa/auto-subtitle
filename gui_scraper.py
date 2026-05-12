import customtkinter as ctk
import json
import asyncio
import httpx
import os
import hashlib
import random
import string
import re
import threading
from bs4 import BeautifulSoup
from PIL import Image
import yt_dlp
import warnings
from tkinter import filedialog

# Suppress insecure request warnings
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

def strip_ansi(text):
    if not text: return ""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', str(text))

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ScraperGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Kawaiku Media Scraper & Downloader")
        self.geometry("1000x800")

        # Variables
        self.json_data = []
        self.is_downloading = False
        self.output_dir = os.getcwd()
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.start_async_loop, daemon=True).start()

        self.setup_ui()

    def start_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def setup_ui(self):
        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="KAWAIKU", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.pack(pady=20, padx=20)

        self.btn_load_json = ctk.CTkButton(self.sidebar, text="Load JSON File", command=self.load_json)
        self.btn_load_json.pack(pady=10, padx=20)

        self.dir_label = ctk.CTkLabel(self.sidebar, text="Output Directory:", anchor="w")
        self.dir_label.pack(pady=(20, 0), padx=20, fill="x")
        
        self.output_dir_entry = ctk.CTkEntry(self.sidebar, font=ctk.CTkFont(size=10))
        self.output_dir_entry.insert(0, self.output_dir)
        self.output_dir_entry.pack(pady=5, padx=20, fill="x")

        self.btn_browse = ctk.CTkButton(self.sidebar, text="Browse Folder", fg_color="transparent", border_width=1, command=self.browse_output)
        self.btn_browse.pack(pady=5, padx=20)

        self.btn_clear = ctk.CTkButton(self.sidebar, text="Clear List", command=self.clear_list, fg_color="#444", hover_color="#333")
        self.btn_clear.pack(pady=10, padx=20)

        self.appearance_mode_label = ctk.CTkLabel(self.sidebar, text="Theme:", anchor="w")
        self.appearance_mode_label.pack(side="bottom", padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar, values=["Dark", "Light", "System"], command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.pack(side="bottom", padx=20, pady=(0, 20))

        # --- Main Content ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

        # Top Bar: Single URL Input
        self.url_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.url_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.url_frame.grid_columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(self.url_frame, placeholder_text="Enter single video URL here...")
        self.url_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        self.btn_add_url = ctk.CTkButton(self.url_frame, text="Add URL", width=100, command=self.add_single_url)
        self.btn_add_url.grid(row=0, column=1)

        # Stats/Status Bar
        self.stats_label = ctk.CTkLabel(self.main_frame, text="Status: Ready", font=ctk.CTkFont(size=12))
        self.stats_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")

        # Scrollable List of Items
        self.items_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Video Queue")
        self.items_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.item_widgets = []

        # Progress Section
        self.progress_frame = ctk.CTkFrame(self.main_frame)
        self.progress_frame.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        self.progress_frame.grid_columnconfigure(0, weight=1)

        # Main Progress
        self.main_task_label = ctk.CTkLabel(self.progress_frame, text="Total Queue Progress:", anchor="w")
        self.main_task_label.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="ew")
        self.main_progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.main_progress_bar.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")
        self.main_progress_bar.set(0)

        # Video Specific Progress
        self.video_task_label = ctk.CTkLabel(self.progress_frame, text="Current Video Download:", anchor="w", font=ctk.CTkFont(size=11, slant="italic"))
        self.video_task_label.grid(row=2, column=0, padx=20, pady=(5, 0), sticky="ew")
        
        self.speed_label = ctk.CTkLabel(self.progress_frame, text="Speed: 0 KB/s | ETA: 00:00", font=ctk.CTkFont(size=10))
        self.speed_label.grid(row=2, column=0, padx=20, pady=(5, 0), sticky="e")

        self.video_progress_bar = ctk.CTkProgressBar(self.progress_frame, progress_color="green")
        self.video_progress_bar.grid(row=3, column=0, padx=20, pady=(5, 15), sticky="ew")
        self.video_progress_bar.set(0)

        self.btn_download_all = ctk.CTkButton(self.progress_frame, text="START DOWNLOADS", font=ctk.CTkFont(size=14, weight="bold"), height=45, command=self.start_download_all)
        self.btn_download_all.grid(row=4, column=0, padx=20, pady=(0, 15), sticky="ew")

    def browse_output(self):
        try:
            current_val = self.output_dir_entry.get()
            init_dir = os.path.normpath(current_val).replace("\\", "/") if current_val else None
            if init_dir and not os.path.isdir(init_dir):
                init_dir = None
                
            selected_dir = filedialog.askdirectory(initialdir=init_dir, title="Select Output Folder")
            if selected_dir:
                self.output_dir_entry.delete(0, 'end')
                self.output_dir_entry.insert(0, os.path.normpath(selected_dir))
        except Exception as e:
            print(f"Dialog Error: {e}")
            # Silently fail, user can still type in the entry
            self.stats_label.configure(text="Dialog error - please type path manually", text_color="yellow")

    def change_appearance_mode(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def load_json(self):
        try:
            current_val = self.output_dir_entry.get()
            init_dir = os.path.normpath(current_val).replace("\\", "/") if current_val else None
            if init_dir and not os.path.isdir(init_dir):
                init_dir = None
                
            file_path = filedialog.askopenfilename(
                initialdir=init_dir,
                filetypes=[("JSON Files", "*.json")],
                title="Select JSON File"
            )
            if file_path:
                file_path = os.path.normpath(file_path)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.json_data = data
                    self.refresh_list()
                    self.stats_label.configure(text=f"Status: Loaded {len(data)} items from {os.path.basename(file_path)}", text_color="white")
        except Exception as e:
            self.stats_label.configure(text=f"Error loading JSON: {str(e)}", text_color="red")

    def refresh_list(self):
        for widget in self.item_widgets:
            widget.destroy()
        self.item_widgets = []

        for i, item in enumerate(self.json_data):
            frame = ctk.CTkFrame(self.items_frame)
            frame.pack(fill="x", padx=5, pady=2)
            
            title = item.get("title", "Untitled")
            label = ctk.CTkLabel(frame, text=f"{i+1}. {title}", anchor="w", font=ctk.CTkFont(size=11))
            label.pack(side="left", padx=10, pady=3, fill="x", expand=True)
            
            btn_remove = ctk.CTkButton(frame, text="X", width=25, height=25, fg_color="#aa3333", hover_color="#882222", 
                                       command=lambda idx=i: self.remove_item(idx))
            btn_remove.pack(side="right", padx=5)
            
            self.item_widgets.append(frame)

    def remove_item(self, index):
        self.json_data.pop(index)
        self.refresh_list()
        self.stats_label.configure(text=f"Status: {len(self.json_data)} items remaining")

    def clear_list(self):
        self.json_data = []
        self.refresh_list()
        self.stats_label.configure(text="Status: List cleared")

    def add_single_url(self):
        url = self.url_entry.get().strip()
        if url:
            self.json_data.append({"url": url, "title": "Detecting title..."})
            self.refresh_list()
            self.url_entry.delete(0, 'end')
            asyncio.run_coroutine_threadsafe(self.fetch_metadata_for_last(), self.loop)

    async def fetch_metadata_for_last(self):
        idx = len(self.json_data) - 1
        item = self.json_data[idx]
        async with httpx.AsyncClient(verify=False, follow_redirects=True) as client:
            try:
                resp = await client.get(item['url'])
                soup = BeautifulSoup(resp.text, 'html.parser')
                title_tag = soup.find('title')
                title = title_tag.text.strip().split('|')[0].strip() if title_tag else "Video"
                item['title'] = title
                self.after(0, self.refresh_list)
            except:
                item['title'] = "Failed to fetch metadata"
                self.after(0, self.refresh_list)

    def start_download_all(self):
        if not self.json_data or self.is_downloading:
            return
        
        self.is_downloading = True
        self.btn_download_all.configure(state="disabled", text="DOWNLOADING QUEUE...")
        asyncio.run_coroutine_threadsafe(self.process_queue(), self.loop)

    async def process_queue(self):
        total = len(self.json_data)
        async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=60.0) as client:
            for i, item in enumerate(self.json_data):
                self.after(0, lambda val=(i/total), text=f"Overall Progress ({i+1}/{total})": 
                           self.update_main_progress(val, text))
                
                try:
                    await self.download_item(client, item)
                except Exception as e:
                    print(f"Error downloading {item.get('title')}: {e}")
                
            self.after(0, lambda: self.update_main_progress(1.0, "All tasks completed!"))
            self.after(0, lambda: self.update_video_progress(0, "Ready for next queue"))
            self.after(0, self.reset_ui_after_download)

    def update_main_progress(self, val, text):
        self.main_progress_bar.set(val)
        self.main_task_label.configure(text=text)

    def update_video_progress(self, val, text, speed="", eta=""):
        self.video_progress_bar.set(val)
        self.video_task_label.configure(text=text)
        if speed or eta:
            self.speed_label.configure(text=f"Speed: {speed} | ETA: {eta}")
        else:
            self.speed_label.configure(text="")

    def reset_ui_after_download(self):
        self.is_downloading = False
        self.btn_download_all.configure(state="normal", text="START DOWNLOADS")

    async def download_item(self, client, item):
        url = item['url']
        out_dir = self.output_dir_entry.get()
        
        # 1. Fetch metadata
        resp = await client.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        title = item.get('title')
        if not title or title in ["Detecting title...", "Untitled", "Failed to fetch metadata"]:
            title_tag = soup.find('title')
            title = title_tag.text.strip().split('|')[0].strip() if title_tag else "Video"
        
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        folder_path = os.path.join(out_dir, safe_title)
        os.makedirs(folder_path, exist_ok=True)

        # Save metadata.json
        metadata_path = os.path.join(folder_path, 'metadata.json')
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(item, f, indent=4, ensure_ascii=False)
        except: pass

        video_filename = f"{safe_title}.mp4"
        video_full_path = os.path.join(folder_path, video_filename)

        # Check if already exists
        if os.path.exists(video_full_path):
            self.after(0, lambda: self.update_video_progress(1.0, f"Skipped (Already exists): {title}"))
            return

        self.after(0, lambda: self.update_video_progress(0.1, f"Detecting source: {title}"))

        # 2. Download Thumbnail
        img_url = item.get('img')
        if not img_url:
            img_tag = soup.find('meta', property="og:image") or soup.find('link', rel="image_src")
            if img_tag:
                img_url = img_tag.get('content') or img_tag.get('href')
        
        if img_url:
            if img_url.startswith('/'):
                img_url = "https://en.javfun.me" + img_url
            try:
                img_resp = await client.get(img_url)
                with open(os.path.join(folder_path, 'poster.jpg'), 'wb') as f:
                    f.write(img_resp.content)
            except: pass

        # 3. Detect M3U8
        m3u8_url = await self.detect_m3u8(client, url, resp.text)
        
        if m3u8_url:
            self.after(0, lambda: self.update_video_progress(0.2, f"Downloading: {title}"))
            
            def yt_dlp_hook(d):
                if d['status'] == 'downloading':
                    # Try to get percentage
                    p_str = d.get('_percent_str')
                    float_p = 0.0
                    
                    if p_str:
                        p_str = strip_ansi(p_str)
                        p = p_str.replace('%','').strip()
                        try:
                            float_p = float(p) / 100
                        except: float_p = 0.0
                    else:
                        # Fallback for HLS/M3U8 fragments
                        frag_index = d.get('fragment_index', 0)
                        frag_count = d.get('fragment_count')
                        if frag_count:
                            float_p = frag_index / frag_count
                            p_str = f"{int(float_p * 100)}%"
                        else:
                            float_p = 0.0
                            p_str = f"Frag: {frag_index}"

                    # Final Clamp
                    float_p = max(0.0, min(1.0, float_p))

                    s = strip_ansi(d.get('_speed_str', ''))
                    if not s:
                        speed = d.get('speed')
                        if speed:
                            if speed > 1024 * 1024:
                                s = f"{speed / (1024*1024):.2f} MiB/s"
                            else:
                                s = f"{speed / 1024:.2f} KiB/s"
                        else:
                            s = "N/A"

                    e = strip_ansi(d.get('_eta_str', ''))
                    if not e:
                        eta = d.get('eta')
                        if eta:
                            mins, secs = divmod(eta, 60)
                            hours, mins = divmod(mins, 60)
                            if hours:
                                e = f"{int(hours):02d}:{int(mins):02d}:{int(secs):02d}"
                            else:
                                e = f"{int(mins):02d}:{int(secs):02d}"
                        else:
                            e = "N/A"
                    
                    self.after(0, lambda p=float_p, msg=f"Downloading: {title} ({p_str})", spd=s, et=e: 
                               self.update_video_progress(p, msg, spd, et))
                elif d['status'] == 'finished':
                    self.after(0, lambda: self.update_video_progress(1.0, f"Finished: {title}"))
                elif d['status'] == 'finished':
                    self.after(0, lambda: self.update_video_progress(1.0, f"Finished: {title}"))

            def dl_thread():
                ydl_opts = {
                    'format': 'best',
                    'concurrent_fragment_downloads': 10,
                    'outtmpl': video_full_path,
                    'nocheckcertificate': True,
                    'quiet': True,
                    'no_warnings': True,
                    'progress_hooks': [yt_dlp_hook],
                    'referer': 'https://en.javfun.me/',
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([m3u8_url])
            
            await asyncio.to_thread(dl_thread)
        else:
            self.after(0, lambda: self.update_video_progress(0, f"Failed to detect source: {title}"))

    async def detect_m3u8(self, client, web_url, html):
        movie_id_match = re.search(r'id="uuid"[^>]+value="([^"]+)"', html)
        if not movie_id_match:
            movie_id_match = re.search(r'id:\s*"([^"]+)"', html)
        if not movie_id_match: return None

        movie_id = movie_id_match.group(1)
        token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        salt = "9826avrbi6m49vd7shxkn9815"
        hash_input = movie_id + token + salt
        md5_hash = hashlib.md5(hash_input.encode()).hexdigest()
        
        ajax_url = f"https://en.javfun.me/ajax/get_sources/{movie_id}/{md5_hash}?count=1&mobile=false"
        cookie_name = f"bcq9826avrbi6m49vd7shxkn{movie_id}mhodk06twz87wwxtp3dqiick"
        client.cookies.set(cookie_name, token)
        
        try:
            resp = await client.get(ajax_url)
            if resp.status_code == 200:
                data = resp.json()
                if 'playlist' in data and len(data['playlist']) > 0:
                    sources = data['playlist'][0].get('sources', [])
                    if sources: return sources[0].get('file')
                    return data['playlist'][0].get('file')
        except: pass
        return None

if __name__ == "__main__":
    app = ScraperGUI()
    app.mainloop()
