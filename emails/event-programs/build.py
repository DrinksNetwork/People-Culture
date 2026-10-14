"""Builds the 6-week event-program email sequences as Mailchimp-ready HTML.
Run: python3 emails/event-programs/build.py
 -> writes <track>/<nn>-<key>.html, schedule.csv and event-programs-mailchimp-pack.zip

Tracks (Mailchimp journey start tag in brackets):
  takeover-venue      Bar Takeover host venues        [journey:takeover-venue]
  takeover-brand      Bar Takeover brands             [journey:takeover-brand]
  takeover-bartender  Bar Takeover guest bartenders   [journey:takeover-bartender]
  tasting-venue       Tasting Series host venues      [journey:tasting-venue]
  tasting-brand       Tasting Series brands           [journey:tasting-brand]

Figures: Tasting Series numbers come from /whisky-adventure/tasting-series and the offers sent to venues
($75, five whiskies, about two hours, 50/50 split). Bar Takeover numbers are the owner's brief of 14 Oct 2026
($49 ticket = two cocktails, $500 stipend, fee up to $1,000, ~$2,000). Conversion figures are the owner's.
Images load from https://site.drinksnetwork.com.au/media/email/events/."""
import csv, html, os, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://site.drinksnetwork.com.au'
IMG = SITE + '/media/email/events/'
LOGO = SITE + '/media/logos/drinks-network-script-white.png'
RED, RED_DARK, NAVY, PAPER, SAND, INK, BODY, QUIET, PINK = '#E42E2E', '#B81F24', '#1E2552', '#FBF7F0', '#F1E9DC', '#111111', '#3A3631', '#5A554D', '#FFE3E0'
ORANGE, PLUM, GREEN, GOLD = '#C9500A', '#3D1829', '#1F9D55', '#E9A24A'
DISPLAY = "Anton,Impact,'Arial Narrow Bold','Helvetica Neue',Arial,sans-serif"
NARROW = "'Archivo Narrow','Arial Narrow','Helvetica Neue',Arial,sans-serif"
SERIF = "'Source Serif 4',Georgia,'Times New Roman',serif"
SANS = "'Helvetica Neue',Helvetica,Arial,sans-serif"
HI = '*|IF:FNAME|*Hi *|FNAME|*,*|ELSE:|*Hi there,*|END:IF|*'
CO = '*|IF:COMPANY|**|COMPANY|**|ELSE:|*your venue*|END:IF|*'
COB = '*|IF:COMPANY|**|COMPANY|**|ELSE:|*your brand*|END:IF|*'

TAKEOVER_PACK = SITE + '/media/takeover/bar-takeover-pack.pdf'
TASTING_PACK = SITE + '/media/brief/tasting-partnership-brief.pdf'
MANNY = 'manuel@drinksnetwork.com.au'
MANNY_TEL = '0405 483 898'

# ---- the numbers (change here, every email follows) ----
EB_PCT, EB_FIX = 0.0535, 1.19          # Eventbrite Australia service fee per ticket


def fees(n, price):
    return round(n * price * EB_PCT + n * EB_FIX, 2)


def money(v, cents=False):
    return f'${v:,.2f}' if cents else f'${round(v):,}'


TK_TICKETS, TK_PRICE, TK_DRINKS = 30, 49, 2                       # Bar Takeover example
TK_GROSS = TK_TICKETS * TK_PRICE
TK_FEES = fees(TK_TICKETS, TK_PRICE)
TK_NET = TK_GROSS - TK_FEES
TK_VENUE_SHARE = 1.0                                               # share of net ticket revenue paid to the venue (confirm)
TK_VENUE = TK_NET * TK_VENUE_SHARE
TK_PER_DRINK = TK_PRICE / TK_DRINKS                                # $24.50
TK_PLUSONE = TK_TICKETS * TK_DRINKS * TK_PER_DRINK                 # friends buying two drinks at the bar

TS_GUESTS, TS_PRICE = 40, 75                                       # Tasting Series example (published)
TS_GROSS = TS_GUESTS * TS_PRICE
TS_FEES = fees(TS_GUESTS, TS_PRICE)
TS_NET = TS_GROSS - TS_FEES
TS_HALF = TS_NET / 2

# Corowa on tour (from Drinks Network's own account data, Sept 2026). Set COROWA_UPLIFT to a string such as '+35%'
# once the sales-uplift figure is confirmed; until then the uplift tile is left out.
COROWA_CONVERSION = '40.7%'
COROWA_AUDIENCE = '500–600'
COROWA_UPLIFT = None


def u(path, track, n):
    if path.startswith('mailto:'):
        return path
    sep = '&' if '?' in path else '?'
    base, _, frag = path.partition('#')
    return f'{SITE}{base}{sep}utm_source=mailchimp&utm_medium=email&utm_campaign={track}&utm_content=email-{n}' + (f'#{frag}' if frag else '')


def nw(t):
    parts = t.rsplit(' ', 2)
    if len(parts) == 3 and '<' not in parts[1] + parts[2] and '>' not in parts[1] + parts[2]:
        return f'{parts[0]} {parts[1]}&nbsp;{parts[2]}'
    return t


def button(label, url, bg=RED, fg='#FFFFFF'):
    return f'''<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:12px 0 6px"><tr><td align="center" bgcolor="{bg}" style="border-radius:6px">
<a href="{url}" target="_blank" style="display:inline-block;padding:15px 28px;font:700 16px {NARROW};letter-spacing:1px;text-transform:uppercase;color:{fg};text-decoration:none;border-radius:6px">{label}</a></td></tr></table>'''


def link2(label, url):
    return f'<p style="margin:4px 0 16px;font:700 14px {NARROW};letter-spacing:1px;text-transform:uppercase"><a href="{url}" style="color:{RED}">{label} &rarr;</a></p>'


def img(src, alt, w=600, radius=0):
    return f'<img src="{IMG}{src}" width="{w}" alt="{html.escape(alt)}" style="display:block;width:100%;max-width:{w}px;height:auto;border:0;border-radius:{radius}px">'


def p(t, size=17, col=BODY):
    return f'<p style="margin:0 0 16px;font:400 {size}px/1.6 {SERIF};color:{col}">{nw(t)}</p>'


def h(t, accent=''):
    acc = f'<br><span style="color:{RED}">{accent}</span>' if accent else ''
    return f'<h1 style="margin:0 0 18px;font:400 44px/1.04 {DISPLAY};text-transform:uppercase;letter-spacing:.3px;color:{NAVY}">{t}{acc}</h1>'


def h2(t):
    return f'<h2 style="margin:26px 0 10px;font:700 15px {NARROW};letter-spacing:2px;text-transform:uppercase;color:{RED}">{t}</h2>'


def kick(t):
    return f'<p style="margin:0 0 10px;font:700 13px {NARROW};letter-spacing:3px;text-transform:uppercase;color:{RED}">{t}</p>'


def card(inner, bg=SAND, pad='20px 22px'):
    return f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 18px"><tr><td bgcolor="{bg}" style="border-radius:10px;padding:{pad};font:400 16px/1.55 {SERIF};color:{BODY}">{inner}</td></tr></table>'


def qa(q, a):
    return card(f'<p style="margin:0 0 8px;font:700 13px {NARROW};letter-spacing:2px;text-transform:uppercase;color:{RED}">Straight answer</p>'
                f'<p style="margin:0 0 8px;font:400 22px/1.15 {DISPLAY};text-transform:uppercase;color:{NAVY}">{q}</p>'
                f'<p style="margin:0;font:400 16px/1.6 {SERIF};color:{BODY}">{nw(a)}</p>', PINK)


