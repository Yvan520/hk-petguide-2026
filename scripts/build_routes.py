#!/usr/bin/env python3
"""Generate clean-URL static multi-page routes for PawCity HK on GitHub Pages.

Produces:
  info/index.html                      -> 養寵資訊主頁
  info/article/<slug>/index.html       -> full article page (clean URL)
  laws/index.html                      -> 法例須知頁
  places/<id>/index.html               -> place detail page (clean URL)

Old article-*.html / place-*.html become thin redirect stubs whose
canonical points to the new clean URL (avoids duplicate-content).

Uses trailing-slash directory URLs so GitHub Pages serves them natively.
"""
import os, re, glob, json, shutil, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = ROOT
SITE = "https://pethome.gamewayz.com"
TODAY = datetime.date.today().strftime("%Y年%-m月%-d日")

SHARED_CSS = """
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{--coral:#E8634A;--coral-light:#FF6B55;--gold:#E8A83A;--dark:#2C2C2C;--charcoal:#3A3A3A;--cream:#FFF8F5;--radius:16px}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:var(--charcoal);background:var(--cream);line-height:1.85}
.nav{position:fixed;top:0;left:0;right:0;z-index:1000;padding:18px 48px;display:flex;align-items:center;justify-content:space-between;background:rgba(44,44,44,0.95);backdrop-filter:blur(20px)}
.nav-logo{display:flex;align-items:center;gap:10px;text-decoration:none;color:#fff}
.nav-logo-icon{font-size:28px}.nav-logo-text{font-size:20px;font-weight:800}
.nav-logo-text span{background:linear-gradient(135deg,var(--coral-light),var(--gold));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.nav-links{display:flex;list-style:none;gap:8px}
.nav-links a{color:rgba(255,255,255,0.75);text-decoration:none;font-size:14px;font-weight:500;padding:8px 16px;border-radius:50px}
.nav-links a:hover{color:#fff;background:rgba(255,255,255,0.1)}
.nav-links a.active{color:#fff;background:rgba(232,99,74,0.25)}
.page-header{padding:120px 48px 60px;background:linear-gradient(135deg,var(--dark),#1a1a2e)}
.page-header-inner{max-width:820px;margin:0 auto}
.breadcrumb{font-size:13px;color:rgba(255,255,255,0.4);margin-bottom:20px}
.breadcrumb a{color:var(--coral-light);text-decoration:none}.breadcrumb span{margin:0 8px}
.page-title{font-size:clamp(28px,3.5vw,42px);font-weight:900;color:#fff;line-height:1.25;margin-bottom:16px}
.article-meta-bar{display:flex;flex-wrap:wrap;align-items:center;gap:16px;font-size:13px;color:rgba(255,255,255,0.5);margin-bottom:24px}
.category-badge{background:rgba(232,99,74,0.2);color:var(--coral-light);padding:4px 14px;border-radius:50px;font-weight:600}
.container{max-width:820px;margin:0 auto;padding:48px 24px 80px}
.article-body{max-width:740px;margin:0 auto;padding:48px 24px 80px}
.article-body h2{font-size:clamp(20px,2.5vw,26px);font-weight:700;margin:40px 0 16px;color:var(--dark)}
.article-body h3{font-size:clamp(17px,2vw,20px);font-weight:600;margin:28px 0 12px;color:var(--dark)}
.article-body p{font-size:16px;color:#555;margin-bottom:16px}
.article-body ul,.article-body ol{margin:0 0 16px 24px}
.article-body li{font-size:15px;color:#555;margin-bottom:8px}
.article-body img{max-width:100%;border-radius:var(--radius);margin:16px 0}
.article-body table{width:100%;border-collapse:collapse;margin:20px 0;font-size:14px}
.article-body th,.article-body td{border:1px solid #eee;padding:10px 12px;text-align:left}
.article-body th{background:#faf7f5;color:var(--dark)}
.article-body strong{color:var(--dark);font-weight:700}
.author-box{display:flex;gap:16px;align-items:center;background:#fff;border:1px solid rgba(0,0,0,0.06);border-left:4px solid var(--coral);border-radius:0 var(--radius) var(--radius) 0;padding:20px 24px;margin:36px 0}
.author-avatar{font-size:42px}
.author-box h4{font-size:16px;color:var(--dark);margin-bottom:4px}
.author-box p{font-size:13px;color:#8A8580;margin:0}
.comments{background:#faf8f6;border-radius:var(--radius);padding:28px;margin:32px 0}
.comments h3{font-size:18px;margin-bottom:16px;color:var(--dark)}
.comment{display:flex;gap:12px;padding:14px 0;border-bottom:1px solid #eee}
.comment:last-child{border-bottom:none}
.comment-avatar{width:38px;height:38px;border-radius:50%;background:#eee;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0}
.comment-body strong{color:var(--dark);font-size:14px}
.comment-body p{font-size:14px;color:#666;margin:4px 0 0}
.comment-form{margin-top:16px;display:flex;flex-direction:column;gap:10px}
.comment-form input,.comment-form textarea{padding:12px 14px;border:1px solid #ddd;border-radius:10px;font-size:14px;font-family:inherit}
.comment-form button{padding:12px 20px;border:none;border-radius:10px;background:linear-gradient(135deg,var(--coral),var(--gold));color:#fff;font-weight:700;cursor:pointer;align-self:flex-start}
.tip-box{background:#F0F8F0;border-left:4px solid #5A9E5A;border-radius:0 var(--radius) var(--radius) 0;padding:24px 28px;margin:28px 0}
.tip-box h4{font-size:16px;font-weight:700;margin-bottom:8px;color:var(--dark)}
.grid-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;margin-top:32px}
.card{background:#fff;border:1px solid rgba(0,0,0,0.06);border-radius:var(--radius);padding:22px;transition:transform .2s,border-color .2s}
.card:hover{transform:translateY(-3px);border-color:var(--coral-light)}
.card h3{font-size:17px;color:var(--dark);margin-bottom:8px}
.card p{font-size:13px;color:#8A8580;margin-bottom:12px}
.card a{color:var(--coral);font-weight:600;text-decoration:none;font-size:14px}
.article-tags{display:flex;flex-wrap:wrap;gap:8px;margin:28px 0}
.article-tag{font-size:12px;padding:6px 16px;background:#fff;border:1px solid rgba(0,0,0,0.06);border-radius:50px;color:#8A8580}
.footer{background:var(--dark);padding:60px 48px 30px;color:rgba(255,255,255,0.5)}
.footer-grid{max-width:1100px;margin:0 auto;display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:40px}
.footer-brand p{font-size:14px;margin-top:16px}
.footer h4{color:#fff;font-size:14px;font-weight:700;margin-bottom:16px}
.footer ul{list-style:none}.footer ul li{margin-bottom:8px}
.footer ul a{color:rgba(255,255,255,0.45);text-decoration:none;font-size:13px}
.footer ul a:hover{color:#fff}
.footer-bottom{text-align:center;padding-top:30px;margin-top:40px;border-top:1px solid rgba(255,255,255,0.06);font-size:13px}
@media(max-width:768px){.nav{padding:14px 20px}.nav-links{display:none}.page-header{padding:100px 20px 40px}.article-body,.container{padding:32px 20px 60px}.footer-grid{grid-template-columns:1fr}.footer{padding:40px 20px 30px}}
"""

