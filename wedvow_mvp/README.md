# WedVow — Washy's Golden Jubilee

Interactive surprise birthday invitation for **Washy's 50th** (28 November 2026): envelope open, black-and-gold scroll sections, Google Maps, and RSVP by phone/WhatsApp to Mamsie & Khanyi.

Simple static site — no online form, no backend required for this party.

## Run it

1. Open `Documents/AI-Internship/wedvow_mvp/index.html` in a browser.
2. Tap the envelope, scroll, use **Call** / **WhatsApp** or **Open in Google Maps**.

> Local URL: `python -m http.server 5173` then `http://127.0.0.1:5173/`

## Event details

- Surprise Birthday Party — Washy's Golden Jubilee
- **28 November 2026** at **13:00**
- Greekish Restaurant, Westlake Eco Estate, Modderfontein
- Theme: Black with a touch of gold · Adults only
- RSVP by 5 November → Mamsie / Khanyi only (call or WhatsApp)

## Personalize the invite

Edit [`js/event-config.js`](js/event-config.js) and photos in `assets/`:

- Names, date, venue, dress code, RSVP contacts & deadline
- `portraitImage` / `heroImage`, `dashboardPin`, `storageKey`

Save and refresh the browser.

## What's implemented

- Immersive birthday invitation (hero, story, details, RSVP, extras, close)
- Envelope open animation + scroll reveals + light hero parallax
- RSVP form (accept/decline, guest count, optional note)
- Host dashboard with demo PIN, stats, guest list, CSV export, clear data
- Config-driven content for later multi-event / wedding templates
- Mobile-first layout and `prefers-reduced-motion` support

## Important limitation

RSVP records are stored in browser `localStorage`. They only appear in the same browser on the same device. This is not production storage — do not enter real guest information.

There is no real authentication, multi-host isolation, payments, email, or backend yet. The dashboard PIN is a demo gate only.

## Project layout

```
wedvow_mvp/
  index.html          Guest invitation
  dashboard.html      Host dashboard
  css/invite.css      Shared styles
  js/event-config.js  Edit this to personalize
  js/storage.js       Shared RSVP localStorage helpers
  js/invite.js        Envelope, reveals, RSVP
  js/dashboard.js     PIN gate + stats + CSV
  supabase/schema.sql Starter schema for the next milestone
```

## Next milestone (platform)

1. Move to **Next.js + TypeScript**.
2. Generalize Supabase `weddings` → `events` (`type: birthday | wedding`) using [`supabase/schema.sql`](supabase/schema.sql) as a starting point.
3. Add Auth + row-level security so hosts only see their own events.
4. Public invite route `/i/[slug]` and private `/dashboard`.
5. Server route for RSVP submit (validation + rate limiting).
6. Stripe Checkout for one-time paid unlock; then templates for weddings.

## Suggested pricing experiment (later)

- Essential: €49 one-time per event
- Signature: €89 with extra layouts and gallery
- Studio: €15/month for planners managing multiple events

Hypotheses only — validate before publishing.
