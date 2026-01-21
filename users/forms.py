from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Этот email уже используется.')
        return email

class LoginForm(forms.Form):
    username = forms.CharField(label='Логин')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'avatar': 'Аватар',
            'bio': 'О себе',
        }

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label='Email')

class PasswordResetForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label='Новый пароль')
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Подтвердите пароль')
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Пароли не совпадают.')
        
        return cleaned_data