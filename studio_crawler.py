import httpx
import json
import asyncio
import os
import argparse
import re
from bs4 import BeautifulSoup
import warnings

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

async def fetch_page(client, url):
    """Mengambil konten halaman dengan retry."""
    try:
        response = await client.get(url)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"[!] Gagal mengambil {url}: {e}")
    return None

def extract_movies(html):
    """Mengekstrak list video dari HTML halaman studio."""
    soup = BeautifulSoup(html, 'html.parser')
    movies = []
    
    # Selector umum untuk item video di javfun
    # Biasanya ada di dalam <div class="item"> atau <div class="post">
    items = soup.select('.item') or soup.select('.post') or soup.find_all('div', class_='movie-box')
    
    if not items:
        # Fallback ke pencarian link manual
        for a in soup.find_all('a', href=True):
            if '/movies/' in a['href'] and len(a['href']) > 10:
                url = "https://en.javfun.me" + a['href'] if a['href'].startswith('/') else a['href']
                # Hindari duplikat
                if any(m['url'] == url for m in movies):
                    continue
                    
                img_tag = a.find('img')
                img_url = None
                if img_tag:
                    img_url = img_tag.get('data-original') or img_tag.get('src')
                
                title = a.get('title') or (img_tag.get('alt') if img_tag else a.text.strip())
                
                movies.append({
                    "url": url,
                    "img": img_url,
                    "title": title
                })
        return movies

    for item in items:
        link_tag = item.find('a', href=re.compile(r'/movies/'))
        if not link_tag:
            continue
            
        url = "https://en.javfun.me" + link_tag.get('href') if link_tag.get('href').startswith('/') else link_tag.get('href')
        
        img_tag = item.find('img')
        img_url = None
        if img_tag:
            # Javfun sering pakai lazy loading (data-original)
            img_url = img_tag.get('data-original') or img_tag.get('src')
            if img_url and img_url.startswith('/'):
                img_url = "https://en.javfun.me" + img_url
        
        title_tag = item.find('h3') or item.find('h2') or item.find('div', class_='title')
        title = title_tag.text.strip() if title_tag else (img_tag.get('alt') if img_tag else link_tag.text.strip())
        
        movies.append({
            "url": url,
            "img": img_url,
            "title": title
        })
        
    return movies

async def main():
    parser = argparse.ArgumentParser(description="Scraper Studio Page Javfun")
    parser.add_argument("url", help="URL Studio (contoh: https://en.javfun.me/studio/asiansexdiary/)")
    parser.add_argument("--output", help="Nama file output JSON", default="studio_results.json")
    args = parser.parse_args()

    base_url = args.url.rstrip('/')
    if '/page-' in base_url:
        base_url = re.sub(r'/page-\d+', '', base_url)
    
    all_movies = []
    page = 1
    
    print(f"[*] Memulai crawling dari studio: {base_url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient(verify=False, headers=headers, follow_redirects=True, timeout=30.0) as client:
        while True:
            page_url = f"{base_url}/page-{page}"
            print(f"[*] Mengambil Halaman {page}: {page_url}")
            
            html = await fetch_page(client, page_url)
            if not html:
                break
                
            movies = extract_movies(html)
            if not movies:
                print(f"[*] Tidak ada video lagi di halaman {page}. Selesai.")
                break
            
            # Cek apakah kita cuma dapat data yang sama (looping pagination)
            new_movies = [m for m in movies if m['url'] not in [am['url'] for am in all_movies]]
            if not new_movies:
                print(f"[*] Semua video di halaman {page} sudah pernah diambil. Selesai.")
                break
                
            all_movies.extend(new_movies)
            print(f"[+] Berhasil mengambil {len(new_movies)} video baru (Total: {len(all_movies)})")
            
            # Cek apakah ada tombol "Next" atau "Older"
            if "Next" not in html and "Older" not in html and f"/page-{page+1}" not in html:
                 # Beberapa situs tidak punya kata "Next" tapi punya link page selanjutnya
                 pass
            
            page += 1
            # Delay kecil biar sopan
            await asyncio.sleep(0.5)

    print(f"\n[*] Total video ditemukan: {len(all_movies)}")
    
    # Simpan ke file
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(all_movies, f, indent=4, ensure_ascii=False)
    
    print(f"[OK] Hasil disimpan ke: {args.output}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Dihentikan oleh pengguna.")
