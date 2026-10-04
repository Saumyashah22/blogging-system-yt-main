# Django Blogging System

A Django-based blogging platform built for managing blog posts, categories, featured content, comments, and user dashboards. The project includes a public front-end for readers and a private dashboard for admins/users to manage content.

## Overview

This project is a complete blog application with:
- blog post creation and editing
- category management
- featured and regular posts
- image uploads for media content
- comment support for published posts
- search functionality
- admin and user-specific dashboard workflows
- bootstrap-based UI with Django templates

## Tech Stack
- Python
- Django
- SQLite (default for development)
- Bootstrap 4 via Django Crispy Forms
- Pillow for image handling

## Project Structure

```text
blogging-system-yt-main/
├── assignments/          # additional project sections / About and social data
├── blog_main/            # Django project settings and entry points
├── blogs/                # blog app: models, views, forms, URLs
├── dashboards/           # admin/dashboard logic and management pages
├── media/                # uploaded media files
├── templates/            # shared HTML templates
├── .venv/                # local virtual environment
├── db.sqlite3            # SQLite database
├── manage.py             # Django management script
├── requirements.txt      # dependencies
├── readme.md             # project documentation
└── .gitignore            # project ignore rules
```

## Features

- User registration and login
- Blog post CRUD operations
- Category-wise post listing
- Unique slug generation for blog URLs
- Featured posts section on homepage
- Blog detail pages with comments
- Search by title, short description, or blog body
- Media upload support for post images
- Dashboard for categories and posts
- User/author-specific content visibility
- Admin panel for managing the application

## Requirements

- Python 3.10+
- pip
- virtual environment support

## Setup Instructions

1. Clone the repository

```bash
git clone <repository-url>
cd blogging-system-yt-main
```

2. Create a virtual environment

```bash
python -m venv .venv
```

3. Activate the virtual environment

Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

Windows Command Prompt:
```cmd
.venv\Scripts\activate.bat
```

4. Install dependencies

```bash
pip install -r requirements.txt
```

5. Set a Django secret key

Generate a key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Set the generated value as `DJANGO_SECRET_KEY` in your environment before deployment. For local Windows PowerShell use:

```powershell
$env:DJANGO_SECRET_KEY = "paste-generated-key-here"
```

6. Apply database migrations

```bash
python manage.py migrate
```

7. Create a superuser

```bash
python manage.py createsuperuser
```

8. Run the server

```bash
python manage.py runserver
```

Open the app in your browser at:

```text
http://127.0.0.1:8000/
```

## Main URLs

- Home page: `/`
- Blog detail: `/blogs/<slug>/`
- Search: `/search/`
- Registration: `/register/`
- Login: `/login/`
- Dashboard: `/dashboard/`
- Admin panel: `/admin/`

## Admin Usage

After creating a superuser, sign in to the Django admin panel to:
- manage posts
- manage categories
- manage users
- manage comments and site content

## Default Database

This project uses SQLite in development mode by default, which is configured in `blog_main/settings.py`.

## Notes

- Uploaded media files are stored in the `media/` folder.
- Static assets are handled using Django static configuration.
- The project is structured in a simple way and can be extended for production use.

## License

This project is provided for learning and educational use.

## Author

Built as a Django blog project for practical learning and content management use.
