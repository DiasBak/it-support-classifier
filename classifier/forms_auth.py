from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm
)

from .models import User


class RegisterForm(UserCreationForm):

    username = forms.CharField(

        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Введите username'
            }
        )

    )

    email = forms.EmailField(

        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Введите email'
            }
        )

    )

    password1 = forms.CharField(

        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Введите пароль'
            }
        )

    )

    password2 = forms.CharField(

        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Повторите пароль'
            }
        )

    )

    class Meta:

        model = User

        fields = (

            'username',
            'email',
            'password1',
            'password2'

        )


class LoginForm(AuthenticationForm):

    username = forms.CharField(

        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Введите username'
            }
        )

    )

    password = forms.CharField(

        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Введите пароль'
            }
        )

    )