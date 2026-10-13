"""Builds the RepShare 90-day nurture email tracks (Vendor, Rep, Partner) as Mailchimp-ready HTML.
Run: python3 emails/repshare-nurture/build.py
 -> writes <track>/<nn>-<key>.html, schedule.csv and repshare-nurture-mailchimp-pack.zip.
Images load from https://site.drinksnetwork.com.au/media/nurture/ (public/media/nurture, rendered from
campaign-assets/repshare-nurture/devices/scenes.html).
Every number here is published on the site (brands, reps, retail, repshare-app, legal pages). Change it there first."""
import csv, html, os, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://site.drinksnetwork.com.au'
IMG = SITE + '/media/nurture/'
LOGO = SITE + '/media/logos/drinks-network-repshare-white.png'
RED, RED_DARK, NAVY, PAPER, SAND, INK, BODY, QUIET, PINK = '#E42E2E', '#B81F24', '#1E2552', '#FBF7F0', '#F1E9DC', '#111111', '#3A3631', '#5A554D', '#FFE3E0'
DISPLAY = "Anton,Impact,'Arial Narrow Bold','Helvetica Neue',Arial,sans-serif"
NARROW = "'Archivo Narrow','Arial Narrow','Helvetica Neue',Arial,sans-serif"
SERIF = "'Source Serif 4',Georgia,'Times New Roman',serif"
SANS = "'Helvetica Neue',Helvetica,Arial,sans-serif"
HI = '*|IF:FNAME|*Hi *|FNAME|*,*|ELSE:|*Hi there,*|END:IF|*'
BRAND = '*|IF:COMPANY|**|COMPANY|**|ELSE:|*your brand*|END:IF|*'


def u(path, track, n):
    sep = '&' if '?' in path else '?'
    return f'{SITE}{path}{sep}utm_source=mailchimp&utm_medium=email&utm_campaign=nurture-{track}&utm_content=email-{n}'


def nw(t):
    """Keep the last two words together so a line never ends on one lonely word."""
    parts = t.rsplit(' ', 2)
    if len(parts) == 3 and '<' not in parts[1] + parts[2] and '>' not in parts[1] + parts[2]:
        return f'{parts[0]} {parts[1]}&nbsp;{parts[2]}'
    return t


def button(label, url, bg=RED, fg='#FFFFFF'):
    return f'''<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:10px 0 6px"><tr><td align="center" bgcolor="{bg}" style="border-radius:6px">
<a href="{url}" target="_blank" style="display:inline-block;padding:15px 28px;font:700 16px {NARROW};letter-spacing:1px;text-transform:uppercase;color:{fg};text-decoration:none;border-radius:6px">{label}</a></td></tr></table>'''


def img(src, alt, w=600):
    return f'<img src="{IMG}{src}" width="{w}" alt="{html.escape(alt)}" style="display:block;width:100%;max-width:{w}px;height:auto;border:0">'


def p(t, size=17, col=BODY):
    return f'<p style="margin:0 0 16px;font:400 {size}px/1.6 {SERIF};color:{col}">{nw(t)}</p>'


def h(t, accent=''):
    acc = f'<br><span style="color:{RED}">{accent}</span>' if accent else ''
    return f'<h1 style="margin:0 0 18px;font:400 44px/1.04 {DISPLAY};text-transform:uppercase;letter-spacing:.3px;color:{NAVY}">{t}{acc}</h1>'


def h2(t):
    return f'<h2 style="margin:26px 0 10px;font:700 15px {NARROW};letter-spacing:2px;text-transform:uppercase;color:{RED}">{t}</h2>'


def kick(t):
    return f'<p style="margin:0 0 10px;font:700 13px {NARROW};letter-spacing:3px;text-transform:uppercase;color:{RED}">{t}</p>'


def card(inner, bg=SAND):
    return f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 18px"><tr><td bgcolor="{bg}" style="border-radius:10px;padding:20px 22px;font:400 16px/1.55 {SERIF};color:{BODY}">{inner}</td></tr></table>'


def qa(q, a):
    """The 'straight answer' box: one hard question asked before they ask it."""
    return card(f'<p style="margin:0 0 8px;font:700 13px {NARROW};letter-spacing:2px;text-transform:uppercase;color:{RED}">Straight answer</p>'
                f'<p style="margin:0 0 8px;font:400 22px/1.15 {DISPLAY};text-transform:uppercase;color:{NAVY}">{q}</p>'
                f'<p style="margin:0;font:400 16px/1.6 {SERIF};color:{BODY}">{nw(a)}</p>', PINK)