def steps(rows, start=1):
    tds = ''.join(f'<tr><td valign="top" width="44" style="padding:0 12px 14px 0;font:400 30px/1 {DISPLAY};color:{RED}">{n:02d}</td>'
                  f'<td valign="top" style="padding:0 0 14px;font:400 16px/1.5 {SERIF};color:{BODY}"><b style="font:700 16px {NARROW};letter-spacing:.5px;color:{NAVY};text-transform:uppercase">{t}</b><br>{nw(d)}</td></tr>'
                  for n, (t, d) in enumerate(rows, start))
    return f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 10px">{tds}</table>'


def bullets(items, col=RED):
    tds = ''.join(f'<tr><td valign="top" width="18" style="padding:6px 0 0"><div style="width:9px;height:9px;background:{col}"></div></td>'
                  f'<td style="padding:0 0 9px;font:400 16px/1.5 {SERIF};color:{BODY}">{nw(t)}</td></tr>' for t in items)
    return f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 14px">{tds}</table>'


def table(head, rows, note=''):
    th = ''.join(f'<th align="left" style="padding:8px 8px;font:700 12px {NARROW};letter-spacing:1px;text-transform:uppercase;color:#FFFFFF;background:{NAVY}">{c}</th>' for c in head)
    tr = ''.join('<tr>' + ''.join(f'<td style="padding:9px 8px;border-bottom:1px solid #E6DCCB;font:400 15px/1.4 {SERIF};color:{BODY}">{c}</td>' for c in r) + '</tr>' for r in rows)
    n = f'<p style="margin:6px 0 0;font:400 12px/1.5 {SANS};color:{QUIET}">{note}</p>' if note else ''
    return f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 18px;border-collapse:collapse"><tr>{th}</tr>{tr}</table>{n}'


def stat_row(items, col=RED, bg=None):
    tds = ''.join(f'<td width="{100 // len(items)}%" valign="top" style="padding:14px 8px;{"background:" + bg + ";" if bg else ""}border-radius:8px"><p style="margin:0;font:400 36px/1 {DISPLAY};color:{col}">{n}</p><p style="margin:6px 0 0;font:700 12px/1.35 {NARROW};letter-spacing:.5px;text-transform:uppercase;color:{NAVY}">{l}</p></td>' for n, l in items)
    return f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:8px 0 20px"><tr>{tds}</tr></table>'


def blocks(rows, total=None, note=''):
    """Money in blocks: (label, value, colour, sub). Bars sized against the largest value."""
    mx = max(v for _, v, _, _ in rows)
    out = ''
    for label, v, col, sub in rows:
        w = max(18, round(v / mx * 100))
        out += (f'<tr><td style="padding:0 0 10px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
                f'<td width="{w}%" bgcolor="{col}" style="border-radius:6px;padding:12px 14px;font:400 26px/1 {DISPLAY};color:#FFFFFF">{money(v)}</td>'
                f'<td width="{100 - w}%" style="font-size:0">&nbsp;</td></tr></table>'
                f'<p style="margin:5px 0 0;font:700 13px/1.35 {NARROW};letter-spacing:.5px;text-transform:uppercase;color:{NAVY}">{label}</p>'
                f'<p style="margin:2px 0 0;font:400 14px/1.45 {SERIF};color:{QUIET}">{sub}</p></td></tr>')
    if total:
        out += (f'<tr><td style="padding:8px 0 0;border-top:3px solid {NAVY}"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
                f'<td style="font:700 14px {NARROW};letter-spacing:1px;text-transform:uppercase;color:{NAVY}">{total[0]}</td>'
                f'<td align="right" style="font:400 34px/1 {DISPLAY};color:{RED}">{total[1]}</td></tr></table></td></tr>')
    n = f'<p style="margin:8px 0 0;font:400 12px/1.5 {SANS};color:{QUIET}">{note}</p>' if note else ''
    return f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:10px 0 18px">{out}</table>{n}'


def window(week, kind='takeover night'):
    """The six-week commitment window, with the current week lit up."""
    cells = ''
    for i in range(1, 7):
        on = i <= week
        cells += (f'<td width="14%" align="center" bgcolor="{RED if i == week else (NAVY if on else "#E6DCCB")}" style="padding:10px 0;font:700 12px {NARROW};letter-spacing:1px;text-transform:uppercase;color:{"#FFFFFF" if on else QUIET};border-right:3px solid #FFFFFF">Wk {i}</td>')
    cells += f'<td width="16%" align="center" bgcolor="{GREEN}" style="padding:10px 0;font:700 12px {NARROW};letter-spacing:1px;text-transform:uppercase;color:#FFFFFF">Day 60</td>'
    left = 6 - week
    msg = (f'Week {week} of your 6-week window. ' + (f'{left} week{"s" if left != 1 else ""} left to lock in a date' if left else 'This is the last week to lock in a date')
           + f', for a {kind} inside 60 days of registering.')
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 6px;border-radius:6px;overflow:hidden"><tr>{cells}</tr></table>'
            f'<p style="margin:0 0 18px;font:400 13px/1.5 {SANS};color:{QUIET}">{msg}</p>')


def agree(title, items, pack, pack_label):
    lis = ''.join(f'<li style="margin:0 0 6px">{nw(t)}</li>' for t in items)
    return card(f'<p style="margin:0 0 8px;font:700 13px {NARROW};letter-spacing:2px;text-transform:uppercase;color:#FFE3E0">What you\'re agreeing to</p>'
                f'<p style="margin:0 0 10px;font:400 22px/1.15 {DISPLAY};text-transform:uppercase;color:#FFFFFF">{title}</p>'
                f'<ul style="margin:0 0 12px;padding-left:18px;font:400 15px/1.5 {SERIF};color:#E6E8F2">{lis}</ul>'
                f'<p style="margin:0;font:700 13px {NARROW};letter-spacing:1px;text-transform:uppercase"><a href="{pack}" style="color:#FFFFFF">{pack_label} (PDF) &rarr;</a></p>', NAVY)


def two_img(a, a_alt, b, b_alt):
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 18px"><tr>'
            f'<td width="50%" style="padding-right:5px">{img(a, a_alt, 290, 8)}</td><td width="50%" style="padding-left:5px">{img(b, b_alt, 290, 8)}</td></tr></table>')


def quote(t, who):
    return card(f'<p style="margin:0 0 8px;font:400 24px/1.2 {DISPLAY};text-transform:uppercase;color:{NAVY}">“{t}”</p>'
                f'<p style="margin:0;font:700 12px {NARROW};letter-spacing:1px;text-transform:uppercase;color:{RED}">{who}</p>', '#FFFFFF', '4px 0 4px 18px;border-left:5px solid ' + RED)


TRACKS = {
    'takeover-venue': dict(label='Bar Takeover · Venues', why="You're receiving this because you asked for the Bar Takeover pack as a host venue on site.drinksnetwork.com.au."),
    'takeover-brand': dict(label='Bar Takeover · Brands', why="You're receiving this because you asked for the Bar Takeover pack as a brand on site.drinksnetwork.com.au."),
    'takeover-bartender': dict(label='Bar Takeover · Bartenders', why="You're receiving this because you registered as a guest bartender for Bar Takeover on site.drinksnetwork.com.au."),
    'tasting-venue': dict(label='Tasting Series · Venues', why="You're receiving this because you asked about hosting a Drinks Network tasting on site.drinksnetwork.com.au."),
    'tasting-brand': dict(label='Tasting Series · Brands', why="You're receiving this because you asked about taking your brand on tour with Drinks Network on site.drinksnetwork.com.au."),
}


