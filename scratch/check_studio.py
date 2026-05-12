import httpx
import warnings
import re
from bs4 import BeautifulSoup

warnings.filterwarnings('ignore')
url = 'https://en.javfun.me/studio/asiansexdiary/page-1'
r = httpx.get(url, verify=False, follow_redirects=True)
soup = BeautifulSoup(r.text, 'html.parser')

# Find all links that look like movie links
movies = []
# On javfun, they usually use a specific class or structure
# Let's look for anything inside a .movie-box or similar
for item in soup.select('.item'):
    link = item.find('a', href=re.compile(r'/movies/'))
    img = item.find('img')
    title = item.find('h3') or item.find('h2') or (img.get('alt') if img else None)
    
    if link:
        movies.append({
            "url": "https://en.javfun.me" + link.get('href'),
            "img": img.get('src') if img else None,
            "title": title.text.strip() if hasattr(title, 'text') else str(title)
        })

if not movies:
    # Try another selector
    for a in soup.find_all('a', href=True):
        if '/movies/' in a['href']:
            img = a.find('img')
            movies.append({
                "url": "https://en.javfun.me" + a['href'] if a['href'].startswith('/') else a['href'],
                "img": img.get('src') if img else None,
                "title": a.get('title') or (img.get('alt') if img else a.text.strip())
            })

print(f"Found {len(movies)} movies")
for m in movies[:5]:
    print(m)
