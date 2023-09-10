from django.core.validators import MinValueValidator
from django.db import models
from users.models import User

MAX_LEN = 200


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_LEN,
        verbose_name="Название ингредиента",
        help_text="Введите название ингредиента",
    )
    measurement_unit = models.CharField(
        max_length=MAX_LEN,
        verbose_name="Единица измерения",
        help_text="Введите единицу измерения",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_LEN,
        verbose_name="Тег",
        help_text="Тег рецепта",
        unique=True,
    )
    color = models.CharField(
        max_length=7,
        verbose_name="Цвет",
        help_text="Цвет тега в формате HEX (например, #49B64E)",
    )
    slug = models.SlugField(
        max_length=MAX_LEN,
        unique=True,
        verbose_name="Slug",
        help_text="Уникальное имя для использования в URL",
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name="Автор",
    )
    name = models.CharField(
        max_length=MAX_LEN,
        verbose_name="Название рецепта",
    )
    image = models.ImageField(
        upload_to="recipes/image/",
        verbose_name="Фото блюда",
    )
    text = models.TextField(
        verbose_name="Описание рецепта",
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        verbose_name="Ингредиенты",
        related_name='ingredients',
    )
    tags = models.ManyToManyField(
        'Tag',
        verbose_name="Теги",
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления (в минутах)",
        validators=[MinValueValidator(
            1,
            message="Время приготовления не может быть равно 0!")
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_list'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_list'
    )
    amount = models.IntegerField(
        verbose_name="Количество",
        default=0,
        validators=[MinValueValidator(
            1,
            message="Добавьте ингредиент!")
        ]
    )

    class Meta:
        verbose_name = 'ингридиент'
        verbose_name_plural = 'ингридиенты'

    def __str__(self):
        return f'{self.ingredient} + {self.recipe}'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name="Избранный рецепт",
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_user_recipe',
            ),
        )

    def __str__(self):
        return f"{self.user} -> {self.recipe}"


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_shopping_lists',
        verbose_name="Добавлено в корзину",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепты в списке покупок",
        related_name='recipe_shopping_lists',
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'], name='unique_shopping_list_recipe'
            )
        ]

    def __str__(self):
        return f"Список покупок для {self.user}"
