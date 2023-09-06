from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredient,
                     ShoppingList, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline]
    list_display = ('name', 'author', 'favorited_by_count',)
    list_filter = ('name', 'author', 'tags',)
    readonly_fields = ('favorited_by_count',)

    def favorited_by_count(self, obj):
        return obj.favorited_by.count()

    favorited_by_count.short_description = "Кол-во в избранном"


admin.site.register(RecipeIngredient)
admin.site.register(FavoriteRecipe)
admin.site.register(ShoppingList)
admin.site.register(Tag)
