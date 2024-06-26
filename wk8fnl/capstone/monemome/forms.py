from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Account, Category, Transaction

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Enter your email address")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Enter new email',
        'class': 'form-control',
        'autocomplete': 'off'
    }), required=False)

    class Meta:
        model = User
        fields = ['email']
    
    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = 'New Email'
        self.fields['email'].required = False
        self.fields['email'].initial = None  # Clear the initial email field

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['account_name', 'purpose']
        help_texts = {
            'account_name': 'Enter a name for your account',
            'purpose': 'What is the purpose of this account?'
        }
        widgets = {
            'account_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'account_name', 'style': 'width: 40%;', 'title': 'Enter a name, e.g. Chequing, Main.', 'data-bs-toggle': 'tooltip'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 1, 'title': 'Describe the purpose of this account... Purposes will possess a purpose when future app developments occur.', 'data-bs-toggle': 'tooltip'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'transaction_type', 'value_score']
        labels = {
            'category_name': 'Category Name',
            'transaction_type': 'Transaction Type',
            'value_score': 'Value Score',
        }
        help_texts = {
            'category_name': 'Create a category name for your transactions to keep track of them',
            'value_score': 'Select a value score based on the importance of this category to you',
        }
        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'account', 'title': 'Enter a name for your category, e.g. groceries, fixed income', 'data-bs-toggle': 'tooltip'}),
            'transaction_type': forms.Select(choices=Category.TRANSACTION_TYPES, attrs={'class': 'form-control', 'placeholder': 'Select one', 'title': 'Select the type of transactions this category will represent.', 'data-bs-toggle': 'tooltip'}),
            'value_score': forms.Select(attrs={'class': 'form-control', 'title': 'Rate the importance of tracking this category from 1 (Low) to 5 (High).', 'data-bs-toggle': 'tooltip'}),
        }
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['transaction_type'].required = True
        self.fields['transaction_type'].widget.attrs['placeholder'] = 'Select one'
        self.fields['transaction_type'].empty_label = "Select one"

class TransactionForm(forms.ModelForm):
    TRANSACTION_TYPES = [
        ('Expense', 'Expense'),
        ('Income', 'Income'),
    ]
    
    transaction_type = forms.ChoiceField(choices=TRANSACTION_TYPES, widget=forms.RadioSelect(attrs={'onchange': 'updateFormFields();'}))

    account = forms.ModelChoiceField(
        queryset=Account.objects.none(),  # Initially empty, will be set in the view
        empty_label="Select Account",
        label='Account',
        widget=forms.Select(attrs={'class': 'form-control'})
    )


    class Meta:
        model = Transaction
        fields = ['transaction_type', 'account', 'transaction_name', 'category', 'amount', 'date', 'is_pre_auth', 'is_recurring']
        help_texts = {
            'account': 'Select the account this transaction is for',
            'transaction_name': 'Create a name to remember this transaction, e.g. business name, bill payee',
            'category': 'Select the category this transaction belongs in',
            'is_pre_auth': 'Is this a pre-authorized payment?',
            'is_recurring': 'Is this a recurring payment?',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'transaction_type': forms.RadioSelect,
            'is_pre_auth': forms.CheckboxInput(attrs={'class': 'expense-only'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'income-only'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(TransactionForm, self).__init__(*args, **kwargs)

        # Setting the queryset for account to user-specific accounts and initializing selected value if instance exists
        if self.user:
            self.fields['account'].queryset = Account.objects.filter(user=self.user)

        if 'transaction_type' in self.data:
            # If the form is being submitted, update the queryset based on the selected transaction type.
            transaction_type = self.data.get('transaction_type')
            self.fields['category'].queryset = Category.objects.filter(transaction_type=transaction_type)
        elif self.instance and self.instance.pk:
            # This ensures that during form editing, the current value is valid.
            self.fields['category'].queryset = Category.objects.filter(transaction_type=self.instance.transaction_type)

        self.fields['is_pre_auth'].widget = forms.CheckboxInput(attrs={'class': 'expense-only', 'style': 'display:none;'})
        self.fields['is_recurring'].widget = forms.CheckboxInput(attrs={'class': 'income-only', 'style': 'display:none;'})

    def save(self, commit=True):
        instance = super(TransactionForm, self).save(commit=False)
        if not instance.user_id:  # Only set user if it's not already set
            instance.user = self.user
        if commit:
            instance.save()
            self.save_m2m()  # Needed for saving many-to-many relations
        return instance

    def clean_category(self):
        # Explicitly fetch the category ID to handle cases where the model instance might be passed
        category_id = self.cleaned_data.get('category')
        if isinstance(category_id, Category):
            return category_id
        try:
            # Attempt to get the Category instance by ID
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            raise forms.ValidationError("This category does not exist.")
        return category

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        category = cleaned_data.get('category')

        # Add a check to ensure category is not None before accessing its ID
        if category is None:
            print("Transaction Type:", transaction_type)
            print("Category:", category)
            raise forms.ValidationError("Category is required.")
        
        if not Category.objects.filter(transaction_type=transaction_type, id=category.id).exists():
            raise forms.ValidationError("Select a valid choice. That choice is not one of the available choices.")

        return cleaned_data