def steps(rows):
    tds = ''.join(f'<tr><td valign="top" width="44" style="padding:0 12px 14px 0;font:400 30px/1 {DISPLAY};color:{RED}">{n:02d}</td>'
                  f'<td valign="top" style="padding:0 0 14px;font:400 16px/1.5 {SERIF};color:{BODY}"><b style="font:700 16px {NARROW};letter-spacing:.5px;color:{NAVY};text-transform:uppercase">{t}</b><br>{nw(d)}</td></tr>'
                  for n, (t, d) in enumerate(rows, 1))
    return f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 10px">{tds}</table>'


def table(head, rows, note=''):
    th = ''.join(f'<th align="left" style="padding:8px 8px;font:700 12px {NARROW};letter-spacing:1px;text-transform:uppercase;color:#FFFFFF;background:{NAVY}">{c}</th>' for c in head)
    tr = ''.join('<tr>' + ''.join(f'<td style="padding:9px 8px;border-bottom:1px solid #E6DCCB;font:400 15px/1.4 {SERIF};color:{BODY}">{c}</td>' for c in r) + '</tr>' for r in rows)
    n = f'<p style="margin:6px 0 0;font:400 12px/1.5 {SANS};color:{QUIET}">{note}</p>' if note else ''
    return f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 18px;border-collapse:collapse"><tr>{th}</tr>{tr}</table>{n}'


def stat_row(items):
    tds = ''.join(f'<td width="{100 // len(items)}%" valign="top" style="padding:0 6px"><p style="margin:0;font:400 34px/1 {DISPLAY};color:{RED}">{n}</p><p style="margin:6px 0 0;font:700 12px/1.35 {NARROW};letter-spacing:.5px;text-transform:uppercase;color:{NAVY}">{l}</p></td>' for n, l in items)
    return f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:8px 0 20px"><tr>{tds}</tr></table>'


WHY = {
    'vendor': "You're receiving this because you asked about RepShare for your brand on site.drinksnetwork.com.au.",
    'rep': "You're receiving this because you signed up to work as a RepShare rep on site.drinksnetwork.com.au.",
    'partner': "You're receiving this because you asked about partnering with Drinks Network on site.drinksnetwork.com.au.",
}
LABEL = {'vendor': 'RepShare for brands', 'rep': 'RepShare reps', 'partner': 'RepShare partners'}


