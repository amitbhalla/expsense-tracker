from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Transaction

@receiver(post_save, sender=Transaction)
def update_account_balance_on_transaction(sender, instance, created, **kwargs):
    """
    Update account balance when a transaction is created or updated
    """
    # Update the source account balance
    instance.account.update_balance()
    
    # If this is a transfer, update the destination account balance as well
    if instance.transaction_type == 'TRANSFER' and instance.to_account:
        instance.to_account.update_balance()

@receiver(post_delete, sender=Transaction)
def update_account_balance_on_delete(sender, instance, **kwargs):
    """
    Update account balance when a transaction is deleted
    """
    # Update the source account balance
    instance.account.update_balance()
    
    # If this is a transfer, update the destination account balance as well
    if instance.transaction_type == 'TRANSFER' and instance.to_account:
        instance.to_account.update_balance()