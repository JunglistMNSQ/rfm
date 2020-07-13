from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput
from . import models
from .validators import validate_file_extension


class UserRegistrationForm(ModelForm):
    password = forms.CharField(label='Введите пароль',
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторите пароль',
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Пароли не совпадают')
        return cd['password2']


class ProfileForm(ModelForm):

    class Meta:
        model = models.Profile
        fields = ['sms_login', 'sms_pass']
        widgets = {'sms_pass': forms.PasswordInput}


class CreateOrUpdateTable(ModelForm):

    choice_exist_tab = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label='или обновите существующую таблицу'
    )

    file = forms.FileField(
        validators=[validate_file_extension],
        label='Файл',
    )

    class Meta:

        model = models.Tab
        fields = ['name']
        widgets = {'name': TextInput()}

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop('owner')
        super(CreateOrUpdateTable, self).__init__(*args, **kwargs)
        self.fields[
            'choice_exist_tab'
        ].queryset = models.Tab.objects.filter(owner=owner)

    def clean(self):
        super().clean()
        name = self.cleaned_data['name']
        exist_tab = self.cleaned_data['choice_exist_tab']
        if name and exist_tab:
            raise ValidationError(
                'Нельзя выбрать одновременно создание'
                ' новой таблицы и обновление существующей.'
                ' Выберите один из вариантов')
        if not name and not exist_tab:
            raise ValidationError(
                'Введите название новой таблицы, '
                'либо выберете существующую '
                'для обновления данных.')


class ParserForm(forms.Form):

    DATA_TYPE = [('name', 'Имя'),
                 ('phone', 'Номер телефона'),
                 ('date', 'Дата сделки'),
                 ('pay', 'Сумма сделки'),
                 ('good', 'Услуга / Товар')]

    col0 = forms.ChoiceField(choices=DATA_TYPE, initial='date')
    col1 = forms.ChoiceField(choices=DATA_TYPE, initial='name')
    col2 = forms.ChoiceField(choices=DATA_TYPE, initial='phone')
    col3 = forms.ChoiceField(choices=DATA_TYPE, initial='good')
    col4 = forms.ChoiceField(choices=DATA_TYPE, initial='pay')

    def clean(self):
        super().clean()
        cd = self.cleaned_data
        if cd['col0'] != cd['col1'] != \
                cd['col2'] != cd['col3'] != cd['col4']:
            pass
        else:
            raise ValidationError('Значения в шапке таблице не '
                                  'должны повторяться')
