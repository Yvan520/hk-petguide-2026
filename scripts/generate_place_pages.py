#!/usr/bin/env python3
"""Generate static, SEO-friendly place detail pages from _places_data.json.

Each place gets its own physical URL (place-<id>.html) so Googlebot can
deep-crawl the site instead of relying on JS-rendered modals.
"""
import json
import os
import re
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "_places_data.json")
OUT = ROOT

REGION_NAME = {
    "hki": "港島", "kowloon": "九龍", "nt": "新界", "lantau": "大嶼山",
}

META_DESC_TPL = (
    "{name}係位於{region}{district}嘅寵物友善{type}，評分⭐{rating}。"
    "PawCity HK 為你整理好地址、開放時間、場內設施、入場守則同狗主貼士，"
    "仲有 Google Maps 導航，帶毛孩出門前必睇。"
)


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def list_html(items, cls=""):
    if not items:
        return ""
    lis = "".join(f"<li>{esc(x)}</li>" for x in items)
    return f'<ul class="{cls}">{lis}</ul>'


def build_page(p):
    pid = p["id"]
    name = p["name"]
    region = REGION_NAME.get(p.get("region", ""), p.get("district", ""))
    district = p.get("district", "")
    ptype = p.get("type", "")
    rating = p.get("rating", "")
    reviews = p.get("reviews", "")
    gmaps = p.get("gmaps", "")
    desc = p.get("desc", "")
    full = p.get("fullDesc", desc)
    best = p.get("bestFor", "")
    addr = p.get("addr", "")
    hours = p.get("hours", "")
    size = p.get("size", "")
    parking = p.get("parking", "")
    water = p.get("water", "")
    facilities = p.get("facilities", [])
    rules = p.get("rules", [])
    tips = p.get("tips", [])
    icon = p.get("icon", "🐾")
    tag = p.get("tag", "")
    today = datetime.date.today().strftime("%Y年%-m月%-d日")

    title = f"{name}｜{region}{district}寵物友善{ptype}推介 — PawCity HK"
    meta = META_DESC_TPL.format(name=name, region=region, district=district,
                                type=ptype, rating=rating)
    canonical = f"https://pethome.gamewayz.com/place-{pid}.html"

    # Related places (same region, exclude self) — for internal linking
    related = []
    try:
        with open(os.path.join(OUT, "_places_data.json"), encoding="utf-8") as f:
            allp = json.load(f)
        related = [x for x in allp if x["id"] != pid and x.get("region") == p.get("region")][:4]
    except Exception:
        related = []

    related_html = ""
    if related:
        cards = []
        for r in related:
            cards.append(f'''      <a href="place-{r['id']}.html" class="related-card">
        <div class="related-icon">{r.get('icon','🐾')}</div>
        <div>
          <h4>{esc(r['name'])}</h4>
          <span class="related-meta">📍 {esc(r.get('district',''))} · ⭐ {r.get('rating','')}</span>
        </div>
      </a>''')
        related_html = f'''
  <section class="related-section">
    <div class="section-header"><div class="section-tag">相關推介</div>
    <h2 class="section-title">同區其他<span class="accent">好去處</span></h2></div>
    <div class="related-grid">
{chr(10).join(cards)}
    </div>
  </section>'''

    page = f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(meta)}">
