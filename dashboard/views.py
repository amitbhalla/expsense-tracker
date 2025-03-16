from django.shortcuts import render
from django.db.models import Sum, Count, Q, Avg
from django.db.models.functions import TruncMonth, TruncYear
from accounts.models import Account
from transactions.models import Transaction, Category
import json
from django.core.serializers.json import DjangoJSONEncoder
import datetime
from sklearn.linear_model import LinearRegression
import numpy as np

def home(request):
    # Get sorting parameters from request
    sort = request.GET.get('sort', 'balance')
    order = request.GET.get('order', 'desc')
    account_id = request.GET.get('account_id')
    
    # Get all accounts with sorting
    if sort == 'name':
        if order == 'asc':
            accounts = Account.objects.all().order_by('name')
        else:
            accounts = Account.objects.all().order_by('-name')
    else:
        if order == 'asc':
            accounts = Account.objects.all().order_by('current_balance')
        else:
            accounts = Account.objects.all().order_by('-current_balance')
    
    # Calculate total balance
    if account_id:
        total_balance = Account.objects.get(id=account_id).current_balance
    else:
        total_balance = sum(account.current_balance for account in accounts)
    
    # Get recent transactions
    today = datetime.date.today()
    first_day_of_month = datetime.date(today.year, today.month, 1)
    recent_transactions = Transaction.objects.filter(
        date__gte=first_day_of_month,
        date__lte=today
    )
    
    if account_id:
        recent_transactions = recent_transactions.filter(account_id=account_id)
    
    recent_transactions = recent_transactions.order_by('-date')
    
    context = {
        'accounts': accounts,
        'total_balance': total_balance,
        'recent_transactions': recent_transactions,
        'sort': sort,
        'order': order,
        'selected_account': int(account_id) if account_id else None
    }
    return render(request, 'dashboard/home.html', context)