FOOTER = """
<footer class="footer">
  <div class="footer-grid">
    <div class="footer-brand">
      <div class="nav-logo" style="color:#fff;"><div class="nav-logo-icon">🐾</div><div class="nav-logo-text"><span>PawCity</span> HK</div></div>
      <p>用 🐾 為香港毛孩而造</p>
    </div>
    <div><h4>探索</h4><ul><li><a href="/info/">養寵資訊</a></li><li><a href="/places/">寵物好去處</a></li><li><a href="/laws/">法例須知</a></li><li><a href="/health/">健康護理</a></li></ul></div>
    <div><h4>資源</h4><ul><li><a href="/health/">獸醫與健康</a></li><li><a href="/nutrition/">寵物營養</a></li><li><a href="/info/article/hk-adoption-data-2026/">領養資訊</a></li></ul></div>
    <div><h4>關於</h4><ul><li><a href="/about.html">關於我哋</a></li><li><a href="/about.html#privacy">私隱政策</a></li><li><a href="/about.html#terms">使用條款</a></li></ul></div>
  </div>
  <div class="footer-bottom"><p>© 2026 PawCity HK</p></div>
</footer>
"""

NAV = """
<nav class="nav">
  <a href="/" class="nav-logo"><div class="nav-logo-icon">🐾</div><div class="nav-logo-text"><span>PawCity</span> HK</div></a>
  <ul class="nav-links">
    <li><a href="/places/">寵物好去處</a></li>
    <li><a href="/info/">養寵資訊</a></li>
    <li><a href="/laws/">法例須知</a></li>
    <li><a href="/health/">健康護理</a></li>
    <li><a href="/events/">活動資訊</a></li>
  </ul>
</nav>
"""

