from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse
import csv
import io
import datetime
from django.db import transaction
from decimal import Decimal
from .models import Transaction, Category
from accounts.models import Account
from .forms import TransactionForm, CategoryForm, TransferForm

def transaction_list(request):
    transactions = Transaction.objects.all().order_by('-date')
    categories = Category.objects.all().order_by('name')
    
    context = {
        'transactions': transactions,
        'categories': categories,
    }
    return render(request, 'transactions/transaction_list.html', context)

def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save()
            messages.success(request, 'Transaction created successfully.')
            return redirect('transaction_list')
    else:
        form = TransactionForm()
        # Default to today's date
        form.fields['date'].initial = datetime.date.today()
    
    context = {'form': form, 'title': 'Create Transaction'}
    return render(request, 'transactions/transaction_form.html', context)

def transaction_update(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            transaction = form.save()
            messages.success(request, 'Transaction updated successfully.')
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction)
    
    context = {'form': form, 'title': 'Update Transaction'}
    return render(request, 'transactions/transaction_form.html', context)

def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    
    if request.method == 'POST':
        account = transaction.account
        transaction.delete()
        account.update_balance()
        
        # Update to_account if this was a transfer
        if transaction.transaction_type == 'TRANSFER' and transaction.to_account:
            transaction.to_account.update_balance()
            
        messages.success(request, 'Transaction deleted successfully.')
        return redirect('transaction_list')
    
    context = {'transaction': transaction}
    return render(request, 'transactions/transaction_confirm_delete.html', context)

def category_list(request):
    categories = Category.objects.all().order_by('name')
    context = {'categories': categories}
    return render(request, 'transactions/category_list.html', context)

def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    context = {'form': form, 'title': 'Create Category'}
    return render(request, 'transactions/category_form.html', context)

def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    
    context = {'form': form, 'title': 'Update Category'}
    return render(request, 'transactions/category_form.html', context)

def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('category_list')
    
    context = {'category': category}
    return render(request, 'transactions/category_confirm_delete.html', context)

def create_transfer(request):
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            # Get data from the form
            from_account = form.cleaned_data['account']
            to_account = form.cleaned_data['to_account']
            amount = form.cleaned_data['amount']
            date = form.cleaned_data['date']
            description = form.cleaned_data['description']
            
            # Get or create a transfer category
            transfer_category, created = Category.objects.get_or_create(
                name='Transfer',
                defaults={'description': 'Transfer between accounts'}
            )
            
            # Create the outgoing transaction
            transaction = Transaction.objects.create(
                account=from_account,
                category=transfer_category,
                amount=amount,
                transaction_type='TRANSFER',
                date=date,
                description=description,
                to_account=to_account
            )
            
            messages.success(request, 'Transfer created successfully.')
            return redirect('transaction_list')
    else:
        form = TransferForm()
        # Default to today's date
        form.fields['date'].initial = datetime.date.today()
    
    context = {'form': form, 'title': 'Create Transfer'}
    return render(request, 'transactions/transfer_form.html', context)

def export_transactions_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Account', 'Category', 'Type', 'Amount', 'Description'])
    
    transactions = Transaction.objects.all().order_by('-date')
    
    for transaction in transactions:
        writer.writerow([
            transaction.date,
            transaction.account.name,
            transaction.category.name,
            transaction.transaction_type,
            transaction.amount,
            transaction.description
        ])
    
    return response

