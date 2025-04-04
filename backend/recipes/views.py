from django.conf import settings
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from rest_framework import status

from recipes.models import Recipe


def redirect_short_link(request, short_link):
    try:
        recipe = Recipe.objects.get(short_link=short_link)
    except Recipe.DoesNotExist:
        raise ValidationError(message='Рецепт ненайден',
                              code=status.HTTP_404_NOT_FOUND)

    return redirect(
        f'{settings.SITE_URL}/recipes/{recipe.id}/'
    )
