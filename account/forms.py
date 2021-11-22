from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegisterForm(forms.ModelForm):

    GROUP_CHOICES = [
        ('admin', 'Administrator'),
        ('employee', 'Pracownik')
    ]

    group = forms.ChoiceField(choices=GROUP_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

        widgets = {
            'first_name': forms.TextInput(attrs={'required': 'True'}),
            'last_name': forms.TextInput(attrs={'required': 'True'}),
            'email': forms.TextInput(attrs={'required': 'True'}),
        }
