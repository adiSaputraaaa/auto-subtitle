import yt_dlp
import json
import asyncio
import httpx
import os
import argparse
import hashlib
import random
import string
import re
from bs4 import BeautifulSoup
import warnings

# Suppress insecure request warnings for proxied/debugging environments
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

def sanitize_filename(name):
    """Membersihkan string agar aman untuk nama folder/file."""
    return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()

async def get_m3u8_url(web_url, client):
    """Mendeteksi URL M3U8 secara otomatis dari halaman web javfun.me."""
    print(f"[*] Mencoba mendeteksi M3U8 secara otomatis dari: {web_url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": web_url
    }
    
    try:
        response = await client.get(web_url)
        html = response.text
        
        # 1. Ekstrak Movie ID (UUID)
        movie_id_match = re.search(r'id="uuid"[^>]+value="([^"]+)"', html)
        if not movie_id_match:
            movie_id_match = re.search(r'id:\s*"([^"]+)"', html)
        
        if not movie_id_match:
            # Fallback: Cari .m3u8 langsung di HTML jika ada
            m3u8_matches = re.findall(r'https?://[^\s<>"\']+\.m3u8[^\s<>"\']*', html)
            if m3u8_matches:
                print("[*] M3U8 ditemukan langsung di HTML.")
                return m3u8_matches[0]
            return None

        movie_id = movie_id_match.group(1)
        print(f"[*] Movie ID ditemukan: {movie_id}")
        
        # 2. Bypass Logic (Reverse Engineered dari fix-backup.js)
        # Token random 6 karakter
        token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        # Salt rahasia dari JS
        salt = "9826avrbi6m49vd7shxkn9815"
        # MD5(ID + Token + Salt)
        hash_input = movie_id + token + salt
        md5_hash = hashlib.md5(hash_input.encode()).hexdigest()
        
        # 3. Panggil API get_sources
        # Berdasarkan L0(32) -> index 34: "ajax/get_sources/"
        # L0(240) -> index 242: "/"
        # URL format: ajax/get_sources/{movie_id}/{md5_hash}?count={count}&mobile={is_mobile}
        ajax_url = f"https://en.javfun.me/ajax/get_sources/{movie_id}/{md5_hash}?count=1&mobile=false"
        
        # Cookie bypass (Token diletakkan di cookie)
        cookie_name = f"bcq9826avrbi6m49vd7shxkn{movie_id}mhodk06twz87wwxtp3dqiick"
        client.cookies.set(cookie_name, token)
        
        resp = await client.get(ajax_url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            # print(f"[*] API Data: {json.dumps(data)}") # Debug
            if 'playlist' in data and len(data['playlist']) > 0:
                playlist_item = data['playlist'][0]
                if 'sources' in playlist_item and len(playlist_item['sources']) > 0:
                    m3u8 = playlist_item['sources'][0].get('file')
                    if m3u8:
                        return m3u8
                # Fallback if 'sources' is not present but 'file' is at root of playlist item
                m3u8 = playlist_item.get('file')
                if m3u8:
                    return m3u8
        else:
            print(f"[!] API Error {resp.status_code}: {resp.text[:200]}")

    except Exception as e:
        print(f"[!] Gagal dalam proses deteksi: {e}")
        
    return None

async def scrape_info(url, client):
    """Mengambil metadata video."""
    print(f"[*] Mengambil metadata...")
    response = await client.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    title = soup.find('title').text.strip() if soup.find('title') else "video_download"
    title = title.split('|')[0].strip()
    
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    description = meta_desc['content'].strip() if meta_desc else ""
    
    return {
        "title": title,
        "description": description,
        "url": url
    }

def download_video(m3u8_url, title, folder):
    """Download menggunakan yt-dlp."""
    safe_title = sanitize_filename(title)
    output_path = os.path.join(folder, f"{safe_title}.mp4")
    
    print(f"\n[*] Mendownload: {title}")
    print(f"[*] Lokasi: {output_path}")
    
    ydl_opts = {
        'format': 'best',
        'concurrent_fragment_downloads': 10,
        'outtmpl': output_path,
        'nocheckcertificate': True,
        'quiet': False,
        'no_warnings': True,
        'referer': 'https://en.javfun.me/',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([m3u8_url])

async def main():
    parser = argparse.ArgumentParser(description="Fully Automated M3U8 Scraper")
    parser.add_argument("url", nargs="?", help="URL Video Page")
    args = parser.parse_args()

    print("========================================")
    print("   Kawaiku Auto-Scraper (M3U8 Pro)      ")
    print("========================================\n")

    target_url = args.url if args.url else input("Masukkan URL Halaman Video: ").strip()
    
    if not target_url:
        print("[!] URL diperlukan.")
        return

    async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=60.0) as client:
        # 1. Scrape Info
        info = await scrape_info(target_url, client)
        print(f"[+] Judul: {info['title']}")
        
        # 2. Buat Folder
        folder = sanitize_filename(info['title'])
        os.makedirs(folder, exist_ok=True)
        
        # Simpan metadata
        with open(os.path.join(folder, 'metadata.json'), 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=4, ensure_ascii=False)
        
        # 3. Detect M3U8
        m3u8_url = await get_m3u8_url(target_url, client)
        
        if m3u8_url:
            print(f"[+] M3U8 Berhasil Dideteksi!")
            # 4. Download
            download_video(m3u8_url, info['title'], folder)
            print("\n[OK] Semua proses selesai!")
        else:
            print("\n[FAIL] Gagal mendeteksi M3U8 secara otomatis.")
            manual = input("[?] Ingin masukkan M3U8 secara manual? (y/n): ").lower()
            if manual == 'y':
                m3u8_url = input("Masukkan URL M3U8: ").strip()
                download_video(m3u8_url, info['title'], folder)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Dihentikan oleh pengguna.")
