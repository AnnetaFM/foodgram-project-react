# Generated by Django 3.2.3 on 2023-08-30 05:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_rename_quantity_recipeingredient_amount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shoppinglist',
            old_name='recipes',
            new_name='recipe',
        ),
    ]
