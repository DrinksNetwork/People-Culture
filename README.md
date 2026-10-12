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
  index.html            Home                                  -> site.drinksnetwork.com.au/
  start.html            Start here funnel (working, 4 steps)  -> /start   (?role=rep | vendor | partner pre-selects)
  brands.html           RepShare for Brands: 4 subscription plans (Kickstart, Roll Out, Take Over, Campaigner) -> /brands
  reps.html             Become a Rep (earnings calculator)    -> /reps
  securicode.html       SecuriCode                            -> /securicode
  courses.html          Courses index                         -> /courses
  courses/<slug>.html   Course page + player                  -> /courses/<slug>
  courses/<slug>.json   Course data: lessons, media, questions (see Course data)
  about.html            About                                 -> /about
  contact.html          Contact                               -> /contact
  faqs.html             FAQs                                  -> /faqs
  blog/index.html       People & Culture blog                 -> /blog
  blog/<slug>.html      Blog posts (same slugs as the old site) -> /blog/<slug>
  privacy-policy.html, cookie-policy.html, user-terms.html    -> legal pages
  campaign/
    bar-takeover.html   Bar Takeover campaign                 -> campaign.drinksnetwork.com.au/bar-takeover
  assets/site.css, assets/site.js   shared styles; forms, plan picker, calculator and funnel
  assets/course.js      course player (review -> listen -> answer, gated)
  media/
    photos/           real trade photos: bar, back-bar, retail and tasting events
    products/         product cutouts (Lady Trieu, Nhau, Corowa, Headlands, Imbue, Diablo Co, San Junipero, Panda, BLVD)
    logos/            Drinks Network script logo: white (on red or dark) and red (on white or paper)
    subscriptions/    plan tiles and photos from the Vendor Subscription prototype
scripts/
  build.mjs             builds dist/site and dist/campaign; fails on any broken link, missing image, placeholder link or disallowed host
  serve.mjs             local preview server (clean URLs: /brands -> brands.html, /blog -> blog/index.html)
  import-wordpress.mjs  one-off import from the old WordPress site (see below)
  partials/             shared header and footer used by the import
```

## Import from the old WordPress site (run once, on Replit)

```
npm run import:wordpress
```

This uses the public WordPress REST API, so no login is needed:
- copies every blog post word for word into `public/blog/<slug>.html` and rebuilds `public/blog/index.html`
- copies the privacy policy, cookie policy and user terms into their pages
- downloads every image and video still loading from `www.drinksnetwork.com.au/wp-content/uploads/` into `public/media/legacy/`, and rewrites the pages to use the local copies
- rewrites links to old posts and pages to the new addresses

After it runs, `npm run build` should report no images left on the old site. Until then, those pages show the summary and a link to the full version on the old site.

## Courses (run once, on Replit, with a WordPress login)

The course player is built and working (try `/courses/how-drinks-network-courses-work`). Each lesson runs **Review** (read), **Listen** (recording, video, or the lesson read aloud), then **Answer** (questions; 80% unlocks the next lesson). Progress is kept in the learner's browser; starting a course and finishing it post to `/api/enquiries` (form `course-start` / `course-complete`, tag Trade, campaign `course:<slug>`).

The five WordPress courses show "Lessons are on their way" until their content is imported. The lessons are behind the paid course pages, so the import needs a login:

```
WP_USER=<admin username> WP_APP_PASSWORD="<application password>" npm run import:courses
npm run import:wordpress   # then copy course and lesson images into the project
```

Create the application password in WordPress: Users -> Profile -> Application Passwords. Tutor LMS endpoints vary by version; the script tries the known ones and reports what it found. Lessons without a quiz show "Complete lesson"; add questions to the JSON to gate them.

### Course data (`public/courses/<slug>.json`)

```
{ "slug", "title", "description", "image", "legacyUrl",
  "lessons": [ { "id": "l1", "title", "review": "<p>html</p>",
                 "listen": { "type": "tts" } | { "type": "youtube", "id" } | { "type": "audio" | "video", "src" },
                 "questions": [ { "q", "options": ["a","b","c"], "answer": 1, "explain" } ] } ] }
