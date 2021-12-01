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

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Istnieje już użytkownik o podanym adresie e-mail')
        return self.cleaned_data['email']


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

        widgets = {
            'first_name': forms.TextInput(attrs={'required': 'True'}),
            'last_name': forms.TextInput(attrs={'required': 'True'}),
            'email': forms.TextInput(attrs={'required': 'True'}),
        }


class UserUpdateFormAdmin(UserUpdateForm):
    GROUP_CHOICES = [
        ('admin', 'Administrator'),
        ('employee', 'Pracownik')
    ]

    group = forms.ChoiceField(choices=GROUP_CHOICES)

    def __init__(self, *args, **kwargs):
        super(UserUpdateFormAdmin, self).__init__(*args, **kwargs)

        if self.instance.id:
            if self.instance.groups.filter(name="admin").exists():
                self.fields["group"].initial = "admin"
            else:
                self.fields["group"].initial = "employee"