def page(track, subject, body, hero, hero_alt):
    t = TRACKS[track]
    return f'''<!doctype html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="X-UA-Compatible" content="IE=edge">
<title>{html.escape(subject)}</title>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Archivo+Narrow:wght@500;700&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
<style>body{{margin:0;padding:0;background:{PAPER}}} a{{color:{RED}}} @media (max-width:620px){{.px{{padding-left:22px!important;padding-right:22px!important}} h1{{font-size:36px!important}}}}</style>
</head>
<body style="margin:0;padding:0;background:{PAPER}">
<span style="display:none!important;visibility:hidden;opacity:0;color:transparent;height:0;width:0;overflow:hidden;mso-hide:all">*|MC_PREVIEW_TEXT|*</span>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{PAPER}"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:600px;background:#FFFFFF;border-radius:10px;overflow:hidden">
<tr><td bgcolor="{RED}" style="padding:16px 30px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
<td><img src="{LOGO}" width="140" alt="Drinks Network" style="display:block;width:140px;height:auto;border:0"></td>
<td align="right" style="font:700 12px {NARROW};letter-spacing:2px;text-transform:uppercase;color:#FFFFFF">{t["label"]}</td></tr></table></td></tr>
<tr><td style="padding:0">{img(hero, hero_alt)}</td></tr>
<tr><td class="px" style="padding:34px 40px 30px">{body}
<p style="margin:22px 0 0;font:400 16px/1.6 {SERIF};color:{BODY}">Questions? Reply to this email, or call Manuel Terron (Events) on {MANNY_TEL}.<br><b>The Drinks Network team</b></p></td></tr>
<tr><td bgcolor="{NAVY}" style="padding:24px 40px;font:400 12px/1.6 {SANS};color:#C9CCE0">
<b style="color:#FFFFFF">Drinks Network Pty Ltd</b> · ABN 89 680 725 802 · Sydney · Melbourne · Brisbane<br>
{t["why"]}<br>
<a href="*|UPDATE_PROFILE|*" style="color:#FFFFFF">Update preferences</a> · <a href="*|UNSUB|*" style="color:#FFFFFF">Unsubscribe</a><br>*|LIST:ADDRESSLINE|*</td></tr>
</table></td></tr></table></body></html>'''


# ================================================================== shared blocks
def tk_venue_agree():
    return agree('Hosting a Bar Takeover', [
        'Lock in a date within 6 weeks, for a night inside 60 days of registering.',
        'One guest shift, 6 pm to 10 pm (later if you like), under your licence and house rules.',
        'An opening order of the brand before the night, kept on your list after it.',
        'Buy the ingredients from the bartender\'s mise en place list, sent at least two weeks before.',
        'A run-through with the bartender the day before, with garnish prep.',
        'A duty manager and bar back alongside the guest.',
        'Tickets sold through Drinks Network\'s Eventbrite. Ticket-holder and trade contact details go to the brand that funds the night, and no one else.',
    ], TAKEOVER_PACK, 'Read the full Bar Takeover pack')


def tk_brand_agree():
    return agree('Taking your brand on a Bar Takeover', [
        'Lock in a city, venue and date within 6 weeks.',
        'Fund the guest bartender: return flights and accommodation at cost, a $500 stipend, and an optional fee of up to $1,000. Around $2,000 all in.',
        'Program hours are drawn from your RepShare subscription: Roll Out (10 hours a week, one state) or Take Over (15 hours a week, across two states).',
        'Product support for the menu build, and a drinks tab for the trade buyers our reps bring.',
        'You receive the ticket-holder and trade contacts. They are shared with you only.',
    ], TAKEOVER_PACK, 'Read the full Bar Takeover pack')


def tk_bar_agree():
    return agree('When a brand picks you', [
        'Send the menu and full mise en place list to the venue at least two weeks before you arrive.',
        'Meet the venue team the day before to check every ingredient and prep complicated garnishes.',
        'Work a 6 pm to 10 pm shift under the venue\'s duty manager and house rules.',
        'Hold an RSA that\'s valid in the host state.',
        'Make time for photos, a short video and the trade buyers.',
    ], TAKEOVER_PACK, 'Read the full Bar Takeover pack')


def ts_venue_agree():
    return agree('Hosting a distiller\'s tasting', [
        'Lock in a date within 6 weeks, for a night inside 60 days of registering.',
        'A main contact for the event, the space, glassware, water and bar staff, and snacks or a food option.',
        f'An opening order of the tasted range at wholesale, on a mixed-case intro deal.',
        'Glassware hire, if needed, split 50/50.',
        f'Tickets sold through Drinks Network\'s Eventbrite. Your venue receives 50% of net ticket revenue in cash. Ticket-holder and trade contact details go to the brand that funds the night, and no one else.',
    ], TASTING_PACK, 'Read the full Tasting Series brief')


def ts_brand_agree():
    return agree('Taking your brand on tour', [
        'Lock in a city, venue and date within 6 weeks.',
        'A speaker for the night (maker or representative), a short bio and headshot three weeks out, the tasting line-up and stock to pour.',
        'Event set-up (about 10 hours) and management on the night (4–5 hours): $1,500–$2,000, drawn from your RepShare subscription.',
        '50% of net ticket revenue comes back to you as account credit.',
        'You receive the ticket-holder and trade contacts. They are shared with you only.',
    ], TASTING_PACK, 'Read the full Tasting Series brief')


def conversion_tiles():
    return (stat_row([('5–10%', 'Product only. 15% at best'), ('30%+', 'With an activity or a high-value offer'), ('50%+', 'When the offer and the room are right')], RED, SAND))


def corowa_block():
    tiles = [(COROWA_CONVERSION, 'Corowa first-order conversion, touring its distiller'), (COROWA_AUDIENCE, 'Queensland whisky drinkers on its list')]
    if COROWA_UPLIFT:
        tiles.append((COROWA_UPLIFT, 'Sales uplift on tour'))
    return (two_img('poster-corowa.jpg', 'Corowa Distiller\'s Tasting poster with Dean Druce', 'poster-headlands.jpg', 'Australian Whisky Night Headlands tasting poster') +
            stat_row(tiles, RED, SAND))


def tk_money():
    return blocks([
        (f'{TK_TICKETS} tickets at ${TK_PRICE}, after Eventbrite fees', TK_VENUE, RED, f'{TK_TICKETS * TK_DRINKS} cocktails pre-sold before the doors open: {money(TK_GROSS)} in tickets, less {money(TK_FEES, True)} in Eventbrite fees.'),
        ('The plus-one effect', TK_PLUSONE, ORANGE, f'If each ticket-holder brings one friend who buys two drinks at ${TK_PER_DRINK:.2f}: another {TK_TICKETS} guests and {TK_TICKETS * TK_DRINKS} drinks.'),
    ], ('One night, before stock costs', money(TK_VENUE + TK_PLUSONE)),
        'Example only. Third drinks, food and the menu staying on after the night come on top. Your costs are the opening order (stock you keep selling) and the menu ingredients.')


