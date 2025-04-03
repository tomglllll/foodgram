from django.conf import settings
from django.shortcuts import get_object_or_404, redirect

from recipes.models import Recipe


def redirect_short_link(request, short_link):
    short_link = get_object_or_404(Recipe, short_link=short_link)

    return redirect(
        f'{settings.SITE_URL}/recipes/{short_link.recipe.id}/'
    )
