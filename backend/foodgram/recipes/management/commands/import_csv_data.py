import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = '''Load ingredients from a CSV file into the database'''

    def handle(self, *args, **options):
        csv_file = 'recipes/data/ingredients.csv'
        with open(csv_file, encoding='utf-8') as file:
            file_reader = csv.reader(file)
            for row in file_reader:
                name, measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit
                )
