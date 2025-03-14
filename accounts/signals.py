from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Account

@receiver(post_save, sender=Account)
def initialize_account_balance(sender, instance, created, **kwargs):
    """
    Set the current balance to opening balance when an account is created
    """
    if created:
        instance.current_balance = instance.opening_balance
        instance.save(update_fields=['current_balance'])