<meta name="keywords" content="{esc(name)}, 寵物友善, {esc(ptype)}, {esc(district)}, 香港寵物好去處, PawCity">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(meta)}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="article">
<link rel="manifest" href="/manifest.json">
<script type="application/ld+json">{{{{
  "@context": "https://schema.org",
  "@type": "TouristAttraction",
  "name": "{esc(name)}",
  "description": "{esc(meta)}",
  "url": "{canonical}",
  "image": "https://pethome.gamewayz.com/favicon.ico",
  "address": {{{{
    "@type": "PostalAddress",
    "addressLocality": "{esc(district)}",
    "addressRegion": "Hong Kong",
    "addressCountry": "HK"
  }}}},
  "aggregateRating": {{{{
    "@type": "AggregateRating",
    "ratingValue": "{rating}",
    "reviewCount": "{reviews}"
  }}}},
  "openingHours": "{esc(hours)}"
}}}}</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XN13C8R94Y"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-XN13C8R94Y');</script>
<style>
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
:root{{--coral:#E8634A;--coral-light:#FF6B55;--gold:#E8A83A;--dark:#2C2C2C;--charcoal:#3A3A3A;--cream:#FFF8F5;--radius:16px}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:var(--charcoal);background:var(--cream);line-height:1.8}}
.nav{{position:fixed;top:0;left:0;right:0;z-index:1000;padding:18px 48px;display:flex;align-items:center;justify-content:space-between;background:rgba(44,44,44,0.95);backdrop-filter:blur(20px)}}
.nav-logo{{display:flex;align-items:center;gap:10px;text-decoration:none;color:#fff}}
.nav-logo-icon{{font-size:28px}}
.nav-logo-text{{font-size:20px;font-weight:800}}
.nav-logo-text span{{background:linear-gradient(135deg,var(--coral-light),var(--gold));-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.nav-links{{display:flex;list-style:none;gap:8px}}
.nav-links a{{color:rgba(255,255,255,0.75);text-decoration:none;font-size:14px;font-weight:500;padding:8px 16px;border-radius:50px}}
.nav-links a:hover{{color:#fff;background:rgba(255,255,255,0.1)}}
.page-header{{padding:120px 48px 60px;background:linear-gradient(135deg,var(--dark),#1a1a2e)}}
.page-header-inner{{max-width:800px;margin:0 auto}}
.breadcrumb{{font-size:13px;color:rgba(255,255,255,0.4);margin-bottom:20px}}
.breadcrumb a{{color:var(--coral-light);text-decoration:none}}
.breadcrumb span{{margin:0 8px}}
.page-title{{font-size:clamp(28px,3.5vw,42px);font-weight:900;color:#fff;line-height:1.25;margin-bottom:16px}}
.article-meta-bar{{display:flex;flex-wrap:wrap;align-items:center;gap:16px;font-size:13px;color:rgba(255,255,255,0.5);margin-bottom:24px}}
.category-badge{{background:rgba(232,99,74,0.2);color:var(--coral-light);padding:4px 14px;border-radius:50px;font-weight:600}}
.article-body{{max-width:740px;margin:0 auto;padding:48px 24px 80px}}
.article-body h2{{font-size:clamp(20px,2.5vw,26px);font-weight:700;margin:40px 0 16px;color:var(--dark)}}
.article-body p{{font-size:16px;color:#555;margin-bottom:16px}}
.article-body ul{{margin:0 0 16px 24px}}
.article-body li{{font-size:15px;color:#555;margin-bottom:8px}}
.article-body strong{{color:var(--dark);font-weight:700}}
.info-card{{background:#fff;border:1px solid rgba(0,0,0,0.06);border-radius:var(--radius);padding:24px;margin:28px 0}}
.info-card h3{{font-size:18px;margin-bottom:12px;color:var(--dark)}}
.info-row{{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f0f0f0;font-size:15px}}
.info-row:last-child{{border-bottom:none}}
.info-row .label{{color:#8A8580}}
.info-row .value{{font-weight:600;color:var(--dark);text-align:right;max-width:60%}}
.tip-box{{background:#F0F8F0;border-left:4px solid #5A9E5A;border-radius:0 var(--radius) var(--radius) 0;padding:24px 28px;margin:28px 0}}
.tip-box h4{{font-size:16px;font-weight:700;margin-bottom:8px;color:var(--dark)}}
.cta-buttons{{display:flex;gap:12px;flex-wrap:wrap;margin:28px 0}}
.cta-btn{{flex:1;min-width:200px;text-align:center;padding:16px 20px;border-radius:var(--radius);text-decoration:none;font-weight:700;font-size:15px}}
.cta-gmaps{{background:linear-gradient(135deg,var(--coral),var(--gold));color:#fff}}
.cta-back{{background:#fff;border:1px solid rgba(0,0,0,0.08);color:var(--charcoal)}}
.related-section{{background:#fff;padding:60px 24px}}
.related-section .section-header{{max-width:740px;margin:0 auto 32px}}
.related-grid{{max-width:740px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.related-card{{display:flex;gap:14px;align-items:center;background:var(--cream);border-radius:var(--radius);padding:16px;text-decoration:none;color:inherit;border:1px solid rgba(0,0,0,0.04)}}
.related-card:hover{{border-color:var(--coral-light)}}
.related-icon{{font-size:32px}}
.related-card h4{{font-size:15px;color:var(--dark);margin-bottom:4px}}
.related-meta{{font-size:12px;color:#8A8580}}
.footer{{background:var(--dark);padding:60px 48px 30px;color:rgba(255,255,255,0.5)}}
.footer-grid{{max-width:1100px;margin:0 auto;display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:40px}}
.footer-brand p{{font-size:14px;margin-top:16px}}
.footer h4{{color:#fff;font-size:14px;font-weight:700;margin-bottom:16px}}
.footer ul{{list-style:none}}
.footer ul li{{margin-bottom:8px}}
.footer ul a{{color:rgba(255,255,255,0.45);text-decoration:none;font-size:13px}}
.footer ul a:hover{{color:#fff}}
.footer-bottom{{text-align:center;padding-top:30px;margin-top:40px;border-top:1px solid rgba(255,255,255,0.06);font-size:13px}}
@media(max-width:768px){{.nav{{padding:14px 20px}}.nav-links{{display:none}}.page-header{{padding:100px 20px 40px}}.article-body{{padding:32px 20px 60px}}.related-grid{{grid-template-columns:1fr}}.footer-grid{{grid-template-columns:1fr}}.footer{{padding:40px 20px 30px}}}}
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
      <a href="/">首頁</a><span>›</span><a href="places.html">寵物好去處</a><span>›</span><span>{esc(name)}</span>
    </div>
    <h1 class="page-title">{icon} {esc(name)}</h1>
    <div class="article-meta-bar">
      <span class="category-badge">{esc(ptype)}</span>
      <span>📍 {esc(region)} · {esc(district)}</span>
      <span>⭐ {rating} ({reviews} 評論)</span>
      <span>🔄 最後更新：{today}</span>
    </div>
  </div>
</div>
<article class="article-body">

<h2>{esc(name)}係咩嚟？</h2>
<p>{esc(full)}</p>

<div class="info-card">
  <h3>📍 基本資料</h3>
  <div class="info-row"><span class="label">地區</span><span class="value">{esc(district)} · {esc(ptype)}</span></div>
  <div class="info-row"><span class="label">地址</span><span class="value">{esc(addr)}</span></div>
  <div class="info-row"><span class="label">開放時間</span><span class="value">{esc(hours)}</span></div>
  <div class="info-row"><span class="label">面積</span><span class="value">{esc(size)}</span></div>
  <div class="info-row"><span class="label">停車</span><span class="value">{esc(parking)}</span></div>
  <div class="info-row"><span class="label">飲水設施</span><span class="value">{esc(water)}</span></div>
</div>

<h2>🏷️ 場內設施</h2>
{list_html(facilities, "facilities")}

<h2>📋 入場守則</h2>
{list_html(rules, "rules")}

<h2>💡 狗主貼士</h2>
{list_html(tips, "tips")}

<div class="tip-box">
<h4>🎯 最適合</h4>
<p>{esc(best)}</p>
</div>

<div class="cta-buttons">
  <a href="{esc(gmaps)}" target="_blank" rel="noopener" class="cta-btn cta-gmaps">🗺️ Google Maps 導航</a>
  <a href="places.html" class="cta-btn cta-back">← 返回全部好去處</a>
</div>

</article>{related_html}
<footer class="footer">
  <div class="footer-grid">
    <div class="footer-brand">
      <div class="nav-logo" style="color:#fff;"><div class="nav-logo-icon">🐾</div><div class="nav-logo-text"><span>PawCity</span> HK</div></div>
      <p>用 🐾 為香港毛孩而造</p>
    </div>
    <div><h4>探索</h4><ul><li><a href="places.html">寵物好去處</a></li><li><a href="knowledge.html">養寵資訊</a></li><li><a href="laws.html">法例須知</a></li><li><a href="health.html">健康護理</a></li></ul></div>
    <div><h4>資源</h4><ul><li><a href="health.html">獸醫與健康</a></li><li><a href="nutrition.html">寵物營養</a></li><li><a href="article-hk-adoption-data-2026.html">領養資訊</a></li></ul></div>
    <div><h4>關於</h4><ul><li><a href="about.html">關於我哋</a></li><li><a href="about.html#privacy">私隱政策</a></li><li><a href="about.html#terms">使用條款</a></li></ul></div>
  </div>
  <div class="footer-bottom"><p>© 2026 PawCity HK</p></div>
</footer>
</body>
</html>'''
    return page


def main():
    with open(DATA, encoding="utf-8") as f:
        places = json.load(f)
    for p in places:
        page = build_page(p)
        out = os.path.join(OUT, f"place-{p['id']}.html")
        with open(out, "w", encoding="utf-8") as f:
            f.write(page)
        print("wrote", out)


if __name__ == "__main__":
    main()
