import yt_dlp
import json
import asyncio
import httpx
from bs4 import BeautifulSoup
import warnings

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

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
        
        # Ekstrak Deskripsi
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'].strip() if meta_desc else "Tidak ada deskripsi"
        
        metadata = {
            "title": title,
            "description": description,
            "source_url": url,
        }
        
        # Simpan ke JSON
        with open('metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)
            
        return metadata

def download_m3u8(m3u8_url, title):
    print(f"\n[*] Memulai proses download video dari M3U8...")
    print(f"[*] Target File: {title}.mp4")
    
    # yt-dlp adalah master dalam mendownload file M3U8/HLS secara paralel
    ydl_opts = {
        'format': 'best',
        
        # Fitur Parallel Download: Memecah donwload jadi 10 koneksi bersamaan (sangat ngebut!)
        'concurrent_fragment_downloads': 10,
        
        # Penamaan file output (otomatis disatukan jadi .mp4 oleh yt-dlp+ffmpeg)
        'outtmpl': ''.join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip() + '.mp4',
        
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
            print("\n[*] Download selesai dan video sudah digabungkan menjadi MP4!")
        except yt_dlp.utils.DownloadError as e:
            print(f"\n[!] Error saat mendownload m3u8: {e}")

async def main():
    # 1. URL Halaman Web (Hanya untuk ambil Judul & Deskripsi ke JSON)
    web_url = "https://en.javfun.me/movies/asiansexdiary-bangkok-lockdown-nate-pa-b"
    
    # 2. URL M3U8 (Video Asli yang baru saja kamu temukan)
    m3u8_url = "https://cdnasa1.gogocdnaws-2.online/playlists/0d791451-1cbe-4550-ac52-b34a5b9a4130/u8lmahqjne.m3u8"
    
    # Eksekusi Scraping Metadata
    metadata = await scrape_metadata(web_url)
    print(f"[*] Berhasil mendapatkan judul: {metadata['title']}")
    print(f"[*] Metadata disimpan ke metadata.json")
    
    # Eksekusi Download M3U8 -> MP4
    download_m3u8(m3u8_url, metadata['title'])

if __name__ == "__main__":
    asyncio.run(main())
