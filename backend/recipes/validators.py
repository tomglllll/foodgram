from django.core.exceptions import ValidationError
import re

from .constants import SLUG_REGEX


def validate_slug(value):
    if not re.match(SLUG_REGEX, value):
        raise ValidationError('Допустимы только латинские буквы, '
                              'цифры, дефис и подчёркивание.')