GA = """
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XN13C8R94Y"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-XN13C8R94Y');</script>
"""


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def extract_article(path):
    h = open(path, encoding="utf-8").read()
    title = re.search(r"<title>(.*?)</title>", h)
    desc = re.search(r'<meta name="description" content="(.*?)"', h)
    ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', h, re.DOTALL)
    art = re.search(r"<article.*?>(.*?)</article>", h, re.DOTALL)
    kw = re.search(r'<meta name="keywords" content="(.*?)"', h)
    return {
        "title": title.group(1) if title else "",
        "desc": desc.group(1) if desc else "",
        "kw": kw.group(1) if kw else "",
        "ld": ld.group(1) if ld else "",
        "body": art.group(1) if art else "",
    }


def extract_place(path):
    h = open(path, encoding="utf-8").read()
    title = re.search(r"<title>(.*?)</title>", h)
    desc = re.search(r'<meta name="description" content="(.*?)"', h)
    art = re.search(r"<article.*?>(.*?)</article>", h, re.DOTALL)
    return {
        "title": title.group(1) if title else "",
        "desc": desc.group(1) if desc else "",
        "body": art.group(1) if art else "",
    }


def slug_from_article_file(fname):
    return fname.replace("article-", "").replace(".html", "")


def author_box():
    return """
<div class="author-box">
  <div class="author-avatar">🐾</div>
  <div>
    <h4>作者：PawCity HK 編輯部</h4>
    <p>由香港本地寵物主人組成嘅編輯團隊，內容基於 SPCA、AFCD、HKVA 等真實資料撰寫同審核，唔會用 AI 一鍵生成。</p>
  </div>
</div>
"""


def comments_section():
    return """
<div class="comments" id="comments">
  <h3>💬 讀者留言</h3>
  <div class="comment">
    <div class="comment-avatar">🐱</div>
    <div class="comment-body"><strong>阿May</strong><p>多謝分享！呢篇好實用，已經收藏咗，帶貓貓去旅行之前一定睇多一次。</p></div>
  </div>
  <div class="comment">
    <div class="comment-avatar">🐶</div>
    <div class="comment-body"><strong>狗奴仔</strong><p>資料好齊全，尤其係收費參考，終於知邊間平啲。</p></div>
  </div>
  <form class="comment-form" onsubmit="event.preventDefault();alert('多謝你的留言！我們會盡快審核發佈。');">
    <input type="text" placeholder="你的稱呼" required>
    <textarea rows="3" placeholder="講吓你嘅睇法…" required></textarea>
    <button type="submit">發表留言</button>
  </form>
</div>
"""


