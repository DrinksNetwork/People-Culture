"""Sign-up social content for the event programs: Bar Takeover (venues, brands, bartenders) and the
Tasting Series (venues, brands). Carousels (5 cards each, PDF for LinkedIn), one single post and one link image per audience.
Run: python3 campaign-assets/event-social/build.py -> slides.html, then render (see CAPTIONS.md).
Every figure matches emails/event-programs/build.py."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'emails', 'event-programs'))
import build as E  # noqa: E402  (the shared numbers)

M = '../../public/media/'
money = E.money

CSS = """
:root{--red:#E42E2E;--red-dark:#B81F24;--navy:#1E2552;--paper:#FBF7F0;--sand:#F1E9DC;--orange:#C9500A;--green:#1F9D55;--body:#3A3631}
*{box-sizing:border-box;margin:0}
body{background:#666}
.s{position:relative;overflow:hidden;background:var(--paper);color:var(--navy);font-family:'Source Serif 4',Georgia,serif}
.sq{width:1080px;height:1080px}.ln{width:1200px;height:627px}
.navy{background:var(--navy);color:#fff}.red{background:var(--red);color:#fff}.sand{background:var(--sand)}.ink{background:#111;color:#fff}
.bar{position:absolute;left:0;right:0;top:0;height:14px;background:var(--red);z-index:3}.red .bar{background:var(--navy)}
.photo{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(17,17,17,.15) 0%,rgba(17,17,17,.25) 40%,rgba(17,17,17,.9) 78%)}
.pad{position:absolute;left:72px;right:72px;top:96px;z-index:2}
.bottom{top:auto;bottom:170px}
.k{font:700 28px 'Archivo Narrow';letter-spacing:6px;text-transform:uppercase;color:var(--red)}
.ink .k,.navy .k{color:#FF8A84}.red .k{color:#FFE3E0}
.h{font:400 112px/.94 Anton,Impact,sans-serif;text-transform:uppercase;text-wrap:balance;margin-top:16px}
.h .a{color:var(--red)}.ink .h .a,.navy .h .a{color:#FF6B63}.red .h .a{color:var(--navy)}
.t{font:400 36px/1.38 'Source Serif 4',Georgia,serif;color:var(--body);margin-top:24px;text-wrap:balance}
.ink .t,.navy .t,.red .t{color:#fff}
.logo{position:absolute;left:72px;bottom:58px;height:60px;z-index:3}
.pg{position:absolute;right:72px;bottom:66px;font:700 26px 'Archivo Narrow';letter-spacing:4px;color:var(--red);z-index:3}
.ink .pg,.navy .pg,.red .pg{color:#fff}
.tag{position:absolute;right:72px;top:46px;z-index:3;font:700 22px 'Archivo Narrow';letter-spacing:4px;text-transform:uppercase;background:var(--red);color:#fff;padding:12px 18px;border-radius:8px}
.red .tag{background:var(--navy)}
.blocks{margin-top:44px;display:grid;gap:22px}
.blk b{display:block;font:400 64px/1 Anton,Impact,sans-serif;color:#fff;border-radius:12px;padding:20px 26px}
.blk span{display:block;margin-top:10px;font:700 24px/1.3 'Archivo Narrow';letter-spacing:1.5px;text-transform:uppercase;color:var(--navy)}
.navy .blk span,.ink .blk span{color:#fff}
.total{display:flex;justify-content:space-between;align-items:baseline;border-top:5px solid var(--navy);padding-top:18px;margin-top:6px;font:700 26px 'Archivo Narrow';letter-spacing:2px;text-transform:uppercase}
.total i{font-style:normal;font:400 84px/1 Anton,Impact,sans-serif;color:var(--red)}
.fine{position:absolute;left:72px;right:72px;bottom:140px;font:400 22px/1.4 'Source Serif 4',Georgia,serif;color:#6b655c;z-index:2}
.stats{display:grid;gap:22px;margin-top:50px}
.stats.c3{grid-template-columns:repeat(3,1fr)}.stats.c2{grid-template-columns:repeat(2,1fr)}
.stats div{background:#fff;border-radius:16px;padding:30px 26px}
.navy .stats div,.ink .stats div{background:rgba(255,255,255,.08)}
.stats b{display:block;font:400 92px/1 Anton,Impact,sans-serif;color:var(--red)}
.navy .stats b,.ink .stats b{color:#FF6B63}
.stats span{display:block;margin-top:12px;font:700 25px/1.3 'Archivo Narrow';letter-spacing:1.5px;text-transform:uppercase}
.list{margin-top:44px;display:grid;gap:24px}
.list div{display:grid;grid-template-columns:96px 1fr;align-items:baseline;font:400 34px/1.3 'Source Serif 4',Georgia,serif;color:var(--body)}
.navy .list div,.ink .list div{color:#fff}
.list b{font:400 60px/1 Anton,Impact,sans-serif;color:var(--red)}
.list strong{font:700 34px 'Archivo Narrow';letter-spacing:1px;text-transform:uppercase;color:var(--navy)}
.navy .list strong,.ink .list strong{color:#fff}
.cta{display:inline-block;margin-top:40px;background:var(--red);color:#fff;font:700 34px 'Archivo Narrow';letter-spacing:3px;text-transform:uppercase;padding:26px 44px;border-radius:10px}
.red .cta{background:#fff;color:var(--red)}
.url{margin-top:22px;font:700 30px 'Archivo Narrow';letter-spacing:1px}
.window{display:flex;gap:8px;margin-top:40px}
.window span{flex:1;text-align:center;padding:20px 0;border-radius:8px;font:700 24px 'Archivo Narrow';letter-spacing:2px;text-transform:uppercase;background:rgba(255,255,255,.18);color:#fff}
.window span.on{background:#fff;color:var(--red)}.window span.go{background:var(--green);color:#fff;flex:1.3}
.duo{position:absolute;left:72px;right:72px;bottom:150px;display:grid;grid-template-columns:1fr 1fr;gap:24px;height:380px;z-index:2}
.duo{grid-template-rows:380px}.duo img{width:100%;height:380px;min-height:0;object-fit:cover;border-radius:14px}
.shelf{position:absolute;left:72px;right:72px;bottom:150px;height:420px;display:flex;align-items:flex-end;justify-content:space-around;z-index:2}
.shelf img{height:100%;width:auto;max-width:24%;object-fit:contain;filter:drop-shadow(0 18px 18px rgba(0,0,0,.4))}
.shelf img.disp{height:72%}
.brandtile{align-self:flex-end;width:250px;height:300px;border-radius:18px;background:linear-gradient(160deg,#C9500A,#3D1829);display:flex;flex-direction:column;justify-content:flex-end;padding:26px;box-shadow:0 18px 30px rgba(0,0,0,.4)}.brandtile b{font:400 64px/1 Anton,Impact,sans-serif;text-transform:uppercase;color:#fff}.brandtile span{margin-top:10px;font:700 20px/1.3 'Archivo Narrow';letter-spacing:1.5px;text-transform:uppercase;color:#FFE3CF}
.shelfcap{position:absolute;left:72px;right:72px;bottom:110px;text-align:center;font:700 22px 'Archivo Narrow';letter-spacing:2px;text-transform:uppercase;color:#C9CCE0;z-index:2}
.tight .blocks{margin-top:26px;gap:12px}.tight .blk b{font-size:46px;padding:12px 22px}.tight .blk span{margin-top:6px;font-size:21px}.tight .total{padding-top:12px}.tight .total i{font-size:60px}
.stats.c3 b{font-size:78px;white-space:nowrap}
.k{text-shadow:0 2px 12px rgba(0,0,0,.25)}
.ln .pad{left:60px;right:560px;top:70px}.ln .h{font-size:74px}.ln .t{font-size:27px;margin-top:16px}
.ln .side{position:absolute;right:0;top:0;width:520px;height:100%;object-fit:cover}
.ln .logo{left:60px;bottom:40px;height:46px}
"""

DN_W = M + 'logos/drinks-network-script-white.png'
DN_R = M + 'logos/drinks-network-script-red.png'


def slide(id_, cls, inner, n=None, size='sq', tag=''):
    dark = any(c in cls for c in ('navy', 'red', 'ink'))
    logo = f'<img class="logo" src="{DN_W if dark else DN_R}" alt="">'
    pg = f'<div class="pg">{n:02d} / 05</div>' if n else ''
    tg = f'<div class="tag">{tag}</div>' if tag else ''
    return f'<div class="s {size} {cls}" id="{id_}"><div class="bar"></div>{tg}{inner}{logo}{pg}</div>'


def photo(src, pos='50% 50%'):
    return f'<img class="photo" src="{M}{src}" style="object-position:{pos}" alt=""><div class="shade"></div>'


def pad(k, h, t='', extra='', cls=''):
    tt = f'<p class="t">{t}</p>' if t else ''
    return f'<div class="pad {cls}"><p class="k">{k}</p><h1 class="h">{h}</h1>{tt}{extra}</div>'


def blocks(rows, total):
    mx = max(v for _, v, _ in rows)
    b = ''.join(f'<div class="blk"><b style="background:{c};width:{max(30, round(v / mx * 100))}%">{money(v)}</b><span>{l}</span></div>' for l, v, c in rows)
    return f'<div class="blocks">{b}<div class="total"><span>{total[0]}</span><i>{total[1]}</i></div></div>'


def stats(items, cols=3):
    return f'<div class="stats c{cols}">' + ''.join(f'<div><b>{n}</b><span>{l}</span></div>' for n, l in items) + '</div>'


def lst(rows):
    return '<div class="list">' + ''.join(f'<div><b>{i:02d}</b><span><strong>{a}</strong><br>{b}</span></div>' for i, (a, b) in enumerate(rows, 1)) + '</div>'


def window():
    return '<div class="window">' + ''.join(f'<span class="{"on" if i == 1 else ""}">Wk {i}</span>' for i in range(1, 7)) + '<span class="go">Day 60</span></div>'


TKV = money(E.TK_VENUE + E.TK_PLUSONE)
S = []
# ---------------- BAR TAKEOVER · VENUE
a, tag = 'takeover-venue', 'Bar Takeover · Venues'
S += [
 slide(f'{a}-1', 'ink', photo('takeover/full-bar-room.jpg', '50% 40%') + pad('Bar Takeover · Host venues', 'One night.<br>One guest.<br><span class="a">Your bar.</span>', 'A guest bartender, a cocktail brand and a ticketed crowd. We run the lot.', cls='bottom'), 1, tag=tag),
 slide(f'{a}-2', 'sand', pad('The money', f'${E.TK_PRICE} a ticket.<br><span class="a">Two cocktails.</span>', extra=blocks([
     (f'{E.TK_TICKETS} tickets, after Eventbrite fees', E.TK_VENUE, '#E42E2E'), ('The plus-one effect: friends buying two drinks', E.TK_PLUSONE, '#C9500A')], ('One night, example', TKV))), 2, tag=tag),
 slide(f'{a}-3', '', pad('Your side of it', 'Four things.<br><span class="a">That\'s it.</span>', extra=lst([
     ('Take the brand on', 'An opening order before the night.'), ('Buy the ingredients', 'From the mise en place list, two weeks out.'),
     ('Run it through', 'With the bartender, the day before.'), ('Host the shift', '6 pm to 10 pm, your licence, your rules.')])), 3, tag=tag),
 slide(f'{a}-4', 'navy', pad('The risk', 'Tickets sold.<br><span class="a">Bartender paid.</span>', 'The brand pays the guest. We run the tickets, artwork and posts. The stock stays on your shelf.') +
       f'<div class="duo"><img src="{M}takeover/cocktail-handoff.jpg" style="object-position:50% 40%"><img src="{M}legacy/Roy-Das-Cocktail-rotated.jpg"></div>', 4, tag=tag),
 slide(f'{a}-5', 'red', pad('6 weeks to lock a date', 'Put a guest<br><span class="a">behind your bar.</span>', 'Lock in within 6 weeks. Host inside 60 days.', window() + '<p class="cta">Get the takeover pack</p><p class="url">site.drinksnetwork.com.au/bar-takeover</p>'), 5, tag=tag),
]
# ---------------- BAR TAKEOVER · BRAND
a, tag = 'takeover-brand', 'Bar Takeover · Brands'
S += [
 slide(f'{a}-1', 'ink', photo('takeover/straining-a-martini.jpg', '45% 40%') + pad('Bar Takeover · Brands', 'Take your brand<br><span class="a">on tour.</span>', 'A guest bartender, a new venue and a room full of your drinks.', cls='bottom'), 1, tag=tag),
 slide(f'{a}-2', 'sand', pad('Why it works', 'Product alone<br><span class="a">isn\'t enough.</span>', extra=stats([('5–10%', 'Product only. 15% at best'), ('30%+', 'With an activity or a high-value offer'), ('50%+', 'When the offer and room are right')])), 2, tag=tag),
 slide(f'{a}-3', 'tight', pad('The investment', 'About $2,000.<br><span class="a">One new account.</span>', extra=blocks([
     ('Bartender fee, optional', 1000, '#C9500A'), ('Stipend', 500, '#E42E2E'), ('Flights and accommodation, at cost', 500, '#1E2552')], ('Typical outlay', '~$2,000'))), 3, tag=tag),
 slide(f'{a}-4', 'navy', pad('What you get', 'Your contacts.<br><span class="a">Your orders.</span>', extra=lst([
     ('A new venue account', 'The host takes your product on.'), ('Contacts, yours only', 'Ticket-holders and trade buyers.'),
     ('Trade on your tab', 'Reps bring buyers on the night.'), ('Six days of follow-up', 'Visits, offers and a report.')])), 4, tag=tag),
 slide(f'{a}-5', 'red', pad('Built into your plan', 'Your brand,<br><span class="a">on tour.</span>', 'Program hours come from Roll Out (10 hrs a week, one state) or Take Over (15 hrs a week, two states).', '<p class="cta">Get the takeover pack</p><p class="url">site.drinksnetwork.com.au/bar-takeover</p>'), 5, tag=tag),
]
# ---------------- BAR TAKEOVER · BARTENDER
a, tag = 'takeover-bartender', 'Bar Takeover · Bartenders'
S += [
 slide(f'{a}-1', 'ink', photo('takeover/bartender-leaning-in.jpg', '45% 35%') + pad('Bar Takeover · Bartenders', 'Your menu.<br><span class="a">Their bar.</span>', 'Get flown to a new city to take over a bar for a night.', cls='bottom'), 1, tag=tag),
 slide(f'{a}-2', 'sand', pad('What you get', 'Paid to<br><span class="a">take over.</span>', extra=stats([('$500', 'Stipend for the day'), ('$1,000', 'Fee, on some takeovers'), ('Flights', 'And accommodation, paid')])), 2, tag=tag),
 slide(f'{a}-3', '', pad('How it works', 'Two weeks out.<br><span class="a">Then showtime.</span>', extra=lst([
     ('Send your list', 'Menu and mise en place, two weeks out.'), ('Run it through', 'Meet the team the day before.'),
     ('Take over', '6 pm to 10 pm, a new city\'s bar.'), ('Meet the trade', 'Buyers on the brand\'s tab.')])), 3, tag=tag),
 slide(f'{a}-4', 'navy', pad('Brands that back bartenders', 'Spirits made<br><span class="a">to be mixed.</span>') +
       f'<div class="shelf"><img src="{M}products/lady-trieu-gin.png"><img src="{M}products/nhau-vodka.png"><img src="{M}products/barlei-orange-liqueur.png"><img src="{M}products/barlei-coffee-liqueur.png"></div><p class="shelfcap">Lady Triệu · Nhau · Barlei</p>', 4, tag=tag),
 slide(f'{a}-5', 'red', pad('Get on the list', 'Pitch a menu.<br><span class="a">Get picked.</span>', 'We keep you on the list until a brand wants you behind a new bar.', '<p class="cta">Join the list</p><p class="url">site.drinksnetwork.com.au/bar-takeover</p>'), 5, tag=tag),
]
# ---------------- TASTING SERIES · VENUE
a, tag = 'tasting-venue', 'Tasting Series · Venues'
S += [
 slide(f'{a}-1', 'ink', photo('tasting/hero.jpg', '50% 50%') + pad('Tasting Series · Host venues', 'Meet the people<br><span class="a">behind the brand.</span>', f'A ticketed distiller\'s tasting in your room. ${E.TS_PRICE}, five pours, two hours.', cls='bottom'), 1, tag=tag),
 slide(f'{a}-2', 'sand', pad('The money', 'Half the door.<br><span class="a">In cash.</span>', extra=blocks([
     (f'{E.TS_GUESTS} tickets at ${E.TS_PRICE}', E.TS_GROSS, '#1E2552'), ('Your 50%, after Eventbrite fees', E.TS_HALF, '#E42E2E')], ('Cash to your venue', money(E.TS_HALF))) ), 2, tag=tag),
 slide(f'{a}-3', '', pad('Your side of it', 'Your room.<br><span class="a">Their whisky.</span>', extra=lst([
     ('A main contact', 'Before and on the night.'), ('Space and service', 'Glassware, water, bar staff.'),
     ('Food', 'Snacks, or a food-inclusive ticket.'), ('Stock what you pour', 'An opening order, at wholesale.')])), 3, tag=tag),
 slide(f'{a}-4', 'navy', pad('We fill the room', 'Posters, ads,<br><span class="a">a full house.</span>') +
       f'<div class="duo"><img src="{M}photos/corowa-distillers-tasting-poster.jpg" style="object-fit:contain;background:#1E2552"><img src="{M}photos/headlands-whisky-night-poster.jpg" style="object-fit:contain;background:#1E2552"></div>', 4, tag=tag),
 slide(f'{a}-5', 'red', pad('6 weeks to lock a date', 'Host a<br><span class="a">tasting night.</span>', 'Lock in within 6 weeks. Host inside 60 days.', window() + '<p class="cta">Host a night</p><p class="url">site.drinksnetwork.com.au/whisky-adventure/venues</p>'), 5, tag=tag),
]
# ---------------- TASTING SERIES · BRAND
a, tag = 'tasting-brand', 'Tasting Series · Brands'
S += [
 slide(f'{a}-1', 'ink', photo('photos/corowa-pour-spirits-wall.jpg', '50% 50%') + pad('Tasting Series · Brands', 'Put the maker<br><span class="a">in the room.</span>', 'Ticketed tastings led by your distiller, in venues that stock you after.', cls='bottom'), 1, tag=tag),
 slide(f'{a}-2', 'sand', pad('Brand on tour', 'People buy<br><span class="a">from people.</span>', extra=stats([('5–10%', 'Product only'), ('30%+', 'With an activity'), (E.COROWA_CONVERSION, 'Corowa, touring its distiller')])), 2, tag=tag),
 slide(f'{a}-3', 'tight', pad('One night can make', '$6,449<br><span class="a">to $7,100.</span>', extra=blocks([
     ('Bottles on the night', 3100, '#1E2552'), ('Trade orders', 2604, '#C9500A'), ('Ticket credit', 1396, '#E42E2E')], ('Against', '$1,500–$2,000'))) +
       '<p class="fine" style="bottom:132px">Illustration: a 40-guest night. Sales value and credit, before stock and costs.</p>', 3, tag=tag),
 slide(f'{a}-4', 'navy', pad('Part of your plan', 'Not on top<br><span class="a">of it.</span>', extra=lst([
     ('Set-up, about 10 hrs', 'Tickets, artwork, ads, coordination.'), ('The night, 4–5 hrs', 'Check-in, trade liaison, orders.'),
     ('From your subscription', 'Roll Out or Take Over.'), ('Contacts, yours only', 'Ticket-holders and trade guests.')])), 4, tag=tag),
 slide(f'{a}-5', 'red', pad('6 weeks to book your tour', 'Your brand,<br><span class="a">on tour.</span>', 'Lock in a city, a venue and a date within 6 weeks.', '<p class="cta">Book your tour</p><p class="url">site.drinksnetwork.com.au/whisky-adventure/brands</p>'), 5, tag=tag),
]
# ---------------- single posts
S += [
 slide('post-takeover-venue', 'ink', photo('takeover/cocktail-handoff.jpg', '50% 40%') + pad('Bar Takeover · Venues', f'{E.TK_TICKETS} tickets.<br><span class="a">{E.TK_TICKETS * E.TK_DRINKS} cocktails.</span>', f'Pre-sold before the doors open. One guest bartender, one night, up to {TKV} through your bar. Example only.', cls='bottom'), tag='Venues'),
 slide('post-takeover-brand', 'ink', photo('takeover/team-toast.jpg', '50% 40%') + pad('Bar Takeover · Brands', 'Not a prize.<br><span class="a">A shift for your brand.</span>', 'About $2,000 takes a bartender, your menu and your brand into a new venue.', cls='bottom'), tag='Brands'),
 slide('post-takeover-bartender', 'ink', photo('takeover/bartenders-laughing.jpg', '50% 40%') + pad('Bar Takeover · Bartenders', 'Fly in.<br><span class="a">Take over.</span>', 'Flights, accommodation and a $500 stipend, paid by the brand.', cls='bottom'), tag='Bartenders'),
 slide('post-tasting-venue', 'ink', photo('photos/distillers-dinner.jpg', '50% 50%') + pad('Tasting Series · Venues', f'{money(E.TS_HALF)}<br><span class="a">in cash.</span>', f'Your half of a {E.TS_GUESTS}-guest tasting night at ${E.TS_PRICE}, after fees. Plus the bar.', cls='bottom'), tag='Venues'),
 slide('post-tasting-brand', 'ink', photo('photos/corowa-back-bar-brisbane.jpg', '50% 50%') + pad('Tasting Series · Brands', f'{E.COROWA_CONVERSION}<br><span class="a">first-order conversion.</span>', 'Corowa put its distiller in the room. Product alone converts at 5–10%.', cls='bottom'), tag='Brands'),
]
# ---------------- link images 1200x627
for key, k, h, t, img, pos in [
    ('takeover-venue', 'Bar Takeover · Venues', 'Put a guest <span class="a">behind your bar.</span>', 'One night, a ticketed crowd, run end to end.', 'takeover/full-bar-room.jpg', '50% 45%'),
    ('takeover-brand', 'Bar Takeover · Brands', 'Your brand, <span class="a">on tour.</span>', 'About $2,000. One new account. Contacts yours only.', 'takeover/straining-a-martini.jpg', '45% 45%'),
    ('takeover-bartender', 'Bar Takeover · Bartenders', 'Your menu. <span class="a">Their bar.</span>', 'Flights, accommodation and a $500 stipend.', 'takeover/bartender-leaning-in.jpg', '45% 40%'),
    ('tasting-venue', 'Tasting Series · Venues', 'Half the door, <span class="a">in cash.</span>', f'${E.TS_PRICE}, five pours, two hours, in your room.', 'tasting/hero.jpg', '50% 50%'),
    ('tasting-brand', 'Tasting Series · Brands', 'Put the maker <span class="a">in the room.</span>', 'Ticketed tastings led by your distiller.', 'photos/corowa-pour-spirits-wall.jpg', '50% 50%')]:
    S.append(f'<div class="s ln navy" id="link-{key}"><div class="bar"></div><img class="side" src="{M}{img}" style="object-position:{pos}" alt=""><div class="pad"><p class="k">{k}</p><h1 class="h">{h}</h1><p class="t">{t}</p></div><img class="logo" src="{DN_W}" alt=""></div>')

FONTS = '<link href="https://fonts.googleapis.com/css2?family=Anton&family=Archivo+Narrow:wght@500;700&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">'
open(os.path.join(HERE, 'slides.html'), 'w').write(f'<!doctype html><html><head><meta charset="utf-8">{FONTS}<style>{CSS}</style></head><body>' + '\n'.join(S) + '</body></html>')
print(len(S), 'slides')
