# 🌊 AquaReserve — Boat & Jet Ski Reservation Platform

A modern, full-stack Django reservation platform for water tourism businesses. Customers browse and reserve boats, jet skis, yachts and speedboats online with real-time availability and zero booking conflicts. Operators manage their fleet, approve reservations and view analytics from a dedicated admin dashboard.

## ✨ Features

- **JWT Authentication** (register / login / logout) with role-based access (customer vs admin)
- **Watercraft management** — CRUD with type categorization (boat, jet ski, yacht, speed boat), pricing, capacity, location, image URL
- **Smart booking system** with server-side validation:
  - ❌ Overlapping reservations rejected
  - ❌ Past dates rejected
  - ❌ Passenger count > capacity rejected
  - ❌ Unavailable watercraft cannot be booked
  - ✅ Auto-calculated total price (duration × hourly rate)
  - ✅ Min 30 min, max 12 hr duration enforced
- **Customer dashboard** — view upcoming/past bookings, cancel pending reservations
- **Admin dashboard** — approve/reject/complete reservations, manage fleet, KPIs, top-booked watercraft
- **Public availability endpoint** — see what slots are taken for any watercraft on a date
- **Ocean-themed responsive UI** built with vanilla JS + a hand-crafted CSS design system
- **REST API** powered by Django REST Framework + SimpleJWT

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 6.0 |
| API | Django REST Framework |
| Auth | djangorestframework-simplejwt (JWT) |
| Database | SQLite (production-ready: swap to PostgreSQL via `DATABASES` setting) |
| Frontend | Server-rendered HTML templates + vanilla JS (no build step) |
| Styling | Custom CSS design system (ocean palette, fluid typography) |
| Images | Pillow for uploads, external URL fallback supported |
| CORS | django-cors-headers |

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install django djangorestframework django-cors-headers Pillow djangorestframework-simplejwt

# 2. Run migrations
python manage.py migrate

# 3. Seed demo data (admin + customer + 8 watercraft)
python manage.py seed

# 4. Start dev server
python manage.py runserver
```

Visit **http://localhost:8000** and log in with:

- **Admin** → `admin` / `admin123` (full operator console)
- **Customer** → `demo` / `demo1234` (booking flow)

## 📁 Project Structure

```
aquareserve/
├── aquareserve/         # Project settings + URL routing
│   ├── settings.py
│   └── urls.py
├── accounts/            # Custom User model + JWT auth endpoints
│   ├── models.py        # User(role=customer|admin)
│   ├── serializers.py
│   └── views.py
├── watercraft/          # Fleet CRUD
│   ├── models.py        # Watercraft(type, price, capacity, …)
│   ├── permissions.py   # IsAdminOrReadOnly
│   └── management/commands/seed.py
├── reservations/        # Booking system (the heart)
│   ├── models.py        # Reservation with overlap-detection logic
│   ├── serializers.py
│   ├── permissions.py   # IsOwnerOrAdmin
│   └── views.py         # ViewSet + admin endpoints
├── templates/           # 8 server-rendered pages
├── static/
│   ├── css/styles.css   # Ocean design system
│   └── js/{api.js,app.js}  # API client + UI helpers
├── media/               # Uploaded watercraft images
└── manage.py
```

## 🔌 API Reference

All endpoints prefixed with `/api`. Protected endpoints require `Authorization: Bearer <access_token>`.

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new customer |
| POST | `/auth/login` | Get JWT pair |
| POST | `/auth/logout` | Blacklist refresh token |
| GET/PATCH | `/auth/me` | Get / update profile |

### Watercraft
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/watercraft/` | List (filter by `?type=` `?available=true` `?search=`) | Public |
| GET | `/watercraft/{id}/` | Detail | Public |
| POST | `/watercraft/` | Create | Admin |
| PUT | `/watercraft/{id}/` | Update | Admin |
| DELETE | `/watercraft/{id}/` | Delete | Admin |
| GET | `/watercraft/{id}/availability?date=YYYY-MM-DD` | Booked time slots | Public |

### Reservations
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/reservations/` | List own (admin sees all) | User |
| POST | `/reservations/` | Create booking | User |
| GET | `/reservations/{id}/` | Detail | Owner/Admin |
| PUT | `/reservations/{id}/` | Update | Owner/Admin |
| DELETE | `/reservations/{id}/` | Delete | Owner/Admin |
| POST | `/reservations/{id}/cancel/` | Soft-cancel | Owner/Admin |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/reservations` | All reservations (filter by `?status=`) |
| PATCH | `/admin/reservations/{id}/status` | `{"status":"approved\|rejected\|completed"}` |
| GET | `/admin/stats` | KPIs + top-booked watercraft |

## 🧪 Tested Scenarios

The booking validator was tested end-to-end via curl and returns clean, field-keyed error messages:

```json
// Overlapping booking
{ "start_time": ["This time slot overlaps with an existing reservation."] }

// Over capacity
{ "passenger_count": ["Passenger count exceeds capacity (8)."] }

// Past date
{ "reservation_date": ["Cannot book a slot in the past."] }
```

## 🎨 Design Notes

The UI uses a hand-crafted ocean-inspired palette (`--ocean-900 → --aqua-200 → --sand-50`) with **Playfair Display** for headings and **Manrope** for body. The hero section features a custom SVG wave divider, and the fleet grid uses CSS aspect-ratio for consistent imagery. Inline SVG placeholder images per craft type ensure every card looks polished even without uploaded photos.

## 🚧 Optional Enhancements (Roadmap)

- Online payment integration (Stripe / PayPal)
- Email notifications on status changes
- QR-coded reservation tickets
- Weather forecast integration
- Reviews & star ratings
- Google Maps marker per dock location
- Booking countdown timers
- Real-time availability via WebSockets (Django Channels)

## 📄 License

MIT — built as a Django learning showcase.