# ================================================================== BAR TAKEOVER · VENUE
TV = 'takeover-venue'
TAKEOVER_VENUE = [
 dict(n='00', key='welcome', day=0, subject='Your Bar Takeover pack, and what happens next',
  pre='One night, one guest bartender, your bar. Here is how it works.', hero='tk-full-bar-room.jpg', alt='A packed cocktail bar on a takeover night',
  body=lambda: kick('Day 0 · Welcome') + h('One night. One guest.', 'Your bar.') + p(HI) +
   p(f'Thanks for asking for the Bar Takeover pack for {CO}. A takeover brings three partners together for one night: your venue, a cocktail brand and a guest bartender. Drinks Network runs it from the first post to the last follow-up call.') +
   h2('What happens next') +
   steps([('A call within one business day', 'Manuel Terron, our events lead, calls to talk through dates, your room and the brands that suit your list.'),
          ('Pick a date', 'You have 6 weeks to lock in a date, for a night inside 60 days of registering.'),
          ('We match the brand and the bartender', 'You get a guest and a menu built for your room.')]) +
   window(1) +
   p('Over the next six weeks we\'ll send you one email a week. Each one covers a part of the night: the money, the work, the risk and the run sheet, so you know exactly what you\'re saying yes to.') +
   button('Open the Bar Takeover pack', u('/bar-takeover?pack=open', TV, '00')) + tk_venue_agree()),
 dict(n='01', key='the-money', day=7, subject=f'What one takeover night can make: {money(TK_VENUE + TK_PLUSONE)}',
  pre=f'{TK_TICKETS} tickets, {TK_TICKETS * TK_DRINKS} cocktails pre-sold, and the friends they bring.', hero='tk-cocktail-handoff.jpg', alt='A guest bartender handing a cocktail across the bar',
  body=lambda: kick('Week 2 · The money') + h('The night,', 'in blocks.') + p(HI) +
   p(f'Every Bar Takeover ticket is ${TK_PRICE} and covers two cocktails from the guest bartender\'s menu. We sell the tickets before the night, so the drinks are paid for before the guest pours the first one.') +
   tk_money() +
   qa('Who gets the ticket money?', f'Ticket revenue is paid to your venue after Eventbrite fees, for the drinks you pour. Everything else guests buy at the bar is yours too.') +
   window(2) + button('See the full numbers in the pack', u('/bar-takeover?pack=open', TV, '01')) + tk_venue_agree()),
 dict(n='02', key='what-hosting-involves', day=14, subject='What hosting a guest bartender actually involves',
  pre='The menu, the ingredients, the run-through and the night itself.', hero='tk-bartender-leaning-in.jpg', alt='A guest bartender talking a guest through the menu',
  body=lambda: kick('Week 3 · The work') + h('Your bar,', 'their menu.') + p(HI) +
   p('You lend your bar to a guest for one night. Your licence, house rules and team stay in charge. Here is your side of it:') +
   steps([('Take the brand on', 'An opening order of the brand before the night, so the menu can be poured and stays on after.'),
          ('Get the mise en place list', 'The bartender sends the menu and a full list of every spirit, modifier, syrup, garnish and glass at least two weeks before.'),
          ('Buy the ingredients', 'Your venue buys everything on the list, so it\'s in the building before the guest arrives.'),
          ('Run it through the day before', 'Meet the bartender, check nothing is missing and prep any complicated garnishes.'),
          ('Back them on the night', 'A duty manager and bar back, a station, ice, glassware and POS buttons for the menu.')]) +
   qa('Who buys the ingredients?', 'The venue. You get the full list at least two weeks out, and the day-before run-through catches anything that\'s missing.') +
   window(3) + button('Read the venue section of the pack', u('/bar-takeover?pack=open', TV, '02')) + tk_venue_agree()),
 dict(n='03', key='the-risk', day=21, subject='How much is at risk? Less than a quiet Tuesday',
  pre='Tickets are sold before the night and the stock stays on your shelf.', hero='tk-straining-a-martini.jpg', alt='A martini being fine-strained into a frosted coupe',
  body=lambda: kick('Week 4 · The risk') + h('Low risk.', 'Real upside.') + p(HI) +
   p('Here is what you put in, and who carries the rest.') +
   table(['You put in', 'Covered by others'], [
     ['The opening order: stock you keep and keep selling', 'The bartender\'s flights, accommodation and stipend (the brand)'],
     ['Ingredients for the guest menu', 'Eventbrite page, ticket sales and check-in (Drinks Network)'],
     ['One shift of your own team', 'Artwork, captions and posts (Drinks Network)'],
     ['Promotion to your regulars', 'Trade buyers\' drinks, on the brand\'s tab'],
   ]) +
   qa('What if tickets are slow?', 'We push tickets across our channels, yours and the brand\'s, and walk-ins still buy at the bar as normal. The opening order is stock you sell long after the night.') +
   window(4) + button('Talk it through with Manuel', f'mailto:{MANNY}?subject=Bar%20Takeover%20questions') + tk_venue_agree()),
 dict(n='04', key='make-it-pay', day=28, subject='Five things that fill the room (and the till)',
  pre='What the best host venues do in the three weeks before the night.', hero='tk-bartenders-laughing.jpg', alt='Two bartenders laughing behind a busy back bar',
  body=lambda: kick('Week 5 · Make it pay') + h('Fill the room.', 'Fill the till.') + p(HI) +
   p('The takeover pays best when your venue pushes it too. Five things that work:') +
   steps([('Post it three times', 'The announcement, a week-out reminder and the day of. We give you the artwork and captions.'),
          ('Tell your regulars', 'Staff mention it at the bar for two weeks. Regulars buy tickets and bring friends.'),
          ('Put the menu on the tables', 'Table cards for the night, so walk-ins order the guest\'s drinks too.'),
          ('Plan food', 'Snacks or a small menu keep people in for a third drink.'),
          ('Keep the menu on', 'The opening order is on your shelf. Keep one or two of the guest\'s drinks on your list after the night.')]) +
   two_img('ck-foam-sour.jpg', 'A foam-topped sour on a marble bar', 'ck-three-cocktails.jpg', 'Three cocktails on a terrace table') +
   window(5) + p('<b>One week left to lock in your date.</b>') +
   button('Lock in a date', f'mailto:{MANNY}?subject=Lock%20in%20a%20Bar%20Takeover%20date') + tk_venue_agree()),
 dict(n='05', key='run-sheet', day=35, subject='Your takeover run sheet, from yes to the night',
  pre='What happens when, once you lock in a date.', hero='tk-team-toast.jpg', alt='A bar team raising cocktails',
  body=lambda: kick('Week 6 · The run sheet') + h('From yes', 'to the night.') + p(HI) +
   steps([('The day you lock in', 'Brand and bartender confirmed. Your opening order goes in. Tickets go on sale.'),
          ('Two weeks out', 'The bartender sends the menu and mise en place list. You order the ingredients. Announcement posts go out and reps send trade invites.'),
          ('The day before', 'The bartender flies in and meets your team. Check every ingredient, prep the garnishes.'),
          ('6 pm – 10 pm', 'Ticket-holders check in, the guest works the menu, reps host trade buyers on the brand.'),
          ('The next six days', 'Trade follow-up, a recap post with your venue in it, and a report to the brand.')]) +
   window(6) + p('<b>This is the last week to lock in a date.</b> After that, we\'ll offer the slot to the next venue on the list.') +
   button('Lock in a date', f'mailto:{MANNY}?subject=Lock%20in%20a%20Bar%20Takeover%20date') + tk_venue_agree()),
 dict(n='06', key='last-call', day=42, subject='Last call: lock in your Bar Takeover',
  pre='Your 6-week window closes today.', hero='ck-three-cocktails.jpg', alt='Three cocktails on a terrace table',
  body=lambda: kick('Day 42 · Last call') + h('Last call.', 'Lock it in.') + p(HI) +
   p(f'Your 6-week window to lock in a Bar Takeover at {CO} closes today. Here\'s the night in one look:') +
   stat_row([(f'{TK_TICKETS}', 'Tickets sold'), (f'{TK_TICKETS * TK_DRINKS}', 'Cocktails pre-sold'), (money(TK_VENUE + TK_PLUSONE), 'Example night, before stock')], RED, SAND) +
   p('Reply to this email or call Manuel on ' + MANNY_TEL + ' and we\'ll lock in a date inside your 60 days. If now isn\'t the time, we\'ll keep you on the list for the next round.') +
   button('Lock in a date', f'mailto:{MANNY}?subject=Lock%20in%20a%20Bar%20Takeover%20date') + tk_venue_agree()),
]

