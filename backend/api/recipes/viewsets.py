from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .serializers import (IngredientSerializer,
                          TagSerializer,
                          RecipeListSerializer,
                          RecipeCreateSerializer,
                          ShoppingListSerializer,
                          SubscriptionSerializer,
                          SubscriptionCreateSerializer,
                          FavoriteSerializer)

from recipes.models import (Tag, Ingredient, IngredientInRecipe,
                            Recipe, ShoppingList, Favorite)
from users.models import Subscription

from .mixins import ListRetrieveGenericMixin


class IngredientViewSet(ListRetrieveGenericMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class TagsViewSet(ListRetrieveGenericMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

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

    @action(
        detail=False,
        methods=('GET',)
    )
    def download_shopping_cart(self, request):
        pass
