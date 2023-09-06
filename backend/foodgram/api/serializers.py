import djoser.serializers
from django.contrib.auth import password_validation
from django.db import transaction
from drf_base64.fields import Base64ImageField
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingList, Tag)
from rest_framework import exceptions, serializers
from rest_framework.exceptions import ValidationError
from users.models import Subscription, User


class UserSerializer(djoser.serializers.UserSerializer):

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return Subscription.objects.filter(
                user=request.user, author=obj).exists()
        return False


class UserCreateSerializer(djoser.serializers.UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'password')


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value

    def validate(self, attrs):
        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')

        if not self.context['request'].user.check_password(current_password):
            raise ValidationError(
                {'current_password': 'Текущий пароль указан неверно!'}
            )

        if current_password == new_password:
            raise ValidationError(
                {'new_password': 'Новый пароль должен отличаться от старого!'}
            )
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()

        return validated_data


class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count',)
        read_only_fields = ('email', 'username', 'last_name', 'first_name')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Subscription.objects.filter(user=user, author=author).exists():
            raise exceptions.ValidationError(
                'Вы уже подписаны на этого пользователя!')
        if user == author:
            raise exceptions.ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = ShowRecipeAddedSerializer(recipes,
                                               many=True,
                                               read_only=True)
        return serializer.data


class ShowRecipeAddedSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='ingredient_list',
        read_only=True
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart')

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (obj.favorited_by.filter(user=user).exists()
                if user.is_authenticated else False)

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (obj.recipe_shopping_lists.filter(user=user).exists()
                if user.is_authenticated else False)


class RecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image',
                  'text', 'ingredients', 'tags', 'cooking_time')
        extra_kwargs = {
            'name': {'required': True, 'allow_blank': False},
            'image': {'required': True, 'allow_blank': False},
            'text': {'required': True, 'allow_blank': False},
            'ingredients': {'required': True, 'allow_blank': False},
            'tags': {'required': True, 'allow_blank': False},
            'cooking_time': {'required': True},
        }

    def validate(self, obj):
        required_fields = ['name', 'text', 'cooking_time']
        for field in required_fields:
            if not obj.get(field):
                raise serializers.ValidationError(
                    f'{field} - Заполните обязательное поле!'
                )
        if not obj.get('ingredients'):
            raise serializers.ValidationError(
                'Укажите ингрединеты!'
            )
        inrgedient_id_list = [item['id'] for item in obj.get('ingredients')]
        unique_ingredient_id_list = set(inrgedient_id_list)
        if len(inrgedient_id_list) != len(unique_ingredient_id_list):
            raise serializers.ValidationError(
                'Ингредиенты не могут повторяться!'
            )
        return obj

    @transaction.atomic
    def creating_of_tags_and_ingredients(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        self.creating_of_tags_and_ingredients(recipe, tags, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.creating_of_tags_and_ingredients(instance, tags, ingredients)
        return super().update(instance, validated_data)


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')

    def validate(self, data):
        user = self.context['request'].user
        if user.favorite_recipes.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Вы уже добавили рецепт в избранное!'
            )
        return data

    def to_representation(self, instance):
        return ShowRecipeAddedSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class ShoppingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')

    def validate(self, data):
        user = self.context['request'].user
        if user.user_shopping_lists.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Вы уже добавили этот рецепт!'
            )
        return data

    def to_representation(self, instance):
        return ShowRecipeAddedSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
