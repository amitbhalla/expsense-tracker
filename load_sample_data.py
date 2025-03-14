# Sample Data Script for Expense Tracker
# Place this in your project root and run with: python load_sample_data.py

import os
import django
import datetime
from decimal import Decimal

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "expense_tracker.settings")
django.setup()

# Import models after Django setup
from accounts.models import AccountType, Account
from transactions.models import Category, Transaction


def create_sample_data():
    print("Creating sample data...")

    # Create Account Types
    print("Creating account types...")
    savings_type = AccountType.objects.create(
        name="Savings", description="Regular savings accounts"
    )
    investment_type = AccountType.objects.create(
        name="Investment", description="Investment accounts like mutual funds"
    )
    credit_type = AccountType.objects.create(
        name="Credit Card", description="Credit card accounts"
    )
    cash_type = AccountType.objects.create(name="Cash", description="Physical cash")

    # Create Categories
    print("Creating categories...")
    # Income categories
    salary = Category.objects.create(
        name="Salary", description="Income from employment"
    )
    interest = Category.objects.create(
        name="Interest", description="Interest income from investments"
    )
    dividend = Category.objects.create(
        name="Dividends", description="Dividend income from stocks"
    )
    other_income = Category.objects.create(
        name="Other Income", description="Miscellaneous income sources"
    )

    # Expense categories
    groceries = Category.objects.create(
        name="Groceries", description="Food and household supplies"
    )
    utilities = Category.objects.create(
        name="Utilities", description="Electricity, water, internet, etc."
    )
    rent = Category.objects.create(name="Rent", description="Housing rent")
    dining = Category.objects.create(
        name="Dining Out", description="Restaurants and takeout"
    )
    transport = Category.objects.create(
        name="Transportation", description="Public transport, fuel, etc."
    )
    entertainment = Category.objects.create(
        name="Entertainment", description="Movies, subscription services, etc."
    )
    shopping = Category.objects.create(
        name="Shopping", description="Clothing, electronics, etc."
    )
    healthcare = Category.objects.create(
        name="Healthcare", description="Medical expenses"
    )

    # Create transfer category
    transfer = Category.objects.create(
        name="Transfer", description="Transfers between accounts"
    )

    # Create Accounts
    print("Creating accounts...")
    main_savings = Account.objects.create(
        name="Main Savings",
        account_type=savings_type,
        opening_balance=Decimal("5000.00"),
        description="Primary savings account",
    )

    secondary_savings = Account.objects.create(
        name="Secondary Savings",
        account_type=savings_type,
        opening_balance=Decimal("2500.00"),
        description="Emergency fund",
    )

    mutual_fund = Account.objects.create(
        name="Growth Mutual Fund",
        account_type=investment_type,
        opening_balance=Decimal("10000.00"),
        description="Long-term investment",
    )

    credit_card = Account.objects.create(
        name="Credit Card",
        account_type=credit_type,
        opening_balance=Decimal("0.00"),
        description="Primary credit card",
    )

    wallet = Account.objects.create(
        name="Cash Wallet",
        account_type=cash_type,
        opening_balance=Decimal("200.00"),
        description="Physical cash on hand",
    )

    # Create Transactions
    print("Creating transactions...")
    today = datetime.date.today()

    # Generate some transactions for the past 3 months
    for month_offset in range(3):
        transaction_date = today.replace(day=1) - datetime.timedelta(
            days=month_offset * 30
        )

        # Monthly salary
        Transaction.objects.create(
            account=main_savings,
            category=salary,
            amount=Decimal("5000.00"),
            transaction_type="INCOME",
            date=transaction_date.replace(day=5),
            description="Monthly salary",
        )

        # Rent payment
        Transaction.objects.create(
            account=main_savings,
            category=rent,
            amount=Decimal("1200.00"),
            transaction_type="EXPENSE",
            date=transaction_date.replace(day=2),
            description="Monthly rent",
        )

        # Utilities
        Transaction.objects.create(
            account=main_savings,
            category=utilities,
            amount=Decimal("150.00"),
            transaction_type="EXPENSE",
            date=transaction_date.replace(day=10),
            description="Electricity and internet",
        )

        # Groceries (multiple times a month)
        for day in [7, 14, 21, 28]:
            if day <= transaction_date.replace(day=28).day:
                Transaction.objects.create(
                    account=main_savings,
                    category=groceries,
                    amount=Decimal("75.00") + Decimal(str(month_offset * 5)),
                    transaction_type="EXPENSE",
                    date=transaction_date.replace(day=day),
                    description="Weekly grocery shopping",
                )

    # Update all account balances
    for account in Account.objects.all():
        account.update_balance()

    print("Sample data created successfully!")


if __name__ == "__main__":
    # Check if data already exists
    if (
        AccountType.objects.count() > 0
        or Account.objects.count() > 0
        or Category.objects.count() > 0
        or Transaction.objects.count() > 0
    ):

        choice = input(
            "Database already contains data. Replace with sample data? (y/n): "
        )
        if choice.lower() != "y":
            print("Operation cancelled.")
            exit()

        # Clear existing data
        print("Clearing existing data...")
        Transaction.objects.all().delete()
        Category.objects.all().delete()
        Account.objects.all().delete()
        AccountType.objects.all().delete()

    # Create sample data
    create_sample_data()
