from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Account, AccountType
from .forms import AccountForm, AccountTypeForm

def account_list(request):
    accounts = Account.objects.all().order_by('name')
    account_types = AccountType.objects.all().order_by('name')
    
    # Calculate total balance
    total_balance = sum(account.current_balance for account in accounts)
    
    context = {
        'accounts': accounts,
        'account_types': account_types,
        'total_balance': total_balance,
    }
    return render(request, 'accounts/account_list.html', context)

def account_create(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save()
            account.current_balance = account.opening_balance
            account.save()
            messages.success(request, 'Account created successfully.')
            return redirect('account_list')
    else:
        form = AccountForm()
    
    context = {'form': form, 'title': 'Create Account'}
    return render(request, 'accounts/account_form.html', context)

def account_update(request, pk):
    account = get_object_or_404(Account, pk=pk)
    
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            old_opening_balance = account.opening_balance
            account = form.save()
            
            # If opening balance changed, update current balance accordingly
            if old_opening_balance != account.opening_balance:
                account.update_balance()
            
            messages.success(request, 'Account updated successfully.')
            return redirect('account_list')
    else:
        form = AccountForm(instance=account)
    
    context = {'form': form, 'title': 'Update Account'}
    return render(request, 'accounts/account_form.html', context)

def account_delete(request, pk):
    account = get_object_or_404(Account, pk=pk)
    
    if request.method == 'POST':
        account.delete()
        messages.success(request, 'Account deleted successfully.')
        return redirect('account_list')
    
    context = {'account': account}
    return render(request, 'accounts/account_confirm_delete.html', context)

def account_type_list(request):
    account_types = AccountType.objects.all().order_by('name')
    context = {'account_types': account_types}
    return render(request, 'accounts/account_type_list.html', context)

def account_type_create(request):
    if request.method == 'POST':
        form = AccountTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account type created successfully.')
            return redirect('account_type_list')
    else:
        form = AccountTypeForm()
    
    context = {'form': form, 'title': 'Create Account Type'}
    return render(request, 'accounts/account_type_form.html', context)

def account_type_update(request, pk):
    account_type = get_object_or_404(AccountType, pk=pk)
    
    if request.method == 'POST':
        form = AccountTypeForm(request.POST, instance=account_type)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account type updated successfully.')
            return redirect('account_type_list')
    else:
        form = AccountTypeForm(instance=account_type)
    
    context = {'form': form, 'title': 'Update Account Type'}
    return render(request, 'accounts/account_type_form.html', context)

def account_type_delete(request, pk):
    account_type = get_object_or_404(AccountType, pk=pk)
    
    if request.method == 'POST':
        account_type.delete()
        messages.success(request, 'Account type deleted successfully.')
        return redirect('account_type_list')
    
    context = {'account_type': account_type}
    return render(request, 'accounts/account_type_confirm_delete.html', context)