# ================================================================== BAR TAKEOVER · BRAND
TB = 'takeover-brand'
TAKEOVER_BRAND = [
 dict(n='00', key='welcome', day=0, subject='Your brand on tour: the Bar Takeover pack',
  pre='A guest bartender, a new venue and a full room for your brand.', hero='tk-straining-a-martini.jpg', alt='A martini being strained, Lady Triệu Gin on the back bar',
  body=lambda: kick('Day 0 · Welcome') + h('Your brand', 'on tour.') + p(HI) +
   p(f'Thanks for asking for the Bar Takeover pack for {COB}. A takeover puts a guest bartender behind a new venue\'s bar for one night, pouring a menu built on your product, with ticket-holders and trade buyers in the room.') +
   p('It isn\'t a prize. It\'s a working shift for your brand, and it\'s how brands get onto cocktail lists and stay there.') +
   h2('What happens next') +
   steps([('A call within one business day', 'Manuel Terron, our events lead, talks through cities, venues and bartenders that suit your range.'),
          ('Six weeks to commit', 'Lock in a city, venue and date within 6 weeks.'),
          ('We run it end to end', 'Matching, media, tickets, trade invites, the night and six days of follow-up.')]) +
   window(1, 'takeover') + button('Open the Bar Takeover pack', u('/bar-takeover?pack=open', TB, '00')) + tk_brand_agree()),
 dict(n='01', key='why-activity', day=7, subject='Product alone converts at 5–10%. A takeover converts at 30%+',
  pre='Why there needs to be something more than the product for sale.', hero='tk-cocktail-handoff.jpg', alt='A guest bartender handing a cocktail across the bar',
  body=lambda: kick('Week 2 · Why it works') + h('Give them a reason', 'to say yes.') + p(HI) +
   p('Walk into a venue with a product and a price list and you\'ll convert 5 to 10% of the time, 15% at best. Walk in with an activity or a high-value offer and that number goes above 30%, and sometimes past 50%, depending on how good the offer is and who it\'s aimed at.') +
   conversion_tiles() +
   p('A Bar Takeover is that offer. The venue takes your product on to host the night, the room tastes it poured properly, and trade buyers try it on your tab with a rep beside them.') +
   window(2, 'takeover') + button('See how a takeover works', u('/bar-takeover', TB, '01')) + tk_brand_agree()),
 dict(n='02', key='the-investment', day=14, subject='What you\'re investing in: about $2,000 a takeover',
  pre='Flights, accommodation, a stipend, and the hours from your subscription.', hero='tk-bartender-leaning-in.jpg', alt='A guest bartender leaning in to talk to a guest',
  body=lambda: kick('Week 3 · The investment') + h('About $2,000.', 'One new account.') + p(HI) +
   p('You\'re investing in the campaign and the activity around your product, not just the product.') +
   blocks([('Bartender fee, optional', 1000, ORANGE, 'For a bigger name or a longer menu build.'),
           ('Stipend', 500, RED, 'Ubers, meals and a day\'s work in another venue for your brand.'),
           ('Flights and accommodation', 500, NAVY, 'Booked at cost. Shown here as the balance of a typical $2,000 takeover.')],
          ('Typical brand outlay', '~$2,000'), 'Flights and accommodation are charged at cost and vary by city.') +
   h2('Included in your subscription') +
   p('Running the program (matching, media, ticketing, trade invites and the six-day follow-up) is drawn from your RepShare hours. It\'s built into <b>Roll Out</b> (10 hours a week, one state) and <b>Take Over</b> (15 hours a week, across two states). If you don\'t have any other plan, this is what you\'re signing up to: it\'s how brands are built in the on-premise.') +
   window(3, 'takeover') + button('See the plans', u('/brands', TB, '02')) + tk_brand_agree()),
 dict(n='03', key='brand-on-tour', day=21, subject='What happens when the brand goes on tour',
  pre='Corowa took its distiller on the road. Here is what it did for conversion.', hero='ts-pour-wall.jpg', alt='Whisky poured neat in front of a wall of spirits',
  body=lambda: kick('Week 4 · Brand on tour') + h('Put a face', 'to the bottle.') + p(HI) +
   p('When a brand owner or a great bartender stands behind the bar, buyers listen. Corowa Distilling took Dean Druce on tour with ticketed distiller\'s tastings, and its first-order conversion went to ' + COROWA_CONVERSION + '.') +
   corowa_block() +
   p('A Bar Takeover does the same for cocktail brands: a name on the poster, a story on the menu and a room that tastes it at its best.') +
   window(4, 'takeover') + button('See the takeover pack', u('/bar-takeover?pack=open', TB, '03')) + tk_brand_agree()),
 dict(n='04', key='contacts-and-trade', day=28, subject='Every ticket-holder is your contact. Every buyer gets a follow-up',
  pre='The contacts are yours alone, and the reps follow up for six days.', hero='tk-full-bar-room.jpg', alt='A full bar during a takeover',
  body=lambda: kick('Week 5 · Contacts and trade') + h('Your contacts.', 'Your orders.') + p(HI) +
   p('You fund the night, so the people it brings are yours. Ticket-holders who opt in at checkout are passed to you, and so is the trade list. We don\'t share them with anyone else.') +
   h2('Six days of trade follow-up') +
   table(['When', 'What happens'], [
     ['The night', 'Reps host trade buyers, with drinks on your tab'],
     ['Day 1', 'Thank-you message and specs to every buyer'],
     ['Day 2', 'Recap post with your brand and the bartender'],
     ['Day 3', 'Rep visits to the warmest buyers'],
     ['Day 5', 'Intro offers and orders through ALM, Paramount, ILG or direct'],
     ['Day 6', 'Your report: tickets, contacts and orders'],
   ]) + window(5, 'takeover') + p('<b>One week left to lock in your takeover.</b>') +
   button('Lock in a takeover', f'mailto:{MANNY}?subject=Lock%20in%20a%20Bar%20Takeover%20for%20my%20brand') + tk_brand_agree()),
 dict(n='05', key='pick-your-takeover', day=35, subject='Pick your bartender, your venue and your city',
  pre='Any city with a great bar: Sydney, Melbourne, Brisbane, Ballarat, Wollongong.', hero='tk-bartenders-laughing.jpg', alt='Two bartenders laughing behind the bar',
  body=lambda: kick('Week 6 · Your takeover') + h('Your city.', 'Your guest.') + p(HI) +
   p('Takeovers work anywhere with a good bar and people who want a night out, from Sydney, Melbourne and Brisbane to Ballarat and Wollongong. We keep a list of bartenders ready to go, and a list of venues that want a guest.') +
   two_img('ck-lady-trieu.jpg', 'Lady Triệu Gin bottle', 'ck-frozen-coupe.jpg', 'A frozen coupe cocktail') +
   p('Cocktail-led products suit the program best: gins, vodkas and ready-to-pour cocktails that one great drink on a menu turns into a case a week.') +
   window(6, 'takeover') + p('<b>This is the last week to lock in your takeover.</b>') +
   button('Lock in a takeover', f'mailto:{MANNY}?subject=Lock%20in%20a%20Bar%20Takeover%20for%20my%20brand') + tk_brand_agree()),
 dict(n='06', key='last-call', day=42, subject='Last call: take your brand on a Bar Takeover',
  pre='Your 6-week window closes today.', hero='tk-team-toast.jpg', alt='A bar team raising cocktails',
  body=lambda: kick('Day 42 · Last call') + h('Last call.', 'Book the tour.') + p(HI) +
   p(f'Your 6-week window to lock in a Bar Takeover for {COB} closes today.') +
   stat_row([('~$2,000', 'Typical brand outlay'), ('30%+', 'Conversion with an activity'), ('6 days', 'Of trade follow-up')], RED, SAND) +
   p('Reply to this email or call Manuel on ' + MANNY_TEL + ' and we\'ll lock in a city, a venue and a date.') +
   button('Lock in a takeover', f'mailto:{MANNY}?subject=Lock%20in%20a%20Bar%20Takeover%20for%20my%20brand') + tk_brand_agree()),
]

