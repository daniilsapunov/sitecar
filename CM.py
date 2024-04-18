import json
from carsite.models import Category, Product


def populate_polls_database(name, clean_database=True):
    with open(name) as f:
        file_content = f.read()
        templates = json.loads(file_content)
    for i in templates:
        print('Question = ', i)
        category = Category.objects.create(name=С)
        for j in templates[i]:
            print(j, templates[i].get(j))
            Cars = Product.objects.create(name=templates[i][0],description=templates[i][1],price=[templates][i][2],category=category)
        print()

populate_polls_database('data.json')
