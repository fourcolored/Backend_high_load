from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Email, Product

class EmailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ['recipient', 'subject', 'body']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def clean_name(self):
        name = self.cleaned_data['name']
        if '<' in name or '>' in name or '<script>' in name:
            raise forms.ValidationError("Invalid input")
        return name
    
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email Address')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']