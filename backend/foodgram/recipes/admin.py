from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import transaction

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

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        if not obj.cooking_time > 0:
            raise ValidationError(
                "Время приготовления должно быть больше 0 минут!")
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if not form.instance.ingredients.exists():
            raise ValidationError("Укажите ингредиенты!")

    def clean(self):
        super().clean()
        if not self.cleaned_data.get('ingredients'):
            raise ValidationError("Укажите ингредиенты!")


admin.site.register(RecipeIngredient)
admin.site.register(FavoriteRecipe)
admin.site.register(ShoppingList)
admin.site.register(Tag)
