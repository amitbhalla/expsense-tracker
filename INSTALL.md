# Expense Tracker: Installation and Launch Guide

## Prerequisites
- macOS on Apple Silicon
- Python 3.9 or higher (pre-installed on newer Macs)
- Terminal access

## Step 1: Create a Project Directory
1. Open Terminal
2. Create and navigate to a directory for your project:
```bash
mkdir ~/Projects/expense_tracker
cd ~/Projects/expense_tracker
```

## Step 2: Set Up Virtual Environment
1. Create a Python virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate
```
You should see `(venv)` at the beginning of your terminal prompt.

## Step 3: Install Required Packages
```bash
pip install django django-crispy-forms crispy-bootstrap5 pandas matplotlib
```

## Step 4: Create Django Project Structure
1. Create the main Django project:
```bash
django-admin startproject expense_tracker .
```

2. Create the required apps:
```bash
python manage.py startapp accounts
python manage.py startapp transactions
python manage.py startapp dashboard
```

3. Create necessary directories:
```bash
mkdir -p templates/accounts
mkdir -p templates/transactions
mkdir -p templates/dashboard
mkdir -p static/css
mkdir -p static/js
mkdir -p static/img
```

## Step 5: Copy the Code Files
1. Copy all the project files from the code samples into their respective locations:
   - Python files (.py) to their appropriate directories
   - HTML templates to the templates directory
   - CSS/JS files to the static directory

## Step 6: Initialize the Database
1. Create the initial migration files:
```bash
python manage.py makemigrations accounts
python manage.py makemigrations transactions
python manage.py makemigrations dashboard
```

2. Apply the migrations to create the database schema:
```bash
python manage.py migrate
```

## Step 7: Create Admin User
```bash
python manage.py createsuperuser
```
Follow the prompts to create your username, email, and password.

## Step 8: Run the Development Server
```bash
python manage.py runserver
```
You should see output indicating the server is running, typically at http://127.0.0.1:8000/

## Step 9: Access the Application
1. Open your web browser
2. Navigate to: http://127.0.0.1:8000/