def dashboard(request):
    # Get date range from request or use default (current month)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    account_id = request.GET.get('account_id')
    
    today = datetime.date.today()
    
    if not start_date:
        # Default to first day of current month
        start_date = datetime.date(today.year, today.month, 1)
    else:
        try:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            # Handle invalid date format
            start_date = datetime.date(today.year, today.month, 1)
    
    if not end_date:
        # Default to today
        end_date = today
    else:
        try:
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            # Handle invalid date format
            end_date = today
    
    # Filter transactions by date range
    transactions = Transaction.objects.filter(date__range=[start_date, end_date])
    
    # Apply account filter if selected
    if account_id:
        transactions = transactions.filter(account_id=account_id)
    
    # Get all accounts for the filter dropdown
    accounts = Account.objects.all()
    
    # Get spending by category - with case insensitive filtering
    category_spending = transactions.filter(
        transaction_type__iexact='EXPENSE'
    ).values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Get income by category - with case insensitive filtering
    category_income = transactions.filter(
        transaction_type__iexact='INCOME'
    ).values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Get monthly spending trend
    monthly_spending = transactions.filter(
        transaction_type__iexact='EXPENSE'
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')
    
    # Get monthly income trend
    monthly_income = transactions.filter(
        transaction_type__iexact='INCOME'
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')
    
    # Get yearly comparison
    yearly_comparison = transactions.annotate(
        year=TruncYear('date')
    ).values('year', 'transaction_type').annotate(
        total=Sum('amount')
    ).order_by('year', 'transaction_type')
    
    # Calculate year-on-year growth data
    yearly_data = Transaction.objects.annotate(
        year=TruncYear('date')
    ).values('year').annotate(
        income=Sum('amount', filter=Q(transaction_type__iexact='INCOME')),
        expense=Sum('amount', filter=Q(transaction_type__iexact='EXPENSE')),
        net=Sum('amount', filter=Q(transaction_type__iexact='INCOME')) - 
            Sum('amount', filter=Q(transaction_type__iexact='EXPENSE'))
    ).order_by('year')
    
    # Calculate growth percentages
    yoy_growth_data = {
        'labels': [],
        'income_growth': [],
        'expense_growth': [],
        'net_growth': [],
        'income_values': [],
        'expense_values': [],
        'net_values': []
    }
    
    # If we have yearly data, process it
    if yearly_data:
        prev_income = None
        prev_expense = None
        prev_net = None
        
        for i, data in enumerate(yearly_data):
            year_label = data['year'].strftime('%Y')
            yoy_growth_data['labels'].append(year_label)
            yoy_growth_data['income_values'].append(float(data['income'] or 0))
            yoy_growth_data['expense_values'].append(float(data['expense'] or 0))
            yoy_growth_data['net_values'].append(float(data['net'] or 0))
            
            # Calculate growth percentages
            if i > 0 and prev_income is not None and prev_expense is not None and prev_net is not None:
                # Income growth
                if prev_income > 0:
                    income_growth = ((data['income'] - prev_income) / prev_income) * 100
                else:
                    income_growth = 0
                yoy_growth_data['income_growth'].append(round(income_growth, 2))
                
                # Expense growth
                if prev_expense > 0:
                    expense_growth = ((data['expense'] - prev_expense) / prev_expense) * 100
                else:
                    expense_growth = 0
                yoy_growth_data['expense_growth'].append(round(expense_growth, 2))
                
                # Net growth
                if prev_net > 0:
                    net_growth = ((data['net'] - prev_net) / prev_net) * 100
                else:
                    net_growth = 0
                yoy_growth_data['net_growth'].append(round(net_growth, 2))
            else:
                # First year has no growth percentage
                yoy_growth_data['income_growth'].append(0)
                yoy_growth_data['expense_growth'].append(0)
                yoy_growth_data['net_growth'].append(0)
            
            # Update previous values for next iteration
            prev_income = data['income'] or 0
            prev_expense = data['expense'] or 0
            prev_net = data['net'] or 0
    else:
        # No yearly data available, provide default
        current_year = datetime.date.today().year
        yoy_growth_data = {
            'labels': [str(current_year)],
            'income_growth': [0],
            'expense_growth': [0],
            'net_growth': [0],
            'income_values': [0],
            'expense_values': [0],
            'net_values': [0]
        }
    
    # Handle case where there's no monthly spending data
    if not monthly_spending:
        # Create a single month entry with the current month and zero spending
        current_month = datetime.date.today().replace(day=1)
        monthly_trend_data = {
            'labels': [current_month.strftime('%b %Y')],
            'spending': [0],
            'income': [0],
        }
    else:
        try:
            monthly_trend_data = {
                'labels': [item['month'].strftime('%b %Y') for item in monthly_spending],
                'spending': [float(item['total']) for item in monthly_spending],
                'income': [],
            }
            
            # Match income data with the same months
            for month_label in monthly_trend_data['labels']:
                # Find income for this month
                try:
                    month_obj = datetime.datetime.strptime(month_label, '%b %Y').date().replace(day=1)
                    month_income = next(
                        (float(item['total']) for item in monthly_income if item['month'].replace(day=1) == month_obj),
                        0
                    )
                    monthly_trend_data['income'].append(month_income)
                except Exception as e:
                    print(f"Error processing income for month {month_label}: {e}")
                    monthly_trend_data['income'].append(0)
        except Exception as e:
            print(f"Error creating monthly trend data: {e}")
            # Create default data in case of error
            current_month = datetime.date.today().replace(day=1)
            monthly_trend_data = {
                'labels': [current_month.strftime('%b %Y')],
                'spending': [0],
                'income': [0],
            }
    
    # Prepare chart data
    category_spending_data = {
        'labels': [item['category__name'] for item in category_spending],
        'data': [float(item['total']) for item in category_spending],
    }
    
    category_income_data = {
        'labels': [item['category__name'] for item in category_income],
        'data': [float(item['total']) for item in category_income],
    }
    
    # Ensure we have data - create empty arrays if necessary
    if not category_spending_data['labels']:
        category_spending_data['labels'] = []
        category_spending_data['data'] = []
        
    if not category_income_data['labels']:
        category_income_data['labels'] = []
        category_income_data['data'] = []
    
    context = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'accounts': accounts,
        'selected_account': int(account_id) if account_id else None,
        'category_spending': category_spending,
        'category_income': category_income,
        'monthly_spending': monthly_spending,
        'monthly_income': monthly_income,
        'yearly_comparison': yearly_comparison,
        'yoy_growth_data': json.dumps(yoy_growth_data, cls=DjangoJSONEncoder),
        'transactions': transactions,
        'category_spending_data': json.dumps(category_spending_data),
        'category_income_data': json.dumps(category_income_data),
        'monthly_trend_data': json.dumps(monthly_trend_data),
        'transaction_types': list(transactions.values_list('transaction_type', flat=True).distinct()),
    }
    
    return render(request, 'dashboard/dashboard.html', context)

def reports(request):
    # Get date range from request or use default (current month)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    account_id = request.GET.get('account_id')
    category_id = request.GET.get('category_id')
    
    today = datetime.date.today()
    
    if not start_date:
        # Default to first day of current month
        start_date = datetime.date(today.year, today.month, 1)
    else:
        try:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            # Handle invalid date format
            start_date = datetime.date(today.year, today.month, 1)
    
    if not end_date:
        # Default to today
        end_date = today
    else:
        try:
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            # Handle invalid date format
            end_date = today
    
    # Filter transactions by date range
    transactions = Transaction.objects.filter(date__range=[start_date, end_date])
    
    # Additional filters if provided
    if account_id:
        transactions = transactions.filter(account_id=account_id)
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    
    # Get monthly spending and income trend
    monthly_data = transactions.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        income=Sum('amount', filter=Q(transaction_type__iexact='INCOME')),
        expense=Sum('amount', filter=Q(transaction_type__iexact='EXPENSE'))
    ).order_by('month')
    
    # Filter transactions by account if selected
    if account_id:
        transactions = transactions.filter(account_id=account_id)
        monthly_data = monthly_data.filter(account_id=account_id)
    
    # Now prepare the data for the charts
    monthly_trend = list(monthly_data)  # Convert to list to make it iterable
    
    # Process the data for Chart.js
    labels = []
    income_data = []
    expense_data = []
    
    # Convert your monthly_trend data to the format needed for the chart
    for item in monthly_trend:
        month_str = item['month'].strftime('%b %Y')
        income = float(item.get('income', 0) or 0)  # Handle None values
        expense = float(item.get('expense', 0) or 0)  # Handle None values
            
        labels.append(month_str)
        income_data.append(income)
        expense_data.append(expense)
    
    # Calculate historical net worth month by month
    net_worth_dates = []
    net_worth_values = []
    
    # Get initial balances for all accounts
    accounts = Account.objects.all()
    initial_balance = sum(account.opening_balance for account in accounts)
    
    # Get all months between start_date and end_date
    current_month = start_date.replace(day=1)
    months = []
    while current_month <= end_date:
        months.append(current_month)
        # Get next month
        if current_month.month == 12:
            current_month = current_month.replace(year=current_month.year + 1, month=1)
        else:
            current_month = current_month.replace(month=current_month.month + 1)
    
    # Calculate cumulative net worth for each month
    running_balance = initial_balance
    for month in months:
        month_end = month.replace(day=28) if month.month != 2 else month.replace(day=month.day)
        
        # Get all transactions up to this month
        month_transactions = Transaction.objects.filter(date__lte=month_end)
        
        # Apply account filter if selected
        if account_id:
            month_transactions = month_transactions.filter(account_id=account_id)
        
        # Calculate net effect of all transactions
        income = month_transactions.filter(transaction_type__iexact='INCOME').aggregate(total=Sum('amount'))['total'] or 0
        expenses = month_transactions.filter(transaction_type__iexact='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
        
        # Update running balance
        running_balance = initial_balance + income - expenses
        
        month_str = month.strftime('%b %Y')
        net_worth_dates.append(month_str)
        net_worth_values.append(float(running_balance))
    
    # If no months found, use current net worth
    if not months:
        current_net_worth = sum(account.current_balance for account in accounts)
        net_worth_dates.append(today.strftime('%b %Y'))
        net_worth_values.append(float(current_net_worth))
    
    # Initialize current net worth
    current_net_worth = net_worth_values[-1] if net_worth_values else 0

    # Calculate historical growth rate
    if len(net_worth_values) > 1:
        growth_rates = []
        for i in range(1, len(net_worth_values)):
            if net_worth_values[i-1] > 0:
                growth_rate = (net_worth_values[i] - net_worth_values[i-1]) / net_worth_values[i-1]
                growth_rates.append(growth_rate)

        # Use weighted average of growth rates, giving more weight to recent years
        if growth_rates:
            weights = list(range(1, len(growth_rates) + 1))
            avg_growth_rate = sum(r * w for r, w in zip(growth_rates, weights)) / sum(weights)
            
            # Generate forecasts using historical growth rate
            forecast_data = []
            for years in [5, 10, 15, 20]:
                projected_value = current_net_worth * (1 + avg_growth_rate) ** years
                forecast_data.append({
                    'years': years,
                    'projected_net_worth': round(projected_value, 2)
                })
    else:
        # Not enough historical data for projections
        forecast_data = [
            {'years': 5, 'projected_net_worth': current_net_worth * 1.25},
            {'years': 10, 'projected_net_worth': current_net_worth * 1.5},
            {'years': 15, 'projected_net_worth': current_net_worth * 1.75},
            {'years': 20, 'projected_net_worth': current_net_worth * 2.0}
        ]
    
    # Create context with JSON-serialized data
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'selected_account': int(account_id) if account_id else None,
        'chart_labels': json.dumps(labels),
        'chart_income': json.dumps(income_data),
        'chart_expenses': json.dumps(expense_data),
        
        # Net worth chart data
        'net_worth_dates': json.dumps(net_worth_dates),
        'net_worth_values': json.dumps(net_worth_values),
        
        # Original data (if needed elsewhere in template)
        'monthly_trend': monthly_trend,
        'forecast_data': forecast_data,
        
        # Add accounts and categories for filter dropdowns if needed
        'accounts': Account.objects.all(),
        'categories': Category.objects.all(),
        'selected_account': account_id,
    }
    
    return render(request, 'dashboard/reports.html', context)