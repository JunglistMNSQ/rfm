from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm, TextInput, RadioSelect, \
    CheckboxSelectMultiple
from . import models
from .validators import *


class UserRegistrationForm(ModelForm):
    password = forms.CharField(label='Введите пароль',
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторите пароль',
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Пароли не совпадают')
        return cd['password2']


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

        model = models.ManageTable
        fields = ['name']
        widgets = {'name': TextInput()}

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop('owner')
        super(CreateOrUpdateTable, self).__init__(*args, **kwargs)
        self.fields[
            'choice_exist_tab'
        ].queryset = models.ManageTable.objects.filter(owner=owner)

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
        if cd['col0'] != cd['col1'] != cd['col2'] != cd['col3'] != cd['col4']:
            pass
        else:
            raise ValidationError('Значения в шапке таблице не '
                                  'должны повторяться')


#
# class RfmOptions(forms.ModelForm):
#
#     class Meta:
#
#         model = models.ManageTable
#         fields = ['choice_rec_1', 'choice_rec_2',
#                   'recency_raw_1', 'recency_raw_2',
#                   'frequency_1', 'frequency_2',
#                   'monetary_1', 'monetary_2',
#                   'on_off'
#                   ]
#         widgets = {
#             'recency_raw_1': TextInput,
#             'recency_raw_2': TextInput,
#             'frequency_1': TextInput,
#             'frequency_2': TextInput,
#             'monetary_1': TextInput,
#             'monetary_2': TextInput,
#             'on_off': RadioSelect(attrs={'id': 'on_off'}),
#         }
#
#
class ClientManage(forms.ModelForm):

    class Meta:
        model = models.Person
        fields = ['phone', 'active_client']

#
# class Rule(forms.ModelForm):
#
#     class Meta:
#         model = models.Rules
#         fields = ['name', 'from_to', 'message', 'on_off_rule']
#         widgets = {'on_off_rule': RadioSelect(attrs={'id': 'on_off'}),
#                    'from_to': CheckboxSelectMultiple}