def page(track, subject, preheader, body, hero, hero_alt):
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
<tr><td bgcolor="{NAVY}" style="padding:18px 30px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
<td><img src="{LOGO}" width="150" alt="Drinks Network RepShare" style="display:block;width:150px;height:auto;border:0"></td>
<td align="right" style="font:700 12px {NARROW};letter-spacing:2px;text-transform:uppercase;color:#FFFFFF">{LABEL[track]}</td></tr></table></td></tr>
<tr><td height="6" bgcolor="{RED}" style="font-size:0;line-height:0">&nbsp;</td></tr>
<tr><td style="padding:0">{img(hero, hero_alt)}</td></tr>
<tr><td class="px" style="padding:34px 40px 30px">{body}
<p style="margin:22px 0 0;font:400 16px/1.6 {SERIF};color:{BODY}">Questions? Just reply to this email and the team will come back to you.<br><b>The Drinks Network team</b></p></td></tr>
<tr><td bgcolor="{NAVY}" style="padding:24px 40px;font:400 12px/1.6 {SANS};color:#C9CCE0">
<b style="color:#FFFFFF">Drinks Network Pty Ltd</b> · ABN 89 680 725 802 · Sydney · Melbourne · Brisbane<br>
{WHY[track]}<br>
<a href="*|UPDATE_PROFILE|*" style="color:#FFFFFF">Update preferences</a> · <a href="*|UNSUB|*" style="color:#FFFFFF">Unsubscribe</a><br>*|LIST:ADDRESSLINE|*</td></tr>
</table></td></tr></table></body></html>'''


# ------------------------------------------------------------------ VENDOR (tag Vendor)
V = 'vendor'
VENDOR = [
 dict(n='00', key='welcome', day=0, subject='Your sales team on tap starts here',
  pre='What happens next, and what RepShare does for your brand.', hero='dual-vendor-dashboard.jpg',
  alt='RepShare vendor dashboard on a laptop and the app on a phone',
  body=lambda: kick('Day 0 · Welcome') + h('A sales team on tap.', 'No salaries. No lock-ins.') + p(HI) +
   p(f'Thanks for asking about RepShare for {BRAND}. RepShare gives emerging brands seasoned reps (bartenders, brand ambassadors, ex-wholesaler sales) for 5 to 15 hours a week in Sydney, Melbourne and Brisbane. They already know the buyers.') +
   h2('What happens next') +
   steps([('A call within one business day', 'Manuel, Joe, Emma or Hayden calls to confirm your start date, cities and first circuit.'),
          ('Your listings as drafts', 'We set up your product listings from your website as drafts for you to approve. Nothing goes live until you approve it.'),
          ('Your first circuit', 'The venues your reps will work, picked from 31,000+ licensed venues down the east coast.')]) +
   p('Over the next 90 days we will send you one email a fortnight. Each one shows a part of the platform and answers the questions brands ask us before they sign.') +
   qa('Do I need to download anything?', 'No. RepShare is a web app that runs in the browser on any phone or computer. Your dashboard is live 24/7.') +
   button('See the plans', u('/brands', V, '00'))),
 dict(n='01', key='cost-and-break-even', day=14, subject='What RepShare costs, and when you break even',
  pre='The plans, the hourly rates and a simple break-even sum for your brand.', hero='dual-funded-hours.jpg',
  alt='Funded hours dashboard on a laptop and a rep booking on a phone',
  body=lambda: kick('Day 14 · Cost and break-even') + h('What it costs.', 'And when it pays back.') + p(HI) +
   p('A subscription buys your brand a set number of RepShare hours each week, billed monthly from your wallet. Move up, down or top up as you grow.') +
   table(['Plan', 'Hours a week', 'Per month', 'Hourly rate'],
         [['Kickstart', '5', '$2,695', '$95–$115'], ['Roll Out', '10', '$4,180', '$85–$105'], ['Take Over', '15', '$5,610', '$75–$95'], ['Campaigner', '25+', 'Priced with you', 'Quoted per campaign']],
         'Monthly prices include GST, as published on our Brands page. Cars, phones, tolls and parking are included.') +
   h2('Your break-even sum') +
   p('Break-even is the number of cases a month whose gross profit covers your monthly RepShare cost: your plan, plus any usage above its allowance.') +
   card(f'<p style="margin:0;font:400 24px/1.25 {DISPLAY};text-transform:uppercase;color:{NAVY}">Monthly cost ex GST ÷ your gross profit per case = cases a month to break even</p>', SAND) +
   p('For example, Kickstart is $2,450 a month ex GST. With no usage above the allowance and $60 gross profit a case, that is about 41 cases a month across all the venues your reps open and re-order. Put your own margin in: the sum is the same.', 16) +
   p('Two things shorten it: the $500 credit off your first month, and reorders. When a venue orders your brand again, a repeat-order credit comes back off your usage.', 16) +
   qa('What if it doesn’t work?', 'Every plan has a 30-day pro-rata money-back guarantee on your first month, and no lock-ins. Targets and KPIs are goals, not guarantees: nobody can promise sales, but you can see every hour and every visit.') +
   button('Compare the plans', u('/brands#packages', V, '01'))),
 dict(n='02', key='build-a-circuit', day=28, subject='Build your first circuit',
  pre='Pick the venues, attach an offer, and every account on the circuit gets it.', hero='dual-circuit.jpg',
  alt='Adding venues to a circuit on a laptop and the jobs list on a phone',
  body=lambda: kick('Day 28 · Circuits') + h('Build a circuit.', 'Aim at the right doors.') + p(HI) +
   p('A circuit is the list of venues your reps work. You build it from 31,000+ licensed venues across QLD, NSW and VIC.') +
   steps([('Search', 'Narrow by name, suburb, venue type and distance.'),
          ('Select', 'See each venue with photos, contacts and a map link. Venues already on your books are marked.'),
          ('Attach an offer', 'Add an intro deal and every account on the circuit gets it.'),
          ('Hand it to your reps', 'The circuit becomes jobs in your reps’ app.')]) +
   p('Venue types to choose from include bars, hotels, pubs, bottle shops and restaurants.') +
   qa('Which venues will my reps actually visit?', 'The ones on your circuit. You see the list, you can change it, and your first 10 site visits are lined up before day one, with a typical 20–30% conversion.') +
   button('See how circuits work', u('/repshare-app', V, '02'))),
 dict(n='03', key='leads-to-jobs', day=42, subject='From lead to job: how your hours are spent',
  pre='Job stages, 30-minute bookings, and why a third charge is held for review.', hero='two-phones-jobs.jpg',
  alt='The jobs list and a job with an on-job timer on two phones',
  body=lambda: kick('Day 42 · Jobs and hours') + h('Every lead is a job.', 'Every hour is accounted for.') + p(HI) +
   p('Each venue on a circuit becomes a job. Your reps work it through clear stages, and the app closes jobs that go nowhere so your hours don’t drift.') +
   table(['Stage', 'How long it can sit'], [['New job', 'Up to 2 weeks'], ['In progress', 'Up to 1 month'], ['First order', 'Up to 1 month'], ['Cold', 'Archived after 1 month'], ['Dead', 'Archived after 2 weeks']]) +
   h2('How hours are charged') +
   steps([('30 minutes', 'A standard field booking, per brand, per customer. Up to an hour for tastings, training or negotiations.'),
          ('Two charges, then an order', 'A rep can charge a venue twice before a first order. A third charge is held for review.'),
          ('30 days to act', 'An allocated job not actioned in 30 days can be reassigned.')]) +
   qa('How do I know my hours aren’t wasted?', 'Every visit is logged with a timer, an outcome and notes. Hours are charged in 15-minute blocks and show in your funded-hours dashboard as approved, pending or remaining.') +
   button('See the app', u('/repshare-app', V, '03'))),
 dict(n='04', key='orders', day=56, subject='How orders are processed: ALM, Paramount, ILG or direct',
  pre='Your reps close; the venue orders through the channel it already uses.', hero='dual-orders.jpg',
  alt='Vendor dashboard of ordering venues on a laptop and a visit outcome on a phone',
  body=lambda: kick('Day 56 · Orders') + h('They close it.', 'The venue orders its way.') + p(HI) +
   p('A RepShare order goes through one of four channels: your wholesaler or direct with you.') +
   stat_row([('ALM', 'Wholesaler'), ('Paramount', 'Wholesaler'), ('ILG', 'Wholesaler'), ('Direct', 'From you')]) +
   steps([('Listed first', 'As part of your launch we list your products with wholesalers, so venues can order the moment a rep closes.'),
          ('Order logged', 'The rep logs the order against the job and the venue moves to First order.'),
          ('You see it', 'Your vendor dashboard shows ordering venues, order value, repeat venues and account performance.')]) +
   p('Billing follows the work: venues worked, jobs run and orders processed are counted as they happen. Venues nobody touched are never charged, and reorders earn a repeat-order credit.', 16) +
   qa('Do I need a wholesaler before I start?', 'No. Getting listed is part of the first 30 days. If a venue prefers to buy direct, that works too.') +
   button('See the vendor dashboard', u('/repshare-app', V, '04'))),
 dict(n='05', key='hard-questions', day=70, subject='The hard questions brands ask us, answered',
  pre='Guarantees, cancelling, hiring a rep, and what we can’t promise.', hero='dual-proof.jpg',
  alt='Funded hours on a laptop and visit notes on a phone',
  body=lambda: kick('Day 70 · Straight answers') + h('The hard questions.', 'Answered before you ask.') + p(HI) +
   p('These are the questions experienced brand owners put to us before they sign. Here are the answers in writing.') +
   qa('Can I cancel?', 'Yes. There are no lock-ins. Give 30 days’ notice. Any unused balance is refunded within 14 days of your final statement, less work done and costs already committed.') +
   qa('Do my reps carry other brands?', 'Yes. One rep visit can present several brands. Field bookings are charged per brand, per customer, so you pay only for time booked to yours.') +
   qa('Can I hire a rep I meet through you?', 'Yes. A placement fee of 30% of their first-year pay applies if you hire them within 12 months.') +
   qa('How do I pay?', 'From a prepaid wallet, by direct debit (preferred) or card. You are alerted when the balance falls below 20% of one billing period, and unused funds roll over while you subscribe.') +
   qa('Will you guarantee sales?', 'No one honestly can. What you get is every visit logged, every hour approved before it’s charged, and a 30-day pro-rata money-back guarantee on your first month.') +
   button('Read the payment terms', u('/legal/payment-terms', V, '05'), NAVY)),
 dict(n='06', key='first-30-days', day=84, subject='Your first 30 days with RepShare',
  pre='Wholesaling, targeting and strategy in a 24-hour launch campaign, plus $500 off.', hero='dual-splash.jpg',
  alt='The Drinks Network RepShare app on a laptop and a phone',
  body=lambda: kick('Day 84 · Ready to start') + h('Your first 30 days.', 'Planned before day one.') + p(HI) +
   p('Every plan includes a 24-hour sales, strategy and awareness campaign in your first 30 days:') +
   steps([('Wholesaling', 'We list your products with wholesalers so venues can order the moment a rep closes.'),
          ('Targeting', 'Your first 10 site visits lined up before day one, with a typical 20–30% conversion.'),
          ('Strategy', 'Brand learning, a strategy document, a sales kit and a launch campaign your reps run from.')]) +
   card(f'<p style="margin:0 0 6px;font:400 26px/1.1 {DISPLAY};text-transform:uppercase;color:{NAVY}">What a 60-day retail run looked like</p><p style="margin:0">A spirits brand with two products sold <b>60 cases across 16 stores in 60 days</b> in a national bottle-shop chain, with tastings every weekend and photo proof of every visit.</p>') +
   p('Claim a $500 credit off your first month when you start. Pick a plan, and we’ll call you within one business day.') +
   button('Start with RepShare', u('/start?role=vendor', V, '06'))),
]

# ------------------------------------------------------------------ REP (tag Rep)
R = 'rep'
REP = [
 dict(n='00', key='welcome', day=0, subject='Welcome to RepShare: here’s how the work works',
  pre='Pick your jobs, work the venues you know, get paid in days.', hero='dual-rep-earnings.jpg',
  alt='Rep earnings dashboard on a laptop and a job booking on a phone',
  body=lambda: kick('Day 0 · Welcome') + h('Sell what you love.', 'On your hours.') + p(HI) +
   p('Thanks for signing up to rep with RepShare. Brands book experienced trade people like you for 5 to 15 hours a week to open doors, run tastings and win orders in Sydney, Melbourne and Brisbane.') +
   steps([('Apply', 'Pick your city and tell us who you know. Takes three minutes.'),
          ('Get set up', '24 hours of onboarding: product knowledge, targets, go-to-market.'),
          ('Take jobs', 'Assignments land in the RepShare app. Accept the ones you want.'),
          ('Get paid', 'Cash out and you are paid within 7 days. Most payments arrive much sooner.')]) +
   qa('What do I need?', 'A current ABN, an RSA for any job involving alcohol, and a phone. RepShare is a web app, so there’s nothing to download.') +
   p('Every fortnight for the next 90 days we’ll send one email showing a part of the job and the app.') +
   button('Finish your profile', u('/start?role=rep', R, '00'))),
 dict(n='01', key='what-you-earn', day=14, subject='What you can earn as a RepShare rep',
  pre='Field rates, a worked month, and the 5% Super Sale bonus.', hero='dual-rep-earnings.jpg',
  alt='Rep dashboard showing earnings, cash-outs, hours and first orders',
  body=lambda: kick('Day 14 · Earnings') + h('$47.50 to $70.', 'An hour, in the field.') + p(HI) +
   p('You earn a share of the rate the brand pays for each job. Field rates run between $47.50 and $70 an hour, for 5 to 15 hours a week.') +
   card(f'<p style="margin:0 0 8px;font:700 13px {NARROW};letter-spacing:2px;text-transform:uppercase;color:{RED}">A worked month</p>'
        f'<p style="margin:0">10 hours a week × $47.50 × 4.33 weeks = <b>$2,057</b><br>Plus a 5% Super Sale bonus on each single order over $1,000: $5,000 of big orders adds <b>$250</b>.</p>'
        f'<p style="margin:10px 0 0;font:400 30px/1 {DISPLAY};color:{NAVY}">$2,307 a month</p>'
        f'<p style="margin:6px 0 0;font:400 12px {SANS};color:{QUIET}">Indicative only. Try your own hours on the earnings calculator.</p>') +
   qa('When do I get paid?', 'Submit your charges, they’re approved, then cash out. We pay within 7 days of cashing out, and most payments arrive much sooner. You’re paid for approved work even if the brand hasn’t paid us yet.') +
   button('Try the earnings calculator', u('/reps', R, '01'))),
 dict(n='02', key='four-taps', day=28, subject='Four taps from visit to charge',
  pre='Open the job, tap Charges, pick the template, add notes and save.', hero='four-taps.jpg',
  alt='Four phone screens: jobs list, charges with a timer, charge template, visit notes',
  body=lambda: kick('Day 28 · The app') + h('Four taps.', 'From visit to charge.') + p(HI) +
   p('Logging a visit is four taps on your phone:') +
   steps([('Open Jobs', 'Open the Jobs tab and select the job.'),
          ('Tap Charges', 'Select your booking and start the on-job timer at the venue.'),
          ('Charge template', 'Pick Field, Desk, Service or Custom. A standard venue visit is 30 minutes.'),
          ('Notes and save', 'Tag the outcome with quick chips, add real notes, and save.')]) +
   qa('Why do notes matter so much?', 'Your notes are what the brand reads. Quick chips help, but they don’t replace a line about who you spoke to and what happens next.') +
   button('See the app', u('/repshare-app', R, '02'))),
 dict(n='03', key='circuits-and-jobs', day=42, subject='How circuits turn into your jobs',
  pre='Brands build circuits of venues; you work them as jobs, at your pace.', hero='dual-rep-circuit.jpg',
  alt='Venue search for a circuit on a laptop and the jobs list on a phone',
  body=lambda: kick('Day 42 · Circuits') + h('Work the circuit.', 'Win the first order.') + p(HI) +
   p('Brands build circuits: lists of venues picked from 31,000+ licensed venues, often with an intro offer attached. Each venue becomes a job in your app.') +
   table(['Job stage', 'What it means'], [['New job', 'Yours to start, within 2 weeks'], ['In progress', 'Visited, working towards an order'], ['First order', 'The venue has ordered'], ['Cold or dead', 'Archived so your list stays clean']]) +
   p('You can charge a venue twice before a first order; a third charge is held for review. A job you don’t action within 30 days can be reassigned.', 16) +
   qa('Can I choose my jobs?', 'Yes. Assignments land in the app and you accept the ones you want.') +
   button('See open jobs', u('/reps', R, '03'))),
 dict(n='04', key='processing-orders', day=56, subject='Processing orders, and the Super Sale bonus',
  pre='ALM, Paramount, ILG or direct: log it in the app and it counts.', hero='two-phones-orders.jpg',
  alt='A charge template and a visit outcome on two phones',
  body=lambda: kick('Day 56 · Orders') + h('Close it.', 'Log it. Get the credit.') + p(HI) +
   p('When a venue says yes, the order is placed with the brand or its wholesaler:') +
   stat_row([('ALM', 'Wholesaler'), ('Paramount', 'Wholesaler'), ('ILG', 'Wholesaler'), ('Direct', 'From the brand')]) +
   steps([('Log the outcome', 'Mark the visit with the order and add notes on what was ordered.'),
          ('First order', 'The job moves to First order and shows on your dashboard.'),
          ('Bonus', 'A single order over $1,000 earns you a 5% Super Sale bonus.')]) +
   qa('Who places the order?', 'You take it, and it’s placed with the brand or its wholesaler. Log it in the app so it counts.') +
   button('See how reps work', u('/reps', R, '04'))),
 dict(n='05', key='straight-answers', day=70, subject='Straight answers about repping with us',
  pre='Contractor status, tax, costs and what we ask of you.', hero='dual-proof.jpg',
  alt='Funded hours on a laptop and visit notes on a phone',
  body=lambda: kick('Day 70 · Straight answers') + h('Before you ask.', 'The fine print, plainly.') + p(HI) +
   qa('Am I an employee?', 'No. You work as an independent contractor under a Subcontractor Agreement issued in RepShare when you onboard. We issue you a recipient-created tax invoice for each payment.') +
   qa('What if I don’t have an ABN?', 'You’ll need one. Without it we must withhold tax from your pay.') +
   qa('Who pays my running costs?', 'You do: fuel, parking, phone and insurance aren’t reimbursed.') +
   qa('Is there a non-solicit?', 'Yes. For 6 months after you leave, you can’t approach a brand you worked with to work for it directly, unless you introduced that brand. It’s in the Service Terms.') +
   qa('Can rates change?', 'Yes, with 14 days’ notice, and changes apply to new jobs only.') +
   button('Read the service terms', u('/legal/service-terms', R, '05'), NAVY)),
 dict(n='06', key='first-job', day=84, subject='Ready for your first job?',
  pre='Onboarding, free courses and your first circuit.', hero='dual-splash.jpg',
  alt='The Drinks Network RepShare app on a laptop and a phone',
  body=lambda: kick('Day 84 · First job') + h('Your first job.', 'Done right.') + p(HI) +
   steps([('Onboard', '24 hours of onboarding: product knowledge, targets and go-to-market.'),
          ('Learn the category', 'Take our free courses on whisky, bourbon, tequila, rice spirits and rice wine. Each ends in a certificate.'),
          ('Work the circuit', 'Accept the jobs you want and log every visit with notes.'),
          ('Write real notes', 'Your notes are what the brand reads after every visit.')]) +
   stat_row([('1,382', 'People in the network'), ('3–7 days', 'Typical payout'), ('5–15', 'Hours a week')]) +
   button('Take a free course', u('/courses', R, '06'), NAVY) + button('Finish your profile', u('/start?role=rep', R, '06'))),
]

# ------------------------------------------------------------------ PARTNER (tag Partner)
P = 'partner'
PARTNER = [
 dict(n='00', key='welcome', day=0, subject='Partnering with Drinks Network: where to start',
  pre='Take the RepShare tech and network into your market or business.', hero='dual-splash.jpg',
  alt='The Drinks Network RepShare app on a laptop and a phone',
  body=lambda: kick('Day 0 · Welcome') + h('Take RepShare further.', 'Into your market.') + p(HI) +
   p('Thanks for asking about partnering. We work with partners who want to take the RepShare tech and network into their market or business.') +
   steps([('Agency or distributor', 'Agencies and distributors working with drinks brands.'), ('Tech reseller', 'Resellers taking the RepShare tech to their clients.'), ('Venue group', 'Groups of licensed venues.'), ('Overseas market', 'Taking RepShare into a market outside Australia.')]) +
   p('A team member will call to talk through your territory and what you need. Over the next 90 days we’ll send one email a fortnight on how the platform and the network work.') +
   button('Tell us about your territory', u('/start?role=partner', P, '00'))),
 dict(n='01', key='the-network', day=14, subject='The RepShare network in numbers',
  pre='Venues, reps, field activities and suppliers across the east coast.', hero='laptop-circuit-search.jpg',
  alt='RepShare venue search on a laptop',
  body=lambda: kick('Day 14 · The network') + h('The network.', 'Already in the field.') + p(HI) +
   stat_row([('31K+', 'Licensed venues as distribution points'), ('3', 'States: QLD, NSW, VIC'), ('20', 'Reps across BNE, SYD, MEL')]) +
   stat_row([('1,800+', 'Field activities completed'), ('20+', 'Suppliers onboarded'), ('30%+', 'Conversion on field sales calls')]) +
   p('Behind it: 20 years of making connections in the Australian drinks trade, and 1,382 people in the network.') +
   qa('Where do you operate?', 'Sydney, Melbourne and Brisbane for RepShare field work. We also place talent in Asia and the UAE.') +
   button('See the platform', u('/repshare-app', P, '01'))),
 dict(n='02', key='circuits', day=28, subject='How your clients would target venues',
  pre='Circuits: pick venues from 31,000+, attach an offer, hand it to reps.', hero='dual-circuit.jpg',
  alt='Adding venues to a circuit on a laptop and the jobs list on a phone',
  body=lambda: kick('Day 28 · Circuits') + h('Targeting.', 'Without the spreadsheet.') + p(HI) +
   steps([('Search', 'Start from 31,000+ licensed venues and narrow by name, suburb, type and distance.'),
          ('Select', 'Each venue comes with photos, contacts and a map link; existing clients are marked.'),
          ('Offer', 'Attach an intro deal and every account on the circuit gets it.'),
          ('Assign', 'The circuit becomes jobs for reps, tracked through to first order.')]) +
   qa('Does it need an app install?', 'No. RepShare is a web app that runs on any phone or computer, which makes rollout to a new team simple.') +
   button('See circuits in the app', u('/repshare-app', P, '02'))),
 dict(n='03', key='control', day=42, subject='Visibility and control over every field hour',
  pre='Timers, templates, approvals and funded hours, in one place.', hero='dual-funded-hours.jpg',
  alt='Funded hours dashboard on a laptop and a job booking on a phone',
  body=lambda: kick('Day 42 · Control') + h('Every hour.', 'Logged and approved.') + p(HI) +
   steps([('Booked', 'Reps book time against a job with an on-job timer. A standard visit is 30 minutes.'),
          ('Templated', 'Each charge uses a Field, Desk, Service or Custom template.'),
          ('Approved', 'Charges are approved before anyone is paid; a third charge before a first order is held for review.'),
          ('Reported', 'Funded hours show as available, approved, pending and remaining, by rep.')]) +
   qa('Who sees what?', 'Brands see their own dashboards 24/7. Reps see their own jobs, hours and earnings.') +
   button('See the app', u('/repshare-app', P, '03'))),
 dict(n='04', key='orders-and-reporting', day=56, subject='Orders through any channel, reported in one place',
  pre='ALM, Paramount, ILG or direct, with a vendor dashboard on top.', hero='dual-orders.jpg',
  alt='Vendor dashboard on a laptop and a visit outcome on a phone',
  body=lambda: kick('Day 56 · Orders') + h('Four ways to order.', 'One dashboard.') + p(HI) +
   stat_row([('ALM', 'Wholesaler'), ('Paramount', 'Wholesaler'), ('ILG', 'Wholesaler'), ('Direct', 'From the brand')]) +
   p('Whichever channel a venue uses, the order is logged against the job, and the brand sees ordering venues, order value, repeat venues and account performance on its dashboard.') +
   p('Billing is a subscription for reps’ hours, plus usage measured as it happens: venues worked, jobs run and orders processed. Reorders earn a repeat-order credit.', 16) +
   button('See the vendor dashboard', u('/repshare-app', P, '04'))),
 dict(n='05', key='straight-answers', day=70, subject='Partner questions, answered straight',
  pre='Terms, territory, data and support.', hero='dual-vendor-dashboard.jpg',
  alt='Vendor dashboard on a laptop and the app on a phone',
  body=lambda: kick('Day 70 · Straight answers') + h('Partner questions.', 'Plain answers.') + p(HI) +
   qa('What are the commercial terms?', 'We talk them through on the first call. There’s no published partner rate, because every partnership is different.') +
   qa('Can we have a territory?', 'That’s the first thing we discuss. Tell us the territory you have in mind when you complete the partner form.') +
   qa('What about our clients’ data?', 'Contacts and records are handled under the RepShare Privacy Policy, and each brand sees only its own dashboard.') +
   qa('What support do we get?', 'We cover it on the call. On brand plans, weCare support tickets come with Roll Out and above.') +
   button('Read the privacy policy', u('/legal/privacy-policy', P, '05'), NAVY)),
 dict(n='06', key='map-your-territory', day=84, subject='Let’s map your territory',
  pre='A short call to see what RepShare could do in your market.', hero='laptop-vendor-dashboard.jpg',
  alt='RepShare vendor dashboard on a laptop',
  body=lambda: kick('Day 84 · Next step') + h('Map your territory.', 'In one call.') + p(HI) +
   p('If RepShare could work in your market or business, the next step is a short call. We’ll look at your territory, the brands or venues involved, and what a first program would look like.') +
   steps([('Tell us your territory', 'Complete the partner form, or reply to this email.'),
          ('A call', 'A team member walks you through the platform with your market in mind.'),
          ('Next steps together', 'What a first program in your market could look like.')]) +
   button('Book the call', u('/start?role=partner', P, '06'))),
]

TRACKS = [('vendor', 'Vendor', VENDOR), ('rep', 'Rep', REP), ('partner', 'Partner', PARTNER)]


def main():
    rows = []
    for track, tag, emails in TRACKS:
        os.makedirs(os.path.join(HERE, track), exist_ok=True)
        for e in emails:
            fn = f"{track}/{e['n']}-{e['key']}.html"
            with open(os.path.join(HERE, fn), 'w') as f:
                f.write(page(track, e['subject'], e['pre'], e['body'](), e['hero'], e['alt']))
            rows.append([track, tag, e['n'], e['day'], 'On sign-up' if e['day'] == 0 else f"{e['day']} days after sign-up", e['subject'], e['pre'], fn])
    with open(os.path.join(HERE, 'schedule.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['Track', 'Trigger tag', '#', 'Day', 'When', 'Subject line', 'Preview text', 'HTML file']); w.writerows(rows)
    z = os.path.join(HERE, 'repshare-nurture-mailchimp-pack.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for r in rows: zf.write(os.path.join(HERE, r[7]), r[7])
        for extra in ('schedule.csv', 'MAILCHIMP-SETUP.md'):
            if os.path.exists(os.path.join(HERE, extra)): zf.write(os.path.join(HERE, extra), extra)
    for r in rows: print(' | '.join(map(str, r[:7])))


if __name__ == '__main__':
    main()
