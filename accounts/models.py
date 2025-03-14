from django.db import models
from django.utils import timezone

class AccountType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Account(models.Model):
    name = models.CharField(max_length=100)
    account_type = models.ForeignKey(AccountType, on_delete=models.CASCADE, related_name='accounts')
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.account_type.name})"
    
    def update_balance(self):
        """Update the current balance based on transactions"""
        from transactions.models import Transaction
        
        # Start with opening balance
        balance = self.opening_balance
        
        # Add incoming transactions
        incoming = Transaction.objects.filter(
            account=self, 
            transaction_type='INCOME'
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        # Subtract outgoing transactions
        outgoing = Transaction.objects.filter(
            account=self, 
            transaction_type='EXPENSE'
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        # Calculate current balance
        balance = balance + incoming - outgoing
        
        # Update the current balance
        self.current_balance = balance
        self.save(update_fields=['current_balance'])
        
        return self.current_balance