```

## Build and preview

Requires Node 18 or later. There are no npm dependencies, so `npm install` isn't needed.

```
npm run build     # -> dist/site and dist/campaign; prints "Build OK" or lists every problem
npm run preview   # -> http://localhost:3000 (PORT env var respected); campaign at /campaign/bar-takeover
```

## Notes for wiring into the RepShare app

- All internal links are clean root paths (`/brands`, `/blog/<slug>`). Serve `x.html` at `/x` and `x/index.html` at `/x`.
- Everything is wired: the package picker, earnings calculator, Start here funnel and every form (newsletter, brands enquiry, contact, SecuriCode, Start here, Bar Takeover). Forms in `assets/site.js` and the campaign page post JSON to `window.DN_ENQUIRY_ENDPOINT` (default `/api/enquiries`). Fields include tags (Vendor, Rep, Partner, Buyer, Trade), form name, campaign, package, pageUrl, UTMs, the honeypot field `website` and consent status plus wording.
- Start funnel log: every step of /start (who, details, circuit, done) posts an anonymous event to `window.DN_FUNNEL_ENDPOINT` (default `/api/funnel-events`) with `sessionId`, `step`, `roles`, pageUrl, UTMs and a timestamp. The final submission carries the same `sessionId`, so drop-off and completed leads can be joined in the lead manager.
- Brands subscription Q&A: choosing a plan on /brands jumps straight into four questions (Plan, Brand, Market, You) and submits once to `/api/enquiries` as form `brands-subscription`, tag Vendor, with `package`, `startWhen`, `cities[]`, `company`, `category`, `skus`, `companyWebsite`, `soldIn[]`, `goals[]`, `targets`, `notes`, `firstName`, `jobTitle`, `email`, `mobile`, consent and `sessionId`. Each step also posts to `/api/funnel-events` with `flow: brands-subscription`, so you can see where brands drop off. The new-lead email should include the plan and every answer.
- New-lead emails: every Start, Brands, contact, SecuriCode and campaign submission should notify hayden@, manuel@, joe@ and emma@drinksnetwork.com.au.
- Still to add in the app: AI product import for brands after Start here (draft, unpublished listings for approval).
- Subscriptions on /brands: hourly rates carried over from the old WordPress /repshare page (Kickstart $95–$115/hr at 5+ hrs/wk, Roll Out $85–$105/hr at 10+, Take Over $75–$95/hr at 15+). Monthly figures are hours × rate × 4.33. Campaigner is quoted per campaign.
- `campaign/bar-takeover.html` has a working form. It posts JSON to `window.DN_ENQUIRY_ENDPOINT` (default `/api/enquiries`) with: firstName, lastName, email, mobile, city, venue, instagram, a honeypot field `website`, tags (`Trade`, or `Buyer` when "I buy drinks for this venue" is ticked), campaign `bar-takeover`, pageUrl, UTM source/medium/campaign, and consent status plus wording. Point it at the secure enquiry endpoint.
- Every form saves the contact in RepShare first, then syncs it to Mailchimp with tags Vendor, Rep, Partner, Buyer or Trade, plus `campaign:<slug>`.
- Bar Takeover: this round is closed; the page collects registrations for the next round.

## Style rules

- Colours: paper #FBF7F0 and white backgrounds; Drinks Network red #E42E2E (matches the script logo) leads, often as white-on-red bands; duotone navy #1E2552 and magenta #C2185B as secondary colours; very little black.
- Fonts: Anton for uppercase display headlines, Source Serif 4 for body text and italic standfirsts, Archivo Narrow for letter-spaced kickers, nav and captions.
- Never lay an image or the logo over another image or over text. Images sit alone or side by side, each with a caption under it.
- Must work at phone width.
