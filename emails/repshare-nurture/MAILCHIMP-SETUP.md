# RepShare 90-day nurture: Mailchimp setup

For Emma (emma@drinksnetwork.com.au). Three tracks, seven emails each, one email every 14 days for 90 days.
Each person only gets the track for the role they chose on the site. About 45 minutes in total.

| Track | Starts when this tag is added | Emails | Sent from |
|---|---|---|---|
| Vendors (brands, producers) | `Vendor` | `vendor/00` to `vendor/06` | Drinks Network |
| Reps (bartenders, brand ambassadors and reps already selling) | `Rep` | `rep/00` to `rep/06` | Drinks Network |
| Partners (agencies, distributors, resellers, venue groups) | `Partner` | `partner/00` to `partner/06` | Drinks Network |

The subject line, preview text and send day for all 21 emails are in `schedule.csv`.

## How people get into a track

Every site form already saves the contact in the Replit database and adds tags in Mailchimp:

- Start here (`form:start-here`): `Vendor`, `Rep` and/or `Partner`, as chosen at step 1
- Brands subscription, Retail program, Whisky Adventure (brand), SecuriCode: `Vendor`
- Newsletter: the role picked (`Vendor`, `Rep` or `Partner`; `Buyer` and `Trade` have no track yet)

Someone who picks two roles (a founder who also reps) gets both tracks. That's intended.

## 1. Import the 21 templates (about 15 minutes)

1. **Content → Email templates → Create template → Code your own → Import HTML**.
2. Upload each file from the `vendor`, `rep` and `partner` folders. Name them by track and number, e.g. **RS Vendor 00 Welcome**, **RS Rep 03 Circuits**.

Images load from site.drinksnetwork.com.au/media/nurture/, so they show once the site is republished on Replit.

## 2. Build one Customer Journey per track (about 10 minutes each)

1. **Automations → Customer Journeys → Create journey**, named *RepShare nurture: Vendors* (then *Reps*, *Partners*).
2. Starting point: **Tag is added → `Vendor`** (or `Rep`, `Partner`). Contacts start the journey **once only**.
3. Add **Send email** with template 00. From name **Drinks Network**, reply-to **emma@drinksnetwork.com.au**; subject and preview text from `schedule.csv`.
4. Add **Time delay → 14 days**, then **Send email** with template 01. Repeat until 06 (six delays of 14 days: days 14, 28, 42, 56, 70, 84).
5. Optional: before each email add **If/Else → Tag `stage:Active`** and exit the journey on Yes, so people who have signed up stop getting "are you ready?" emails.
6. **Turn on** the journey.

## 3. Before you turn anything on

- Send yourself a test of every email and click every button.
- Check the numbers still match the site (plans, prices and rates are in `build.py`, taken from the Brands, Reps and legal pages). If the site changes, ask for the emails to be rebuilt.
- People already tagged `Vendor`, `Rep` or `Partner` won't start a journey that triggers on a new tag. To include them, add them through the journey's **Add contacts** option.
- If the site's instant "We've got your enquiry" email is on, the welcome email arrives straight after it. That's fine: they say different things.
