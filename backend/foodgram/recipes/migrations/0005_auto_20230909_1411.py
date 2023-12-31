# Generated by Django 3.2.3 on 2023-09-09 07:11

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20230909_1305'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Время приготовления не может быть равно 0!')], verbose_name='Время приготовления (в минутах)'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(1, message='Добавьте ингредиент!')], verbose_name='Количество'),
        ),
    ]
