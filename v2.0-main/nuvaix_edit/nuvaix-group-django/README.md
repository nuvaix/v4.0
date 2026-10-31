# NUVAIX GROUP | Django corporate website

Python/Django website for NUVAIX GROUP / NUVAIX SOLUTIONS LTD (RC 9597904).
No Node.js or npm needed.

**Contents**
1. [Quick start (run it locally)](#1-quick-start)
2. [What's new: enquiries → WhatsApp group / email](#2-enquiries--whatsapp-group-and-email)
3. [WhatsApp group relay setup](#3-whatsapp-group-relay-setup)
4. [Email setup](#4-email-setup)
5. [Android app + Google Play install buttons](#5-android-app--google-play-install-buttons)
6. [Admin](#6-admin)
7. [Project layout](#7-project-layout)
8. [Tests](#8-tests)
9. [Deployment (PythonAnywhere / Docker / Heroku-style)](#9-deployment)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Quick start

Requirements: Python 3.10+ (3.12 recommended), pip.

### Linux / macOS / WSL
```bash
cd nuvaix-group-django
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # then edit .env (see sections 3-5)
python manage.py migrate
python manage.py createsuperuser
python manage.py test           # optional but recommended
python manage.py runserver
```

### Windows PowerShell
```powershell
cd nuvaix-group-django
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ (admin: http://127.0.0.1:8000/admin/).

> Migrations are included (`core/migrations/`). If you previously generated your own
> `0001_initial.py` on a server, keep it: `0002_enquiry_delivery_channels.py` builds on it.
> After pulling this update always run `python manage.py migrate`.

---

## 2. Enquiries → WhatsApp group and email

Every "Start a conversation", "Let's talk", "Contact", "Enquire…" and "Send enquiry"
button leads to **one** form: `/contact/`. The visitor picks how to send it:

| Choice | What happens |
|---|---|
| **Send via WhatsApp** | The enquiry is posted into the NUVAIX WhatsApp group (needs the relay, section 3). The message contains the customer's name, email, phone, subject, message and a **one-tap `wa.me` link** so staff can reply to the customer privately. If the relay isn't set up (or fails), the customer gets an "Open WhatsApp" button with the message pre-written, addressed to the NUVAIX number. |
| **Send via email** | The enquiry is emailed to `NUVAIX_EMAIL` with *Reply-To* set to the customer, so staff just press Reply. If SMTP isn't set up, the customer gets an "Open email app" button instead. |
| **Both** | Both of the above. |

Every enquiry is **always saved** in the database first (visible in `/admin/`), so nothing is
lost if WhatsApp or email is down. The admin shows per-channel delivery status and has a
*Re-send* action.

Built-in protection: CSRF, a hidden honeypot field, and a per-IP limit
(`ENQUIRY_RATE_LIMIT`, default 8/hour), important because the form posts into a group chat.

### Free mode: send customers to the group link (no gateway, no cost)
Set `WHATSAPP_GROUP_PUBLIC=1` and `WHATSAPP_GROUP_INVITE_URL=<your invite link>`. After the customer submits the form
(with "Send via WhatsApp" ticked) the thank-you page shows **Copy my message** and **Open WhatsApp group**. They tap
copy, open the group, join, and paste. The enquiry is also saved in `/admin/` and emailed if they chose email.
Limits: a group invite link cannot receive a message by itself, so the customer must paste it; customers become
members of the group and can see its other members and messages. If a gateway is configured and works, it is used
instead and this screen is not shown.

### Why the group invite link was kept private by default
`https://chat.whatsapp.com/…` only lets someone **join** the group. If it were a public
button, every visitor would land inside your internal staff group. WhatsApp offers no official
way for a web form to "type" into a normal group, so the site does it through a gateway
(next section). The invite link is kept in `.env` (`WHATSAPP_GROUP_INVITE_URL`) only as a staff reference.

---

## 3. WhatsApp group relay setup

To have the form post into the group automatically you need a **WhatsApp gateway**: a
service that links a WhatsApp number (like WhatsApp Web) and exposes an HTTP API. The code
in `core/notifications.py` (`send_whatsapp_group`) is written for the Whapi.cloud-style API:
`POST {WHATSAPP_GATEWAY_URL}` with `Authorization: Bearer <token>` and JSON
`{"to": "<group id>@g.us", "body": "<text>"}`. Other gateways (UltraMsg, Evolution API, self-hosted…)
need only a small edit in that one function.

Steps:
1. Create a gateway account and **link a WhatsApp number that is already a member of the NUVAIX group**
   (a dedicated company SIM is best, not anyone's personal number).
   To join that number to the group, open the invite link `https://chat.whatsapp.com/CkOMYcFNLrLGcJRXezDnjE` on it.
2. Copy the API token into `.env` as `WHATSAPP_GATEWAY_TOKEN`.
3. Find the **group ID**. Most gateways have a "list groups" endpoint, e.g. for Whapi:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" https://gate.whapi.cloud/groups
   ```
   Find the NUVAIX group and copy its id (looks like `120363012345678901@g.us`) into `WHATSAPP_GROUP_ID`.
4. Restart the app and submit a test enquiry from `/contact/`. It should appear in the group.

Notes and cautions
- Gateways that link a normal WhatsApp number are **unofficial**; WhatsApp can restrict such numbers.
  Use a dedicated number and keep message volume low. Check the gateway's terms and Meta's current
  WhatsApp Business Platform docs if you need an official route.
- Staff reply flow: tap the **Reply on WhatsApp** link in the group message to open a private chat with the customer.
  If the customer only gave an email, reply by email.
- Without a token and group id the relay is off and customers use the "Open WhatsApp" fallback described above.
- The floating "Chat with us" button and the manual fallback use `WHATSAPP_NUMBER` (default +234 913 216 5565).

---

## 4. Email setup

Set in `.env`:
```
NUVAIX_EMAIL=info@yourdomain.com      # where enquiries are delivered
EMAIL_HOST=smtp.yourprovider.com
EMAIL_PORT=587
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...               # use an app password where the provider supports it
EMAIL_USE_TLS=1                       # or EMAIL_USE_SSL=1 with port 465
DEFAULT_FROM_EMAIL=NUVAIX GROUP <no-reply@yourdomain.com>
```
- With **no `EMAIL_HOST`** and `DJANGO_DEBUG=1`, emails are printed in the terminal (handy for development).
- With no `EMAIL_HOST` and `DJANGO_DEBUG=0`, email delivery is marked *skipped* and the customer sees the mailto fallback.
- Use a sender address on your own domain and set up SPF/DKIM so messages don't land in spam.

---

## 5. Android app + Google Play install buttons

An **Install** button (Google Play) is shown on:
- the **NUVAIX Paint** page (`/paint/`),
- the **Technology** page (`/technology/`),
- **every business division page** (`/businesses/<slug>/`): construction, real estate, technology, automobile,
  logistics, manufacturing, **healthcare/medicine**, retail & agriculture, consultancy, investments,
- and as an "Android app" link in the footer.

Until you have a published app the button shows **"Coming soon · notify me"** (it opens the enquiry form with
type "NUVAIX Android app"). To switch every button to the real Play Store listing, set in `.env`:

```
ANDROID_APP_PACKAGE=com.nuvaix.app
# or the full URL:
PLAY_STORE_URL=https://play.google.com/store/apps/details?id=com.nuvaix.app
```

One app for the whole group is the default. If you publish **separate apps per division**, add overrides
(slug upper-cased, `-` becomes `_`):

```
PLAY_STORE_URL_PAINT=https://play.google.com/store/apps/details?id=com.nuvaix.paint
PLAY_STORE_URL_TECHNOLOGY=...                    # /technology/ page
PLAY_STORE_URL_TECHNOLOGY_IT_SOLUTIONS=...       # Technology & IT division page
PLAY_STORE_URL_REAL_ESTATE=...
PLAY_STORE_URL_HEALTHCARE=...
PLAY_STORE_URL_AUTOMOBILE=...   # etc.
```
Links are tagged with a Play `referrer` (`utm_campaign=<division>`) so you can see in Play Console which
page drove installs.

The button uses a simple generic icon. When the app is live, you may swap in Google's official
"Get it on Google Play" badge; follow Google's badge guidelines.

Publishing the app itself (Android Studio build → Play Console) happens outside this repo.

---

## 6. Admin
`/admin/` → **Enquiries**: filter by status/type/channel, see WhatsApp/email delivery status, one-click
*Reply* links, edit status (new / in progress / closed), and use the **Re-send** action to retry delivery.
Keep admin credentials private.

---

## 7. Project layout
```
config/            settings.py (env-driven), urls.py, wsgi/asgi
core/views.py      pages, enquiry form, thank-you page
core/notifications.py  WhatsApp group relay + email delivery
core/links.py      wa.me / Google Play link helpers
core/models.py     Enquiry (+ channels and delivery status)
core/migrations/   0001_initial, 0002_enquiry_delivery_channels
core/templates/core/   base, contact, contact_sent, _install_button, ...
core/static/core/      css, js, images
.env.example       every setting, documented
```

## 8. Tests
```bash
python manage.py check
python manage.py test
```
Covers: pages load, enquiry validation, WhatsApp gateway success/failure/fallback, email delivery,
honeypot, rate limit, and the Play Store buttons (coming-soon, default link, per-division link).

## 9. Deployment
1. `DJANGO_SECRET_KEY` = long random value (`python -c "import secrets; print(secrets.token_urlsafe(50))"`)
2. `DJANGO_DEBUG=0`
3. `DJANGO_ALLOWED_HOSTS` = your hostnames; `DJANGO_CSRF_TRUSTED_ORIGINS` = full https origins
4. Set the WhatsApp, email and Play Store variables from sections 3-5
5. `python manage.py migrate` and `python manage.py collectstatic --noinput`
6. Serve over HTTPS; configure backups for the database (use PostgreSQL for real scale, not SQLite on ephemeral hosting)

**PythonAnywhere:** put the variables in the `.env` file in the project folder (or the WSGI file), then
click *Reload*. Free PythonAnywhere accounts can only reach an allow-listed set of external sites, so the
WhatsApp gateway and some SMTP servers may be blocked; check their allow-list or use a paid account.

A `Dockerfile` and `Procfile` are included as starting points.

## 10. Troubleshooting
| Symptom | Fix |
|---|---|
| `no such table: core_enquiry` | Run `python manage.py migrate` |
| Enquiry saved but not in the group | Check `WHATSAPP_GATEWAY_TOKEN` / `WHATSAPP_GROUP_ID`; the admin *delivery note* shows the gateway error; the number linked in the gateway must be a member of the group |
| Email shows "skipped" | Set `NUVAIX_EMAIL` and `EMAIL_HOST` (and `DJANGO_DEBUG=0` needs real SMTP) |
| Install button says "Coming soon" | Set `PLAY_STORE_URL` or `ANDROID_APP_PACKAGE` and restart |
| CSRF error on the form behind HTTPS | Add your `https://…` origin to `DJANGO_CSRF_TRUSTED_ORIGINS` |

## Production notes
- Projects, careers, insights and partner listings show an editorial placeholder until approved content exists.
- Privacy and Terms pages are draft notices and need legal review before launch.
- Product packaging artwork is concept/placeholder material, not confirmed inventory.
- Not yet verified by the author of this change: a live run of the test-suite and a real WhatsApp-gateway / SMTP delivery in your environment. Run `python manage.py test` and send a test enquiry before launch.
