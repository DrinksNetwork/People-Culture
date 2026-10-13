"""RepShare LinkedIn + Facebook campaign: carousels (PDF + square cards), single posts, link images.
Run: python3 campaign-assets/repshare-social/build.py  -> writes slides.html; then render with
node <scratchpad>/render-social.mjs (see README in this folder). Facts match emails/repshare-nurture/build.py."""
import html, os
HERE = os.path.dirname(os.path.abspath(__file__))
M = '../../public/media/'

CSS = """
:root{--red:#E42E2E;--red-dark:#B81F24;--navy:#1E2552;--paper:#FBF7F0;--sand:#F1E9DC;--pink:#FFE3E0;--body:#3A3631}
*{box-sizing:border-box;margin:0}
body{background:#666}
.s{position:relative;overflow:hidden;background:var(--paper);color:var(--navy);font-family:'Source Serif 4',Georgia,serif}
.sq{width:1080px;height:1080px}.ln{width:1200px;height:627px}
.navy{background:var(--navy);color:#fff}.red{background:var(--red);color:#fff}.sand{background:var(--sand)}
.bar{position:absolute;left:0;right:0;top:0;height:14px;background:var(--red)}
.navy .bar{background:var(--red)} .red .bar{background:var(--navy)}
.logo{position:absolute;left:72px;bottom:58px;height:62px}
.pg{position:absolute;right:72px;bottom:66px;font:700 26px 'Archivo Narrow';letter-spacing:4px;color:var(--red)}
.navy .pg,.red .pg{color:#fff}
.k{font:700 28px 'Archivo Narrow';letter-spacing:6px;text-transform:uppercase;color:var(--red)}
.red .k{color:#fff}.navy .k{color:#FF8A84}
.h{font:400 118px/.96 Anton,Impact,sans-serif;text-transform:uppercase;letter-spacing:.5px}
.h .a{color:var(--red)} .red .h .a{color:var(--navy)} .navy .h .a{color:#FF6B63}
.t{font:400 36px/1.38 'Source Serif 4',Georgia,serif;color:var(--body)}
.navy .t,.red .t{color:#fff}
.t,.fine,.list div,.stats span,.shelfcap,.ln .t{text-wrap:balance}.h{text-wrap:balance}
.pad{position:absolute;left:72px;right:72px;top:96px}
.shotw{position:absolute;left:48px;right:48px;bottom:132px;display:flex;justify-content:center;align-items:flex-start}.shotw img{display:block;max-width:100%;max-height:100%;object-fit:contain}
.shelf{position:absolute;left:72px;right:72px;bottom:150px;display:flex;align-items:flex-end;justify-content:space-around;gap:20px}
.shelf img{display:block;height:100%;width:auto;filter:drop-shadow(0 18px 18px rgba(17,17,17,.28))}.shelf img.disp{height:86%}
.shelfcap{position:absolute;left:72px;right:72px;bottom:104px;text-align:center;font:700 20px 'Archivo Narrow';letter-spacing:2px;text-transform:uppercase;color:#6b655c}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;margin-top:56px}
.stats b{display:block;font:400 104px/1 Anton,Impact,sans-serif;color:var(--red)}
.navy .stats b{color:#FF6B63}
.stats span{display:block;margin-top:12px;font:700 26px/1.3 'Archivo Narrow';letter-spacing:1.5px;text-transform:uppercase}
.list{margin-top:44px;display:grid;gap:26px}
.list div{display:grid;grid-template-columns:96px 1fr;align-items:baseline;font:400 36px/1.3 'Source Serif 4',Georgia,serif;color:var(--body)}
.navy .list div{color:#fff}
.list div b{font:400 64px/1 Anton,Impact,sans-serif;color:var(--red)}
.plans{margin-top:44px;display:grid;gap:18px}
.plans div{display:grid;grid-template-columns:1fr 200px 260px;align-items:center;background:#fff;border-radius:16px;padding:26px 32px;font:400 32px 'Source Serif 4',Georgia,serif;color:var(--body)}
.plans div b{font:400 48px Anton,Impact,sans-serif;color:var(--navy);text-transform:uppercase}
.plans div i{font-style:normal;font:400 52px Anton,Impact,sans-serif;color:var(--red);text-align:right}
.cta{display:inline-block;margin-top:46px;background:var(--red);color:#fff;font:700 34px 'Archivo Narrow';letter-spacing:3px;text-transform:uppercase;padding:26px 44px;border-radius:10px}
.red .cta{background:var(--navy)}
.url{margin-top:22px;font:700 30px 'Archivo Narrow';letter-spacing:1px}
.chips{display:flex;gap:18px;flex-wrap:wrap;margin-top:44px}
.chips span{background:#fff;color:var(--navy);border-radius:12px;padding:20px 30px;font:400 52px Anton,Impact,sans-serif;text-transform:uppercase}
.fine{position:absolute;left:72px;right:72px;bottom:150px;font:400 22px/1.4 'Source Serif 4',Georgia,serif;color:#6b655c}
.navy .fine{color:#C9CCE0}
.ln .pad{left:60px;right:620px;top:70px}.ln .h{font-size:76px}.ln .t{font-size:28px;margin-top:20px}
.ln .shot2{position:absolute;right:30px;top:90px;width:560px}
.herologo{position:absolute;left:50%;bottom:66px;width:420px;transform:translateX(-50%)}
.ln .logo{left:60px;bottom:40px;height:46px}.ln .pad{top:96px}
"""

