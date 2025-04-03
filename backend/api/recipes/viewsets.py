from django.conf import settings
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.pagination import RecipePagination
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingList,
    Tag
)

from .filters import IngredientFilter, RecipeFilter
from .mixins import ListRetrieveGenericMixin
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeListSerializer,
    ShoppingListSerializer,
    TagSerializer
)


class IngredientViewSet(ListRetrieveGenericMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class TagsViewSet(ListRetrieveGenericMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly,)
    pagination_class = RecipePagination
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, **kwargs):
        recipe = self.get_object()
        short_url = request.build_absolute_uri(f'/s/{recipe.short_link}/')
        return Response({'short-link': short_url}, status=status.HTTP_200_OK)

    def __add_recipe(self, request, pk, serializer_class):
        serializer = serializer_class(
            data={'recipe': get_object_or_404(Recipe, id=pk).id,
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
    def shopping_cart(self, request, **kwargs):
        return self.__add_recipe(request,
                                 kwargs.get('pk'),
                                 ShoppingListSerializer)

    @action(detail=True,
            methods=('POST',),
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, **kwargs):
        return self.__add_recipe(request,
                                 kwargs.get('pk'),
                                 FavoriteSerializer)

    def __delete_recipe(self, request, pk, model, error_detail):
        deleted_count, _ = model.objects.filter(
            user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()

        if deleted_count == 0:
            raise serializers.ValidationError(
                detail=error_detail,
                code=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, **kwargs):
        return self.__delete_recipe(
            request, kwargs.get('pk'),
            ShoppingList,
            'Рецепт не в списке покупок, нельзя удалить')

    @favorite.mapping.delete
    def delete_favorite(self, request, **kwargs):
        return self.__delete_recipe(
            request, kwargs.get('pk'),
            Favorite,
            'Рецепт не в избранном, нельзя удалить')

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
