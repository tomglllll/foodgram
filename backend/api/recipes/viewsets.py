from django.conf import settings
from django.db.models import Sum
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action

from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer,
                          TagSerializer,
                          RecipeListSerializer,
                          RecipeCreateSerializer,
                          ShoppingListSerializer,
                          FavoriteSerializer)

from recipes.models import (Tag, Ingredient, IngredientInRecipe,
                            Recipe, ShoppingList, Favorite)
from users.models import Subscription
from .mixins import ListRetrieveGenericMixin
from .filters import IngredientFilter, RecipeFilter


class IngredientViewSet(ListRetrieveGenericMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = None


class TagsViewSet(ListRetrieveGenericMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticated & IsAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return RecipeCreateSerializer

    @action(detail=True,
            methods=('POST',),
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        serializer = ShoppingListSerializer(
            data={'recipe': kwargs.get('pk'),
                  'user': request.user.id},
            context={
                'request': request
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True,
            methods=('POST',),
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, **kwargs):
        serializer = FavoriteSerializer(
            data={'recipe': kwargs.get('pk'),
                  'user': request.user.id},
            context={
                'request': request
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, **kwargs):
        ShoppingList.objects.filter(
            user=request.user,
            recipe_id=kwargs.get('pk')
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @favorite.mapping.delete
    def delete_favorite(self, request, **kwargs):
        Favorite.objects.filter(
            user=request.user,
            recipe_id=kwargs.get('pk')
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _data_preprocessing(self, ingredients):
        result = ''
        total_amount = 0
        m_unit = None

        prev_item = None
        for ingredient in ingredients:
            name = ingredient.get('ingredient__name')
            measurement_unit = ingredient.get('ingredient__measurement_unit')
            curr_amount = ingredient.get('total_amount')

            if prev_item and prev_item != name:
                result += f'{prev_item} - {total_amount} {measurement_unit}\n'

            prev_item = name
            m_unit = measurement_unit
            total_amount += curr_amount

        if prev_item:
            result += f'{prev_item} - {total_amount} {m_unit}\n'

        return result

    @action(detail=False,
            methods=('GET',))
    def download_shopping_cart(self, request):
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_list__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        filename = settings.SHOPPING_LIST_FILENAME
        with open(filename, mode='w', encoding='UTF-8') as file:
            file.write(self._data_preprocessing(ingredients))

        headers = {
            'Content-Description': f'attachment: filename={filename}'
        }
        return FileResponse(open(filename, 'rb'), headers=headers)
