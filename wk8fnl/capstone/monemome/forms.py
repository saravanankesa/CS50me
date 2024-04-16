from django import forms
from django.contrib.auth.models import User

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
        self.fields['email'].initial = None