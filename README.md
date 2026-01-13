---

# 🚚 Altivox Logistics API

A **Django REST API** for managing logistics operations — users, shipments, drivers, and invoices. Built with **Django**, **DRF**, **JWT authentication**, and **Celery** for async tasks.

---

## ✨ Features

* 👤 **User Management**: Register, login, logout, profile update, assign admin roles, list & delete users.
* 📦 **Shipments Management**: Create shipments, track orders, assign drivers, update status, delete shipments.
* 🚛 **Driver Operations**: List driver orders, update order status.
* 🧾 **Invoicing**: Create, update, delete, and list invoices. Async invoice generation supported.
* 📊 **Reporting Dashboard**: Shipment & driver summaries, order efficiency, average delivery times.
* ⚡ **Async Tasks**: Contact emails, quote emails, registration mails, invoice generation (Celery).
* 🔐 **JWT Authentication**: Secure API endpoints.
* 🌐 **CORS Support**: Frontend integration ready.

---

## 🛠 Tech Stack

* **Backend**: Django 4.2, Django REST Framework
* **Auth**: JWT (djangorestframework-simplejwt)
* **Database**: SQLite (dev)
* **Async Tasks**: Celery
* **Containerization**: Docker (optional)
* **CORS Handling**: django-cors-headers

---

## ⚡ Getting Started

### Prerequisites

* Python 3.11+
* pip
* Docker 
* Gmail or SMTP credentials for sending emails

### Setup

1. Clone the repo:

```bash
git clone <repo-url>
cd altivox
```

2. Create & activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables (`.env`):

```
EMAIL_HOST=<your-email@gmail.com>
EMAIL_PASSWORD=<app-password>
```

5. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create a superuser (optional):

```bash
python manage.py createsuperuser
```

7. Start the server:

```bash
python manage.py runserver
```

API available at: `http://127.0.0.1:8000/api/`

---

### 🐳 Docker Setup 

1. Build the image:

```bash
docker build -t altivox .
```

2. Run container with persistent SQLite:

```bash
docker run -p 8000:8000 -v $(pwd)/db.sqlite3:/app/db.sqlite3 altivox
```

3. Apply migrations inside container:

```bash
docker exec -it <container_id> python manage.py migrate
```

---

## 📌 API Endpoints

| Method           | Endpoint                             | Description                 |
| ---------------- | ------------------------------------ | --------------------------- |
| POST             | `/api/auth/register/`                | 👤 Register new user        |
| POST             | `/api/auth/login/`                   | 🔑 Get JWT token            |
| POST             | `/api/auth/logout/`                  | 🚪 Logout & blacklist token |
| GET              | `/api/profile/`                      | 📝 Get profile              |
| PUT/PATCH        | `/api/profile/`                      | ✏️ Update profile           |
| GET              | `/api/drivers/`                      | 🚛 List all drivers         |
| GET              | `/api/dashboard/`                    | 📊 Admin dashboard summary  |
| GET/POST         | `/api/shipments/`                    | 📦 List/create shipments    |
| PATCH            | `/api/shipments/<id>/assign_driver/` | 👷 Assign driver            |
| DELETE           | `/api/shipments/<id>/delete/`        | ❌ Delete shipment           |
| GET/POST         | `/api/invoices/`                     | 🧾 List/create invoices     |
| PUT/PATCH/DELETE | `/api/invoices/<id>/`                | ✏️ Update/Delete invoice    |
| POST             | `/api/request_quote/`                | 💬 Submit quote request     |
| POST             | `/api/contact/`                      | 📧 Contact via email        |
| POST             | `/api/order/track/`                  | 🔍 Track shipment           |

---

## ⚡ Celery Tasks

* ✉️ `register_mail` — Welcome email on registration
* ✉️ `send_contact_email` — Handle contact form submissions
* ✉️ `send_quote_email` — Handle quote requests
* 🧾 `invoice_generate` — Generate & send invoices

---

## 💡 Notes

* SQLite is for **development only**
* Production → use PostgreSQL/MySQL for persistence
* SMTP credentials required for email
* Docker is optional, helps with dev isolation & deployment

---

## 📄 License

MIT License

---
