# Wachemo SaPS - Django School Portal

A Django-based school portal styled with Tailwind CSS, ready for deployment on Render.

## Local Development

1. Create virtual environment and install deps:
```bash
python -m venv .venv
. .venv/Scripts/activate  # on Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Set environment variables (you can create a .env file):
- DJANGO_SECRET_KEY=change-me
- DJANGO_DEBUG=True
- DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

3. Run migrations and start the server:
```bash
python manage.py migrate
python manage.py runserver
```

4. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

## Environment Variables
- DJANGO_SECRET_KEY: Secret key for Django
- DJANGO_DEBUG: True/False (default False)
- DJANGO_ALLOWED_HOSTS: Comma-separated hosts (e.g. localhost,127.0.0.1,wachemo.onrender.com)
- DATABASE_URL (optional): Database connection string (e.g. Postgres on Render)
- DJANGO_SSL_REDIRECT (prod): True/False (default True if not DEBUG)
- DJANGO_HSTS_SECONDS (prod): seconds for HSTS (default 31536000)

## Static Files
- Served with WhiteNoise. Collect them before deploy:
```bash
python manage.py collectstatic --noinput
```

## Deploy to Render
1. Push this repo to GitHub.
2. Create a new Web Service on Render.
3. Use render.yaml (auto) or set:
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput`
   - Start Command: `gunicorn wachemo.wsgi`
4. Set env vars: DJANGO_SECRET_KEY, DJANGO_ALLOWED_HOSTS, DJANGO_DEBUG=False (and DATABASE_URL if using Postgres).

## Tailwind CSS
- Uses Tailwind CDN for zero-build setup.
- All pages converted to Tailwind. No Bootstrap/JS plugins required.

## Apps
- wachemosaps: public pages, auth
- student: student dashboard and features

## Admin
- Visit `/admin/` with superuser credentials.
