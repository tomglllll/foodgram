from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingList,
    ShortLink,
    Tag
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class IngredientInRecipeAdmin(admin.TabularInline):
    model = IngredientInRecipe
    min_num = 1
    validate_min = True


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'get_favorites_count'
    )

    search_fields = (
        'name', 'author__username', 'tags__name'
    )

    readonly_fields = ('get_favorites_count',)
    inlines = (IngredientInRecipeAdmin,)

    list_filter = ('tags',)

    def get_favorites_count(self, recipe):
        return recipe.favorites.count()

    get_favorites_count.short_description = 'Число добавлений в избранное'


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ('slug', 'recipe', 'created_at')
    search_fields = ('slug', 'recipe__name')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('recipe__tags',)
    search_fields = ('recipe__name',)


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('recipe__tags',)
    search_fields = ('recipe__name',)
