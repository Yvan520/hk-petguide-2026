import { readFileSync, writeFileSync, mkdirSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const distDir = resolve(__dirname, "../dist/news");
const publicDir = resolve(__dirname, "../public/news");
const sitemapPath = resolve(__dirname, "../sitemap.xml");
const siteUrl = "https://berty.gamewayz.com";

const articles = [
  {
    id: "talandre-expansion", title: "Talandre 资料片上线 — 等级上限提升至55",
    date: "2026-03-06", author: "TL攻略站",
    icon: "🏔️",
    content: `<p>3月6日，Throne and Liberty 迎来了迄今为止最大的更新 —— Wilds of Talandre。</p>
<p>本次更新将等级上限提升至55级，新增Talandre广阔地图区域，并引入了全新的武器精通系统（Weapon Mastery），彻底改变了原有的技能搭配方式。</p>
<h2>新增内容</h2>
<ul>
<li>新地图区域：Talandre 荒野，包含多个全新副本入口和野外首领刷新点</li>
<li>装备等级扩展：新增 Epic Lv.2 装备，包含世界树套装等多套新装备</li>
<li>武器精通系统：每把武器独立的精通树，提供被动加成和技能特化选择</li>
<li>新增4星副本：Crypt of Augmentation，需要战力5000+进入</li>
<li>新增耳环装备栏位：所有角色自动解锁</li>
<li>位置攻击系统：从侧面/背面攻击获得额外伤害加成</li>
</ul>
<p>同时引入 Interserver Siege 跨服攻城战，每3周一次，城堡所有者可跨服对战。</p>`,
  },
  {
    id: "update-331", title: "更新 3.31.0 — 战场调整 & 武器平衡",
    date: "2026-04-22", author: "TL攻略站",
    icon: "📋",
    content: `<p>4月22日的 3.31.0 更新主要聚焦战场和武器平衡。</p>
<h2>战场改动</h2>
<ul>
<li>移除战场中的角色分工效果（坦克/打手/补师）</li>
<li>浮空精灵花园：胜利分从150k降至120k，占领分从200提升至500</li>
<li>移除锻造能量得分，仅交付锻造能量才得分</li>
</ul>
<h2>武器修复</h2>
<ul>
<li>短剑「暗影精灵」技能修复：效果结束后战斗状态不结束的问题</li>
<li>长矛「丧钟」修复：PVP触发概率从15%提升至30%，PVE从30%降至15%</li>
</ul>
<h2>其他</h2>
<ul>
<li>Lucien's Code of the Heretic 装备效果限制为每秒最多10次</li>
<li>修复多个月光石让角色穿模的问题</li>
<li>装备/属性预设切换现在会有技能冷却</li>
</ul>`,
  },
  {
    id: "new-dungeon-crypt", title: "新4星副本：Crypt of Augmentation 攻略要点",
    date: "2026-03-15", author: "TL攻略站",
    icon: "💀",
    content: `<p>Crypt of Augmentation 是 Talandre 更新中新增的4星副本，最终Boss为死灵法师 Velentra。</p>
<p>副本要求战力5000+，推荐队伍配置：1坦+1补+2输出。</p>
<h2>Boss机制要点</h2>
<ul>
<li>Velentra 会召唤多个亡灵小兵，需要坦克快速聚怪</li>
<li>阶段转换时场地会出现黑暗法阵，站在法阵内会持续掉血</li>
<li>Boss 会施放「灵魂吸取」技能，需要补师及时驱散</li>
<li>50%血量以下进入P2，Boss会释放全屏AOE，需要躲到柱子后面</li>
</ul>
<h2>掉落物</h2>
<ul>
<li>T2 史诗装备（头盔、胸甲、手套等）</li>
<li>高磨结晶</li>
<li>混沌符文</li>
</ul>
<h2>速通技巧</h2>
<ul>
<li>带净化技能解除Boss的诅咒DOT</li>
<li>坦克保持Boss背对团队</li>
<li>输出在P2阶段注意柱子位置</li>
</ul>`,
  },
  {
    id: "invasion-event", title: "Arkeum 入侵活动 — 限时奖励 & 日程",
    date: "2026-01-15", author: "TL攻略站",
    icon: "⚔️",
    content: `<p>1月15日起，Arkeum Legion 入侵活动正式上线，持续至1月28日。</p>
<p>活动期间，Arkeum 侵略者会在多个区域定时出现，玩家需要组队击退他们。</p>
<h2>活动日程</h2>
<ul>
<li>工作日每天3场</li>
<li>周末每天4场</li>
<li>覆盖多个地图区域</li>
</ul>
<h2>限时奖励</h2>
<ul>
<li>全新表情动作</li>
<li>变形形态（Shapeshift Morph）</li>
<li>混沌棱晶（Chaos Prisms）</li>
</ul>
<h2>平衡调整</h2>
<ul>
<li>多个生成额外弹道的技能不再叠加增伤</li>
<li>弩弓技能全面调整</li>
<li>装备技能减伤效果翻倍</li>
<li>战场弱势方增益效果增强（分差越大增益越强）</li>
<li>新增家具和游戏设置选项</li>
</ul>`,
  },
  {
    id: "server-merge", title: "亚服服务器合并 & 新手追赶机制",
    date: "2026-05-10", author: "TL攻略站",
    icon: "🔄",
    content: `<p>NCsoft 宣布亚服服务器合并计划，旨在整合低人口服务器，提升玩家体验。</p>
<h2>服务器合并安排</h2>
<ul>
<li>多个低活跃服务器合并为更少的活跃服务器</li>
<li>角色数据、公会数据、仓库物品完整保留</li>
<li>合并期间短暂维护</li>
</ul>
<h2>新手追赶机制</h2>
<ul>
<li>新增「世界树的引导」系统，新手可获得整套装备</li>
<li>1阶段：高级→稀有→英雄1→英雄2装备逐步解锁</li>
<li>战力5000+玩家获得转换石/萃取石</li>
<li>2阶段获得项链</li>
<li>1-5阶段逐步解锁重要物品</li>
</ul>
<h2>亚服专属快速成长箱</h2>
<ul>
<li>含整套英雄装备</li>
<li>技能成长书</li>
<li>人工制品</li>
<li>符文</li>
</ul>`,
  },
  {
    id: "nebula-island", title: "星云岛激战场全面指南 — 跨服PVE/PVP",
    date: "2026-05-20", author: "TL攻略站",
    icon: "🌌",
    content: `<p>星云岛激战场（Nebula Island）是跨服务器共同游玩的混合PVE/PVP区域。</p>
<h2>入场</h2>
<ul>
<li>每周基本5小时（可用星云充能石增加）</li>
<li>中立区：抵抗军探查基地（安全区）</li>
<li>PVE区：迷雾森林（PVE刷怪）</li>
<li>PVP区：亚奇恩驻地/兽人部落/牺牲寺院/被封印圣所</li>
</ul>
<h2>活动时间</h2>
<ul>
<li>每地区不定时整点出现野外首领</li>
<li>每天1场活动+1场星云岛首领</li>
<li>周日2场首领皆为公会模式</li>
</ul>
<h2>奖励</h2>
<ul>
<li>星云石</li>
<li>符文</li>
<li>人工制品</li>
<li>星云饰品</li>
</ul>
<h2>注意事项</h2>
<ul>
<li>PVP区注意敌对公会偷袭</li>
<li>星云充能石可增加入场时间</li>
<li>建议组队前往PVP区</li>
</ul>`,
  },
  {
    id: "summer-event-2026", title: "2026夏日活动「幻象回廊」限时开启",
    date: "2026-05-28", author: "TL攻略站",
    icon: "🏖️",
    content: `<p>5月28日，2026夏日活动「幻象回廊」正式上线！</p>
<p>幻象回廊为限时隐藏地图，需要通过神秘环球随机进入。</p>
<h2>活动亮点</h2>
<ul>
<li>新增8种幻象鱼，可兑换限定外观</li>
<li>隐藏地图「凯洛斯幻象回廊」开放，内含稀有宝箱</li>
<li>限定夏日外观套装</li>
<li>活动期间钓鱼经验+50%</li>
<li>特殊钓点刷新频率提升</li>
</ul>
<h2>参与方式</h2>
<ul>
<li>每日使用神秘环球钥匙开启环球</li>
<li>有概率触发幻象回廊入口</li>
<li>进入后限时探索，采集特殊资源和鱼点</li>
</ul>
<p>本次夏日活动将持续至6月25日。</p>`,
  },
  {
    id: "new-map-nix", title: "冰封边界：尼克斯 — TL史上最大更新 亚服6/23·国际服6/25",
    date: "2026-05-25", author: "TL攻略站",
    icon: "❄️",
    content: `<p>6月，Throne and Liberty 将迎来史上最大规模更新——「冰封边界：尼克斯」（The Frozen Divide: Nix）。</p>
<p><strong>亚服上线日期：2026年6月23日</strong><br><strong>国际服上线日期：2026年6月25日</strong></p>
<h2>新地图「尼克斯」</h2>
<ul>
<li>TL 迄今为止最大的区域，极寒冰原主题</li>
<li>新增「天刺」俯冲滑翔和「米里奈」空中快速穿梭两种特殊移动机制</li>
<li>冰封遗迹、扭曲时空裂缝、红色迷雾等全新探索元素</li>
<li>新增定居点和交通工具</li>
</ul>
<h2>全新武器「拳套」</h2>
<ul>
<li>坦克/输出混合型近战武器</li>
<li>双姿态切换系统：重击姿态（高防御+压倒性打击）和利爪姿态（高机动+快速连击）</li>
<li>融合生存能力、攻击性和卓越机动性</li>
</ul>
<h2>等级上限提升至60级</h2>
<ul>
<li>全新装备等级和成长系统改革</li>
<li>新增两个合作副本（各自有全新首领和机制）</li>
<li>挑战模式（Challenge Mode）新增</li>
<li>世界树引导功能进一步完善</li>
<li>房屋和生活内容便利性大幅提升</li>
</ul>
<h2>装备系统重大革新</h2>
<ul>
<li>道具系统全面改革，冒险者更自由选择装备升级路线</li>
<li>角色构建自定义范围进一步拓展</li>
<li>高难内容顶级奖励更有意义</li>
<li>降低成长门槛的便利性更新</li>
</ul>
<h2>前瞻预告</h2>
<ul>
<li>5/25当周：尼克斯地区新巨型威胁和首领预览</li>
<li>6/1当周：全新PVP内容预览</li>
<li>6/8当周：拳套武器深入分析</li>
<li>6/15当周：合辑影片发布</li>
</ul>`,
  },
  {
    id: "star-journey", title: "「星之旅程」系统上线 — 累积成长型内容",
    date: "2026-05-12", author: "TL攻略站",
    icon: "⭐",
    content: `<p>5月12日亚服更新新增了累积成长型内容——「星之旅程」系统。</p>
<p>星之旅程将原本分散的内容整合起来，玩家在游戏中的行动将直接转化为角色的成长。</p>
<h2>核心机制</h2>
<ul>
<li>完成「冒险宝典」→「序章」→「序幕.拥有星星的孩子」后解锁</li>
<li>在冒险宝典、探查宝典、时空痕迹等内容中可获得「星之记忆」</li>
<li>每个星之记忆都会永久提升能力值</li>
<li>星之记忆在获得时会自动使用</li>
</ul>
<h2>时空痕迹</h2>
<ul>
<li>各领地新增时空奇异点和文物垂钓名胜</li>
<li>点击时空奇异点传送门进入后可完成目标获得星之记忆</li>
<li>文物垂钓名胜可在该地点通过钓鱼获得星之记忆</li>
<li>星之旅程—时空痕迹达成100%后，每天出现2个随机时空奇异点和1个文物垂钓名胜</li>
<li>完成每个目标后可获得特级抵抗军勋章</li>
</ul>
<h2>冒险宝典/探查宝典改善</h2>
<ul>
<li>UI改版，更容易了解当前进度</li>
<li>冒险宝典加入阶段细分（第1章/第2章/间幕）</li>
<li>探查宝典适配每个领地和区域地图</li>
<li>希雷乌斯深渊探查宝典整合为统一界面</li>
</ul>
<h2>竞技场第6赛季 &amp; 战场第1赛季</h2>
<ul>
<li>新增基于排名的荣誉奖励</li>
<li>新增3个战场奖杯（金/银/铜）可在工坊制作</li>
<li>赫乐巴村庄英勇广场新增顶级玩家雕像</li>
<li>新增战场铸币商人、星云石商人等NPC</li>
</ul>`,
  },
  {
    id: "summer-roadmap-2026", title: "尼克斯之后：7-8月更新路线图 — 龙骑士·泰拉首领·新战场",
    date: "2026-05-25", author: "TL攻略站",
    icon: "🗓️",
    content: `<p>NCsoft 在尼克斯前瞻中同步公布了6月上线之后的更新路线图。</p>
<h2>7月更新</h2>
<ul>
<li>新篇章首领「龙骑士拉姆斯」登场</li>
<li>新增拉姆斯相关支线故事集</li>
<li>全新增强力的弧形Boss拉姆斯装备</li>
<li>与大法师相关的法典内容和强大的大法师装备</li>
<li>合作副本「铁矿石摇篮」与「霜息洞穴」</li>
<li>挑战次元阵开放</li>
<li>全新战场模式「密封战斗」，包含新规则、目标和全新战场地图</li>
</ul>
<h2>8月更新</h2>
<ul>
<li>TL 中出现空前巨大的「泰拉首领」</li>
<li>新增与泰拉首领相关的支线故事法典</li>
<li>新增与泰拉首领遭遇战相关的强大首领装备</li>
<li>改进岩石镇攻城和税收运输体验</li>
</ul>
<p>此外，亚服将于6月2日进行服务器整合，解决人口不平衡问题。</p>`,
  },
  {
    id: "update-3-37-0-mq0wgpt7", title: "更新 3.37.0",
    date: "2026-06-03", author: "TL攻略站",
    icon: "📋",
    content: `<p>2026-06-03，来自Throne and Liberty 官方新闻的消息。</p>
<p>近日，Throne and Liberty 更新 3.37.0 downtime will begin at 10:30 p.m. PT (5:30 a.m. UTC) on June 3rd and last approximately 3 hours. TL攻略站将持续关注后续更新动态，第一时间为玩家带来详细解读。</p>
<hr />
<p style="color:#6a5a4a;font-size:13px">来源：<a href="https://www.playthroneandliberty.com/en-US/news/articles/update-3-37-0" style="color:#c9a227" target="_blank" rel="noopener">Throne and Liberty 官方新闻</a> · TL攻略站编译整理</p>`,
  },
];

function buildPage(article) {
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${article.title} — 王权与自由 TL攻略站</title>
  <meta name="description" content="${article.title} - 王权与自由 Throne and Liberty 最新资讯和攻略" />
  <meta name="keywords" content="王权与自由, Throne and Liberty, TL, 攻略, ${article.title}" />
  <meta property="og:title" content="${article.title} — 王权与自由 TL攻略站" />
  <meta property="og:description" content="王权与自由 Throne and Liberty 最新资讯" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="${siteUrl}/news/${article.id}.html" />
  <link rel="canonical" href="${siteUrl}/news/${article.id}.html" />
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Noto Sans SC", "Segoe UI", sans-serif;
      background: #0a0a12; color: #c0b090; line-height: 1.8;
    }
    .container { max-width: 800px; margin: 0 auto; padding: 40px 20px; }
    .back {
      display: inline-flex; align-items: center; gap: 6px;
      color: #c9a227; text-decoration: none; font-size: 14px; margin-bottom: 30px;
    }
    .back:hover { opacity: 0.8; }
    .tag {
      display: inline-block; padding: 4px 12px; border-radius: 20px;
      font-size: 12px; background: rgba(201,162,39,0.1); color: #c9a227;
      border: 1px solid rgba(201,162,39,0.2); margin-bottom: 16px;
    }
    h1 {
      font-size: 28px; color: #fff; margin-bottom: 12px; line-height: 1.4;
    }
    .meta { color: #6a5a4a; font-size: 13px; margin-bottom: 30px; }
    .content h2 {
      font-size: 20px; color: #d0b890; margin: 28px 0 12px; padding-bottom: 6px;
      border-bottom: 1px solid rgba(201,162,39,0.15);
    }
    .content p { margin-bottom: 14px; }
    .content ul { padding-left: 20px; margin-bottom: 14px; }
    .content li { margin-bottom: 6px; }
    hr { border: none; border-top: 1px solid rgba(201,162,39,0.1); margin: 40px 0; }
    .footer-link {
      text-align: center; color: #6a5a4a; font-size: 13px;
    }
    .footer-link a { color: #c9a227; text-decoration: none; }
    .footer-link a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <div class="container">
    <a class="back" href="${siteUrl}">← 返回 TL攻略站 首页</a>
    <div class="tag">${article.icon} ${article.date}</div>
    <h1>${article.title}</h1>
    <div class="meta">${article.date} · ${article.author}</div>
    <div class="content">${article.content}</div>
    <hr />
    <div class="footer-link">
      <a href="${siteUrl}">王权与自由 · TL攻略站</a> — 最全面的 Throne and Liberty 游戏指南
    </div>
  </div>
</body>
</html>`;
}

function generateSitemap() {
  const urls = articles.map((a) => {
    return `  <url>
    <loc>${siteUrl}/news/${a.id}.html</loc>
    <lastmod>${a.date}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>`;
  }).join("\n");
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>${siteUrl}/</loc>
    <lastmod>${new Date().toISOString().slice(0, 10)}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
${urls}
</urlset>
`;
  writeFileSync(sitemapPath, xml, "utf-8");
  console.log("  ✓ sitemap.xml updated");
}

function main() {
  mkdirSync(publicDir, { recursive: true });
  articles.forEach((a) => {
    const html = buildPage(a);
    writeFileSync(resolve(publicDir, `${a.id}.html`), html, "utf-8");
    console.log(`  ✓ news/${a.id}.html`);
  });
  generateSitemap();
}

main();
