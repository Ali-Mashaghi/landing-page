# Ali Mashaghi — Personal Portfolio

A modern personal website and portfolio built with **Django**.  
Reusable for any developer: edit the profile in the dashboard and the public site updates.

**Live:** [mashaghi.ir](https://mashaghi.ir)

---

## Screenshots

### Home
![Homepage](pics%20of%20website/1.png)

### Resume
![Resume page](pics%20of%20website/2.png)

### Digital business card
![Business card](pics%20of%20website/3.png)

### Contact
![Contact page](pics%20of%20website/4.png)

### Dashboard — private card link & QR
![Dashboard profile](pics%20of%20website/5.png)

---

## Features

- **Home** — hero intro, bio, and CTAs
- **Resume** — profile card, skills, Telegram QR, resume download
- **Projects** — portfolio list with images and repo links
- **Contact** — form with email notification + auto-reply
- **Digital business card** — flip card UI with contact links
- **Private card QR** — secret `/card/<token>/` link (shareable without login); regenerate from dashboard
- **Staff dashboard** — edit profile, manage projects, read contact messages
- **REST API** — profile, projects, skills, contact
- **Jalali dates** — Persian calendar helpers in templates
- **S3 media** — optional Object Storage for uploads (Liara-friendly)

---

## Tech stack

| Layer | Choice |
|--------|--------|
| Backend | Django 6 |
| API | Django REST Framework |
| Database | PostgreSQL |
| Frontend | HTML, CSS, JavaScript (Bootstrap-based UI) |
| Server | Gunicorn |
| Deploy | Liara (+ GitHub Actions) |
| Media | Local disk or S3-compatible storage |

---

## Quick start

```bash
# Clone
git clone https://github.com/<your-username>/landing-page.git
cd landing-page

# Virtualenv
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# Dependencies
pip install -r requirements.txt

# Env (minimum for local run)
# Create a .env file — see below

# Database
python manage.py migrate

# Admin / staff user
python manage.py createsuperuser

# Run
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).  
Dashboard: [http://127.0.0.1:8000/dashboard/login/](http://127.0.0.1:8000/dashboard/login/)

---

## Environment variables

Create a `.env` in the project root:

```env
DJANGO_SECRET_KEY=change-me-to-a-long-random-string

# Database (defaults target PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=herodb
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Optional: SQLite for quick local testing
# DB_ENGINE=django.db.backends.sqlite3
# DB_NAME=db.sqlite3

# Email (contact form)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your@gmail.com
CONTACT_NOTIFICATION_EMAIL=your@gmail.com
```

### S3 / Liara Object Storage (production uploads)

Container disks on Liara are limited; use Object Storage for profile images, resumes, and project images:

```env
S3_BUCKET_NAME=your-bucket-name
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_ENDPOINT_URL=https://your-s3-endpoint
S3_REGION_NAME=us-east-1
S3_QUERYSTRING_AUTH=False
```

Make the bucket publicly readable for images, or set `S3_QUERYSTRING_AUTH=True` for signed URLs.

---

## Main routes

| Path | Description |
|------|-------------|
| `/` | Home |
| `/resume/` | Resume |
| `/projects/` | Projects |
| `/contact/` | Contact form |
| `/card/` | Business card preview (login required) |
| `/card/<uuid>/` | **Public private-link card** (token QR target) |
| `/dashboard/login/` | Staff login |
| `/dashboard/` | Admin dashboard |
| `/dashboard/profile/` | Edit profile + secret card URL / QR |
| `/api/` | REST API root |

---

## Private business card QR

Each user gets a unique `card_token`.

1. Sign in as staff → **Dashboard → Edit Profile**
2. Copy the **secret card URL** or use the QR image
3. Anyone with that link can open the card **without logging in**
4. **Regenerate link** invalidates the old URL and QR

Preview at `/card/` always points the on-card QR to your token URL.

> After deploying schema changes, run migrations on the server:
> `python manage.py migrate`  
> Missing `card_token` causes login / homepage **500** errors.

---

## Project structure

```
landing-page/
├── config/                 # Django settings, URLs, WSGI/ASGI
├── hero/                   # App: models, views, API, migrations
├── Templates/              # HTML templates (site + dashboard)
├── static/                 # CSS, JS, fonts
├── media/                  # Local uploads (dev)
├── pics of website/        # README screenshots
├── liara.json              # Liara deploy config
├── .github/workflows/      # CD to Liara
├── requirements.txt
└── manage.py
```

---

## Deploy (Liara)

This repo includes [`.github/workflows/liara.yaml`](.github/workflows/liara.yaml) for deploy on push to `main`.

After each release that changes models:

```bash
python manage.py migrate
```

Set the same env vars in the Liara app settings (secret key, DB, email, S3).

---

## License

All rights reserved.
