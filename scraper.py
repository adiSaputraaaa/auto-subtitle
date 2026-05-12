import yt_dlp
import json
import asyncio
import httpx
import os
import argparse
from bs4 import BeautifulSoup
import warnings

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

def sanitize_filename(name):
    """Sanitize string to be safe for filenames and folder names."""
    return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()

async def scrape_metadata(url):
    print(f"[*] Scraping metadata (Judul & Deskripsi) dari: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Melakukan request ke halaman web asli
    async with httpx.AsyncClient(verify=False, headers=headers, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ekstrak Judul
        title = soup.find('title').text.strip() if soup.find('title') else "Unknown_Title"
        safe_title = sanitize_filename(title)
        
        # Ekstrak Deskripsi
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'].strip() if meta_desc else "Tidak ada deskripsi"
        
        metadata = {
            "title": title,
            "description": description,
            "source_url": url,
        }
        
        # Buat folder berdasarkan judul yang sudah disanitasi
        folder_path = safe_title
        os.makedirs(folder_path, exist_ok=True)
        
        # Simpan ke JSON di dalam folder tersebut
        json_path = os.path.join(folder_path, 'metadata.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)
            
        return metadata, folder_path

def download_m3u8(m3u8_url, title, folder_path):
    print(f"\n[*] Memulai proses download video dari M3U8...")
    safe_title = sanitize_filename(title)
    output_filename = f"{safe_title}.mp4"
    output_path = os.path.join(folder_path, output_filename)
    
    print(f"[*] Target File: {output_path}")
    
    # yt-dlp adalah master dalam mendownload file M3U8/HLS secara paralel
    ydl_opts = {
        'format': 'best',
        
        # Fitur Parallel Download: Memecah donwload jadi 10 koneksi bersamaan (sangat ngebut!)
        'concurrent_fragment_downloads': 10,
        
        # Penamaan file output dengan path folder
        'outtmpl': output_path,
        
        # Abaikan sertifikat SSL
        'nocheckcertificate': True,
        
        # Header referer opsional agar server M3U8 tidak mem-block request kita
        'referer': 'https://en.javfun.me/',
        'http_headers': {
            'Origin': 'https://en.javfun.me',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([m3u8_url])
            print(f"\n[*] Download selesai! File tersimpan di: {output_path}")
        except yt_dlp.utils.DownloadError as e:
            print(f"\n[!] Error saat mendownload m3u8: {e}")

async def main():
    parser = argparse.ArgumentParser(description="Scrape metadata and download M3U8 video.")
    parser.add_argument("--web", help="URL Halaman Web (untuk metadata)")
    parser.add_argument("--m3u8", help="URL M3U8 (Video Asli)")
    args = parser.parse_args()

    print("=== Auto Subtitle Scraper & Downloader ===")
    
    # Mengambil input dari argument CLI atau prompt terminal jika tidak diberikan
    web_url = args.web if args.web else input("Masukkan URL Halaman Web (untuk metadata) : ").strip()
    m3u8_url = args.m3u8 if args.m3u8 else input("Masukkan URL M3U8 (Video Asli)          : ").strip()
    
    if not web_url or not m3u8_url:
        print("[!] URL Halaman Web dan M3U8 tidak boleh kosong.")
        return

    # Eksekusi Scraping Metadata
    try:
        metadata, folder_path = await scrape_metadata(web_url)
        print(f"[*] Berhasil mendapatkan judul: {metadata['title']}")
        print(f"[*] Metadata disimpan ke {os.path.join(folder_path, 'metadata.json')}")
        
        # Eksekusi Download M3U8 -> MP4
        download_m3u8(m3u8_url, metadata['title'], folder_path)
    except Exception as e:
        print(f"\n[!] Terjadi kesalahan: {e}")

if __name__ == "__main__":
    asyncio.run(main())