# ================================================================== BAR TAKEOVER · BARTENDER
TT = 'takeover-bartender'
TAKEOVER_BARTENDER = [
 dict(n='00', key='on-the-list', day=0, subject='You\'re on the Bar Takeover list',
  pre='What happens now, and how a brand picks you.', hero='tk-bartender-leaning-in.jpg', alt='A guest bartender leaning in to talk to a guest',
  body=lambda: kick('Day 0 · You\'re on the list') + h('Your menu.', 'Their bar.') + p(HI) +
   p('Thanks for registering for Bar Takeover. You\'re now on our list of guest bartenders. When a brand wants to take a bartender to a new bar (Lady Triệu, Nhau, BLVD or another of our brands), we match them with someone from this list.') +
   h2('How you get picked') +
   steps([('We get to know you', 'Your bar, your style and the spirits you love to work with. Reply with your Instagram and a drink you\'re proud of.'),
          ('A brand picks you', 'We put you forward when a brand and a venue line up. You stay on the list until then.'),
          ('You fly in and take over', 'A 6 pm to 10 pm shift, your menu, a new city.')]) +
   qa('Is this a competition?', 'No. It\'s a paid working trip. The brand covers flights, accommodation and a $500 stipend, and some takeovers add a fee of up to $1,000.') +
   button('Read the Bar Takeover pack', u('/bar-takeover?pack=open', TT, '00')) + tk_bar_agree()),
 dict(n='01', key='what-it-involves', day=7, subject='What a guest shift involves',
  pre='Two weeks out, the day before and the night itself.', hero='tk-cocktail-handoff.jpg', alt='A guest bartender handing over a cocktail',
  body=lambda: kick('Week 2 · The shift') + h('Two weeks out.', 'Then showtime.') + p(HI) +
   steps([('Two weeks out', 'Send the venue your menu and a full mise en place list: every spirit, modifier, syrup, garnish and piece of glassware. The venue buys it all.'),
          ('The day before', 'Fly in, meet the team and run through everything. Prep any complicated garnishes so the night runs fast.'),
          ('6 pm – 10 pm', 'Work the menu under the venue\'s duty manager and house rules, with a bar back beside you.'),
          ('Through the night', 'Photos, a short video and a chat with the trade buyers our reps bring in.')]) +
   qa('Do I need anything special?', 'An RSA that\'s valid in the host state, and a menu you can make fast on a busy night.') +
   button('Read the bartender section', u('/bar-takeover?pack=open', TT, '01')) + tk_bar_agree()),
 dict(n='02', key='build-the-menu', day=14, subject='Build a menu a brand will back',
  pre='Two or three drinks, quick to make, with a story each.', hero='ck-three-cocktails.jpg', alt='Three cocktails on a terrace table',
  body=lambda: kick('Week 3 · The menu') + h('Two or three drinks.', 'Each with a story.') + p(HI) +
   p('Brands pick bartenders whose menus sell their product. What works:') +
   bullets(['Two or three drinks built around the brand, at least one of them simple enough to sell all night.',
            'Quick and consistent on a busy Friday: batch what you can.',
            'A short story for each drink: the flavour, the moment and why it suits the room.',
            'Ingredients a venue can buy easily, listed in full.']) +
   two_img('ck-lady-trieu.jpg', 'Lady Triệu Gin bottle', 'ck-foam-sour.jpg', 'A foam-topped sour') +
   p('Got a drink you\'re proud of? Reply with the spec and a photo and we\'ll keep it on your file for the brands.') +
   button('Reply with a drink', f'mailto:{MANNY}?subject=My%20Bar%20Takeover%20menu') + tk_bar_agree()),
 dict(n='03', key='whats-in-it', day=28, subject='What\'s in it for you',
  pre='Flights, accommodation, a stipend, a fee on some takeovers, and a new city.', hero='tk-team-toast.jpg', alt='A bar team raising cocktails',
  body=lambda: kick('Week 5 · What you get') + h('Paid to', 'take over.') + p(HI) +
   stat_row([('$500', 'Stipend for the day'), ('Up to $1,000', 'Fee on some takeovers'), ('2 nights', 'Accommodation, with return flights')], RED, SAND) +
   bullets(['Return flights and accommodation, paid by the brand.',
            'A profile, poster and posts across Drinks Network and the venue.',
            'A new city\'s bar scene, and the people in it.']) +
   button('See the full pack', u('/bar-takeover?pack=open', TT, '03')) + tk_bar_agree()),
 dict(n='04', key='keep-your-spot', day=42, subject='Still keen? Keep your spot on the list',
  pre='Tell us what\'s changed and we\'ll keep you ready for the next brand.', hero='tk-bartenders-laughing.jpg', alt='Two bartenders laughing',
  body=lambda: kick('Day 42 · Stay on the list') + h('Still keen?', 'Stay ready.') + p(HI) +
   p('Brands line up takeovers through the year, so your spot on the list stays open. Reply with anything new: where you\'re working, your Instagram, a new drink, or the cities you\'d love to take over.') +
   button('Update my details', f'mailto:{MANNY}?subject=Bar%20Takeover%20list%20update') + tk_bar_agree()),
]

