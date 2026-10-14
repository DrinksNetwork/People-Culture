# Event programs: sign-up social content and captions

Five audiences, each pushed to the form that starts its 6-week email journey (see `emails/event-programs`).

| Audience | Sign-up link | Journey it starts |
|---|---|---|
| Bar Takeover · Venues | https://site.drinksnetwork.com.au/bar-takeover?utm_source=SOURCE&utm_medium=social&utm_campaign=takeover-venue | `journey:takeover-venue` (choose "Host venue") |
| Bar Takeover · Brands | https://site.drinksnetwork.com.au/bar-takeover?utm_source=SOURCE&utm_medium=social&utm_campaign=takeover-brand | `journey:takeover-brand` (choose "Brand") |
| Bar Takeover · Bartenders | https://site.drinksnetwork.com.au/bar-takeover?utm_source=SOURCE&utm_medium=social&utm_campaign=takeover-bartender | `journey:takeover-bartender` (choose "Bartender") |
| Tasting Series · Venues | https://site.drinksnetwork.com.au/whisky-adventure/venues?utm_source=SOURCE&utm_medium=social&utm_campaign=tasting-venue | `journey:tasting-venue` |
| Tasting Series · Brands | https://site.drinksnetwork.com.au/whisky-adventure/brands?utm_source=SOURCE&utm_medium=social&utm_campaign=tasting-brand | `journey:tasting-brand` |

Replace SOURCE with `linkedin`, `facebook` or `instagram`.

**Files in `out/`:**
- `linkedin-carousel-<audience>.pdf`: upload as a LinkedIn document.
- `<audience>-1…5.jpg`: Facebook and Instagram carousel cards, 1080 × 1080.
- `post-<audience>.jpg`: single posts.
- `link-<audience>.jpg`: link-share images, 1200 × 627.

**Voice:** written for people who've closed a bar at 3am. Every number is the same one the emails and packs use. The takeover money figures are an example night and say so.

## Posting plan (6 weeks, 3 posts a week)

| Week | Mon | Wed | Fri |
|---|---|---|---|
| 1 | Takeover venues carousel | Takeover bartenders carousel | Tasting venues carousel |
| 2 | Takeover brands carousel | Tasting brands carousel | Post: takeover venues |
| 3 | Post: tasting venues | Post: takeover bartenders | Link: takeover brands |
| 4 | Post: tasting brands | Link: takeover venues | Post: takeover brands |
| 5 | Takeover venues carousel (repost) | Link: tasting venues | Takeover bartenders carousel (repost) |
| 6 | Tasting brands carousel (repost) | Link: tasting brands | Link: takeover bartenders |

- **Venue and bartender content:** Instagram and Facebook first, with a boost in the target city.
- **Brand content:** LinkedIn first.

## Bar Takeover · Venues

**Carousel**
- Instagram/Facebook: One night. One guest bartender. Your bar. We fly in a bartender, build a menu on a cocktail brand and sell the tickets before the doors open. $49 gets a guest two cocktails, and 30 tickets is 60 drinks paid for before you've cut a lemon. You lock in a date within 6 weeks and host inside 60 days. Grab the pack 👉 [link]
- LinkedIn: Bar Takeover is open to host venues in any city with a good bar, from Sydney, Melbourne and Brisbane to Ballarat and Wollongong. The brand pays the guest bartender. Drinks Network runs tickets, artwork, posts, trade invites and six days of follow-up. You bring the room, the ingredients and an opening order. [link]

**Post**
- Instagram/Facebook: 30 tickets. 60 cocktails, sold before the doors open. Then the friends they bring buy a round at the bar. Example night: up to $2,826 through your till. [link]

**Link post**
- All: Put a guest behind your bar. One night, a ticketed crowd, run end to end. [link]

## Bar Takeover · Brands

**Carousel**
- LinkedIn: Walk into a venue with a product and a price list and you'll convert 5 to 10% of the time. Walk in with an activity or a high-value offer and it's 30% and up, sometimes past 50%. A Bar Takeover is that offer. A guest bartender builds a menu on your product, a new venue takes it on, and trade buyers taste it on your tab with a rep beside them. About $2,000 a takeover, with the program hours drawn from Roll Out or Take Over. [link]
- Facebook: Your brand, on tour. A guest bartender, a new venue and a room full of your drinks. [link]

**Post**
- LinkedIn: It's not a prize. It's a shift for your brand. Flights, accommodation, a $500 stipend, and every ticket-holder and trade contact comes back to you, and only you. [link]

**Link post**
- All: Your brand, on tour. About $2,000. One new account. Contacts yours only. [link]

## Bar Takeover · Bartenders

**Carousel**
- Instagram/Facebook: Your menu, their bar. Get flown to a new city and take over a bar for a night: flights, accommodation and a $500 stipend from the brand, with a fee of up to $1,000 on some takeovers. Send your mise en place list two weeks out, run it through the day before, then own the well from 6 to 10. Get on the list 👉 [link]
- LinkedIn: We're building a list of guest bartenders for Bar Takeover. Brands like Lady Triệu, Nhau and Barlei back a bartender into a new venue for one night. It's paid work, not a competition. [link]

**Post**
- Instagram/Facebook: Fly in. Take over. Flights, accommodation and a $500 stipend, paid by the brand. Your name on the poster. [link]

**Link post**
- All: Your menu. Their bar. Flights, accommodation and a $500 stipend. [link]

## Tasting Series · Venues

**Carousel**
- Instagram/Facebook: Meet the people behind the brand, in your room. A ticketed distiller's tasting: $75 a head, five pours, about two hours. We bring the distiller and sell the tickets, and you keep half the net door in cash plus everything they drink after. Lock in a date within 6 weeks. [link]
- LinkedIn: Host venues earn 50% of net ticket revenue in cash. That's $1,396 from a 40-guest night at $75, after Eventbrite fees, plus all food and drink sales. You bring the room, glassware and an opening order of the tasted range at wholesale. [link]

**Post**
- Instagram/Facebook: $1,396 in cash. Your half of a 40-guest tasting night, after fees. Then the bar's open. [link]

**Link post**
- All: Half the door, in cash. $75, five pours, two hours, in your room. [link]

## Tasting Series · Brands

**Carousel**
- LinkedIn: People buy from people. Product alone converts at 5 to 10%. Put the maker in the room and it changes: Corowa toured its distiller through ticketed tastings and hit 40.7% first-order conversion. One 40-guest night can return $6,449 to $7,100 in ticket credit, bottles and trade orders, against $1,500–$2,000 drawn from your subscription. [link]
- Facebook: Put the maker in the room. Ticketed tastings led by your distiller, in venues that stock you after. [link]

**Post**
- LinkedIn: 40.7% first-order conversion. That's what happened when Corowa put its distiller in front of the room. Brand on tour is built into Roll Out and Take Over. [link]

**Link post**
- All: Put the maker in the room. Ticketed tastings led by your distiller. [link]

## Rendering

```
python3 campaign-assets/event-social/build.py
node <scratchpad>/render-social.mjs $PWD/campaign-assets/event-social/slides.html <tmp>
```

Then convert the PNGs to JPGs in `out/` and join cards 1–5 per audience into `linkedin-carousel-<audience>.pdf`.
