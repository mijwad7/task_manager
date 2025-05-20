# Task Manager

Task Manager is a web application built with Django, allowing users to create, manage, and visualize tasks. It features user authentication (email/password and OTP login), a task dashboard with a calendar view powered by FullCalendar, and a modern UI styled with Bootstrap. The app is deployed on Vercel with a Neon PostgreSQL database for persistent storage.

## Features
- **User Authentication**:
  - Register and log in with email and password.
  - OTP-based login via email.
  - Secure session management with cache control to prevent unauthorized access.
- **Task Management**:
  - Create, edit, and delete tasks with title, description, due date, and status (pending/completed).
  - View tasks in a table and on an interactive calendar.
  - REST API for task CRUD operations (using Django REST Framework).
- **UI/UX**:
  - Responsive design with Bootstrap 5.3.
  - Elegant modals for task details and deletion confirmation.
  - FullCalendar for visualizing task due dates.
- **Deployment**:
  - Hosted on Vercel for serverless scalability.
  - Neon PostgreSQL for reliable database storage.

## Prerequisites
To run the application locally, ensure you have the following:

- **Python**: Version 3.9 or higher (3.11 recommended).
- **Git**: For cloning the repository.
- **PostgreSQL**: For local database (or use Neon for deployment).
- **Email Service**: SMTP configuration (e.g., Gmail) for OTP emails.

## Setup Instructions (Local)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/task-manager.git
cd task-manager
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
Install the required Python packages listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

Example `requirements.txt`:
```
asgiref==3.8.1
Django==5.2.1
djangorestframework==3.16.0
dotenv==0.9.9
psycopg2-binary==2.9.10
python-dotenv==1.1.0
sqlparse==0.5.3
tzdata==2025.2
```

### 4. Configure Environment Variables
Create a `.env` file in the project root and add the following variables:
```
SECRET_KEY=your-django-secret-key
DATABASE_URL='your-database-url'
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
DJANGO_SETTINGS_MODULE=task_manager.settings
```

- **Generate `SECRET_KEY`**: Use a secure random string (e.g., via `python -c "import secrets; print(secrets.token_hex(32))"`).
- **Email**: Use a Gmail App Password or another SMTP service for OTP emails.
- **Database**: For local setup, install PostgreSQL and create a database.

### 5. Set Up the Database
Run migrations to create the database schema:
```bash
python manage.py migrate
```

### 6. Collect Static Files
Collect static files (CSS, JS) for production-like serving:
```bash
python manage.py collectstatic
```

### 7. Create a Superuser (Optional)
For admin access:
```bash
python manage.py createsuperuser
```

### 8. Run the Development Server
Start the Django development server:
```bash
python manage.py runserver
```

Access the app at `http://localhost:8000`.

### 9. Test the Application
- Register a new user at `http://localhost:8000/register/`.
- Log in at `http://localhost:8000/login/` or use OTP at `http://localhost:8000/otp-login/`.
- Create and manage tasks at `http://localhost:8000/dashboard/`.
- Access the admin panel at `http://localhost:8000/admin/` (with superuser credentials).

## Project Structure
```
task-manager/
├── manage.py
├── task_manager/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── tasks/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── login.html
│   │   ├── otp_login.html
│   │   ├── register.html
│   │   ├── task_form.html
│   ├── urls.py
│   ├── views.py
├── static/
│   ├── css/
│   │   ├── styles.css
│   ├── js/
│   │   ├── calendar.js
│   │   ├── tasks.js
├── staticfiles/
├── .env
├── .gitignore
├── build_files.sh
├── requirements.txt
├── vercel.json
```
