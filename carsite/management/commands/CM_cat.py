from django.core.management import BaseCommand
from carsite.models import CategoryForTopic, Topic

import json


class Command(BaseCommand):
    help = 'Add question and choice'

    def add_arguments(self, parser):
        parser.add_argument('--data_file_path', type=str, required=False,
                            default='carsite/management/commands/category.json')

    def handle(self, *args, **options):
        CategoryForTopic.objects.all().delete()  # Очищаем таблицу CategoryForTopic
        file = options['data_file_path']

        with open(file) as f:
            data = json.load(f)
            category_data = data.get('CategoryForTopic', [])  # Получаем список категорий

        for category_item in category_data:
            name = category_item.get('name')
            description = category_item.get('description')

            category = CategoryForTopic.objects.create(name=name, description=description)
            print(f"Добавлена категория: {category}")

        print("Данные успешно добавлены в базу данных.")
