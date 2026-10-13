"""Builds the San Junipero Melbourne retailer email series as Mailchimp-ready HTML.
Run: python3 emails/san-junipero/build.py  -> writes 01..07 *.html, schedule.csv and the Mailchimp pack zip.
Images load from https://site.drinksnetwork.com.au/media/san-junipero/ (in public/media/san-junipero)."""
import csv, html, os, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
IMG = 'https://site.drinksnetwork.com.au/media/san-junipero/'
PAGE = 'https://campaign.drinksnetwork.com.au/san-junipero-melbourne'
IG = 'https://www.instagram.com/drinksanjunipero/'
VOID, PAPER, GLOW, SUNSET, TORCH, PINK, VIOLET, SOL = '#101820', '#FBF6F1', '#FFBD26', '#FC5940', '#F51C40', '#FF69B5', '#732768', '#EEDBC6'
HEAD = "'Helvetica Neue',Helvetica,Arial,sans-serif"
SERIF = "Georgia,'Times New Roman',serif"

def button(label, url, bg=GLOW, fg=VOID):
    return f'''<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:8px 0 4px"><tr><td align="center" bgcolor="{bg}" style="border-radius:999px">
<a href="{url}" target="_blank" style="display:inline-block;padding:15px 30px;font:700 16px {HEAD};color:{fg};text-decoration:none;border-radius:999px">{label}</a></td></tr></table>'''

def img(src, alt, w=600):
    return f'<img src="{IMG}{src}" width="{w}" alt="{html.escape(alt)}" style="display:block;width:100%;max-width:{w}px;height:auto;border:0">'

def p(t, size=17):
    return f'<p style="margin:0 0 16px;font:400 {size}px/1.55 {HEAD};color:{VOID}">{t}</p>'

def h(t, accent=''):
    acc = f'<br><span style="font:italic 400 38px/1.05 {SERIF};color:{SUNSET};letter-spacing:-.5px">{accent}</span>' if accent else ''
    return f'<h1 style="margin:0 0 18px;font:800 40px/1.02 {HEAD};letter-spacing:-1.5px;color:{VOID}">{t}{acc}</h1>'

def kick(t, col=VIOLET):
    return f'<p style="margin:0 0 10px;font:700 12px {HEAD};letter-spacing:3px;text-transform:uppercase;color:{col}">{t}</p>'

def card(inner, bg='#FFFFFF'):
    return f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 18px"><tr><td bgcolor="{bg}" style="border-radius:18px;padding:20px 22px;font:400 16px/1.5 {HEAD};color:{VOID}">{inner}</td></tr></table>'

def packs():
    cell = lambda f, a, name: f'<td width="50%" valign="bottom" align="center" style="padding:0 6px">{img(f, a, 200)}<p style="margin:8px 0 0;font:700 13px/1.3 {HEAD};color:{VOID}">{name} four-pack<br><span style="color:{SUNSET}">RRP $20</span></p></td>'
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:14px 0 12px"><tr>'
            + cell('four-pack-limoncello.png', 'San Junipero Limoncello Spritz four-pack', 'Limoncello')
            + cell('four-pack-blood-orange.png', 'San Junipero Blood Orange Spritz four-pack', 'Blood Orange') + '</tr></table>'
            + f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0"><tr><td bgcolor="#FFFFFF" style="border-radius:14px;padding:14px 16px;font:400 14px/1.6 {HEAD};color:{VOID}">'
            + '<b style="font-size:15px">Your margin on the 5+1</b><br>RRP $20 a four-pack · your cost $8.33 · profit $9.85 a four-pack<br>'
            + f'<b style="font-size:18px;color:{SUNSET}">54% margin</b> · <b>$354.60 profit</b> on 36 four-packs'
            + '<br><span style="font-size:12px;color:#5B5550">Cost, profit and margin ex GST; RRP inc GST. RRP is a recommendation only.</span></td></tr></table>')

def stripe():
    cols = [GLOW, SUNSET, TORCH, PINK, VIOLET]
    tds = ''.join(f'<td height="6" bgcolor="{c}" style="font-size:0;line-height:0">&nbsp;</td>' for c in cols)
    return f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>{tds}</tr></table>'

HI = '*|IF:FNAME|*Hi *|FNAME|*,*|ELSE:|*Hi there,*|END:IF|*'
STORE = '*|IF:COMPANY|**|COMPANY|**|ELSE:|*your store*|END:IF|*'

