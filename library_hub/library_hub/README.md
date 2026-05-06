# Online Library – Django Project

## Project Structure

```
online_library/
├── library/          # Project config (settings, urls, wsgi)
├── users/            # Auth: register, login, logout, profile
├── books/            # (future) Book listings
├── reading/          # (future) Reading lists
├── reviews/          # (future) Book reviews
├── templates/        # All HTML templates
│   ├── base.html
│   ├── home.html
│   └── users/
│       ├── login.html
│       ├── register.html
│       └── profile.html
├── db.sqlite3
└── manage.py
```

## How to Run

### 1. Set up a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install django
```

### 2. Apply migrations

```bash
python manage.py migrate
```

### 3. (Optional) Create a superuser for admin access

```bash
python manage.py createsuperuser
```

### 4. Run the development server

```bash
python manage.py runserver
```

### 5. Open in browser

| URL | Page |
|-----|------|
| http://127.0.0.1:8000/ | Home |
| http://127.0.0.1:8000/users/register/ | Register |
| http://127.0.0.1:8000/users/login/ | Login |
| http://127.0.0.1:8000/users/profile/ | Profile (login required) |
| http://127.0.0.1:8000/admin/ | Django Admin |
