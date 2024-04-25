from django.db import models
from django.contrib.auth.models import User


class Service(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class CategoryService(models.Model):
    name = models.CharField(max_length=100)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='category')

    def __str__(self):
        return self.name


class CategoryForTopic(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Topic(models.Model):
    class Status(models.TextChoices):
        NotApproved = 'NotApproved'
        Approved = 'Approved'

    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(CategoryForTopic, on_delete=models.CASCADE)
    status = models.CharField(max_length=200, default=Status.NotApproved, choices=Status.choices)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Topic, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    child_posts = models.ManyToManyField('ChildComment', blank=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.author, self.post)


class ChildComment(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='child_comments')
    parent_com = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child')

    def __str__(self):
        return f"Child comment by {self.author.username} on {self.parent_comment.body}"


class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Engine(models.Model):
    size = models.FloatField()
    horse_power = models.IntegerField()
    category = models.CharField(max_length=100, default='Бензин')
    speed = models.TextField()
    price = models.FloatField()
    engine = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='engines')

    def __str__(self):
        return self.engine.name


class OrderEntry(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='+')
    count = models.IntegerField(default=0)
    engine = models.ForeignKey('Engine', on_delete=models.CASCADE, default=None, null=True, unique=False)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order')

    def total(self):
        return f'{self.count * self.engine.price}'

    def __str__(self):
        # return f'{self.product} - {self.count} - {self.count * self.product.price}'
        return f'{self.product}'


class Order(models.Model):
    class Status(models.TextChoices):
        INITIAL = 'INITIAL', 'Сбор Машины'
        COMPLETED = 'COMPLETED', 'Автомобиль готов к выдаче'

    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=200, default=Status.INITIAL, choices=Status.choices)

    def total(self):
        total = 0
        for x in self.order.all():
            total += x.engine.price * x.count
        return total

    def __str__(self):
        return f"{self.profile.user.username}-{self.status}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shopping_cart = models.OneToOneField(Order, on_delete=models.SET_NULL,
                                         null=True, blank=True, related_name='+')

    def __str__(self):
        return f'{self.user.username}'
