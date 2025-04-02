from django.conf import settings
from django.shortcuts import get_object_or_404, redirect

from recipes.models import ShortLink


def redirect_short_link(request, slug):
    short_link = get_object_or_404(ShortLink, slug=slug)

    return redirect(
        f'{settings.SITE_URL}/recipes/{short_link.recipe.id}/'
    )
