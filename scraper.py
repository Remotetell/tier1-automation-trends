import os
import json
import xml.etree.ElementTree as ET
import requests

TRENDS_FEEDS = {
    "US": "https://google.com",
    "GB": "https://google.com",
    "CA": "https://google.com",
    "AU": "https://google.com",
    "DE": "https://google.com",
    "FR": "https://google.com",
    "IT": "https://google.com",
    "ES": "https://google.com",
    "JP": "https://google.com",
    "IN": "https://google.com",
    "BR": "https://google.com"
}

def load_backend_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def fetch_filtered_trends(keywords):
    articles = []
    headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"}
    for country, url in TRENDS_FEEDS.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200: continue
            root = ET.fromstring(response.content)
            for item in root.findall('.//item'):
                title = item.find('title').text
                approx_traffic = "10K+"
                for child in item:
                    if 'approx_traffic' in child.tag and child.text:
                        approx_traffic = child.text
                if any(kw in title.lower() for kw in keywords):
                    search_link = f"https://google.com{title.replace(' ', '+')}"
                    articles.append({
                        "title": title, "country": country, 
                        "traffic": approx_traffic, "link": search_link
                    })
        except Exception:
            continue
    return articles[:20]

def get_mondiad_token():
    client_id = os.environ.get("MONDIAD_CLIENT_ID")
    secret = os.environ.get("MONDIAD_SECRET")
    if not client_id or not secret: return ""
    try:
        url = "https://mondiad.com"
        res = requests.post(url, json={"client_id": client_id, "secret": secret}, timeout=8)
        return res.json().get("access_token", "")
    except Exception:
        return ""

def compile_platform():
    cfg = load_backend_config()
    trends = fetch_filtered_trends(cfg["target_keywords"])
    mondiad_token = get_mondiad_token()
    
    cards_html = ""
    for idx, item in enumerate(trends):
        cards_html += f"""
        <article class="news-card">
            <div class="card-meta">
                <span class="geo-badge">\ud83c\udf0d {item['country']}</span>
                <span class="traffic-badge">\ud83d\udd25 {item['traffic']} searches</span>
            </div>
            <h2>{item['title']}</h2>
            <p>Breaking automation developments monitored directly across Tier-1 global indicators.</p>
            <a href="{item['link']}" target="_blank" rel="noopener noreferrer">Read Full Report \u2192</a>
        </article>
        """
        if idx == 2 or idx == 7:
            cards_html += f'<div class="ad-slot inline-ad">{cfg["body_ads_html"]}</div>'

    if not cards_html:
        cards_html = "<p style='text-align:center;color:#6b7280;'>Scanning global data streams for automation break-outs...</p>"

    html_page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{cfg['site_meta']['title']}</title>
    <meta name="description" content="{cfg['site_meta']['description']}">
    <style>
        :root {{ --bg: #070a13; --surface: #111625; --border: #1f293d; --text: #f3f4f6; --accent: #38bdf8; }}
        body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 12px; line-height: 1.5; }}
        .wrapper {{ max-width: 620px; margin: 0 auto; }}
        header {{ text-align: center; padding: 24px 16px; background: linear-gradient(145deg, #111827, #0f172a); border-radius: 12px; margin-bottom: 16px; border: 1px solid var(--border); }}
        h1 {{ margin: 0; font-size: 1.6rem; color: var(--accent); letter-spacing: -0.025em; }}
        header p {{ margin: 6px 0 0 0; color: #9ca3af; font-size: 0.9rem; }}
        .news-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 16px; margin-bottom: 16px; content-visibility: auto; contain-intrinsic-size: 150px; }}
        .card-meta {{ display: flex; gap: 8px; margin-bottom: 8px; font-size: 0.75rem; font-weight: bold; }}
        .geo-badge {{ background: #1e3a8a; color: #93c5fd; padding: 2px 6px; border-radius: 4px; }}
        .traffic-badge {{ background: #7c2d12; color: #fdba74; padding: 2px 6px; border-radius: 4px; }}
        h2 {{ margin: 4px 0; font-size: 1.2rem; color: #fff; font-weight: 700; }}
        .news-card p {{ font-size: 0.9rem; color: #9ca3af; margin: 6px 0 12px 0; }}
        .news-card a {{ color: var(--accent); text-decoration: none; font-weight: 600; font-size: 0.9rem; display: inline-block; }}
        .ad-slot {{ background: #0f172a; border: 1px dashed #374151; border-radius: 8px; text-align: center; display: flex; align-items: center; justify-content: center; overflow: hidden; }}
        .header-ad {{ min-height: 90px; margin-bottom: 16px; }}
        .inline-ad {{ min-height: 250px; margin-bottom: 16px; }}
        .footer-ad {{ min-height: 90px; margin-top: 16px; }}
    </style>
    <script>window.mondiadData = {{ token: "{mondiad_token}" }};</script>
    {cfg["header_ads_html"]}
</head>
<body>
    <div class="wrapper">
        <div class="ad-slot header-ad">{cfg["header_ads_html"]}</div>
        <header>
            <h1>\u26a1 Automation Core</h1>
            <p>Instant Tier-1 Market Feeds Updated 24/7</p>
        </header>
        <main id="feed">{cards_html}</main>
        <div class="ad-slot footer-ad">{cfg["footer_ads_html"]}</div>
    </div>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_page)

if __name__ == "__main__":
    compile_platform()
      