# ================================================================== TASTING SERIES · VENUE
SV = 'tasting-venue'
TASTING_VENUE = [
 dict(n='00', key='welcome', day=0, subject='Meet the people behind the brand, in your room',
  pre='A ticketed distiller\'s tasting at your venue. Here is how it works.', hero='ts-tasting-room.jpg', alt='Guests at a long tasting table under pendant lights',
  body=lambda: kick('Day 0 · Welcome') + h('Meet the people', 'behind the brand.') + p(HI) +
   p(f'Thanks for asking about hosting a tasting at {CO}. It\'s a ticketed night: ${TS_PRICE} a head, five pours over about two hours, led by the distiller or the brand\'s maker. Drinks Network sells the tickets and runs the night, and your venue keeps half the net door in cash.') +
   h2('What happens next') +
   steps([('A call within one business day', 'Manuel Terron, our events lead, talks through dates, capacity and the brands that suit your room.'),
          ('Pick a date', 'You have 6 weeks to lock in a date, for a night inside 60 days of registering.'),
          ('We bring the distiller and the crowd', 'Artwork, tickets, ads and trade invites, with your venue front and centre.')]) +
   window(1, 'tasting night') + button('Open the Tasting Series brief', u('/whisky-adventure/tasting-series?brief=open', SV, '00')) + ts_venue_agree()),
 dict(n='01', key='the-money', day=7, subject=f'What one tasting night pays your venue: {money(TS_HALF)} in cash',
  pre=f'{TS_GUESTS} guests at ${TS_PRICE}, split 50/50, plus everything they buy.', hero='ts-distillers-dinner.jpg', alt='A candlelit distiller\'s dinner',
  body=lambda: kick('Week 2 · The money') + h('Half the door,', 'in cash.') + p(HI) +
   blocks([(f'{TS_GUESTS} tickets at ${TS_PRICE}', TS_GROSS, NAVY, 'Sold by Drinks Network on Eventbrite.'),
           ('Less Eventbrite fees', TS_FEES, QUIET, '5.35% + $1.19 a ticket.'),
           ('Your 50%, in cash', TS_HALF, RED, 'Paid with a sales statement after the night.')],
          ('Cash to your venue', money(TS_HALF, True)),
          'Plus every drink and plate your guests buy on the night. Food-inclusive tickets ($75 + $40–$50 food) earn your venue a higher share.') +
   table(['Guests', 'Ticket revenue', 'Your 50% after fees'], [[str(g), money(g * TS_PRICE), money((g * TS_PRICE - fees(g, TS_PRICE)) / 2, True)] for g in (20, 30, 40)], f'At ${TS_PRICE} a ticket.') +
   window(2, 'tasting night') + button('See the numbers in the brief', u('/whisky-adventure/tasting-series?brief=open', SV, '01')) + ts_venue_agree()),
 dict(n='02', key='what-hosting-involves', day=14, subject='What hosting a tasting involves',
  pre='Your room, your glassware, an opening order. We do the rest.', hero='ts-tasting-table.jpg', alt='A set tasting table with glasses',
  body=lambda: kick('Week 3 · The work') + h('Your room.', 'Their whisky.') + p(HI) +
   steps([('A main contact', 'One person at your venue, before and on the night.'),
          ('The space and the service', 'Glassware, water and bar staff for about two hours.'),
          ('Food', 'Snacks, or a food-inclusive ticket with small plates matched to the pours.'),
          ('Stock what you pour', 'An opening order of the tasted range at wholesale, on a mixed-case intro deal, so guests keep ordering it after the night.'),
          ('Promote it', 'Share the event with your guests and on your socials.')]) +
   qa('What about glassware?', 'If you need to hire tasting glasses, the cost is usually split 50/50 between your venue and the brand side.') +
   window(3, 'tasting night') + button('Read the venue section', u('/whisky-adventure/tasting-series?brief=open', SV, '02')) + ts_venue_agree()),
 dict(n='03', key='the-risk', day=21, subject='How much is at risk? Very little',
  pre='Tickets are sold before the night. The stock stays on your shelf.', hero='ts-back-bar.jpg', alt='A whisky range on a back bar',
  body=lambda: kick('Week 4 · The risk') + h('Low risk.', 'Cash upside.') + p(HI) +
   table(['You put in', 'Covered by others'], [
     ['The opening order: stock you keep selling', 'The distiller or speaker, and the tasting stock (the brand)'],
     ['Your room, glassware and staff for two hours', 'Eventbrite page, tickets, trade codes and check-in (Drinks Network)'],
     ['Snacks, or a food option', 'Artwork, social posts and paid ads (Drinks Network)'],
   ]) +
   qa('Who gets the guest list?', 'Ticket-holder and trade contacts go to the brand that funds the night, and no one else. You get the crowd, the cash and the bar sales.') +
   window(4, 'tasting night') + button('Talk it through with Manuel', f'mailto:{MANNY}?subject=Tasting%20night%20questions') + ts_venue_agree()),
 dict(n='04', key='fill-the-room', day=28, subject='Fill the room: bring your own people',
  pre='Staff join free, trade come on a $0 code, regulars buy a ticket.', hero='ts-trade-tasting.jpg', alt='Guests at a courtyard tasting',
  body=lambda: kick('Week 5 · Fill the room') + h('Bring your', 'own people.') + p(HI) +
   bullets(['Venue staff join free.', 'Your trade guests book with a trade code that takes the ticket to $0.', 'Friends and regulars book a paying ticket.', 'Every invited guest is either trade or paying. One or the other.']) +
   two_img('poster-corowa.jpg', 'Corowa Distiller\'s Tasting poster', 'poster-whisky-night.jpg', 'Australian Whisky Night poster') +
   p('We build posters like these for every night, with your venue on them, and run them across social and paid ads.') +
   window(5, 'tasting night') + p('<b>One week left to lock in your date.</b>') +
   button('Lock in your night', u('/whisky-adventure/tasting-series?brief=open#join', SV, '04')) + ts_venue_agree()),
 dict(n='05', key='the-night', day=35, subject='Your tasting night, start to finish',
  pre='From the agreement to the sales statement.', hero='ts-candlelit.jpg', alt='A candlelit tasting table',
  body=lambda: kick('Week 6 · The night') + h('Start', 'to finish.') + p(HI) +
   steps([('Lock it in', 'Complete the partner agreement online. It takes about three minutes.'),
          ('Three weeks out', 'The speaker\'s bio and headshot become the artwork. Tickets go on sale. Your opening order goes in.'),
          ('The night', 'Five pours over about two hours, with the people who make the whisky.'),
          ('Settlement', 'A sales statement to both sides, and your 50% of net ticket revenue in cash.')]) +
   window(6, 'tasting night') + p('<b>This is the last week to lock in a date.</b>') +
   button('Complete the partner agreement', u('/whisky-adventure/tasting-series?brief=open#join', SV, '05')) + ts_venue_agree()),
 dict(n='06', key='last-call', day=42, subject='Last call: lock in your tasting night',
  pre='Your 6-week window closes today.', hero='ts-pour-wall.jpg', alt='Whisky poured in front of a wall of spirits',
  body=lambda: kick('Day 42 · Last call') + h('Last call.', 'Lock in your night.') + p(HI) +
   stat_row([(f'${TS_PRICE}', 'A ticket, five pours'), ('50%', 'Of the net door, in cash'), (money(TS_HALF), f'Your share, {TS_GUESTS} guests')], RED, SAND) +
   p(f'Your 6-week window to host a tasting at {CO} closes today. Complete the agreement, or reply and Manuel will lock it in with you.') +
   button('Complete the partner agreement', u('/whisky-adventure/tasting-series?brief=open#join', SV, '06')) + ts_venue_agree()),
]

