#!/usr/bin/env python3
"""Generate static detail pages for the 25 venues listed on places.html.

Each card on places.html becomes place-<slug>.html with crawlable <a> links.
Content is synthesized from the real card data (name, category, district, tags,
price, image) so every page is unique and SEO-meaningful.
"""
import os, re, json, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLACES_HTML = os.path.join(ROOT, "places.html")
OUT = ROOT

CAT_EN = {
    "restaurant": "餐廳", "park": "寵物公園", "mall": "商場", "hotel": "住宿",
    "outdoor": "戶外", "cafe": "咖啡店",
}
TYPE_LABEL = {
    "餐廳": "寵物友善餐廳", "寵物公園": "寵物公園", "商場": "寵物友善商場",
    "住宿": "寵物友善酒店", "戶外": "戶外好去處", "咖啡店": "寵物友善咖啡店",
}


def slugify(name):
    # Prefer a trailing latin token (e.g. "西貢寵物公園 Sai Kung" -> "sai-kung")
    latin = re.findall(r"[A-Za-z][A-Za-z0-9\s\.']*", name)
    base = ""
    if latin:
        base = latin[-1].strip().lower()
    if not base or len(base) < 3:
        # fall back to stripping non-ascii -> keep any ascii
        base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    if not base:
        base = "place"
    return "place-" + base


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def parse_cards():
    h = open(PLACES_HTML, encoding="utf-8").read()
    # Each card: <div class="place-card" data-category="X"> ... <h3>NAME<span...> LOC</span></h3> ... tags ... footer price
    cards = re.findall(r'<div class="place-card" data-category="([^"]+)">(.*?)</div>\s*</div>\s*</div>', h, re.DOTALL)
    out = []
    for cat, body in cards:
        # name
        h3 = re.search(r"<h3>(.*?)</h3>", body, re.DOTALL)
        raw = h3.group(1)
        name = re.sub(r"<[^>]+>", "", raw).strip()
        # image
        img = re.search(r'<img[^>]+src="([^"]+)"', body)
        image = img.group(1) if img else ""
        alt = re.search(r'<img[^>]+alt="([^"]+)"', body)
        alt = alt.group(1) if alt else name
        # location
        loc = re.search(r'class="place-card-location">([^<]+)<', body)
        location = loc.group(1).strip() if loc else ""
        # tags
        tags = re.findall(r"<span>([^<]+)</span>", body)
        # price (footer span)
        price = re.search(r'class="place-card-footer">\s*<span>([^<]+)<', body)
        price = price.group(1).strip() if price else ""
        out.append({
            "name": name, "category": cat, "image": image, "alt": alt,
            "location": location, "tags": tags, "price": price,
        })
    return out


TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{meta}">
<meta name="keywords" content="{kw}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{meta}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="article">
<link rel="manifest" href="/manifest.json">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"TouristAttraction","name":"{name}","description":"{meta}","url":"{canonical}","address":{{"@type":"PostalAddress","addressLocality":"{district}","addressCountry":"HK"}},"openingHours":"每日"}}</script>
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
.hero-img{{width:100%;border-radius:var(--radius);margin:24px 0;display:block}}
.info-card{{background:#fff;border:1px solid rgba(0,0,0,0.06);border-radius:var(--radius);padding:24px;margin:28px 0}}
.info-row{{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f0f0f0;font-size:15px}}
.info-row:last-child{{border-bottom:none}}
.info-row .label{{color:#8A8580}}
.info-row .value{{font-weight:600;color:var(--dark);text-align:right;max-width:60%}}
.tip-box{{background:#F0F8F0;border-left:4px solid #5A9E5A;border-radius:0 var(--radius) var(--radius) 0;padding:24px 28px;margin:28px 0}}
.tip-box h4{{font-size:16px;font-weight:700;margin-bottom:8px;color:var(--dark)}}
.cta-buttons{{display:flex;gap:12px;flex-wrap:wrap;margin:28px 0}}
.cta-btn{{flex:1;min-width:200px;text-align:center;padding:16px 20px;border-radius:var(--radius);text-decoration:none;font-weight:700;font-size:15px}}
.cta-back{{background:#fff;border:1px solid rgba(0,0,0,0.08);color:var(--charcoal)}}
.cta-all{{background:linear-gradient(135deg,var(--coral),var(--gold));color:#fff}}
.footer{{background:var(--dark);padding:60px 48px 30px;color:rgba(255,255,255,0.5)}}
.footer-grid{{max-width:1100px;margin:0 auto;display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:40px}}
.footer-brand p{{font-size:14px;margin-top:16px}}
.footer h4{{color:#fff;font-size:14px;font-weight:700;margin-bottom:16px}}
.footer ul{{list-style:none}}
.footer ul li{{margin-bottom:8px}}
.footer ul a{{color:rgba(255,255,255,0.45);text-decoration:none;font-size:13px}}
.footer ul a:hover{{color:#fff}}
.footer-bottom{{text-align:center;padding-top:30px;margin-top:40px;border-top:1px solid rgba(255,255,255,0.06);font-size:13px}}
@media(max-width:768px){{.nav{{padding:14px 20px}}.nav-links{{display:none}}.page-header{{padding:100px 20px 40px}}.article-body{{padding:32px 20px 60px}}.footer-grid{{grid-template-columns:1fr}}.footer{{padding:40px 20px 30px}}}}
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
      <a href="/">首頁</a><span>›</span><a href="places.html">寵物好去處</a><span>›</span><span>{name}</span>
    </div>
    <h1 class="page-title">{name}</h1>
    <div class="article-meta-bar">
      <span class="category-badge">{type_label}</span>
      <span>📍 {location}</span>
      <span>🔄 最後更新：{today}</span>
    </div>
  </div>
</div>
<article class="article-body">
<img class="hero-img" src="{image}" alt="{alt}" loading="lazy">
<h2>{name} 係點嘅地方？</h2>
<p>{intro}</p>
<div class="info-card">
  <h3>📍 基本資料</h3>
  <div class="info-row"><span class="label">類型</span><span class="value">{type_label}</span></div>
  <div class="info-row"><span class="label">地點</span><span class="value">{location}</span></div>
  <div class="info-row"><span class="label">收費</span><span class="value">{price}</span></div>
</div>
<h2>🏷️ 呢度有咩特色</h2>
{tags_html}
<div class="tip-box">
<h4>💡 帶毛孩去嘅貼士</h4>
<p>{tips}</p>
</div>
<div class="cta-buttons">
  <a href="places.html" class="cta-btn cta-all">🐾 睇晒全部好去處</a>
  <a href="/" class="cta-btn cta-back">← 返回首頁</a>
</div>
</article>
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


def build_intro(c):
    name = c["name"]
    t = TYPE_LABEL.get(c["category"], "好去處")
    loc = c["location"] or "香港"
    tags = "、".join(c["tags"][:3]) if c["tags"] else "寵物友善設施"
    return (f"{name} 係位於{loc}嘅{t}，一直深受香港寵物主人歡迎。"
            f"呢度提供{tags}等設施，帶毛孩出門可以玩得盡興又放心。"
            f"PawCity HK 為你整理好地址、收費同實用貼士，去之前睇多一次就唔會中伏。")


def build_tips(c):
    cat = c["category"]
    base = "記得隨身帶定寵物水碗同纸巾，隨時清理毛孩排泄物，做個有禮貌嘅狗主。"
    if cat in ("restaurant", "cafe"):
        base = "餐廳內請用寵物袋或牽繩，避免打擾其他食客；旺市时段建議先預約或選平日前往。"
    elif cat == "park":
        base = "公園放電前先檢查牽繩規定，帶足夠食水同急救用品；夏天避免正午曝曬，小心蚊蟲。"
    elif cat == "mall":
        base = "商場多数要求寵物放喺推車或袋內，大型犬記得戴口罩；可用商場寵物電梯前往各層。"
    elif cat == "hotel":
        base = "入住前務必預先註明帶寵物並查詢附加費，準備好疫苗紀錄同行。"
    elif cat == "outdoor":
        base = "戶外活動留意天氣同補給，帶毛巾同清水沖身；行山路段注意補給點同野生動物。"
    return base


def main():
    cards = parse_cards()
    today = datetime.date.today().strftime("%Y年%-m月%-d日")
    seen = {}
    for c in cards:
        slug = slugify(c["name"])
        if slug in seen:
            slug = slug + "-" + str(seen[slug] + 1)
            seen[slug.split("-")[1] if "-" in slug else slug] = seen.get(slug.split("-")[1] if "-" in slug else slug, 0) + 1
        name = c["name"]
        tlabel = TYPE_LABEL.get(c["category"], "寵物好去處")
        title = f"{name}｜{c['location'] or '香港'}寵物友善{tlabel}推介 — PawCity HK"
        district = (c["location"].split("·")[0].split(" ")[0].strip()
                    if c["location"] else "香港")
        meta = (f"{name}係位於{c['location'] or '香港'}嘅{tlabel}，"
                f"提供{('、'.join(c['tags'][:3]) if c['tags'] else '寵物友善設施')}。"
                f"PawCity HK 為你整理好地址、收費同帶毛孩出門嘅實用貼士。")
        tags_html = "<ul>" + "".join(f"<li>{esc(t)}</li>" for t in c["tags"]) + "</ul>" if c["tags"] else ""
        page = TEMPLATE.format(
            title=esc(title), meta=esc(meta),
            kw=esc(f"{name}, 寵物友善, {tlabel}, {c['location']}, 香港寵物好去處"),
            canonical=f"https://pethome.gamewayz.com/{slug}.html",
            name=esc(name), type_label=esc(tlabel), location=esc(c["location"] or "香港"),
            district=esc(district),
            today=today, image=esc(c["image"]), alt=esc(c["alt"]),
            intro=esc(build_intro(c)), price=esc(c["price"] or "請參考官方"),
            tags_html=tags_html, tips=esc(build_tips(c)),
        )
        with open(os.path.join(OUT, slug + ".html"), "w", encoding="utf-8") as f:
            f.write(page)
        print("wrote", slug + ".html", "->", name)


if __name__ == "__main__":
    main()
