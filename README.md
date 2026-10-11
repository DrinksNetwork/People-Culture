# Drinks Network — website and campaign pages

Approved designs for the Drinks Network brand website, with RepShare as its main offering, plus the first campaign page. Every image is stored in this repository, and nothing loads from other hosts except Google Fonts.

| Hostname | Serves |
| --- | --- |
| site.drinksnetwork.com.au | the pages in `public/` (Home, Start here, RepShare for Brands, Become a Rep) |
| campaign.drinksnetwork.com.au | the pages in `public/campaign/` at `/{slug}`, e.g. `/bar-takeover` |
| repshare.drinksnetwork.com.au | the RepShare app (not in this repository) |

The public site has no Admin pages or links. Admin stays inside the logged-in RepShare app.

## Structure

```
public/
  index.html          Home                              -> site.drinksnetwork.com.au/
  start.html          Start here funnel (step 1 shown)  -> /start
  brands.html         RepShare for Brands               -> /brands
  reps.html           Become a Rep                      -> /reps
  campaign/
    bar-takeover.html Bar Takeover campaign (working form) -> campaign.drinksnetwork.com.au/bar-takeover
  media/
    photos/           real trade photos: bar, back-bar, retail and tasting events
    products/         product cutouts (Lady Trieu, Nhau, Corowa, Headlands, Imbue, Diablo Co, San Junipero, Panda, BLVD)
    logos/            Drinks Network script logo: white (on red or dark) and red (on white or paper)
scripts/
  build.mjs           builds dist/site and dist/campaign, and fails on any broken link or image or disallowed host
  serve.mjs           local preview server
```

## Build and preview

Requires Node 18 or later. There are no npm dependencies, so `npm install` isn't needed.

```
npm run build     # -> dist/site and dist/campaign; prints "Build OK" or lists every problem
npm run preview   # -> http://localhost:3000 (PORT env var respected); campaign at /campaign/bar-takeover
```

## Notes for wiring into the RepShare app

- Page links currently use file names (`brands.html`); serve them at clean paths (`/brands`).
- The site pages are static snapshots of the approved design. Interactive parts (package picker, earnings calculator, Start here funnel steps 2–5, site forms) show their first state and need wiring. The funnel's later steps are: basics by role, AI product import for brands (draft, unpublished listings), first circuit (city, venue types, suburbs), and "You're in the queue" pending approval.
- `campaign/bar-takeover.html` has a working form. It posts JSON to `window.DN_ENQUIRY_ENDPOINT` (default `/api/enquiries`) with: firstName, lastName, email, mobile, city, venue, instagram, a honeypot field `website`, tags (`Trade`, or `Buyer` when "I buy drinks for this venue" is ticked), campaign `bar-takeover`, pageUrl, UTM source/medium/campaign, and consent status plus wording. Point it at the secure enquiry endpoint.
- Every form saves the contact in RepShare first, then syncs it to Mailchimp with tags Vendor, Rep, Partner, Buyer or Trade, plus `campaign:<slug>`.
- Bar Takeover dates, judging and prize details are marked [TO BE CONFIRMED].

## Style rules

- Colours: paper #FBF7F0 and white backgrounds; Drinks Network red #D3221B leads, often as white-on-red bands; duotone navy #1E2552 and magenta #C2185B as secondary colours; very little black.
- Fonts: Anton for uppercase display headlines, Source Serif 4 for body text and italic standfirsts, Archivo Narrow for letter-spaced kickers, nav and captions.
- Never lay an image or the logo over another image or over text. Images sit alone or side by side, each with a caption under it.
- Must work at phone width.
