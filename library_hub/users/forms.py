from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].help_text = (
            "Majburiy. 150 ta belgi yoki kamroq. "
            "Faqat harflar, raqamlar va @/./+/-/_ belgilar."
        )
        self.fields['password1'].help_text = (
            "<ul>"
            "<li>Parol shaxsiy ma'lumotlaringizga o'xshash bo'lmasligi kerak.</li>"
            "<li>Parol kamida 8 ta belgidan iborat bo'lishi kerak.</li>"
            "<li>Parol keng tarqalgan parollardan biri bo'lmasligi kerak.</li>"
            "<li>Parol faqat raqamlardan iborat bo'lmasligi kerak.</li>"
            "</ul>"
        )
        self.fields['password2'].help_text = (
            "Tasdiqlash uchun avvalgi parolni qaytadan kiriting."
        )


class LoginForm(AuthenticationForm):
    pass
