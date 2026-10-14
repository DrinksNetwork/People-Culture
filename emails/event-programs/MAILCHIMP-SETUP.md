# Event program email sequences: Mailchimp set-up

Five Customer Journeys, one for each side of the two event programs. Each journey runs for 6 weeks, matching the 6-week window to commit to a date (for a night inside 60 days of registering).

| Journey | Starts on tag | Who gets it | Emails |
|---|---|---|---|
| Bar Takeover · Venues | `journey:takeover-venue` | Bar Takeover pack form, "Host venue" | 7, days 0, 7, 14, 21, 28, 35, 42 |
| Bar Takeover · Brands | `journey:takeover-brand` | Bar Takeover pack form, "Brand" | 7, days 0, 7, 14, 21, 28, 35, 42 |
| Bar Takeover · Bartenders | `journey:takeover-bartender` | Bar Takeover pack form, "Bartender" | 5, days 0, 7, 14, 28, 42 |
| Tasting Series · Venues | `journey:tasting-venue` | Whisky Adventure venue form, or Tasting Series brief as "Host venue" | 7, days 0, 7, 14, 21, 28, 35, 42 |
| Tasting Series · Brands | `journey:tasting-brand` | Whisky Adventure brand form, or Tasting Series brief as "Brand" | 7, days 0, 7, 14, 21, 28, 35, 42 |

The website adds the journey tag automatically when someone submits the form. The team still gets the new-lead email and still calls within one business day. The journey runs alongside that call so the person keeps learning what's involved.

## Build each journey

1. **Customer Journeys → Create journey.** Starting point: *Tag added*, using the tag in the table.
2. Add the emails in order with a **Time delay** of 7 days between them. For Bartenders, the gaps are 7, 7, 14 and 14 days. `schedule.csv` has the exact day for every email.
3. For each email, choose **Code your own → Paste in code**. Paste the HTML file and set the subject and preview text from `schedule.csv`.
4. **Stop the journey once they commit.** Before each email from the second one onwards, add an **If/Else** step: *Tags contains `event-committed`* → exit. When a venue or brand locks in a date, add the tag `event-committed` to their contact. The Tasting Series partner agreement form adds it automatically.
5. Turn the journey on.

## Merge tags used

`*|FNAME|*` (falls back to "Hi there"), `*|COMPANY|*` (falls back to "your venue" or "your brand"), plus Mailchimp's standard `*|UNSUB|*`, `*|UPDATE_PROFILE|*` and `*|LIST:ADDRESSLINE|*`.

## What every email carries

- A **"What you're agreeing to"** box with the terms for that side, and a link to the full pack:
  - Bar Takeover: `/media/takeover/bar-takeover-pack.pdf`
  - Tasting Series: `/media/brief/tasting-partnership-brief.pdf`
- The **6-week window** bar, showing which week they're in and the day-60 hosting deadline (venue and brand tracks).
- A call to action: open the pack, complete the partner agreement (Tasting Series) or email Manuel to lock in a date (Bar Takeover).

## Data sharing (as stated in every email)

Tickets are sold on Drinks Network's Eventbrite. Ticket-holder and trade contacts go to the brand that funds the night, and no one else.

## Links and images

All links carry UTM tags (`utm_campaign` = the track name, `utm_content` = email number), so sign-ups show by email in the admin area. Images load from `site.drinksnetwork.com.au/media/email/events/`, so the site must be published before the first send.
