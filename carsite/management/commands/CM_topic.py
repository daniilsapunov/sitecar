from django.core.management.base import BaseCommand
from carsite.models import CategoryForTopic, Topic, User
import json


class Command(BaseCommand):
    help = 'Parse and save topics'

    def add_arguments(self, parser):
        parser.add_argument('--data_file_path', type=str, required=False,
                            default='carsite/management/commands/topic.json')

    def handle(self, *args, **options):
        # CategoryForTopic.objects.all().delete()  # Очищаем таблицу CategoryForTopic
        Topic.objects.all().delete()  # Очищаем таблицу Topic

        file_path = options['data_file_path']

        with open(file_path) as f:
            data = json.load(f)
            topics = data['Topic']

            # Спарсивание и сохранение категорий
            # categories = set(topic['category'] for topic in topics)
            # for category_name in categories:
            #     category = CategoryForTopic.objects.create(name=category_name)
            #     self.stdout.write(self.style.SUCCESS(f'Добавлена категория: {category.name}'))

            # Спарсивание и сохранение тем
            for topic_data in topics:
                title = topic_data['title']
                content = topic_data['content']
                created_at = topic_data['created_at']
                author = topic_data['author']
                user = User.objects.get(username=author)
                category_name = topic_data['category']
                print(category_name)
                cat = CategoryForTopic.objects.get(name=category_name)
                status = topic_data['status']

                topic = Topic.objects.create(
                    title=title,
                    content=content,
                    created_at=created_at,
                    author=user,
                    category=cat,
                    status=status
                )
                self.stdout.write(self.style.SUCCESS(f'Добавлена тема: {topic.title}'))

        self.stdout.write(self.style.SUCCESS('Данные успешно добавлены в базу данных.'))
