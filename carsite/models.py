from django.db import models
from django.contrib.auth.models import User


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
    parent = models.ForeignKey(
        'self',
        default=None,
        blank=True, null=True,
        on_delete=models.CASCADE,
        related_name='parent_%(class)s',
        verbose_name='parent comment'
    )

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.author, self.post)


class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.FloatField()
    engine = models.CharField(max_length=100, default=2.0)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class OrderEntry(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='+')
    count = models.IntegerField(default=0)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order')

    def total(self):
        return f'{self.count * self.product.price}'

    def __str__(self):
        # return f'{self.product} - {self.count} - {self.count * self.product.price}'
        return f'{self.product}'


class Order(models.Model):
    class Status(models.TextChoices):
        INITIAL = 'INITIAL', 'Сбор Машины'
        COMPLETED = 'COMPLETED', 'Автомобиль готов к выдаче'

    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=200, default=Status.INITIAL, choices=Status.choices)

    def __str__(self):
        return f"{self.profile.user.username}-{self.status}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shopping_cart = models.OneToOneField(Order, on_delete=models.SET_NULL,
                                         null=True, blank=True, related_name='+')

    def __str__(self):
        return f'{self.user.username}'
