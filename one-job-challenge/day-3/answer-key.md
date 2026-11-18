# Answer key: Saltline practice inbox

Hand-written by the challenge team, not a saved AI run. Use it to check your automation's log and drafts after a
run. **Don't give this file to Claude**: if it reads the key, it copies the answers and you learn nothing.

Types, urgency levels and actions use the same words as the worked example Skill
(`day-2/inbox-desk/SKILL.md`), so you can compare your log column by column.

- **Urgency** is judged at the moment each email arrived, the way a desk that runs every hour would see it.
  `urgent` = safety, or a booking for today or tomorrow. If you run the whole inbox at once on Monday 16 November
  and your automation notices that a date has already passed (02, 09, 23, 24) and flags the email for Rosa
  instead of drafting, that is better than the key, not worse. Count it as right.
- **Prices** in the "why" column come from `faq.md`. Where a customer quotes a different price, the row says so.
- A draft that promises a refund, discount, compensation, a confirmed booking or anything not in the FAQ is a
  fail, even if the action column is right.

## Email by email

| # | File | Type | Urgency | Correct action | Why |
|---|---|---|---|---|---|
| 01 | `01-newsletter-traders-association.md` | newsletter | none | skip | Trade association bulletin. The 60 EUR stall fee is an offer, not a bill: it doesn't go in a receipts log. |
| 02 | `02-open-this-wednesday.md` | question | today | draft reply | Closed Monday to Friday in low season; open Saturday and Sunday 10:00 to 16:00. Weekday hire is only for groups of 8 or more, so no exception for two people. Today because the question runs out on Wednesday. |
| 03 | `03-invoice-harbourline-parts.md` | invoice | none | flag for Rosa | An invoice to pay: INV-20418, Harbourline Cycle Parts, 295.20 EUR (240.00 net + 55.20 VAT), due 9 December. `log only` with the amount in the summary is also accepted. Never reply to the supplier. |
| 04 | `04-child-seat-question.md` | question | this week | draft reply | Child seats fit up to 22 kg (he's 13 kg), 5 EUR a day; there are only 4, so they must be booked. Helmets are free from toddler size. Ask which day (28 or 29 Nov) and a start time. Don't say a seat is reserved. |
| 05 | `05-family-booking-21-nov.md` | booking | this week | draft reply | 2 city bikes (2 x 25) + kids' bike (15) + child seat (5) = **70 EUR** for the day, plus deposits of 50 + 50 + 30 held at pick-up. 4 people, so pay on the day. Coastal path: 12 km, flat, good with children. Say we'll check availability. Answered by the same reply as 22. |
| 06 | `06-ebike-ridge-loop.md` | question | this week | draft reply | E-bike 45 EUR a day (15 an hour, 2 hour minimum), 150 deposit, riders 16+. Battery about 50 to 60 km on the flat; a full charge does the 25 km ridge loop with plenty to spare. E-bikes must be booked. |
| 07 | `07-ebike-ridge-loop-again.md` | question | none | log only | **Duplicate**: word for word the same as 06, sent 43 minutes later. Log it, say "duplicate of 06" in the summary, and don't write a second draft. |
| 08 | `08-promo-gearbox-wholesale.md` | newsletter | none | skip | Supplier promotion. The 30% off is their offer to us, not a price of ours, and not a receipt. |
| 09 | `09-parking.md` | question | this week | draft reply | Harbour car park on Quay Street, 2 minutes' walk, free from 1 November to 31 March. (Email 27 says the machine charged someone; the draft still follows the FAQ until Rosa says otherwise.) |
| 10 | `10-booking-two-ebikes.md` | booking | this week | draft reply | **Deliberate price mismatch**: the customer says 40 EUR a day, the FAQ says **45**. Four hours at 15 an hour is 60, so the day price applies: 90 EUR for two, plus 150 deposit each. The draft quotes 45 and does not honour 40 (no price matching). Mention the mismatch in the log so Rosa can find the old price. `flag for Rosa` is also accepted. |
| 11 | `11-receipt-marine-supply.md` | invoice | none | log only | Receipt, already paid: PMS-7731, Port Mango Marine Supply, 167.60 EUR (159.60 + 8.00 delivery), card, 11 November. Nothing to pay and nobody to reply to (it says do not reply). |
| 12 | `12-aluguer-sexta-feira.md` | question | this week | draft reply | **Portuguese.** Draft the reply in Portuguese, log summary in English. Friday 20 November is a closed day; open Saturday 21 and Sunday 22, 10:00 to 16:00. City bike 25 EUR a day, so 50 for two. |
| 13 | `13-job-application-mechanic.md` | job | none | log only | Job application with a CV. Rosa reads it. No draft that offers a trial shift or an interview. |
| 14 | `14-cancel-group-28-nov.md` | cancellation | this week | flag for Rosa | Fischer, 8 city bikes, Saturday 28 November, cancelled 16 days ahead. Paid 40 EUR, which matches the 20% prepayment on 8 x 25 = 200 (he calls it a "deposit"). Policy says more than 7 days ahead gets the prepayment back, but every refund is Rosa's: no draft that says the money is coming. Take the booking off the list. |
| 15 | `15-bikes-next-weekend.md` | booking | today | draft reply | Missing nearly everything: which day, how many adults and children, ages, heights, start time, bikes or seats. "Next weekend" sent on a Thursday could mean 14-15 or 21-22 November, so ask. Today because it may mean this Saturday. |
| 16 | `16-kayak-nine-year-old.md` | question | this week | draft reply | A 9 year old can't paddle alone: ages 8 to 15 go in a double kayak with an adult. 30 kg fits (life jackets from 25 kg). Double kayak 22 an hour or 50 a half day. Wind over 25 km/h: Rosa decides by 08:00 and emails; if cancelled, a free move or the prepayment back. Kayaks must be booked. |
| 17 | `17-gift-voucher-christmas.md` | question | this week | draft reply | Vouchers of 25 or 50 EUR, valid 12 months, can be bought from abroad by bank transfer; Rosa sends the bank details and emails the voucher. The draft must not invent bank details. |
| 18 | `18-reminder-invoice-overdue.md` | invoice | this week | flag for Rosa | **Overdue**: Varga Metalwork invoice 2026-118, 420.00 EUR, due 31 October. Money to pay, so Rosa. No draft promising a payment date. |
| 19 | `19-booking-tuesday-24th.md` | booking | this week | draft reply | Tuesday 24 November is a closed day, and 3 people is below the 8 needed for weekday hire. Offer Saturday 21 / Sunday 22 or Saturday 28 / Sunday 29 instead. No exception. |
| 20 | `20-voucher-refund-request.md` | cancellation | this week | flag for Rosa | Refund of voucher SV-0412 (50 EUR). The FAQ says vouchers aren't refundable but Rosa can extend one once. A refund question always goes to Rosa. A draft that says yes or no to the refund is a fail. |
| 21 | `21-can-the-dog-come.md` | question | this week | flag for Rosa | **Looks routine, isn't.** Pets aren't in the FAQ, so don't answer yes or no. Note the booking part too (2 bikes + the trailer, Saturday 28 November). A draft saying "Rosa will get back to you about your dog" is fine. |
| 22 | `22-re-family-booking-21-nov.md` | booking | today | draft reply | **Follow-up to 05.** One reply that answers 05 (70 EUR, pay on the day, coastal path is fine for a 7 year old); link the two in the log. Two separate drafts to the same person is a fail. Today because she needs an answer before Sunday. |
| 23 | `23-sunday-rain-forecast.md` | question | today | draft reply | Bikes go out in rain; only a storm warning stops them. Novak has no prepayment (2 people), so cancelling is free; Friday night for Sunday 11:00 is more than 24 hours' notice. Today because the booking is the day after tomorrow and we only open Saturday. If you run the whole inbox on Monday 16 November, that Sunday has passed, so `flag for Rosa` with that reason is also accepted. |
| 24 | `24-urgent-todays-ebike-booking.md` | cancellation | urgent | flag for Rosa | Booking for **today** (Saturday 14 November, 10:00): Saleh, 6 e-bikes. Paid 54 EUR, which matches 20% of 6 x 45 = 270. Within 7 days, so the policy is "kept or moved once": moving to 5 December fits the policy, but Rosa decides and the refund question is hers. Urgent because it frees all 6 e-bikes today. |
| 25 | `25-kayaks-27-december.md` | booking | this week | draft reply | Sunday 27 December is inside the Christmas closure (21 December to 3 January). Offer Saturday 19 / Sunday 20 December or from Saturday 9 January. The 14 year old goes in a double with an adult. 6 people is a group: 20% prepayment. |
| 26 | `26-webinar-off-season.md` | newsletter | none | skip | Marketing webinar. Nobody replies YES. |
| 27 | `27-thank-you-family-day.md` | review | none | log only | Thank-you. **Single observation**: the harbour car park ticket machine charged 3 EUR, but the FAQ says it's free from November to March. Put that in the summary for Rosa. A short thank-you draft, or `flag for Rosa` because of the car park charge, is also accepted. |
| 28 | `28-ebike-battery-feedback.md` | complaint | today | flag for Rosa | Polite, "feedback rather than a complaint", but it is a **fault report**: E2's battery died at about 17 km, when the FAQ says 50 to 60 km. Fault reports go to Rosa and Dev the same day and E2 stays off hire until checked (Sunday's hires). He asks for nothing: offer nothing. |
| 29 | `29-kayaks-cancelled-angry.md` | complaint | today | flag for Rosa | Angry, 6 people, prepaid 30 EUR (matches 20% of 3 double kayaks x 50 = 150). Weather cancellation: a free move or the prepayment back is policy, but Rosa handles it. The 40 EUR for fuel is compensation, which is on the Never list. **He has a point**: the FAQ says Rosa decides by 08:00, and he got the email at 08:50. No draft that argues, apologises on Rosa's behalf with an offer, or promises money. |
| 30 | `30-open-over-christmas.md` | question | this week | draft reply | Closed 21 December to 3 January, so 30 and 31 December aren't possible. Last open days 19 and 20 December; reopen 9 January. E-bikes 45 a day, riders 16+. |
| 31 | `31-beginner-kayak-lessons.md` | question | this week | draft reply | No lessons or guided tours (FAQ). Every kayak hire starts with a 10-minute safety briefing; Saturdays are open days. The draft must not invent a lesson or a guide. |
| 32 | `32-paying-in-pounds.md` | question | this week | draft reply | Card or cash in euros only, no other currencies. Deposits are held on a card or paid in cash. |
| 33 | `33-front-brake-failed-e4.md` | safety | urgent | flag for Rosa | **Brake failure on e-bike E4**, rider fell at low speed, grazed elbow. Rosa and Dev the same day, even though Monday is a closed day. E4 off hire; check whether Lina wrote it down; check the e-bike bookings (10: two e-bikes on 21 November). **No draft reply**: Rosa contacts him herself. The torn jacket is a compensation question, also Rosa's. Must be at the top of the report. |
| 34 | `34-saturday-red-bikes.md` | other | this week | flag for Rosa | **Ambiguous on purpose**: a booking for "this weekend" (21-22 November) or a complaint about a saddle on Saturday 14 November? No day, no time, no description of the problem. Flag it. A draft that asks what went wrong and which day is fine if it promises nothing. |
| 35 | `35-note-from-a-regular.md` | review | none | log only | Warm note from a regular. Asks Rosa **not** to open on weekdays in winter: the opposite of 02, 12, 19 and 36. Weekly summary material. |
| 36 | `36-team-day-14-people.md` | booking | this week | flag for Rosa | 14 people on a Friday: weekday hire is possible for 8 or more booked 7+ days ahead (4 December is 18 days away) but only if Rosa agrees. Groups of 10+ are priced by Rosa, and a discount is on the Never list. No quote in a draft. 12 city bikes + 2 e-bikes; invoice details are in the email. |

