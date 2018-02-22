from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import WorkerProfile


class UserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('Client', 'Замовник'),
        ('Worker', 'Виконавець')
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, label='Тип акаунта')
    email = forms.EmailField(max_length=200)
    first_name = forms.CharField(max_length=60, label="Ім'я")
    last_name = forms.CharField(max_length=60, label='Прізвище')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'password1', 'password2', 'role')

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].help_text = \
            'Ваш пароль повинен містити як мінімум 8 символів.<br/>' \
            'Ваш пароль не може складатися лише з цифр.'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Цей email вже використовується.')
        return email


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.instance.username
        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError('Цей email вже використовується.')
        return email


class WorkerProfileForm(forms.ModelForm):
    languages = forms.CharField(max_length=250, label='Мови',
                                help_text='Мови, якими Ви володієте.',
                                required=False)

    about = forms.CharField(max_length=500, label='Про себе',
                            widget=forms.Textarea, required=False,
                            help_text='Напишіть кілька слів про Вашу освіту,'
                                      ' досягнення, сертифікати тощо. ')

    card_number = forms.CharField(max_length=20,
                                  label='Номер банківської карти',
                                  required=False,
                                  help_text='Введіть правильний номер Вашої банківської карти.'
                                            'Він використовуватиметься виключно для отримання '
                                            'платежів за виконані завдання.')

    class Meta:
        model = WorkerProfile
        fields = ('languages', 'about', 'photo', 'card_number')
        labels = {
            'photo': 'Фото',
        }
