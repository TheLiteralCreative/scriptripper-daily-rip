# Stripe Billing Setup

Distilled from the pre-pivot `STRIPE_SETUP_GUIDE.md`, `FIX_STRIPE_WEBHOOK.md`, and
`create-stripe-price.js`. The *mechanics* of Stripe have not changed with the pivot —
this flow is durable. What has changed is the **pricing model**, flagged below.

---

## How Stripe billing fits together

There are three moving parts, and webhooks are the part people get wrong:

1. **Product + Price** — created once in Stripe. A Price has an ID like `price_...` and
   that ID goes in your environment as `STRIPE_PRO_PRICE_ID`.
2. **Checkout Session** — when a user upgrades, your API calls Stripe to create a
   checkout session and redirects the user to Stripe's hosted payment page.
3. **Webhook** — after the user pays, Stripe calls *your* API back at a webhook URL to
   say "this happened." Your API verifies the call is really from Stripe (signature
   check) and then upgrades the user in the database.

The webhook is the only reliable signal that a payment succeeded. The redirect back to
your "success" page is *not* — a user can close the tab. Always act on the webhook.

---

## ⚠️ Pricing model: decide before you build

The archive sold one thing: a flat **$5/month "ScriptRipper Pro"** subscription. That is
**not** the current model. The current direction (see `MEDIA_RIPPERS_PROGRAM_PLAN.md`) is
the standard Ripper auth/credit model:

> Email registration → one free run → tier-gated continued use, with two paths: buy
> credits against the admin API, or bring your own API key.

So before creating Products and Prices in Stripe, the tier structure and credit pricing
have to be settled. This guide covers the *plumbing*, which is the same regardless of how
many tiers exist. Just don't create a single `price_...` and call it done — that was the
old model.

---

## Step 1 — Create the Product and Price

Three ways, same result. A Price ID (`price_...`) comes out the end.

**Dashboard (simplest):** Stripe Dashboard → Products → Add product. Set name,
description, amount, and billing interval (monthly). Save, then copy the **Price ID**.
Test-mode lives at `dashboard.stripe.com/test/products`; live mode at
`dashboard.stripe.com/products` — they are separate, with separate IDs.

**Stripe CLI:**
```bash
stripe products create --name="ScriptRipper Pro" --description="..."
stripe prices create --product=prod_XXXX --unit-amount=500 \
  --currency=usd --recurring[interval]=month
```
(`unit-amount` is in cents — `500` = $5.00.)

**Script:** the archive's `create-stripe-price.js` is idempotent — it checks for an
existing product/price before creating, so it is safe to re-run. Reuse the *pattern*, but
**do not reuse the file as-is**: it had a Stripe secret key hardcoded as a fallback.
Always read the key from `process.env.STRIPE_SECRET_KEY` with no hardcoded default.

---

## Step 2 — Environment variables

```
STRIPE_SECRET_KEY=sk_test_...      # sk_test_ for testing, sk_live_ for production
STRIPE_PUBLISHABLE_KEY=pk_...
STRIPE_PRO_PRICE_ID=price_...      # from Step 1
STRIPE_WEBHOOK_SECRET=whsec_...    # from Step 3 — empty until then
STRIPE_SUCCESS_URL=https://scriptripper.com/success
STRIPE_CANCEL_URL=https://scriptripper.com/pricing
```

Test keys and live keys are different keys for different worlds. A `price_...` created in
test mode does not exist in live mode. When you go live, every one of these values gets
swapped for its live-mode equivalent.

---

## Step 3 — Webhooks while developing locally

Stripe can't reach `localhost`, so the Stripe CLI tunnels events to your machine:

```bash
stripe listen --forward-to localhost:8000/api/v1/billing/webhook
```

It prints a signing secret (`whsec_...`). Copy that into `STRIPE_WEBHOOK_SECRET` and
restart the API. Keep `stripe listen` running the whole time you're testing.

Trigger fake events in another terminal:
```bash
stripe trigger checkout.session.completed
stripe trigger customer.subscription.deleted
```

> Confirm the real webhook route in `app/api/subscriptions.py`. The archive used
> `/api/v1/billing/webhook`; the current route may differ. Use whatever the code exposes.

---

## Step 4 — Webhooks in production

Once deployed: Stripe Dashboard → Developers → Webhooks → Add endpoint.

- **URL:** `https://api.scriptripper.com/<webhook route>`
- **Events:** at minimum `checkout.session.completed`,
  `customer.subscription.updated`, `customer.subscription.deleted`.
- Copy the endpoint's signing secret into the deployed `STRIPE_WEBHOOK_SECRET` env var.

The production webhook secret is *different* from the `stripe listen` one. They are not
interchangeable.

---

## Step 5 — Test the full flow

Use Stripe's test card — it never charges real money:

```
Card:   4242 4242 4242 4242
Expiry: any future date  (e.g. 12/34)
CVC:    any 3 digits
ZIP:    any 5 digits
```

A complete pass: register a user → start checkout → pay with the test card → land on the
success page → see `checkout.session.completed` in the `stripe listen` terminal → confirm
the user's tier changed in the database.

---

## Recovery: a user paid but wasn't upgraded

This actually happened before (it's why `FIX_STRIPE_WEBHOOK.md` exists). The cause is
almost always the webhook: the API wasn't running when the payment landed, or
`STRIPE_WEBHOOK_SECRET` was wrong so signature verification failed and the event was
rejected. Fix the webhook for the future, then upgrade the affected user by hand. In rough
order of preference:

1. **Admin endpoint** — if an admin "set tier" route exists, call it.
2. **Direct database update** — connect to the database and update the user's tier and
   subscription-source columns for that email. (On Render, use the service Shell tab.)

Then re-test with `stripe trigger` so the next real payment upgrades automatically.

---

## Common issues

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| "Stripe is not configured" | `STRIPE_SECRET_KEY` or `STRIPE_PRO_PRICE_ID` missing | Set them in the environment, restart |
| Webhook signature verification failed | `STRIPE_WEBHOOK_SECRET` doesn't match the endpoint | Copy the correct `whsec_...` — local and prod secrets differ |
| Payment succeeds, user not upgraded | API was down when the webhook fired, or the handler errored | Check API logs; recover the user manually (above) |
| "Invalid price" | Using a `prod_...` ID where a `price_...` is needed | Use the Price ID, not the Product ID |
| Webhook fires but can't find the user | `user_id` not attached to the checkout session metadata | Ensure the checkout session is created with the user's ID in `metadata` |

---

## Security note

The old `STRIPE_SETUP_GUIDE.md` and `create-stripe-price.js` had a real `sk_test_...` key
written directly into the file. That key should be rotated (Stripe Dashboard → Developers
→ API keys → roll it). The rule going forward: **secret keys live in `.env` only**, never
in a tracked file, a guide, or a script's default value.