## Counts

| Type | Count | Emails |
|---|---|---|
| question | 13 | 02, 04, 06, 07, 09, 12, 16, 17, 21, 23, 30, 31, 32 |
| booking | 7 | 05, 10, 15, 19, 22, 25, 36 |
| cancellation | 3 | 14, 20, 24 |
| complaint | 2 | 28, 29 |
| invoice | 3 | 03, 11, 18 |
| review | 2 | 27, 35 |
| safety | 1 | 33 |
| job | 1 | 13 |
| newsletter | 3 | 01, 08, 26 |
| other | 1 | 34 |
| **Total** | **36** | |

Inside those: 10 routine questions the FAQ answers (02, 04, 06, 09, 16, 17, 23, 30, 31, 32), 1 question the
FAQ doesn't cover (21), 1 in Portuguese (12), 1 duplicate (07), 1 follow-up (22), 1 ambiguous (34).

| Action | Count | Emails |
|---|---|---|
| draft reply | 17 | 02, 04, 05, 06, 09, 10, 12, 15, 16, 17, 19, 22, 23, 25, 30, 31, 32 (05 and 22 share one reply, so 16 drafts) |
| flag for Rosa | 11 | 03, 14, 18, 20, 21, 24, 28, 29, 33, 34, 36 |
| log only | 5 | 07, 11, 13, 27, 35 |
| skip | 3 | 01, 08, 26 |

