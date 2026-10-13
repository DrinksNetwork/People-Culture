# San Junipero Melbourne retailer giveaway: Mailchimp setup

For Emma (emma@drinksnetwork.com.au). This takes about 30 minutes. Seven emails cover six weeks:
one instant confirmation when a store enters, then one email every Tuesday up to the 30 November close.

| # | When | Subject line | Preview text | File |
|---|------|--------------|--------------|------|
| 01 | Instantly, on entry | You're in the running for a San Junipero eBike 🚲 | Your 5+1 entry is in. Two eBikes drawn 1 December 2026. | 01-confirmation.html |
| 02 | Tue 20 Oct 2026 | Make the fridge glow ☀️ | Three quick ways to sell more San Junipero this week. | 02-week-1-fridge.html |
| 03 | Tue 27 Oct 2026 | The perfect San Junipero serve 🍋 | Big glass, lots of ice, one slice. That's it. | 03-week-2-serve.html |
| 04 | Tue 3 Nov 2026 | Win a spa retreat with San Junipero 🌴 | Follow @drinksanjunipero on Instagram for the spa retreat giveaway. | 04-week-3-spa.html |
| 05 | Tue 10 Nov 2026 | Double your chances to win an eBike 🚲🚲 | Every extra 5+1 order is another entry. Here's the deal. | 05-week-4-double.html |
| 06 | Tue 17 Nov 2026 | Where would you ride for a picnic? 🧺 | Picnic season is here. So is your chance to win. | 06-week-5-picnic.html |
| 07 | Tue 24 Nov 2026 | Last call: register your 5+1 by 30 November ⏰ | One week left to enter. Two eBikes drawn 1 December. | 07-week-6-last-call.html |

The same list is in `schedule.csv`.

## How entries arrive in Mailchimp

Every entry from the campaign page lands in the Drinks Network audience with:

- tags `Buyer`, `campaign:san-junipero-melbourne`, `form:san-junipero-giveaway` and `enquiry`
- merge fields `FNAME` (contact name), `COMPANY` (store name) and `PHONE`

The emails use `*|FNAME|*` and `*|COMPANY|*`, and fall back to "Hi there" and "your store" if either field is blank.

## 1. Import the seven templates (about 5 minutes)

1. Mailchimp → **Content → Email templates → Create template → Code your own → Import HTML**.
2. Upload `01-confirmation.html` and name it **SJ 01 Confirmation**.
3. Repeat for 02 to 07 (SJ 02 Fridge, SJ 03 Serve, SJ 04 Spa, SJ 05 Double, SJ 06 Picnic, SJ 07 Last call).

Images load from site.drinksnetwork.com.au, so they appear once the site is republished on Replit.

## 2. Email 01: send it automatically on entry (about 10 minutes)

1. **Automations → Customer Journeys → Create journey**, named *San Junipero entry confirmation*.
2. Starting point: **Tag is added → `form:san-junipero-giveaway`**. Allow contacts to start the journey **multiple times**, so every extra 5+1 entry gets a confirmation.
3. Add **Send email** and design it with **SJ 01 Confirmation**:
   - Subject: *You're in the running for a San Junipero eBike 🚲*
   - Preview text: *Your 5+1 entry is in. Two eBikes drawn 1 December 2026.*
   - From name: **San Junipero**; reply-to **emma@drinksnetwork.com.au**
4. **Turn on** the journey.

## 3. Emails 02 to 07: schedule them for Tuesday mornings (about 15 minutes)

Use regular campaigns rather than journey delays. Fixed dates keep the countdown accurate, and stores that enter late still get the remaining emails.

For each email:

1. **Campaigns → Create → Regular email**.
2. **To:** the Drinks Network audience → **Segment or tag → Tags → `campaign:san-junipero-melbourne`**.
3. **From:** San Junipero · reply-to emma@drinksnetwork.com.au.
4. **Subject** and **preview text** from the table above.
5. **Content:** the matching saved template.
6. **Send test** to emma@drinksnetwork.com.au, check it, then **Schedule** for the Tuesday at **10:00 am (Melbourne time)**.

## 4. Before you schedule anything

- Send yourself a test of every email and click every button.
- Check the promotion terms and final bike details are published on the campaign page; emails 01 and 07 refer to them.
- Emails 04 and the footer of every email mention the Instagram spa retreat giveaway. Confirm its dates and terms are live on @drinksanjunipero before email 04 goes out.
- If the site's instant "We've got your enquiry" email is also switched on, entrants will get two confirmations. Ask for that automatic reply to be turned off for this form.

## After the draw (1 December)

Duplicate email 07, change it to announce the winners (with their permission), and send it to the same tag.
