#!/usr/bin/env python3
"""Daily PawCity HK article generator.
Usage: python3 scripts/generate_article.py
Requires env vars: API_KEY, API_BASE_URL, MODEL_NAME
"""

import json, os, re, sys, hashlib
from datetime import date, datetime
from pathlib import Path

from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent.parent
CALENDAR_PATH = BASE_DIR / "scripts" / "content_calendar.json"
SITEMAP_PATH = BASE_DIR / "sitemap.xml"

API_KEY = os.environ.get("API_KEY")
API_BASE_URL = os.environ.get("API_BASE_URL") or "https://api.longcat.chat/openai"
MODEL_NAME = os.environ.get("MODEL_NAME") or "LongCat-2.0-Preview"

LIVE_URL = "https://pethome.gamewayz.com"


def get_today_topic():
    with open(CALENDAR_PATH, "r", encoding="utf-8") as f:
        topics = json.load(f)
    day_of_year = date.today().timetuple().tm_yday
    idx = (day_of_year - 1) % len(topics)
    return topics[idx]


def get_existing_slugs():
    slugs = set()
    for p in BASE_DIR.glob("article-*.html"):
        slugs.add(p.stem)
    return slugs


def build_prompt(topic):
    today = date.today().strftime("%Y年%m月%d日")
    return f"""你係PawCity HK嘅寵物編輯，幫我寫一篇寵物文章。用香港粵語寫，要似真人寫嘅blog文，唔似AI倒模。

## 文章資料
- 標題：{topic['title']}
- 分類：{topic['category']}
- 簡介：{topic['description']}
- 目標關鍵詞：{', '.join(topic['keywords'])}
- 參考來源：{', '.join(topic['sources'])}
- 日期：{today}

## 寫作要求
1. **全文約 600-1000 個中文字**就夠，唔使太長。
2. 用香港粵語口吻（的→嘅、不→唔、們→哋、了→咗、那些→啲、還→仲、在→喺、看→睇、吃→食、找→搵、給→俾），自然啲。
3. 3-4 個小標題（h2）就夠，唔使每段都加emoji開頭。
4. 唔使刻意加FAQ、唔使加emoji圖案喺標題。
5. 引用真實資料要自然融入內文，唔好硬塞。
6. 文末簡單列出參考資料就得，用<a>連去真實網站（如SPCA、AFCD、AVMA）。
7. 文章要讀落似真人分享經驗，有香港本地角度（例如：香港邊度有相關服務、大約幾錢）。
8. 每段 3-5 句就夠，唔好太冗長。
9. 唔好用「你可唔可以」、「你知唔知」呢啲常見AI開場白。

## 輸出格式
就係 <body> 內嘅 HTML 內容直接用 <h2> 分 section，唔使花巧。範例：

<h2>一個自然嘅小標題</h2>
<p>內文內容⋯⋯</p>

<h2>另一個小標題</h2>
<p>內文⋯⋯有引用嘅資料可以括住來源。</p>

<h2>第三個角度</h2>
<p>繼續寫⋯⋯</p>

<div class="conclusion reveal">
  <h3>總結</h3>
  <p>簡單總結幾句。</p>
</div>

<div class="article-tags reveal">
  <span class="article-tag">#標籤1</span>
  <span class="article-tag">#標籤2</span>
  <span class="article-tag">#標籤3</span>
</div>

<div class="references" style="margin-top:40px;padding:28px 24px;background:#FAFAF8;border-radius:16px;">
  <h3>參考資料</h3>
  <ul>
    <li><a href="https://..." target="_blank" rel="noopener">來源 - 標題</a></li>
    <li><a href="https://..." target="_blank" rel="noopener">來源 - 標題</a></li>
  </ul>
</div>
"""


def count_chinese(text):
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    return len(chinese_chars)

