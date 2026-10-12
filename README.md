# Drinks Network — website and campaign pages

Approved designs for the Drinks Network brand website, with RepShare as its main offering, plus the first campaign page. Every image is stored in this repository, and nothing loads from other hosts except Google Fonts.

| Hostname | Serves |
| --- | --- |
| site.drinksnetwork.com.au | the pages in `public/` (Home, Start here, RepShare for Brands, Become a Rep) |
| campaign.drinksnetwork.com.au | the pages in `public/campaign/` at `/{slug}`: `/bar-takeover`, `/san-junipero-melbourne` (5+1 retailer draw, form `san-junipero-giveaway`, tag Buyer) |
| repshare.drinksnetwork.com.au | the RepShare app (not in this repository) |

The public site has no Admin pages or links. Admin stays inside the logged-in RepShare app.

## Structure

```
public/
  index.html            Home                                  -> site.drinksnetwork.com.au/
  start.html            Start here funnel (working, 4 steps)  -> /start   (?role=rep | vendor | partner pre-selects)
  retail.html           Retail Activation: national retail account service program (tastings, store servicing, plans, Q&A sign-up) -> /retail
  whisky-adventure/     Australian Whisky Adventure offer pages: venues.html, brands.html (Q&A sign-ups) -> /whisky-adventure/venues, /whisky-adventure/brands
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
  assets/course.js      course player (watch -> review -> answer, gated) + named certificate
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

All courses are free (no code). The course player is built and working (try `/courses/how-drinks-network-courses-work`). Each course page header is a video "screen": a now-showing player with a playlist strip of every lesson video. Each lesson runs **Watch** (the YouTube lesson plays in-page; the end of the video, or the "watched" tick, unlocks the notes; lessons without video are read aloud), **Review** (notes), then **Answer** (questions; 80% unlocks the next lesson). Finishing a course draws a Drinks Network certificate in the learner's name (canvas, downloadable PNG or print/save as PDF) with a certificate number; the learner can correct the name before downloading. Progress is kept in the learner's browser; starting a course and finishing it post to `/api/enquiries` (form `course-start` / `course-complete`, tag Trade, campaign `course:<slug>`).

The five courses (Whisky, Bourbon, Tequila, Rice Spirits, Rice Wine Explained) now run on the Drinks Network "Explained" YouTube series: 36 lessons, each with lesson notes, the video (thumbnails in public/media/courses/yt) and three questions. The Tutor LMS import below can still replace the notes with the original lesson text. The lessons are behind the paid course pages, so the import needs a login:

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

## Enquiries: RepShare, Mailchimp and emails (server/enquiries.mjs)

`server/enquiries.mjs` is the drop-in handler for `POST /api/enquiries` in the RepShare app (Express example at the bottom of the file; `npm test` runs its checks with Mailchimp mocked). For every form it:
1. saves the contact in RepShare (pass your `saveContact`),
2. adds or updates them in the Mailchimp audience: merge fields FNAME, LNAME, PHONE, COMPANY; tags Vendor / Rep / Partner / Buyer / Trade, `campaign:<slug>`, `form:<name>` and `enquiry`; a note with every answer; status `subscribed` with consent, otherwise `transactional`,
3. emails hayden@, manuel@, joe@ and emma@ with every answer (reply-to is the enquirer),
4. sends the enquirer a "We've got your enquiry" email.

Replit Secrets: `MAILCHIMP_API_KEY` (e.g. `xxxx-us21`), `MAILCHIMP_AUDIENCE_ID`, `MAILCHIMP_TRANSACTIONAL_KEY` (Mailchimp Transactional, for steps 3 and 4), `ENQUIRY_FROM_EMAIL` (a verified sending domain), optional `ENQUIRY_ADMIN_EMAILS`. In Mailchimp, a Customer Journey that starts on the tag `enquiry` can send the enquirer's email instead of step 4, so marketing can edit it there. A Mailchimp outage is logged and never loses the lead.

## Legal pages (content/legal -> public/legal)

The RepShare Terms of Use, Service Terms, Payment Terms and Privacy Policy (written in Claude Docs) live as markdown in `content/legal/`. `npm run legal` turns them into `/legal/terms-of-use`, `/legal/service-terms`, `/legal/payment-terms`, `/legal/privacy-policy` and the `/legal` hub, with anchors for each party (`#4-vendors`, `#5-representatives`, `#6-orders`, `#part-a-vendors`, `#part-b-representatives`, `#part-c-buyers`). To update one, replace its markdown with the latest export and run `npm run legal`. Every page footer links all of them; brand forms link the Vendor parts, rep pages the Representative parts, venue forms the Buyer parts, and every form links the Privacy Policy. The old `/privacy-policy` and `/user-terms` addresses forward to the new pages. The Subcontractor Agreement is not published: it is issued to reps inside RepShare.

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
- Subscriptions on /brands and /retail: Kick Starter $2,695/month inc GST (5 hrs/wk, $95–$115/hr), Roll Out $4,180 (10 hrs, $85–$105/hr), Take Over $5,610 (15 hrs, $75–$95/hr), from the National Retail Service Pitch and the old WordPress /repshare page. Campaigner is quoted per campaign.
- Other forms: `retail-program` (Vendor), `whisky-adventure-venue` (Buyer, Trade), `whisky-adventure-brand` (Vendor), all with the same step log and sessionId as the Brands Q&A.
- GitHub Actions: "Import from WordPress" re-runs the full import to a review branch; "Fetch media from WordPress" downloads named upload URLs into public/media/legacy.
- `campaign/bar-takeover.html` has a working form. It posts JSON to `window.DN_ENQUIRY_ENDPOINT` (default `/api/enquiries`) with: firstName, lastName, email, mobile, city, venue, instagram, a honeypot field `website`, tags (`Trade`, or `Buyer` when "I buy drinks for this venue" is ticked), campaign `bar-takeover`, pageUrl, UTM source/medium/campaign, and consent status plus wording. Point it at the secure enquiry endpoint.
- Every form saves the contact in RepShare first, then syncs it to Mailchimp with tags Vendor, Rep, Partner, Buyer or Trade, plus `campaign:<slug>`.
- Bar Takeover: this round is closed; the page collects registrations for the next round.

