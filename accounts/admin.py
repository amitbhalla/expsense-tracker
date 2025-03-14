from django.contrib import admin
from .models import Account, AccountType

@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_type', 'opening_balance', 'current_balance', 'created_at')
    list_filter = ('account_type', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('current_balance',)