# ================================================================== TASTING SERIES · BRAND
SB = 'tasting-brand'
TASTING_BRAND = [
 dict(n='00', key='welcome', day=0, subject='Take your brand on tour: meet the people behind the brand',
  pre='Ticketed tastings led by your maker, in venues that stock you after.', hero='ts-tasting-room.jpg', alt='Guests at a long tasting table',
  body=lambda: kick('Day 0 · Welcome') + h('Your brand', 'on tour.') + p(HI) +
   p(f'Thanks for asking about taking {COB} on tour. A Drinks Network tasting puts your maker or brand ambassador in front of a ticketed room: ${TS_PRICE} a head, five pours over about two hours, in a venue that takes your range on to host it.') +
   p('There needs to be something more than the product for sale. This is it.') +
   h2('What happens next') +
   steps([('A call within one business day', 'Manuel Terron, our events lead, talks through cities, venues and your speaker.'),
          ('Six weeks to commit', 'Lock in a city, venue and date within 6 weeks.'),
          ('We run it end to end', 'Tickets, artwork, ads, trade orders on the night and six days of follow-up.')]) +
   window(1, 'tasting night') + button('Open the Tasting Series brief', u('/whisky-adventure/tasting-series?brief=open', SB, '00')) + ts_brand_agree()),
 dict(n='01', key='why-activity', day=7, subject='Product alone converts at 5–10%. People convert at 30%+',
  pre='Why a face behind the bottle changes the conversation.', hero='ts-pour-wall.jpg', alt='Whisky poured in front of a wall of spirits',
  body=lambda: kick('Week 2 · Why it works') + h('People buy', 'from people.') + p(HI) +
   p('Sell the product alone and you\'ll convert 5 to 10% of the time, 15% at best. Put an activity or a high-value offer behind it and conversion goes above 30%, and sometimes past 50%, depending on how good the offer is and who it\'s aimed at.') +
   conversion_tiles() +
   p('A tasting is that activity: your maker telling the story, the venue taking the range on, and trade guests tasting it on a $0 code.') +
   window(2, 'tasting night') + button('See how a tasting works', u('/whisky-adventure/tasting-series?brief=open', SB, '01')) + ts_brand_agree()),
 dict(n='02', key='the-investment', day=14, subject='What you\'re investing in: $1,500–$2,000 from your subscription',
  pre='About 10 hours of set-up and 4–5 hours on the night, drawn from your plan.', hero='ts-distillers-dinner.jpg', alt='A distiller\'s dinner',
  body=lambda: kick('Week 3 · The investment') + h('Part of your plan.', 'Not on top of it.') + p(HI) +
   table(['What', 'Hours', ''], [
     ['Event set-up: tickets, Eventbrite page, campaign, artwork, venue and brand coordination', '~10 hrs', ''],
     ['Event management on the night: run of show, check-in, trade liaison and orders', '4–5 hrs', ''],
     ['<b>Total investment</b>', '', '<b>$1,500–$2,000</b>'],
   ], 'Drawn from your RepShare subscription. Follow-up, attendee lists and the end-of-event report are included.') +
   p('Brand-on-tour events are built into <b>Roll Out</b> (10 hours a week, one state) and <b>Take Over</b> (15 hours a week, across two states). If you don\'t have any other plan, this is what you\'re signing up to: it\'s the way to build a brand.') +
   h2('You bring') +
   bullets(['A speaker for the night: the maker or a brand representative.', 'A short bio (80–120 words) and a high-res headshot, three weeks out.', 'The tasting line-up and stock to pour.', 'Product shots, logo, tasting notes and a trade price list.']) +
   window(3, 'tasting night') + button('See the plans', u('/brands', SB, '02')) + ts_brand_agree()),
 dict(n='03', key='what-one-night-makes', day=21, subject='What one tasting night can make: $6,449–$7,100',
  pre='Ticket credit, bottles and trade orders from a single 40-guest night.', hero='ts-back-bar.jpg', alt='A whisky range on a back bar',
  body=lambda: kick('Week 4 · The upside') + h('One night.', 'Three ways to earn.') + p(HI) +
   blocks([('Ticket credit', 1396, RED, f'Your 50% of net ticket revenue from {TS_GUESTS} guests at ${TS_PRICE}, credited to your Drinks Network account.'),
           ('Bottles on the night', 3100, NAVY, '20 bottles at $155, sold direct by the brand. Subject to liquor licensing.'),
           ('Trade orders', 2604, ORANGE, '3–4 orders of 6 bottles at wholesale, about 30% below retail ($1,953–$2,604).')],
          ('Sales value and credit', '$6,449–$7,100'),
          'Illustration only, from the Tasting Series brief. Sales value and credit before stock and other costs, not profit. Follow-up campaign sales come on top.') +
   p('Against $1,500–$2,000 drawn from your subscription.') +
   window(4, 'tasting night') + button('See the full upside', u('/whisky-adventure/tasting-series?brief=open', SB, '03')) + ts_brand_agree()),
 dict(n='04', key='brand-on-tour', day=28, subject='Brand on tour: what Corowa did with its distiller',
  pre=f'{COROWA_CONVERSION} first-order conversion with the maker in the room.', hero='ts-trade-tasting.jpg', alt='Guests at a trade tasting',
  body=lambda: kick('Week 5 · Brand on tour') + h('Put the maker', 'in the room.') + p(HI) +
   p('Corowa Distilling took Dean Druce on tour: distiller\'s tastings in Brisbane bars, ticketed, with trade guests on the list. With the maker in the room, its first-order conversion went to ' + COROWA_CONVERSION + '.') +
   corowa_block() +
   quote('Event-led selling turns a quiet month into a sales period.', 'Drinks Network') +
   window(5, 'tasting night') + p('<b>One week left to lock in your tour date.</b>') +
   button('Lock in your tour', u('/whisky-adventure/tasting-series?brief=open#join', SB, '04')) + ts_brand_agree()),
 dict(n='05', key='contacts-and-follow-up', day=35, subject='Your contacts, your follow-up',
  pre='Ticket-holders and trade guests go to you, then six days of follow-up.', hero='ts-candlelit.jpg', alt='A candlelit tasting table',
  body=lambda: kick('Week 6 · Contacts') + h('Your list.', 'Your orders.') + p(HI) +
   p('You fund the night, so the ticket-holder list and the trade attendee list come to you, and only to you. Then the follow-up starts:') +
   table(['Day', 'What happens'], [
     ['1', 'Thank-you email with tasting notes and a buy link'], ['2', 'Photo recap on social, tagging your brand and the venue'],
     ['3', 'Retargeting ads to attendees and page visitors'], ['4', 'Attendee-only bottle offer'],
     ['5', 'Trade follow-up calls and visits to close orders'], ['6', 'Last-call reminder, then your event report'],
   ]) + window(6, 'tasting night') + p('<b>This is the last week to lock in your tour.</b>') +
   button('Complete the partner agreement', u('/whisky-adventure/tasting-series?brief=open#join', SB, '05')) + ts_brand_agree()),
 dict(n='06', key='last-call', day=42, subject='Last call: book your brand\'s tour',
  pre='Your 6-week window closes today.', hero='ts-tasting-table.jpg', alt='A set tasting table',
  body=lambda: kick('Day 42 · Last call') + h('Last call.', 'Book the tour.') + p(HI) +
   stat_row([('30%+', 'Conversion with an activity'), ('$6,449+', 'Sales value, one night'), ('6 days', 'Of follow-up')], RED, SAND) +
   p(f'Your 6-week window to take {COB} on tour closes today. Complete the agreement, or reply and Manuel will lock in a city, a venue and a date with you.') +
   button('Complete the partner agreement', u('/whisky-adventure/tasting-series?brief=open#join', SB, '06')) + ts_brand_agree()),
]

ALL = {TV: TAKEOVER_VENUE, TB: TAKEOVER_BRAND, TT: TAKEOVER_BARTENDER, SV: TASTING_VENUE, SB: TASTING_BRAND}
START = {TV: 'journey:takeover-venue', TB: 'journey:takeover-brand', TT: 'journey:takeover-bartender', SV: 'journey:tasting-venue', SB: 'journey:tasting-brand'}

if __name__ == '__main__':
    rows = []
    for track, emails in ALL.items():
        os.makedirs(os.path.join(HERE, track), exist_ok=True)
        for e in emails:
            out = page(track, e['subject'], e['body'](), e['hero'], e['alt'])
            assert '{' not in out.replace('{{', '').split('<style>')[0], 'unfilled placeholder'
            name = f"{e['n']}-{e['key']}.html"
            open(os.path.join(HERE, track, name), 'w').write(out)
            rows.append([track, START[track], e['n'], e['day'], e['subject'], e['pre'], f'{track}/{name}'])
    with open(os.path.join(HERE, 'schedule.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['track', 'journey start tag', 'email', 'send on day', 'subject', 'preview text', 'file']); w.writerows(rows)
    z = os.path.join(HERE, 'event-programs-mailchimp-pack.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for r in rows:
            zf.write(os.path.join(HERE, r[6]), r[6])
        zf.write(os.path.join(HERE, 'schedule.csv'), 'schedule.csv')
        if os.path.exists(os.path.join(HERE, 'MAILCHIMP-SETUP.md')):
            zf.write(os.path.join(HERE, 'MAILCHIMP-SETUP.md'), 'MAILCHIMP-SETUP.md')
    print(len(rows), 'emails')
