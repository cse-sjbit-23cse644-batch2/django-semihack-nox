# Event Lifecycle & Certification System

A Django web application for managing academic events: student registration with transaction verification → QR/attendance tracking → feedback → conditional PDF certificate issuance.

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run migrations
python manage.py migrate

# 3. Create a superuser (for admin dashboard)
python manage.py createsuperuser

# 4. Start the server
python manage.py runserver
```

Then visit `http://127.0.0.1:8000/`.

---

## Verification Checklist

| # | Test | Expected |
|---|------|----------|
| 1 | `python manage.py runserver` | App loads at http://127.0.0.1:8000 |
| 2 | Register with valid transaction ID + receipt | Saves to DB, success page shown |
| 3 | Register with duplicate Student ID or Transaction ID | Error shown, no save |
| 4 | Upload invalid file type or file > 2MB | Validation error, no save |
| 5 | Admin toggles attendance button | DB updates, UI reflects change without refresh |
| 6 | Submit feedback via feedback link | Flag updates, certificate becomes available |
| 7 | Visit `/certificate/<token>/` with ALL conditions met | PDF downloads |
| 8 | Visit same URL without all conditions | 403 page with missing conditions listed |
| 9 | Mobile view | Forms usable on phone screen (Bootstrap 5 responsive) |

---

## CO–SDG Mapping

| Course Outcome | How This Project Demonstrates It | SDG Target |
|---|---|---|
| CO1: MVT Architecture | URL routing for `/register/`, `/dashboard/`, `/certificate/<token>/`, `/feedback/<token>/` endpoints | SDG 4.3 — Equal access to education |
| CO2: Models & Forms | `Participant` model with `unique=True` constraints + `RegistrationForm` with `clean_transaction_id()`, `clean_student_id()`, file validators | SDG 4.5 — Eliminate disparities |
| CO3: Template Inheritance | Reusable `base.html` with `{% block content %}` + responsive Bootstrap 5 admin/student views | SDG 4.A — Inclusive learning environments |
| CO4: Non-HTML Output | ReportLab PDF generation in `utils.py` with conditional gatekeeper logic (attendance + feedback + transaction verified) | SDG 16.10 — Public access to information |
| CO5: AJAX Integration | Attendance toggle and transaction verification via `fetch()` in `ajax_toggle.js` — no page refresh | SDG 9.C — Universal access to ICT |

---

## SDG Justification

> Our Event Lifecycle & Certification system advances **SDG 4: Quality Education** (Target 4.5) by digitizing academic event management with transparent transaction verification — ensuring equitable access to registration and verified certificates while preventing fraud. The conditional PDF issuance (CO4) supports **SDG 16: Peace, Justice & Strong Institutions** (Target 16.10) by providing tamper-evident certification tied to verified attendance, feedback, and payment. Built with Django's validated forms (CO2) and AJAX-driven attendance (CO5), the system demonstrates responsive, user-centered design that promotes trust, accountability, and inclusive participation in academic activities.

---

## Project Structure

```
event_lifecycle/
├── events/
│   ├── models.py          # Event, Participant models
│   ├── forms.py           # RegistrationForm, FeedbackForm
│   ├── views.py           # register(), toggle_attendance(), certificate(), api_stats()
│   ├── urls.py            # All app routes
│   ├── utils.py           # generate_pdf() via ReportLab, generate_qr()
│   ├── validators.py      # File type/size validators
│   └── admin.py           # Django admin registration
├── templates/
│   ├── base.html                          # Bootstrap 5 layout
│   ├── events/register.html               # Registration form
│   ├── events/register_success.html
│   ├── events/admin_dashboard.html        # AJAX attendance/verify dashboard
│   ├── events/feedback.html
│   └── events/certificate_blocked.html    # 403 gatekeeper page
├── static/
│   └── js/ajax_toggle.js                  # Attendance + verify AJAX
├── media/
│   └── receipts/                          # Uploaded receipts (gitignored)
├── requirements.txt
└── README.md
```

---

## Bonus Features Implemented

- **Real-time stats counter** — `/api/stats/` polled every 30s on the dashboard
- **QR code utility** — `generate_qr()` in `utils.py` (ready to use in signals/views)