## Style rules

- Colours: paper #FBF7F0 and white backgrounds; Drinks Network red #E42E2E (matches the script logo) leads, often as white-on-red bands; duotone navy #1E2552 and magenta #C2185B as secondary colours; very little black.
- Fonts: Anton for uppercase display headlines, Source Serif 4 for body text and italic standfirsts, Archivo Narrow for letter-spaced kickers, nav and captions.
- Never lay an image or the logo over another image or over text. Images sit alone or side by side, each with a caption under it.
- Must work at phone width.

## Tasting Series partnership brief (gated)

`/whisky-adventure/tasting-series` is the web version of the Tasting Series brief. The hero and "Three partners" are open; the rest (tickets, venue, vendor, Drinks Network fees, what one night can make, partner agreement) opens after the visitor gives first name, last name, email, mobile and venue or brand. They can tick "Email me a copy" and add up to 3 more emails. The form posts `form: "tasting-brief"` to `/api/enquiries` (tag Buyer for venues, Vendor for brands, campaign `tasting-series`); the handler emails the requester the brief links and sends each shared address one email with the links (`shareList`, `briefLinks`, `shareEmail` in `server/enquiries.mjs`, links built from `SITE_URL`). The partner agreement at the bottom also posts `form: "tasting-agreement"` with the agreement text.

The A4 brochure (5 pages) is `public/media/brief/tasting-partnership-brief.pdf`, offered after the gate and linked in the emails. The whisky venue and brand pages show page 1 and link to the brief. The gate is a soft gate: content ships in the page and unlocks in the browser; `?brief=open` opens it (used in the email links).