LOGO_DARK = M + 'logos/drinks-network-script-red.png'
LOGO_LIGHT = M + 'logos/drinks-network-repshare-white.png'


def slide(id_, cls, inner, n=None, of=7, fine='', size='sq'):
    dark = any(c in cls for c in ('navy', 'red'))
    logo = LOGO_LIGHT if dark else LOGO_DARK
    small = '' if 'hero' in cls else f'<img class="logo" src="{logo}" alt="">'
    pg = f'<div class="pg">{n:02d} / {of:02d}</div>' if n else ''
    f = f'<div class="fine">{fine}</div>' if fine else ''
    return f'<div class="s {size} {cls}" id="{id_}"><div class="bar"></div>{inner}{f}{small}{pg}</div>'


def shot(img, top=360):
    return f'<div class="shotw" style="top:{top}px"><img src="scenes/{img.replace(".jpg", ".png")}" alt=""></div>'


SHELF = [('products/lady-trieu-gin.png', ''), ('products/nhau-vodka.png', ''), ('products/headlands-distilling.png', ''), ('tasting/headlands-muscat.png', ''), ('products/blvd-counter-display.png', 'disp')]


def shelf(h, cap='Lady Trieu · Nhau · Headlands · BLVD'):
    imgs = ''.join(f'<img class="{c}" src="{M}{f}" alt="">' for f, c in SHELF)
    return f'<div class="shelf" style="height:{h}px">{imgs}</div><p class="shelfcap">{cap}</p>'


def pad(k, h, t='', extra=''):
    tt = f'<p class="t" style="margin-top:30px">{t}</p>' if t else ''
    return f'<div class="pad"><p class="k">{k}</p><h1 class="h" style="margin-top:22px">{h}</h1>{tt}{extra}</div>'


