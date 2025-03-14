# Expense Tracker App

A comprehensive expense tracker built with Django. This application allows you to manage multiple account types, track transactions, visualize spending patterns, and more.

## Features

- Multiple account management (Saving Account, FDs, Mutual Funds, Insurance, PF, PPF, Shares, etc.)
- Transaction tracking with categories and date-based filtering
- Transfer functionality between accounts
- Dashboard with graphical visualizations of spending patterns
- Data export to CSV
- Modern UI with animations and slick graphics
- Persistent storage using SQLite database

## Installation Instructions for macOS with Apple Silicon

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Setup Steps

1. Clone or download this repository to your local machine

2. Open Terminal and navigate to the project directory

3. Create and activate a virtual environment:
```bash
python3 -m venv expense_tracker_env
source expense_tracker_env/bin/activate
```

4. Install required packages:
```bash
pip install django django-crispy-forms crispy-bootstrap5 pandas matplotlib
```

5. Navigate to the project folder:
```bash
cd expense_tracker
```

6. Initialize the database:
```bash
python manage.py makemigrations accounts
python manage.py makemigrations transactions
python manage.py makemigrations dashboard
python manage.py migrate
```

7. Create a superuser (admin) account:
```bash
python manage.py createsuperuser
```

8. Run the development server:
```bash
python manage.py runserver
```

9. Open your web browser and go to:
```
http://127.0.0.1:8000/
```

## Initial Setup

After installation, you'll need to set up some initial data:

1. First, create Account Types (Savings, Investment, Credit Card, etc.)
2. Then, create Categories for your transactions (Groceries, Utilities, Salary, etc.)
3. Finally, create your Accounts with opening balances

## Usage Guide

### Managing Accounts

- **Add Account**: Create a new account with a type and opening balance
- **Edit Account**: Modify existing account details
- **Delete Account**: Remove an account and all associated transactions

### Tracking Transactions

- **Add Transaction**: Record income, expenses, or transfers between accounts
- **Categorize Transactions**: Assign each transaction to a specific category
- **Filter Transactions**: View transactions by date range

### Dashboard and Reports

- **Overview**: See total balance across all accounts
- **Spending by Category**: Visualize where your money is going
- **Income by Category**: Track your income sources
- **Monthly Trends**: Compare income and expenses over time

### Data Export

- Export all transaction data to CSV for further analysis in spreadsheet software

## Customization

You can customize the application by:

- Adding new account types specific to your needs
- Creating categories that match your spending patterns
- Modifying the CSS in `static/css/custom.css` to change the appearance

## Backup

The application uses SQLite for data storage. To backup your data:

1. Stop the server
2. Copy the `db.sqlite3` file to a safe location
3. Restart the server

## Troubleshooting

- If you see a "No such table" error, make sure you've run all migrations
- If styles aren't loading, check that `DEBUG = True` in `settings.py`
- For any other issues, check the Django development server console for error messages