def page(subject, preheader, body, hero=None, hero_alt='', why="You're receiving this because you entered the San Junipero Melbourne retailer giveaway."):
    hero_html = f'<tr><td style="padding:0">{img(hero, hero_alt)}</td></tr>' if hero else ''
    return f'''<!doctype html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="X-UA-Compatible" content="IE=edge">
<title>{html.escape(subject)}</title>
<style>body{{margin:0;padding:0;background:{PAPER}}} a{{color:{TORCH}}} @media (max-width:620px){{.px{{padding-left:22px!important;padding-right:22px!important}} h1{{font-size:32px!important}}}}</style>
</head>
<body style="margin:0;padding:0;background:{PAPER}">
<span style="display:none!important;visibility:hidden;opacity:0;color:transparent;height:0;width:0;overflow:hidden;mso-hide:all">*|MC_PREVIEW_TEXT|*</span>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{PAPER}"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:600px;background:#FFFFFF;border-radius:22px;overflow:hidden">
<tr><td bgcolor="{VOID}" style="padding:20px 30px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
<td><img src="{IMG}san-junipero-logo.png" width="120" alt="San Junipero" style="display:block;width:120px;height:auto;border:0"></td>
<td align="right" style="font:500 12px {HEAD};color:{SOL}">Melbourne retailer giveaway</td></tr></table></td></tr>
<tr><td>{stripe()}</td></tr>
{hero_html}
<tr><td class="px" style="padding:34px 40px 18px">{body}</td></tr>
<tr><td bgcolor="{SOL}" style="padding:22px 40px;font:400 14px/1.5 {HEAD};color:{VOID}" class="px">
<b>Buy 5 + 1. Ride away.</b> Every qualifying 5+1 order registered by Friday 18 December 2026 is an entry. Two San Junipero eBikes drawn 21 December 2026.<br>
<a href="{PAGE}#enter" style="color:{VIOLET};font-weight:700">Register a 5+1 order</a> &nbsp;·&nbsp; <a href="{IG}" style="color:{VIOLET};font-weight:700">@drinksanjunipero</a></td></tr>
<tr><td bgcolor="{VOID}" style="padding:24px 40px;font:400 12px/1.6 {HEAD};color:#BDB5AD" class="px">
San Junipero, presented by Drinks Network. Prizes supplied by CoLab Wines. Promotion terms and final prize details as published on the campaign page. For licensed retailers. Please enjoy San Junipero responsibly.<br><br>
{why} <a href="*|UPDATE_PROFILE|*" style="color:{GLOW}">Update preferences</a> · <a href="*|UNSUB|*" style="color:{GLOW}">Unsubscribe</a><br>
*|LIST:ADDRESSLINE|*</td></tr>
</table></td></tr></table>
</body></html>'''

