# San Junipero Melbourne retailer giveaway: Mailchimp setup

For Emma (emma@drinksnetwork.com.au). This takes about 30 minutes. Eight emails in all: a launch email to Melbourne retailers,
an instant confirmation when a store enters, then six follow-ups on Tuesday mornings up to the **Friday 18 December** close.
Winners are drawn **Monday 21 December**, before Christmas.

| # | When | Subject line | Preview text | File |
|---|------|--------------|--------------|------|
| 00 | Thu 15 Oct 2026, launch | Buy 5 + 1. Ride away. 🚲 Win a San Junipero eBike | Melbourne retailers: buy five cases, get the sixth free and go into the draw for an eBike. | 00-intro-launch.html |
| 01 | Instantly, on entry | You're in the running for a San Junipero eBike 🚲 | Your 5+1 entry is in. Two eBikes drawn 21 December 2026. | 01-confirmation.html |
| 02 | Tue 20 Oct 2026 | Make the fridge glow ☀️ | Three quick ways to sell more San Junipero this week. | 02-fridge.html |
| 03 | Tue 27 Oct 2026 | The perfect San Junipero serve 🍋 | Big glass, lots of ice, one slice. That's it. | 03-serve.html |
| 04 | Tue 10 Nov 2026 | Win a spa retreat with San Junipero 🌴 | Follow @drinksanjunipero on Instagram for the spa retreat giveaway. | 04-spa.html |
| 05 | Tue 24 Nov 2026 | Double your chances to win an eBike 🚲🚲 | Every extra 5+1 order is another entry. Here's the deal. | 05-double.html |
| 06 | Tue 8 Dec 2026 | Where would you ride for a picnic? 🧺 | Picnic season is here, Christmas is close, and entries close Friday 18 December. | 06-picnic.html |
| 07 | Tue 15 Dec 2026 | Last call: register your 5+1 by Friday 18 December ⏰ | Entries close this Friday. Two eBikes drawn 21 December, just before Christmas. | 07-last-call.html |

Melbourne Cup Day (Tue 3 Nov) is skipped on purpose, as it's a public holiday in Melbourne.

The same list is in `schedule.csv`.

## How entries arrive in Mailchimp

Every entry from the campaign page lands in the Drinks Network audience with:

- tags `Buyer`, `campaign:san-junipero-melbourne`, `form:san-junipero-giveaway` and `enquiry`
- merge fields `FNAME` (contact name), `COMPANY` (store name) and `PHONE`

The emails use `*|FNAME|*` and `*|COMPANY|*`, and fall back to "Hi there" and "your store" if either field is blank.

## 1. Import the eight templates (about 5 minutes)

1. Mailchimp → **Content → Email templates → Create template → Code your own → Import HTML**.
2. Upload `01-confirmation.html` and name it **SJ 01 Confirmation**.
3. Repeat for 00 and 02 to 07 (SJ 00 Launch, SJ 02 Fridge, SJ 03 Serve, SJ 04 Spa, SJ 05 Double, SJ 06 Picnic, SJ 07 Last call).

Images load from site.drinksnetwork.com.au, so they appear once the site is republished on Replit.

## 2. Email 00: the launch (Thu 15 Oct)

**Campaigns → Create → Regular email** to your Melbourne retailer contacts (for example the tag `Buyer`, filtered to Melbourne/VIC), template **SJ 00 Launch**, subject and preview text from the table. Send a test to yourself, then schedule for 10:00 am.

## 3. Email 01: send it automatically on entry (about 10 minutes)

1. **Automations → Customer Journeys → Create journey**, named *San Junipero entry confirmation*.
2. Starting point: **Tag is added → `form:san-junipero-giveaway`**. Allow contacts to start the journey **multiple times**, so every extra 5+1 entry gets a confirmation.
3. Add **Send email** and design it with **SJ 01 Confirmation**:
   - Subject: *You're in the running for a San Junipero eBike 🚲*
   - Preview text: *Your 5+1 entry is in. Two eBikes drawn 21 December 2026.*
   - From name: **San Junipero**; reply-to **emma@drinksnetwork.com.au**
4. **Turn on** the journey.

## 4. Emails 02 to 07: schedule them for Tuesday mornings (about 15 minutes)

Use regular campaigns rather than journey delays. Fixed dates keep the countdown accurate, and stores that enter late still get the remaining emails.

For each email:

1. **Campaigns → Create → Regular email**.
2. **To:** the Drinks Network audience → **Segment or tag → Tags → `campaign:san-junipero-melbourne`**.
3. **From:** San Junipero · reply-to emma@drinksnetwork.com.au.
4. **Subject** and **preview text** from the table above.
5. **Content:** the matching saved template.
6. **Send test** to emma@drinksnetwork.com.au, check it, then **Schedule** for its Tuesday (dates in the table) at **10:00 am (Melbourne time)**.

## 5. Before you schedule anything

- Send yourself a test of every email and click every button.
- Check the promotion terms and final bike details are published on the campaign page; emails 01 and 07 refer to them.
- Emails 04 and the footer of every email mention the Instagram spa retreat giveaway. Confirm its dates and terms are live on @drinksanjunipero before email 04 goes out.
- If the site's instant "We've got your enquiry" email is also switched on, entrants will get two confirmations. Ask for that automatic reply to be turned off for this form.

## After the draw (Monday 21 December)

Duplicate email 07, change it to announce the winners (with their permission), and send it to the same tag.