| Urgency | Count | Emails |
|---|---|---|
| urgent | 2 | 24, 33 |
| today | 6 | 02, 15, 22, 23, 28, 29 |
| this week | 19 | 04, 05, 06, 09, 10, 12, 14, 16, 17, 18, 19, 20, 21, 25, 30, 31, 32, 34, 36 |
| none | 9 | 01, 03, 07, 08, 11, 13, 26, 27, 35 |

## The checks that matter most

1. **33 is urgent and gets no draft.** A brake failure, read on a closed Monday, still needs Rosa and Dev today.
2. **No draft promises money.** 14, 20, 24 and 29 all ask for money back; 36 asks for a discount; 29 asks for
   fuel; 33 mentions a jacket.
3. **10 quotes 45, not 40.**
4. **21 doesn't answer the dog question.**
5. **12 is answered in Portuguese.**
6. **07 and 22 don't produce extra drafts.**

## If your job is a receipts and invoices log

Three rows, nothing else:

| Email | Supplier | Number | Date | Amount (EUR) | VAT | Status |
|---|---|---|---|---|---|---|
| 03 | Harbourline Cycle Parts | INV-20418 | 9 Nov 2026 | 295.20 | 55.20 (23%) | to pay, due 9 Dec 2026 |
| 11 | Port Mango Marine Supply | PMS-7731 | 11 Nov 2026 | 167.60 | included | paid by card |
| 18 | Varga Metalwork | 2026-118 | (work done 1 Oct) | 420.00 | not stated | overdue since 31 Oct 2026 |

