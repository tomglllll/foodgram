from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status, validators
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.validators import UniqueTogetherValidator

from api.users.serializers import UserSerializer
from recipes.constants import (
    INGREDIENT_AMOUNT_VALIDATION_MESSAGE,
)
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingList,
    Tag
)
from users.models import Subscription

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug'
        )


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class IngredientInRecipeAddSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'amount',
        )


class RecipeCardSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class RecipeListSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None)
    author = UserSerializer(read_only=True, many=False)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        allow_empty=False,
        source='ingredient_in_recipe'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, recipe):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and recipe.favorites.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and recipe.shopping_list.filter(user=request.user).exists()
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeAddSerializer(many=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def _create_ingredients(self, obj, ingredients):
        ingredients_in_recipe = [
            IngredientInRecipe(
                recipe=obj,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        IngredientInRecipe.objects.bulk_create(ingredients_in_recipe)

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        validated_data['author'] = self.context.get('request').user
        obj = Recipe.objects.create(**validated_data)
        self._create_ingredients(obj, ingredients)
        obj.tags.set(tags)
        return obj

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.tags.set(validated_data.pop('tags'))
        instance.ingredients.clear()
        self._create_ingredients(instance, validated_data.pop('ingredients'))
        return super().update(instance, validated_data)

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                'Картинка рецепта обязательное поле'
            )
        return value

    def validate(self, attrs):
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                'Укажите хотя бы один тег'
            )

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Теги должны быть уникальными'
            )

        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Укажите хотя бы один ингредиент'
            )
        ingredient_ids = {ingr.get('id') for ingr in ingredients}
        if len(ingredients) != len(ingredient_ids):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальными'
            )

        if not ingredient_ids:
            raise serializers.ValidationError(
                detail=INGREDIENT_AMOUNT_VALIDATION_MESSAGE,
            )

        return attrs

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data


class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ('recipes',
                                               'recipes_count')
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')

        queryset = obj.recipes.all()
        if recipes_limit and recipes_limit.strip().isdigit():
            queryset = queryset[:int(recipes_limit)]

        return RecipeCardSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = (
            'user',
            'author'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['user', 'author'],
                message='Вы уже подписаны на этого пользователя.'
            )]

    def validate(self, attrs):
        user = attrs.get('user')
        author = attrs.get('author')

        if user == author:
            raise serializers.ValidationError(
                detail='Самоподписка запрещена',
                code=status.HTTP_400_BAD_REQUEST
            )

        return attrs

    def to_representation(self, instance):
        return SubscriptionSerializer(
            instance.author,
            context={
                'request': self.context.get('request')
            }
        ).data


class ShoppingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=ShoppingList.objects.all(),
                fields=['user', 'recipe'],
            )
        ]

    def to_representation(self, instance):
        return RecipeCardSerializer(
            instance.recipe,
            context={
                'request': self.context.get('request')
            }
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe'],
            )
        ]

    def to_representation(self, instance):
        return RecipeCardSerializer(
            instance.recipe,
            context={
                'request': self.context.get('request')
            }
        ).data
