import base62
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User

from .constants import (
    COOKING_TIME_VALIDATION_MESSAGE,
    INGREDIENT_AMOUNT_VALIDATION_MESSAGE,
    INGREDIENT_NAME_MAX_LENGTH,
    MAX_COOKING_TIME,
    MAX_INGREDIENT_AMOUNT,
    MEASUREMENT_MAX_LENGTH,
    MIN_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT,
    RECIPE_NAME_MAX_LENGTH,
    SHORT_LINK_MAX_LENGTH,
    TAG_NAME_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH
)


class Ingredient(models.Model):
    name = models.CharField(max_length=INGREDIENT_NAME_MAX_LENGTH)
    measurement_unit = models.CharField(max_length=MEASUREMENT_MAX_LENGTH)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='ingredient_unique'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        max_length=TAG_NAME_MAX_LENGTH,
        unique=True
    )

    slug = models.SlugField(
        max_length=TAG_SLUG_MAX_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(max_length=RECIPE_NAME_MAX_LENGTH)
    image = models.ImageField(
        upload_to='recipes/images/'
    )
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=MIN_COOKING_TIME,
                message=COOKING_TIME_VALIDATION_MESSAGE
            ),
            MaxValueValidator(
                limit_value=MAX_COOKING_TIME,
                message=COOKING_TIME_VALIDATION_MESSAGE
            )
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )
    short_link = models.CharField(
        max_length=SHORT_LINK_MAX_LENGTH,
        unique=True,
        verbose_name='Короткая ссылка',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    @staticmethod
    def generate_slug(recipe_id):
        return base62.encode(recipe_id)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.short_link:
            self.short_link = self.generate_slug(self.id)
            super().save(update_fields=['short_link'])

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipe'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipe'
    )
    amount = models.PositiveIntegerField(
        validators=[
            MinValueValidator(
                limit_value=MIN_INGREDIENT_AMOUNT,
                message=INGREDIENT_AMOUNT_VALIDATION_MESSAGE
            ),
            MaxValueValidator(
                limit_value=MAX_INGREDIENT_AMOUNT,
                message=INGREDIENT_AMOUNT_VALIDATION_MESSAGE
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='ingredient_in_recipe_unique'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'


class UserRecipeRelation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True


class Favorite(UserRecipeRelation):

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        default_related_name = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='favorites_unique'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'


class ShoppingList(UserRecipeRelation):

    class Meta:
        verbose_name = 'Список покупок'
        default_related_name = 'shopping_list'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='shopping_list_unique'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в корзину {self.recipe}'