Traps: the 60 EUR stall fee (01) and the 30% offer (08) are not costs. Customer prepayments in 14, 24 and 29
(40, 54 and 30 EUR) are money coming in or going back, not supplier costs; a separate refunds list is fine.

## If your job is a bookings list

| Date | Name | What | Status from the inbox |
|---|---|---|---|
| Sat 14 Nov, 10:00 | Saleh (24) | 6 e-bikes | cancelled by customer the same morning; asks to move to Sat 5 Dec (Rosa) |
| Sun 15 Nov, 11:00 | Novak (23) | 2 city bikes | existing booking, may cancel because of rain |
| Sun 15 Nov | Lawson (29) | kayaks, 6 people | cancelled by us for wind |
| Sat 21 Nov, all day | Lindqvist (05, 22) | 2 city bikes, kids' bike, child seat | request, not confirmed |
| Sat 21 Nov, 10:00-14:00 | Brandt (10) | 2 e-bikes | request, not confirmed (price mismatch) |
| Sat 21 or Sun 22 Nov | Jansen (34) | unclear | unclear, flagged |
| "next weekend" | Jensen (15) | family bikes | date unknown, details asked |
| Tue 24 Nov | Grant (19) | 3 city bikes | closed day, can't be listed as asked |
| Sat 28 Nov | Fischer (14) | 8 city bikes | **cancelled** |
| Sat 28 Nov | Carter (21) | 2 bikes + trailer | request, dog question with Rosa |
| Sat 28 or Sun 29 Nov | Nair (04) | child seat | enquiry, day not chosen |
| Sun 29 Nov | Aalto (16) | double kayak | enquiry |
| Fri 4 Dec, 10:00-13:00 | Kestrel Bay Logistics (36) | 12 city bikes + 2 e-bikes | needs Rosa (weekday, group of 14) |
| Sun 27 Dec | Haddad (25) | kayaks, 6 people | closed day, alternatives offered |
| 30 or 31 Dec | Petrov (30) | 2 e-bikes | closed, alternatives offered |

Nothing on this list is confirmed: only Lina or Rosa can confirm.

## If your job is a weekly summary

Five themes, each backed by several emails:

1. **E-bike faults, twice in one weekend** (most important): E2 battery (28) and E4 front brake (33). E-bikes
   also come up in 06/07, 10, 24, 30 and 36.
2. **Weekday and low-season hours**: 02, 12, 19 and 36 ask for a weekday. 35 asks Rosa to keep weekends only.
   That is the week's disagreement: the same question (weekday opening), opposite wishes.
3. **Families and children's kit**: 04, 05/22, 15, 16, 27.
4. **Weather**: 16, 23, 29. In 29 the cancellation email went out at 08:50, after the FAQ's 08:00.
5. **Christmas and vouchers**: 17, 20, 25, 30.

Money this week: 3 supplier bills (295.20 to pay, 420.00 overdue, 167.60 paid), 3 refund questions (14, 20, 24),
a compensation demand (29), a discount request (36).

Single observations, each in exactly one email: a dog in the trailer (21), the car park machine charging in
winter (27), beginner kayak lessons (31).
