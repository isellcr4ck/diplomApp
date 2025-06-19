from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .models import Review, Feedback

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(label=_('Электронная почта'), required=True)
    phone = forms.CharField(label=_('Телефон'), max_length=20, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']
        labels = {
            'username': _('Имя пользователя'),
            'email': _('Электронная почта'),
            'phone': _('Телефон'),
            'password1': _('Пароль'),
            'password2': _('Подтверждение пароля'),
        }

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label=_('Email или имя пользователя'))

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'avatar']
        labels = {
            'username': _('Имя пользователя'),
            'email': _('Электронная почта'),
            'phone': _('Телефон'),
            'avatar': _('Аватар'),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        labels = {
            'text': _('Ваш отзыв'),
            'rating': _('Оценка'),
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Поделитесь своим опытом...'}),
            'rating': forms.HiddenInput(),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']
        labels = {
            'name': _('Ваше имя'),
            'email': _('Email для связи'),
            'message': _('Сообщение'),
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ваше имя', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Ваш email', 'class': 'form-control'}),
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ваше сообщение...', 'class': 'form-control'}),
        }