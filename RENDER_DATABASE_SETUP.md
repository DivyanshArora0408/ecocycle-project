# EcoCycle – PostgreSQL on Render

The project is a Django application. It already has Django models and migrations for:
- Django users (registration/login)
- PickupRequest (e-waste pickup requests)
- RecyclerProfile (recycler applications and approval)
- PickupReview (pickup reviews)

## Connect the existing Render website to PostgreSQL

1. Open the Render Dashboard and create a **PostgreSQL** database in the same region as the EcoCycle web service.
2. Open the database page and copy its **Internal Database URL** (not the External URL).
3. Open the existing EcoCycle Web Service → **Environment**.
4. Add an environment variable:
   - Key: `DATABASE_URL`
   - Value: the Internal Database URL copied in step 2.
5. Ensure these web-service settings are present:
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start Command: `gunicorn config.wsgi:application`
6. Deploy the latest code. Render will install dependencies, collect static files, and create the database tables from the existing migrations.
7. Create an admin account from the Render Shell:
   `python manage.py createsuperuser`
8. Open `/admin/` on the website and sign in to manage users, pickup requests, recycler profiles, and reviews.

## Local development

Without `DATABASE_URL`, the app continues to use the local `db.sqlite3` file. Run:

```bash
python -m venv venv
# Windows: venv\\Scripts\\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Important

- Never put the database URL or database password in source code or commit it to GitHub.
- Use Render's **Internal Database URL** for a web service hosted on Render.
- The first deployment to a new PostgreSQL database creates empty tables. Existing SQLite records are not copied automatically. If you need to preserve existing users or pickup data, export/import them separately before switching.
- Uploaded images are stored under `media/`; database migration alone does not move uploaded image files to persistent object storage.
