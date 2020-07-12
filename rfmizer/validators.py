import os
from django.core.exceptions import ValidationError


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.csv']
    if not ext.lower() in valid_extensions:
        raise ValidationError(
            f'Не поддерживаемый тип файла. '
            f'Пожалуйста загрузите CSV файл.')


def validate_input_options(value):
    if int(value) or None:
        return int(value) or None
    else:
        raise ValidationError(f'Введи числовое значение.')
