from django.shortcuts import render
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth, TruncYear
from accounts.models import Account
from transactions.models import Transaction, Category
import json
from django.core.serializers.json import DjangoJSONEncoder
import datetime

def home(request):
    # Get sorting parameters from request
    sort = request.GET.get('sort', 'balance')
    order = request.GET.get('order', 'desc')
    account_id = request.GET.get('account')
    
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
    account_id = request.GET.get('account')
    
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