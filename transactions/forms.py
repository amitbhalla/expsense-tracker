from django import forms
from django.forms import DateInput
from .models import Transaction, Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['account', 'category', 'amount', 'transaction_type', 'date', 'description']
        widgets = {
            'account': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'date': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class TransferForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['account', 'to_account', 'amount', 'date', 'description']
        widgets = {
            'account': forms.Select(attrs={'class': 'form-select'}),
            'to_account': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'] = forms.CharField(
            widget=forms.HiddenInput(),
            initial='TRANSFER'
        )
        
        # Set a default transfer category or create one if it doesn't exist
        from .models import Category
        transfer_category, created = Category.objects.get_or_create(
            name='Transfer',
            defaults={'description': 'Transfer between accounts'}
        )
        self.fields['category'] = forms.ModelChoiceField(
            queryset=Category.objects.all(),
            initial=transfer_category,
            widget=forms.HiddenInput()
        )