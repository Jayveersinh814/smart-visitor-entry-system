# Gate Visitor Pass QR Code System (Python + Django)

This project is a complete starter web app for gate visitor pass management:
- Visitor registration with reference and host details
- Approval workflow (pending -> approved/rejected)
- Signed QR generation per visitor pass
- Gate scan validation (entry/exit), one-time or multi-entry support
- Check-in/check-out tracking + gate tracking
- Watchlist alerts
- Role-based access (admin, guard, host)
- Logs and CSV export

## Quick Start

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Run migrations:
   - `python manage.py migrate`
3. Create superuser:
   - `python manage.py createsuperuser`
4. Start server:
   - `python manage.py runserver`
5. Open:
   - `http://127.0.0.1:8000/`

## Role Setup

1. Login to `/admin`
2. Create users for guards/hosts
3. In `User Profiles`, set role to:
   - `admin`
   - `guard`
   - `host`
4. Create gates in `Gates` (Gate A, Gate B, etc.)

## Email (QR + invite to visitor)

When a pass is **approved**, an email is sent to the visitor’s address (if filled on registration): HTML invite + **QR PNG attached** (`visitor_pass_qr.png`).

- **Development:** emails print to the **console** (terminal where `runserver` runs). See `EMAIL_BACKEND` in `gatepass/settings.py`.
- **Production:** switch to SMTP in `settings.py` (see comments there). Example: Gmail with an app password.

## Other delivery (SMS/WhatsApp/PDF)

- SMS/WhatsApp: Twilio / Meta / provider API
- PDF pass: `reportlab` or HTML-to-PDF renderer

## Notes

- Database: SQLite (easy local start)
- QR security: Django signed token + time validation
- Media uploads: `media/` folder (ID proof + QR images)
