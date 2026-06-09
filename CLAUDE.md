# PawCity HK — Working Notes

## Working Directory
**Use `/Users/admin/Documents/pawcity-hk/` for all PawCity HK changes.**

DO NOT use `/Users/admin/Documents/test/` (contains TL game + stale remote).

## Project
- **Site**: https://pethome.gamewayz.com/
- **Repo**: https://github.com/Yvan520/hk-petguide-2026
- **Stack**: Static HTML/CSS/JS, GitHub Pages
- **Custom domain**: pethome.gamewayz.com (CNAME file in root)

## Daily automation
- `scripts/generate_article.py` — LongCat-2.0-Preview (GitHub Secrets: `LONGCAT_API_KEY`)
- `.github/workflows/daily-article.yml` — cron `0 0 * * *` (08:00 HKT)
- 30 topics in `scripts/content_calendar.json`

## Tone
- Authentic HK Cantonese (的→嘅, 不→唔, 们→哋, 了→咗, 那些→啲, 还→仲, 在→喺, 看→睇, 吃→食, 找→搵, 给→俾)

## Key sections
- Hero slideshow (4 slides)
- Featured articles
- HK Pet Map (#hkpemap, 14 outdoor places + 6 restaurant/mall/hotel via `morePlaces`)
- Knowledge (dogs/cats/small-pets)
- Laws, Health, Events

## Reminders
- API keys NEVER in source — GitHub Secrets only
- Article cards link to individual `article-*.html` for SEO
- TL agent monitors repo name; if conflict, use unique name
