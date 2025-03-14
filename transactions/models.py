from django.db import models
from accounts.models import Account
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
        ('TRANSFER', 'Transfer'),
    )
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # For transfers between accounts
    to_account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='incoming_transfers',
        null=True, 
        blank=True
    )

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} on {self.date}"
    
    def save(self, *args, **kwargs):
        # Ensure transaction_type is uppercase for consistency
        if self.transaction_type:
            self.transaction_type = self.transaction_type.upper()
            
        # Save the transaction
        super().save(*args, **kwargs)
        
        # Update the account balance
        self.account.update_balance()
        
        # If this is a transfer, update the receiving account as well
        if self.transaction_type == 'TRANSFER' and self.to_account:
            self.to_account.update_balance()