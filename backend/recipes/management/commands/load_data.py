import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка данных из Json файлов в базу данных'

    def fill_ingredients(self):
        file_path = os.path.join(
            settings.BASE_DIR,
            'data',
            'ingredients.json'
        )
        self.stdout.write(
            f'Загрузка данных из {file_path}'
        )

        with open(file_path, mode='r', encoding='UTF-8') as file:
            data = json.load(file)

            Ingredient.objects.bulk_create([
                Ingredient(name=ingredient.get('name'),
                           measurement_unit=ingredient.get('measurement_unit'))
                for ingredient in data
            ],
                ignore_conflicts=True
            )

    def handle(self, *args, **kwargs):
        try:
            self.fill_ingredients()
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(
                    'Файл не найден.'
                )
            )
        except Exception as error:
            self.stdout.write(
                self.style.ERROR(
                    f'Неожиданная ошибка - {error}'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    'Данные успешно загружены!'
                )
            )
