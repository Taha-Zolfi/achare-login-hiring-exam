# myapp/forms.py
from django import forms
from .models import CustomUser

class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['phone_number']

class VerificationCodeForm(forms.Form):
    verification_code = forms.CharField(max_length=6)

class PasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