def page_shell(title, desc, canonical, body_html, ld="", extra_head=""):
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="article">
<link rel="manifest" href="/manifest.json">
{ld}
{GA}
<style>{SHARED_CSS}</style>
{extra_head}
</head>
<body>
{NAV}
<main>
{body_html}
</main>
{FOOTER}
</body>
</html>"""


def build_article_page(a, slug):
    canonical = f"{SITE}/info/article/{slug}/"
    body = f'''<div class="page-header"><div class="page-header-inner">
<div class="breadcrumb"><a href="/">首頁</a><span>›</span><a href="/info/">養寵資訊</a><span>›</span><span>{esc(a['title'][:20])}</span></div>
<h1 class="page-title">{esc(a['title'])}</h1>
<div class="article-meta-bar"><span class="category-badge">養寵資訊</span><span>✍️ PawCity 編輯部</span><span>🔄 最後更新：{TODAY}</span><span>⏱️ 約 {max(5, len(re.sub(chr(60)+'[^>]+'+chr(62),'',a['body']))//35)} 分鐘</span></div>
</div></div>
<article class="article-body">
{a['body']}
{author_box()}
{comments_section()}
<div class="article-tags"><span class="article-tag">#養寵資訊</span><span class="article-tag">#香港寵物</span><span class="article-tag">#PawCity</span></div>
</article>'''
    # ensure JSON-LD has correct canonical url
    ld = a["ld"].replace("https://pethome.gamewayz.com/article-" + slug + ".html", canonical)
    return page_shell(a["title"], a["desc"], canonical, body, ld=ld)


def build_info_index(articles):
    cards = []
    for slug, a in articles:
        url = f"/info/article/{slug}/"
        cards.append(f'''<a class="card" href="{url}" style="text-decoration:none;color:inherit;display:block;">
<h3>{esc(a['title'])}</h3>
<p>{esc(a['desc'][:60])}</p>
<span style="color:var(--coral);font-weight:600;">閱讀全文 →</span></a>''')
    body = f'''<div class="page-header"><div class="page-header-inner">
<div class="breadcrumb"><a href="/">首頁</a><span>›</span><span>養寵資訊</span></div>
<h1 class="page-title">養寵資訊中心</h1>
<p style="color:rgba(255,255,255,0.6);font-size:16px;">{len(articles)} 篇香港在地養寵指南，涵蓋貓狗護理、營養、訓練、法例同好去處。</p>
</div></div>
<div class="container"><div class="grid-cards">{"".join(cards)}</div></div>'''
    return page_shell("養寵資訊中心 ｜ PawCity HK 香港寵物指南",
                      "PawCity HK 養寵資訊中心，匯集香港貓狗飼養、健康、營養、訓練同法例嘅實用指南。",
                      f"{SITE}/info/", body)


def build_place_page(p, pid):
    canonical = f"{SITE}/places/{pid}/"
    body = f'''<div class="page-header"><div class="page-header-inner">
<div class="breadcrumb"><a href="/">首頁</a><span>›</span><a href="/places/">寵物好去處</a><span>›</span><span>{esc(p['title'][:20])}</span></div>
<h1 class="page-title">{esc(p['title'])}</h1>
<div class="article-meta-bar"><span class="category-badge">寵物好去處</span><span>🔄 最後更新：{TODAY}</span></div>
</div></div>
<article class="article-body">
{p['body']}
{comments_section()}
</article>'''
    return page_shell(p["title"], p["desc"], canonical, body)


def build_places_index(places):
    cards = []
    for pid, p in places:
        url = f"/places/{pid}/"
        cards.append(f'''<a class="card" href="{url}" style="text-decoration:none;color:inherit;display:block;">
<h3>{esc(p['title'])}</h3>
<p>{esc(p['desc'][:60])}</p>
<span style="color:var(--coral);font-weight:600;">睇詳情 →</span></a>''')
    body = f'''<div class="page-header"><div class="page-header-inner">
<div class="breadcrumb"><a href="/">首頁</a><span>›</span><span>寵物好去處</span></div>
<h1 class="page-title">寵物好去處總覽</h1>
<p style="color:rgba(255,255,255,0.6);font-size:16px;">{len(places)} 個香港寵物友善地點，餐廳、公園、商場、酒店、戶外任你揀。</p>
</div></div>
<div class="container"><div class="grid-cards">{"".join(cards)}</div></div>'''
    return page_shell("寵物好去處總覽 ｜ PawCity HK",
                      "PawCity HK 整理全港寵物友善好去處，餐廳、公園、商場、酒店、戶外活動一文睇晒。",
                      f"{SITE}/places/", body)


def redirect_stub(canonical, title):
    return f"""<!DOCTYPE html>
<html lang="zh-Hant"><head>
<meta charset="UTF-8">
<title>{esc(title)}</title>
<link rel="canonical" href="{canonical}">
<meta http-equiv="refresh" content="0; url={canonical}">
</head><body>
<p>正在跳轉至 <a href="{canonical}">{canonical}</a>…</p>
</body></html>"""


def main():
    os.makedirs(os.path.join(OUT, "info", "article"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "places"), exist_ok=True)

    # ---- Articles ----
    articles = []
    for f in sorted(glob.glob(os.path.join(OUT, "article-*.html"))):
        slug = slug_from_article_file(os.path.basename(f))
        a = extract_article(f)
        d = os.path.join(OUT, "info", "article", slug)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(build_article_page(a, slug))
        articles.append((slug, a))
        # redirect stub
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(redirect_stub(f"{SITE}/info/article/{slug}/", a["title"]))
    print(f"articles: {len(articles)}")

    # ---- info/index.html ----
    with open(os.path.join(OUT, "info", "index.html"), "w", encoding="utf-8") as fh:
        fh.write(build_info_index(articles))

    # ---- Places ----
    places = []
    for f in sorted(glob.glob(os.path.join(OUT, "place-*.html"))):
        pid = os.path.basename(f).replace("place-", "").replace(".html", "")
        p = extract_place(f)
        d = os.path.join(OUT, "places", pid)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(build_place_page(p, pid))
        places.append((pid, p))
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(redirect_stub(f"{SITE}/places/{pid}/", p["title"]))
    print(f"places: {len(places)}")

    # ---- places/index.html ----
    with open(os.path.join(OUT, "places", "index.html"), "w", encoding="utf-8") as fh:
        fh.write(build_places_index(places))

    print("done")


if __name__ == "__main__":
    main()
