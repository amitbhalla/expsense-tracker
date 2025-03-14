# Expense Tracker: Quickstart Guide

## First-Time Launch

### 1. Navigate to Project Directory
Open Terminal and go to your project folder:
```bash
cd ~/Projects/expense_tracker
```

### 2. Activate Virtual Environment
```bash
source venv/bin/activate
```
Your terminal prompt should now show `(venv)` at the beginning.

### 3. Run the Server
```bash
python manage.py runserver
```

### 4. Access the Application
Open your browser and go to:
```
http://127.0.0.1:8000/
```

## Initial Setup Checklist

Follow these steps in order when you first launch the application:

### 1. Create Account Types
- Click on "Account Types" in the sidebar
- Add account types like:
  - Savings Account
  - Fixed Deposit
  - Mutual Fund
  - Stocks/Shares
  - Insurance
  - Provident Fund
  - PPF
  - Credit Card

### 2. Create Categories
- Click on "Categories" in the sidebar
- Add expense categories like:
  - Groceries
  - Utilities
  - Rent
  - Transportation
  - Entertainment
  - Healthcare
- Add income categories like:
  - Salary
  - Interest
  - Dividends
  - Gifts

### 3. Create Your Accounts
- Click on "Accounts" in the sidebar
- Add each of your actual accounts with:
  - Name (e.g., "HDFC Savings")
  - Account Type (select from your created types)
  - Opening Balance

### 4. Add Transactions
- Click on "Transactions" in the sidebar
- Add your income and expenses
- Use "Make Transfer" for moving money between accounts

### 5. View Your Dashboard
- Click on "Dashboard" to see your financial overview
- Use the date selectors to view different time periods