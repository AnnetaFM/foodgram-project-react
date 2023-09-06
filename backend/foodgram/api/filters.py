from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe, Tag
from rest_framework.filters import SearchFilter


class IngredientFilter(SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='filter_favorite_or_cart'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_favorite_or_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_favorite_or_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            if name == 'is_favorited':
                return queryset.filter(favorited_by__user=user)
            elif name == 'is_in_shopping_cart':
                return queryset.filter(recipe_shopping_lists__user=user)
        return queryset
