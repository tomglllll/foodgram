from rest_framework import viewsets
from .serializers import (IngredientSerializer,
                          TagSerializer,
                          RecipeListSerializer,
                          RecipeCreateSerializer,
                          ShoppingListSerializer,
                          SubscriptionSerializer,
                          SubscriptionCreateSerializer,
                          Favorite)

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