HERO = f'<img class="herologo" src="{LOGO_LIGHT}" alt="Drinks Network RepShare">'
HERO_SM = f'<img class="herologo" style="width:340px;bottom:48px" src="{LOGO_LIGHT}" alt="Drinks Network RepShare">'
S = []
# ---------------- VENDOR carousel
v = 'vendor-carousel'
S += [
 slide(f'{v}-1', 'navy', pad('RepShare for drinks brands', 'A sales team<br><span class="a">on tap.</span>', 'Seasoned reps in venues and bottle shops, selling your brand.') + shot('dual-vendor-dashboard.jpg'), 1),
 slide(f'{v}-2', '', pad('How it works', '5 to 15 hours<br><span class="a">a week.</span>', 'Seasoned reps who already know the buyers in Sydney, Melbourne and Brisbane.',
       '<div class="chips"><span>No salaries</span><span>No lock-ins</span></div>') + shelf(215, 'Brands on RepShare include Lady Trieu · Nhau · Headlands · BLVD'), 2),
 slide(f'{v}-3', 'sand', pad('Circuits', 'Pick the venues.<br><span class="a">Attach an offer.</span>') + '<div class="shotw" style="top:380px;bottom:196px"><img src="scenes/journey-map.png" alt=""></div><p class="shelfcap" style="bottom:128px;text-transform:none;letter-spacing:0;font:400 24px/1.3 Source Serif 4,Georgia,serif;color:#3A3631">Start from 31,000+ licensed venues and narrow by suburb, type and distance.</p>', 3),
 slide(f'{v}-4', '', pad('Every hour accounted for', 'Logged.<br><span class="a">Approved.</span>',
       extra='<div class="list"><div><b>30</b>Minutes for a standard venue visit</div><div><b>2</b>Charges before a first order. A third is held for review.</div><div><b>15</b>Minute blocks for every hour charged</div></div>'), 4),
 slide(f'{v}-5', 'sand', pad('Orders', 'Four ways<br><span class="a">to order.</span>', '', '<div class="chips"><span>ALM</span><span>Paramount</span><span>ILG</span><span>Direct</span></div>') + shot('dual-orders.jpg'), 5),
 slide(f'{v}-6', '', pad('Plans', 'From $2,695<br><span class="a">a month.</span>', '',
       '<div class="plans"><div><b>Kickstart</b>5 hrs/wk<i>$2,695</i></div><div><b>Roll Out</b>10 hrs/wk<i>$4,180</i></div><div><b>Take Over</b>15 hrs/wk<i>$5,610</i></div></div>'), 6,
       fine='Per month, inc GST. Cars, phones, tolls and parking included. Campaigner plans for 25+ hours are priced with you.'),
 slide(f'{v}-7', 'red hero', pad('Start here', '$500 off<br><span class="a">your first month.</span>', 'Plus a 30-day pro-rata money-back guarantee. We call you within one business day.',
       '<div class="cta">Start with RepShare</div><p class="url">site.drinksnetwork.com.au/start</p>') + HERO, 7),
]
# ---------------- REP carousel
r = 'rep-carousel'
S += [
 slide(f'{r}-1', 'navy', pad('RepShare reps', 'Sell what you love.<br><span class="a">On your hours.</span>', 'For bartenders, brand ambassadors<br>and reps already selling.') + shot('dual-splash.jpg'), 1),
 slide(f'{r}-2', '', pad('Pay', '$47.50 to $70<br><span class="a">an hour.</span>', 'Field rates for 5 to 15 hours a week, paid in 3 to 7 days, plus 5% on any single order over $1,000.') + shot('payout.png'), 2),
 slide(f'{r}-3', 'sand', pad('The app', 'Four taps.<br><span class="a">Visit to charge.</span>', 'Open Jobs. Tap Charges. Pick the template. Add notes and save.') + shot('four-taps.jpg'), 3),
 slide(f'{r}-4', '', pad('The work', 'Work the circuit.<br><span class="a">Win the order.</span>') + '<div class="shotw" style="top:380px;bottom:196px"><img src="scenes/journey-map.png" alt=""></div><p class="shelfcap" style="bottom:128px;text-transform:none;letter-spacing:0;font:400 24px/1.3 Source Serif 4,Georgia,serif;color:#3A3631">Brands pick venues from 31,000+. Each one becomes a job in your app. Accept the ones you want.</p>', 4),
 slide(f'{r}-5', 'sand', pad('What you do', 'Four kinds<br><span class="a">of job.</span>', '', '<div class="list"><div><b>01</b>Tastings</div><div><b>02</b>Account sales, processed through the wholesaler</div><div><b>03</b>Activations</div><div><b>04</b>Social content</div></div>'), 5),
 slide(f'{r}-6', '', pad('What you need', 'An ABN.<br><span class="a">An RSA. A phone.</span>', 'RepShare is a web app, so there is nothing to download. You work as an independent contractor.'), 6),
 slide(f'{r}-7', 'red hero', pad('Apply', 'Three minutes<br><span class="a">to apply.</span>', 'Pick your city and tell us who you know. 24 hours of onboarding, then jobs land in your app.',
       '<div class="cta">Become a rep</div><p class="url">site.drinksnetwork.com.au/reps</p>') + HERO, 7),
]
# ---------------- PARTNER carousel
pt = 'partner-carousel'
S += [
 slide(f'{pt}-1', 'navy', pad('RepShare partners', 'Take RepShare<br><span class="a">into your market.</span>', 'For agencies, distributors, tech resellers, venue groups and overseas markets.') + shot('dual-splash.jpg'), 1),
 slide(f'{pt}-2', '', pad('The network', 'Already<br><span class="a">in the field.</span>', '', '<div class="stats"><div><b>31K+</b><span>Licensed venues</span></div><div><b>3</b><span>States: QLD, NSW, VIC</span></div><div><b>20</b><span>Reps across BNE, SYD, MEL</span></div></div>'), 2),
 slide(f'{pt}-3', 'sand', pad('The track record', 'The work<br><span class="a">so far.</span>', '', '<div class="stats"><div><b>1,800+</b><span>Field activities</span></div><div><b>20+</b><span>Suppliers onboarded</span></div><div><b>30%+</b><span>Conversion on field sales calls</span></div></div>') + shelf(260, 'Suppliers include Lady Trieu · Nhau · Headlands · BLVD'), 3),
 slide(f'{pt}-4', '', pad('Targeting', 'Circuits,<br><span class="a">not spreadsheets.</span>') + '<div class="shotw" style="top:380px;bottom:196px"><img src="scenes/journey-map.png" alt=""></div><p class="shelfcap" style="bottom:128px;text-transform:none;letter-spacing:0;font:400 24px/1.3 Source Serif 4,Georgia,serif;color:#3A3631">Pick venues from 31,000+, attach an offer, hand it to reps as jobs.</p>', 4),
 slide(f'{pt}-5', 'sand', pad('Control', 'Every hour,<br><span class="a">approved.</span>', 'Timers, charge templates, approvals and funded hours by rep.') + shot('dual-funded-hours.jpg'), 5),
 slide(f'{pt}-6', '', pad('Orders', 'Four ways.<br><span class="a">One dashboard.</span>', '', '<div class="chips"><span>ALM</span><span>Paramount</span><span>ILG</span><span>Direct</span></div>') + shot('laptop-vendor-dashboard.jpg'), 6),
 slide(f'{pt}-7', 'red hero', pad('Next step', 'Map your<br><span class="a">territory.</span>') + '<div class="shotw" style="top:392px;bottom:250px"><img src="scenes/territory-map.png" alt=""></div><p class="url" style="position:absolute;left:72px;right:72px;bottom:196px;margin:0;text-align:center;white-space:nowrap">Book a short call · site.drinksnetwork.com.au/start?role=partner</p>' + HERO_SM, 7),
]
# ---------------- single posts (square)
S += [
 slide('post-vendor-1', 'navy', pad('RepShare for drinks brands', 'Excise goes up<br><span class="a">every six months.</span>', 'Margins feel it first. Add a sales team from 5 hours a week, with no salaries and no lock-ins.') + shot('dual-vendor-dashboard.jpg')),
 slide('post-vendor-2', '', pad('Launch campaign', 'First 10 visits.<br><span class="a">Before day one.</span>') + '<div class="shotw" style="top:380px;bottom:196px"><img src="scenes/journey-map.png" alt=""></div><p class="shelfcap" style="bottom:128px;text-transform:none;letter-spacing:0;font:400 24px/1.3 Source Serif 4,Georgia,serif;color:#3A3631">Every plan starts with wholesaling, targeting and strategy in your first 30 days, with a typical 20–30% conversion.</p>'),
 slide('post-vendor-3', 'red', pad('Offer', '$500 off<br><span class="a">your first month.</span>', 'Plans from $2,695 a month inc GST, with a 30-day pro-rata money-back guarantee.',
       '<div class="cta">Start here</div><p class="url">site.drinksnetwork.com.au/brands</p>')),
 slide('post-rep-1', 'navy', pad('RepShare reps', '$47.50 to $70<br><span class="a">an hour.</span>', '5 to 15 hours a week, in venues and bottle shops you already know.') + shot('payout-red.png')),
 slide('post-rep-2', '', pad('Payouts', 'Cash out.<br><span class="a">Paid in days.</span>', 'Payouts in 3 to 7 days, and you’re paid for approved work even if the brand hasn’t paid us yet.') + shot('payout.png')),
 slide('post-rep-3', 'sand', pad('The app', 'Four taps.<br><span class="a">Visit to charge.</span>') + shot('four-taps.jpg')),
 slide('post-partner-1', 'navy', pad('RepShare partners', '31,000+ venues.<br><span class="a">3 states.</span>', 'Take the RepShare tech and network into your market or business.') + shot('laptop-circuit-search.jpg')),
 slide('post-partner-2', '', pad('Orders', 'Four ways.<br><span class="a">One dashboard.</span>', 'ALM, Paramount, ILG or direct, reported to the brand 24/7.') + shot('dual-orders.jpg')),
 slide('post-partner-3', 'red hero', pad('Next step', 'Map your<br><span class="a">territory.</span>') + '<div class="shotw" style="top:392px;bottom:250px"><img src="scenes/territory-map.png" alt=""></div><p class="url" style="position:absolute;left:72px;right:72px;bottom:196px;margin:0;text-align:center;white-space:nowrap">Book a short call · site.drinksnetwork.com.au/start?role=partner</p>' + HERO_SM),
]
S += [
 slide('post-vendor-4', 'sand', pad('On RepShare', 'Brands that<br><span class="a">already sell.</span>', 'Gin, vodka, Australian whisky and fortifieds, and ready-to-pour cocktails, in venues and bottle shops now.') + shelf(400)),
 slide('post-rep-4', '', pad('RepShare reps', 'Carry brands<br><span class="a">worth pouring.</span>', 'Take brands like Lady Trieu, Nhau, Headlands and BLVD into the venues you already know.') + shelf(400, 'Apply at site.drinksnetwork.com.au/reps')),
]
# ---------------- link images (1200x627)
for key, h1, t, img in [('vendor', 'A sales team<br><span class="a">on tap.</span>', '5 to 15 hours a week. No salaries. No lock-ins.', 'dual-vendor-dashboard.jpg'),
                        ('rep', 'Sell what you love.<br><span class="a">On your hours.</span>', '$47.50 to $70 an hour, paid in days.', 'payout-red.jpg'),
                        ('partner', 'Take RepShare<br><span class="a">into your market.</span>', '31,000+ licensed venues across 3 states.', 'dual-splash.jpg')]:
    S.append(slide(f'link-{key}', 'navy', f'<div class="pad"><h1 class="h">{h1}</h1><p class="t">{t}</p></div><img class="shot2" src="scenes/{img.replace('.jpg', '.png')}" alt="">', size='ln'))

with open(os.path.join(HERE, 'slides.html'), 'w') as f:
    f.write('<!doctype html><html><head><meta charset="utf-8"><style>' + CSS + '</style></head><body>' + '\n'.join(S) + '<script>document.querySelectorAll(".s").forEach(function(sl){var p=sl.querySelector(".pad"),w=sl.querySelectorAll(".shotw");if(!p)return;var pb=p.getBoundingClientRect().bottom-sl.getBoundingClientRect().top;w.forEach(function(x){var t=parseFloat(x.style.top)||0;if(t<pb+28)x.style.top=(pb+28)+"px";});});</script></body></html>')
print(len(S), 'slides')
