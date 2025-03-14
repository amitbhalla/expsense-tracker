from django.contrib import admin
from .models import Transaction, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'account', 'category', 'transaction_type', 'amount', 'description')
    list_filter = ('transaction_type', 'date', 'account', 'category')
    search_fields = ('description',)
    date_hierarchy = 'date'