def generate_article_content(prompt):
    client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL, timeout=60.0)
    best_content = ""
    best_count = 0
    for attempt in range(2):
        try:
            resp = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": "你係PawCity HK嘅寵物編輯。用香港粵語寫原創寵物文章，自然啲似真人寫。引用真實來源。約600-1000字。",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=4096,
                temperature=0.8 + attempt * 0.1,
            )
            content = resp.choices[0].message.content
        except Exception as e:
            print(f"  ↳ Attempt {attempt+1} failed: {type(e).__name__}")
            continue
        cnt = count_chinese(content)
        print(f"  ↳ Attempt {attempt+1}: {cnt} Chinese chars")
        if cnt > best_count:
            best_content = content
            best_count = cnt
        if cnt >= 600:
            print(f"  ✓ Length OK ({cnt} chars)")
            return content
        print(f"  ✗ Too short ({cnt} < 600), retrying...")
    if best_content:
        print(f"  ⚠ Best attempt: {best_count} chars (using anyway)")
        return best_content
    raise RuntimeError("All API attempts failed")


def build_full_html(topic, body_html, today_str):
    slug = topic["slug"]
    title = topic["title"]
    desc = topic["description"]
    category = topic["category"]
    keywords = ", ".join(topic["keywords"])

    existing = get_existing_slugs()

    related_links = ""
    related = [s for s in ["article-" + s for s in list(existing)[:3]] if s != f"article-{slug}"]
    for r in related[:3]:
        name = r.replace("article-", "").replace("-", " ")
        related_links += f'<a href="{r}.html" class="related-card"><h4>{name}</h4></a>\n'

    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | PawCity HK</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="{keywords}">