def import_transactions_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        # Check if the file is a CSV
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('import_transactions_csv')
        
        # Decode the file
        try:
            file_data = csv_file.read().decode('utf-8')
        except UnicodeDecodeError:
            messages.error(request, 'Could not decode the file. Please ensure it is a valid CSV file with UTF-8 encoding.')
            return redirect('import_transactions_csv')
        
        csv_data = csv.reader(io.StringIO(file_data), delimiter=',')
        
        # Skip the header row if it exists
        header = next(csv_data, None)
        
        # Expected header: Date, Account Name, Transaction Category, Type (Income/Expense), Amount
        expected_header = ['Date', 'Account Name', 'Transaction Category', 'Type', 'Amount']
        
        # Check if the header matches the expected format
        if not header or not all(expected_header[i].lower() in header[i].lower() for i in range(min(len(header), len(expected_header)))):
            messages.warning(request, f'CSV header may not match the expected format. Expected: {", ".join(expected_header)}')
        
        # Prepare for import
        success_count = 0
        error_count = 0
        error_messages = []
        
        # Process each row
        with transaction.atomic():  # Use database transaction for atomicity
            for i, row in enumerate(csv_data, start=1):
                try:
                    if len(row) < 5:
                        error_count += 1
                        error_messages.append(f"Row {i}: Not enough columns. Expected 5, got {len(row)}.")
                        continue
                    
                    # Parse date
                    try:
                        # Try multiple date formats
                        date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y']
                        date_str = row[0].strip()
                        transaction_date = None
                        
                        for date_format in date_formats:
                            try:
                                transaction_date = datetime.datetime.strptime(date_str, date_format).date()
                                break
                            except ValueError:
                                continue
                        
                        if transaction_date is None:
                            raise ValueError(f"Could not parse date format for '{date_str}'")
                    except Exception as e:
                        error_count += 1
                        error_messages.append(f"Row {i}: Invalid date format. {str(e)}")
                        continue
                    
                    # Get or create account
                    account_name = row[1].strip()
                    try:
                        account = Account.objects.get(name=account_name)
                    except Account.DoesNotExist:
                        error_count += 1
                        error_messages.append(f"Row {i}: Account '{account_name}' does not exist.")
                        continue
                    
                    # Get or create category
                    category_name = row[2].strip()
                    category, created = Category.objects.get_or_create(name=category_name)
                    
                    # Parse transaction type
                    type_str = row[3].strip().upper()
                    if 'INCOME' in type_str:
                        transaction_type = 'INCOME'
                    elif 'EXPENSE' in type_str:
                        transaction_type = 'EXPENSE'
                    else:
                        error_count += 1
                        error_messages.append(f"Row {i}: Invalid transaction type '{type_str}'. Must be 'INCOME' or 'EXPENSE'.")
                        continue
                    
                    # Parse amount
                    try:
                        # Remove any currency symbols or commas
                        amount_str = row[4].strip().replace('₹', '').replace(',', '')
                        amount = Decimal(amount_str)
                        if amount <= 0:
                            error_count += 1
                            error_messages.append(f"Row {i}: Amount must be positive. Got {amount}.")
                            continue
                    except Exception as e:
                        error_count += 1
                        error_messages.append(f"Row {i}: Invalid amount format. {str(e)}")
                        continue
                    
                    # Create the transaction
                    Transaction.objects.create(
                        account=account,
                        category=category,
                        amount=amount,
                        transaction_type=transaction_type,
                        date=transaction_date,
                        description=f"Imported from CSV on {datetime.date.today()}"
                    )
                    
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    error_messages.append(f"Row {i}: Unexpected error. {str(e)}")
        
        # Provide feedback to the user
        if success_count > 0:
            messages.success(request, f"Successfully imported {success_count} transactions.")
        
        if error_count > 0:
            messages.warning(request, f"Could not import {error_count} transactions. See details below.")
            for error in error_messages[:10]:  # Show only first 10 errors to avoid overwhelming the user
                messages.error(request, error)
            
            if len(error_messages) > 10:
                messages.info(request, f"...and {len(error_messages) - 10} more errors. Please check your CSV file.")
        
        return redirect('transaction_list')
    
    return render(request, 'transactions/import_transactions.html')

def download_csv_template(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transaction_template.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Account Name', 'Transaction Category', 'Type', 'Amount'])
    writer.writerow(['2025-03-12', 'HDFC Saving 62', 'Groceries', 'EXPENSE', '1000.50'])
    writer.writerow(['2025-03-11', 'ICICI Saving', 'Salary', 'INCOME', '50000.00'])
    
    return response