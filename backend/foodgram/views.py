from django.shortcuts import get_object_or_404, redirect

from recipes.models import ShortLink


def redirect_short_link(request, slug):
    short_link = get_object_or_404(ShortLink, slug=slug)

    return redirect(
        request.build_absolute_uri(f'/recipes/{short_link.recipe.id}/')
    )