<link rel="canonical" href="{LIVE_URL}/article-{slug}.html">
<meta property="og:title" content="{title} | PawCity HK">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{LIVE_URL}/article-{slug}.html">
<meta property="og:type" content="article">
<link rel="manifest" href="/manifest.json">
<script type="application/ld+json">{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{title}",
  "description": "{desc}",
  "author": {{
    "@type": "Organization",
    "name": "PawCity HK"
  }},
  "publisher": {{
    "@type": "Organization",
    "name": "PawCity HK"
  }},
  "datePublished": "{today_str}",
  "dateModified": "{today_str}",
  "mainEntityOfPage": "{{
    "@type": "WebPage",
    "@id": "{LIVE_URL}/article-{slug}.html"
  }}
}}</script>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XN13C8R94Y"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-XN13C8R94Y');
</script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
:root {{ --coral:#E8634A; --coral-light:#FF6B55; --gold:#E8A83A; --gold-light:#F0B84A; --sage:#5A9E5A; --sky:#3A7BD5; --dark:#2C2C2C; --charcoal:#3A3A3A; --cream:#FFF8F5; --radius:16px; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; color:var(--charcoal); background:var(--cream); line-height:1.8; }}
.nav {{ position:fixed; top:0; left:0; right:0; z-index:1000; padding:18px 48px; display:flex; align-items:center; justify-content:space-between; background:rgba(44,44,44,0.95); backdrop-filter:blur(20px); transition:all 0.3s; }}
.nav-logo {{ display:flex; align-items:center; gap:10px; text-decoration:none; color:white; }}
.nav-logo-icon {{ font-size:28px; }}
.nav-logo-text {{ font-size:20px; font-weight:800; }}
.nav-logo-text span {{ background:linear-gradient(135deg,var(--coral-light),var(--gold-light)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
.nav-links {{ display:flex; list-style:none; gap:8px; }}
.nav-links a {{ color:rgba(255,255,255,0.75); text-decoration:none; font-size:14px; font-weight:500; padding:8px 16px; border-radius:50px; transition:all 0.3s; }}
.nav-links a:hover {{ color:white; background:rgba(255,255,255,0.1); }}
.page-header {{ padding:120px 48px 60px; background:linear-gradient(135deg,var(--dark),#1a1a2e); }}
.page-header-inner {{ max-width:800px; margin:0 auto; }}
.breadcrumb {{ font-size:13px; color:rgba(255,255,255,0.4); margin-bottom:20px; }}
.breadcrumb a {{ color:var(--coral-light); text-decoration:none; }}
.breadcrumb span {{ margin:0 8px; }}
.page-title {{ font-size:clamp(28px,3.5vw,42px); font-weight:900; color:white; line-height:1.25; margin-bottom:16px; }}
.page-title .accent {{ background:linear-gradient(135deg,var(--coral-light),var(--gold-light)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
.article-meta-bar {{ display:flex; flex-wrap:wrap; align-items:center; gap:16px; font-size:13px; color:rgba(255,255,255,0.5); margin-bottom:24px; }}
.category-badge {{ background:rgba(232,99,74,0.2); color:var(--coral-light); padding:4px 14px; border-radius:50px; font-weight:600; }}
.article-body {{ max-width:740px; margin:0 auto; padding:48px 24px 80px; }}
.article-body h2 {{ font-size:clamp(20px,2.5vw,26px); font-weight:700; margin:40px 0 16px; color:var(--dark); }}
.article-body h2 .h2-icon {{ margin-right:8px; }}
.article-body p {{ font-size:16px; color:#555; margin-bottom:16px; }}
.article-body ul {{ margin:0 0 16px 24px; }}
.article-body li {{ font-size:15px; color:#555; margin-bottom:8px; }}
.conclusion {{ background:linear-gradient(135deg,#FFF8F5,#FFF0E8); border-radius:var(--radius); padding:32px; margin:40px 0; }}
.conclusion h3 {{ font-size:20px; font-weight:700; margin-bottom:12px; color:var(--dark); }}
.conclusion p {{ margin-bottom:0; }}
.article-tags {{ display:flex; flex-wrap:wrap; gap:8px; margin:32px 0; }}
.article-tag {{ font-size:12px; padding:6px 16px; background:white; border:1px solid rgba(0,0,0,0.06); border-radius:50px; color:#8A8580; }}
.references h3 {{ font-size:16px; font-weight:700; margin-bottom:16px; color:var(--dark); }}
.references ul {{ list-style:none; padding:0; }}
.references li {{ font-size:13px; color:#8A8580; padding:6px 0; border-bottom:1px solid rgba(0,0,0,0.04); }}
.references li:last-child {{ border-bottom:none; }}
.subscribe-banner {{ background:linear-gradient(135deg,var(--dark),#1a1a2e); padding:60px 24px; text-align:center; }}
.subscribe-banner-inner {{ max-width:500px; margin:0 auto; }}
.subscribe-banner h2 {{ font-size:24px; color:white; margin-bottom:12px; }}
.subscribe-banner p {{ color:rgba(255,255,255,0.5); font-size:14px; margin-bottom:24px; }}
.subscribe-banner-form {{ display:flex; gap:12px; max-width:420px; margin:0 auto; }}
.subscribe-banner-form input {{ flex:1; padding:14px 20px; border-radius:50px; border:none; font-size:14px; outline:none; }}
.subscribe-banner-form button {{ padding:14px 32px; border-radius:50px; border:none; background:linear-gradient(135deg,var(--coral),var(--gold)); color:white; font-weight:700; cursor:pointer; font-size:14px; }}
.footer {{ background:var(--dark); padding:60px 48px 30px; color:rgba(255,255,255,0.5); }}
.footer-grid {{ max-width:1100px; margin:0 auto; display:grid; grid-template-columns:2fr 1fr 1fr 1fr; gap:40px; }}
.footer-brand p {{ font-size:14px; margin-top:16px; }}
.footer h4 {{ color:white; font-size:14px; font-weight:700; margin-bottom:16px; }}
.footer ul {{ list-style:none; }}
.footer ul li {{ margin-bottom:8px; }}
.footer ul a {{ color:rgba(255,255,255,0.45); text-decoration:none; font-size:13px; }}
.footer ul a:hover {{ color:white; }}
.footer-bottom {{ text-align:center; padding-top:30px; margin-top:40px; border-top:1px solid rgba(255,255,255,0.06); font-size:13px; }}
@media (max-width:768px) {{ .nav {{ padding:14px 20px; }} .nav-links {{ display:none; }} .page-header {{ padding:100px 20px 40px; }} .article-body {{ padding:32px 20px 60px; }} .footer-grid {{ grid-template-columns:1fr; }} .footer {{ padding:40px 20px 30px; }} .subscribe-banner-form {{ flex-direction:column; }} }}
</style>
</head>
<body>
<nav class="nav">
  <a href="/" class="nav-logo"><div class="nav-logo-icon">🐾</div><div class="nav-logo-text"><span>PawCity</span> HK</div></a>
  <ul class="nav-links">
    <li><a href="places.html">寵物好去處</a></li>
    <li><a href="knowledge.html">養寵資訊</a></li>
    <li><a href="laws.html">法例須知</a></li>
    <li><a href="health.html">健康護理</a></li>
    <li><a href="events.html">活動資訊</a></li>
  </ul>
</nav>
<main>
<div class="page-header">
  <div class="page-header-inner">
    <div class="breadcrumb">
      <a href="/">首頁</a><span>›</span><a href="knowledge.html">養寵資訊</a><span>›</span><span>{title}</span>
    </div>
    <h1 class="page-title">{title}</h1>
    <div class="article-meta-bar">
      <span class="category-badge">{category}</span>
      <span>✍️ PawCity編輯部</span>
      <span>🔄 最後更新：{today_str}</span>
      <span>⏱️ 約{max(5, len(re.sub(r'<[^>]+>', '', body_html))//300)}分鐘</span>
    </div>
  </div>
</div>
<article class="article-body">
{body_html}
</article>
<section class="subscribe-banner" id="subscribe">
  <div class="subscribe-banner-inner">
    <h2>📬 接收更多養寵資訊</h2>
    <p>每星期獲取最新養寵貼士、健康資訊同優惠活動</p>
    <form class="subscribe-banner-form" onsubmit="event.preventDefault();alert('多謝訂閱！🐾');">
      <input type="email" placeholder="輸入你嘅電郵地址" required>
      <button type="submit">即時訂閱 →</button>
    </form>
  </div>
</section>
</main>
<footer class="footer">
  <div class="footer-grid">
    <div class="footer-brand">
      <div class="nav-logo" style="color:white;"><div class="nav-logo-icon">🐾</div><div class="nav-logo-text"><span>PawCity</span> HK</div></div>
      <p>用 🐾 為香港毛孩而造</p>
    </div>
    <div><h4>探索</h4><ul><li><a href="places.html">寵物好去處</a></li><li><a href="knowledge.html">養寵資訊</a></li><li><a href="laws.html">法例須知</a></li><li><a href="health.html">健康護理</a></li></ul></div>
    <div><h4>資源</h4><ul><li><a href="#">獸醫網絡</a></li><li><a href="#">寵物保險</a></li><li><a href="#">領養資訊</a></li></ul></div>
    <div><h4>關於</h4><ul><li><a href="#">關於我哋</a></li><li><a href="#">私隱政策</a></li><li><a href="#">使用條款</a></li></ul></div>
  </div>
  <div class="footer-bottom"><p>© 2026 PawCity HK</p></div>
</footer>
</body>
</html>
"""


def update_sitemap(slug, today_str):
    url = f"{LIVE_URL}/article-{slug}.html"
    entry = f"""  <url>
    <loc>{url}</loc>
    <lastmod>{today_str}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>"""

    content = SITEMAP_PATH.read_text(encoding="utf-8") if SITEMAP_PATH.exists() else ""
    if url in content:
        print(f"  ↳ {slug} already in sitemap")
        return
    insert_before = "</urlset>"
    if insert_before in content:
        content = content.replace(insert_before, entry + "\n" + insert_before)
    else:
        content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entry}
</urlset>"""
    SITEMAP_PATH.write_text(content, encoding="utf-8")
    print(f"  ↳ sitemap updated with {url}")


def main():
    force = "--force" in sys.argv
    topic = get_today_topic()
    slug = topic["slug"]
    today_str = date.today().strftime("%Y年%m月%d日")

    existing = get_existing_slugs()
    slug_name = f"article-{slug}"
    if slug_name in existing and not force:
        print(f"✗ {slug_name}.html already exists — skipping")
        sys.exit(0)
    if slug_name in existing and force:
        print(f"⚠ --force: regenerating {slug_name}.html")

    print(f"→ Generating: {topic['title']} ({slug})")
    prompt = build_prompt(topic)
    body_html = generate_article_content(prompt)
    print(f"  ↳ API response: {len(body_html)} chars")

    # Remove h1 from body (already in page header)
    body_html = re.sub(r'<h1[^>]*>.*?</h1>\s*', '', body_html, count=1)
    full_html = build_full_html(topic, body_html, today_str)

    out_path = BASE_DIR / f"article-{slug}.html"
    out_path.write_text(full_html, encoding="utf-8")
    print(f"  ↳ Saved: article-{slug}.html ({len(full_html)} bytes)")

    update_sitemap(slug, today_str)
    print(f"✓ Done — {topic['title']}")


if __name__ == "__main__":
    main()