EMAILS = [
 dict(n='00', key='intro-launch', when='Launch, to Melbourne retailers', date='Thu 15 Oct 2026',
  subject='Buy 5 + 1. Ride away. 🚲 Win a San Junipero eBike', pre='Melbourne retailers: buy five cases, get the sixth free and go into the draw for an eBike.',
  hero='email-hero.jpg', alt='Rider on a San Junipero eBike at sunset', why="You're receiving this as a Drinks Network trade contact.",
  body=lambda: kick('New for Melbourne retailers') + h('Buy 5 + 1.', 'Ride away.') + p(HI) +
   p('San Junipero is the wine-based spritz that brings California sunset to the fridge, in <b>Limoncello</b> and <b>Blood Orange</b>. This summer, every 5+1 case deal puts your store in the draw to win one of <b>two San Junipero eBikes</b>.') +
   card(f'<p style="margin:0 0 6px;font:700 12px {HEAD};letter-spacing:3px">5 + 1 CASE DEAL</p><p style="margin:0;font:800 46px/1 {HEAD};color:{SUNSET};letter-spacing:-1.5px">$299.95</p><p style="margin:8px 0 0">ex GST for five cases at $59.99 each. <b>24 cans per case.</b> Receive six cases / 36 four-packs.</p>' + packs() + '<p style="margin:10px 0 0;font-size:13px;color:#5B5550">250 mL cans · 8% ABV. For licensed retailers. Trade pricing from the current sell card.</p>', '#FFEEC9') +
   f'''<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0 0 18px"><tr>
<td width="33%" valign="top" style="padding-right:8px;font:400 14px/1.45 {HEAD}"><p style="margin:0;font:800 28px {HEAD};color:{SUNSET}">01</p><b>Buy the 5+1</b><br>Order five cases, receive a sixth free.</td>
<td width="33%" valign="top" style="padding:0 4px;font:400 14px/1.45 {HEAD}"><p style="margin:0;font:800 28px {HEAD};color:{SUNSET}">02</p><b>Scan and register</b><br>Enter your order and a picnic answer, 100 words or less.</td>
<td width="33%" valign="top" style="padding-left:8px;font:400 14px/1.45 {HEAD}"><p style="margin:0;font:800 28px {HEAD};color:{SUNSET}">03</p><b>You're in the draw</b><br>One entry per 5+1. Drawn 21 December 2026.</td></tr></table>''' +
   button('See the offer and enter', PAGE) +
   p('Register purchases by <b>Friday 18 December 2026</b>. Talk to your Drinks Network rep to place your order.', 15)),
 dict(n='01', key='confirmation', when='Immediately, when an entry arrives', date='On entry',
  subject="You're in the running for a San Junipero eBike 🚲", pre="Your 5+1 entry is in. Two eBikes drawn 21 December 2026.",
  hero='email-hero.jpg', alt='Rider on a San Junipero eBike at sunset',
  body=lambda: kick('Entry received') + h('Congratulations!', "You're in the running.") +
   p(f'{HI}') + p(f'Thanks for registering your 5+1 order. <b>{STORE}</b> is now in the draw to win one of two San Junipero eBikes. Winners are drawn on <b>21 December 2026</b>, in time for Christmas, and we\'ll email you the result.') +
   card('<b>More deals, more chances.</b> Every extra 5+1 order you register by Friday 18 December is another entry.', '#FFEEC9') +
   card(f'<b>Win a spa retreat.</b> Follow <a href="{IG}">@drinksanjunipero</a> on Instagram for the spa retreat giveaway.', '#FFD9ED') +
   button('Register another 5+1', PAGE + '#enter') + p('Keep an eye on your inbox: between now and Christmas we\'ll send serve ideas, display tips and a few reminders before the draw.', 15)),
 dict(n='02', key='fridge', when='Follow-up 1', date='Tue 20 Oct 2026',
  subject='Make the fridge glow ☀️', pre='Three quick ways to sell more San Junipero this week.', hero='email-cans.jpg', alt='Limoncello and Blood Orange Spritz cans',
  body=lambda: kick('In store') + h('Make the fridge glow.', 'Sunset sells.') + p(HI) +
   p('San Junipero sells on sight. A few small moves make the colour do the work:') +
   card('<b>1. Eye level, side by side.</b> Limoncello next to Blood Orange: the yellow-to-pink gradient stops shoppers.<br><br><b>2. Cold and front.</b> Spritz is an impulse buy. Keep a facing in the door of the fridge.<br><br><b>3. Next to the prosecco.</b> Place it beside aperitivo and sparkling: it\'s the easy, lighter alternative.', '#FBF6F1') +
   button('Register your 5+1 order', PAGE + '#enter')),
 dict(n='03', key='serve', when='Follow-up 2', date='Tue 27 Oct 2026',
  subject='The perfect San Junipero serve 🍋', pre='Big glass, lots of ice, one slice. That\'s it.', hero=None,
  body=lambda: kick('The serve') + h('The perfect serve.', 'Big glass. Lots of ice.') + p(HI) +
   p('Share this with your team and customers: the serve is half the fun.') +
   f'''<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0 0 18px"><tr>
<td width="50%" valign="top" style="padding-right:8px">{img('pour-2.gif','Limoncello Spritz poured over ice with lemon',280)}<p style="margin:10px 0 0;font:700 15px {HEAD}">Limoncello Spritz</p><p style="margin:4px 0 0;font:400 14px/1.5 {HEAD}">Wine glass, ice to the top, a lemon wheel. Pour slowly.</p></td>
<td width="50%" valign="top" style="padding-left:8px">{img('pour-1.gif','Blood Orange Spritz poured over ice with blood orange',280)}<p style="margin:10px 0 0;font:700 15px {HEAD}">Blood Orange Spritz</p><p style="margin:4px 0 0;font:400 14px/1.5 {HEAD}">Wine glass, ice, a blood orange slice. Sunset in a glass.</p></td></tr></table>''' +
   card('<b>Tip:</b> open a can for the team at the start of a shift. Staff who\'ve tasted it sell it.', '#FFEEC9') + button('Register your 5+1 order', PAGE + '#enter')),
 dict(n='04', key='spa', when='Follow-up 3', date='Tue 10 Nov 2026',
  subject='Win a spa retreat with San Junipero 🌴', pre='Follow @drinksanjunipero on Instagram for the spa retreat giveaway.', hero='email-cans-cold.jpg', alt='An ice-cold Blood Orange Spritz can',
  body=lambda: kick('Instagram', PINK) + h('Win a spa retreat.', 'Follow along on Instagram.') + p(HI) +
   p(f'San Junipero is giving away a spa retreat on Instagram. Follow <a href="{IG}"><b>@drinksanjunipero</b></a> for the details and how to enter.') +
   p('While you\'re there, tag @drinksanjunipero in your fridge or display photos. We love sharing our stockists.') +
   button('Follow @drinksanjunipero', IG, PINK, '#FFFFFF') + p('Spa retreat giveaway terms are on Instagram and separate from the eBike draw.', 13)),
 dict(n='05', key='double', when='Follow-up 4', date='Tue 24 Nov 2026',
  subject='Double your chances to win an eBike 🚲🚲', pre='Every extra 5+1 order is another entry. Here\'s the deal.', hero='email-hero.jpg', alt='Rider on a San Junipero eBike',
  body=lambda: kick('More chances') + h('Double your chances.', 'One more 5+1.') + p(HI) +
   p('Every qualifying 5+1 order you register is another entry in the draw for one of two San Junipero eBikes. Running low? Now\'s the time to reorder before the Christmas rush.') +
   card(f'<p style="margin:0 0 6px;font:700 12px {HEAD};letter-spacing:3px">5 + 1 CASE DEAL</p><p style="margin:0;font:800 46px/1 {HEAD};color:{SUNSET};letter-spacing:-1.5px">$299.95</p><p style="margin:8px 0 0">ex GST for five cases at $59.99 each. <b>24 cans per case.</b> Receive six cases / 36 four-packs.</p>' + packs() + '<p style="margin:10px 0 0;font-size:13px;color:#5B5550">Trade pricing from the current sell card; confirm availability with your representative.</p>', '#FFEEC9') +
   button('Register your next 5+1', PAGE + '#enter')),
 dict(n='06', key='picnic', when='Follow-up 5', date='Tue 8 Dec 2026',
  subject='Where would you ride for a picnic? 🧺', pre='Picnic season is here, Christmas is close, and entries close Friday 18 December.', hero='email-pour.jpg', alt='Limoncello Spritz poured over ice with lemon',
  body=lambda: kick('Picnic season') + h('Picnic season.', 'Pack the Spritz.') + p(HI) +
   p('Summer in Melbourne means picnics, and San Junipero is made for them: light, bright and easy in a can. A few spots our team loves for a ride and a picnic:') +
   card('<b>Albert Park Lake</b> · golden hour by the water<br><b>Edinburgh Gardens</b> · Fitzroy North, shade and lawn<br><b>St Kilda foreshore</b> · sea breeze and sunset<br><b>Williamstown</b> · bay views across to the city', '#FBF6F1') +
   p('Make sure your customers can grab one on the way: keep it cold and up front.') + button('Register your 5+1 order', PAGE + '#enter')),
 dict(n='07', key='last-call', when='Follow-up 6', date='Tue 15 Dec 2026',
  subject='Last call: register your 5+1 by Friday 18 December ⏰', pre='Entries close this Friday. Two eBikes drawn 21 December, just before Christmas.', hero='email-hero.jpg', alt='Rider on a San Junipero eBike at sunset',
  body=lambda: kick('Last call', TORCH) + h('Last call.', 'Three days to enter.') + p(HI) +
   p('Entries close on <b>Friday 18 December 2026</b>. If you\'ve placed a 5+1 order that isn\'t registered yet, enter it now. Every qualifying order is another chance.') +
   card('<b>Draw:</b> Monday 21 December 2026, before Christmas<br><b>Prizes:</b> two San Junipero eBikes, supplied by CoLab Wines<br><b>Winners:</b> contacted by email', '#FFEEC9') +
   button('Register by Friday 18 December', PAGE + '#enter') + p('Good luck, and thanks for bringing a bit of sunset to your fridge.', 15)),
]

def main():
    rows = []
    for e in EMAILS:
        fn = f"{e['n']}-{e['key']}.html"
        with open(os.path.join(HERE, fn), 'w') as f:
            f.write(page(e['subject'], e['pre'], e['body'](), e.get('hero'), e.get('alt', ''), **({'why': e['why']} if 'why' in e else {})))
        rows.append([e['n'], e['when'], e['date'], e['subject'], e['pre'], fn])
    with open(os.path.join(HERE, 'schedule.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['#', 'When', 'Send date', 'Subject line', 'Preview text', 'HTML file']); w.writerows(rows)
    z = os.path.join(HERE, 'san-junipero-mailchimp-pack.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for r in rows: zf.write(os.path.join(HERE, r[5]), r[5])
        zf.write(os.path.join(HERE, 'schedule.csv'), 'schedule.csv')
        if os.path.exists(os.path.join(HERE, 'MAILCHIMP-SETUP.md')): zf.write(os.path.join(HERE, 'MAILCHIMP-SETUP.md'), 'MAILCHIMP-SETUP.md')
    print('\n'.join(' | '.join(r) for r in rows))

if __name__ == '__main__':
    main()
