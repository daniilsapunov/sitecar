from django.contrib import admin
from .models import Category, Product, CategoryForTopic, Topic, Comment, Engine, ChildComment, Service, CategoryService, Order,OrderEntry
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
admin.site.register(Product)
admin.site.register(CategoryForTopic)
admin.site.register(Topic)
admin.site.register(ChildComment)
admin.site.register(CategoryService)
admin.site.register(Engine)
admin.site.register(Order)
admin.site.register(OrderEntry)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('author', 'email', 'body')


admin.site.register(Comment, CommentAdmin)


class EngineInline(admin.StackedInline):
    model = Engine
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    inlines = [EngineInline]


class ProductInline(admin.StackedInline):
    model = Product
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [ProductInline]


class CatInline(admin.StackedInline):
    model = CategoryService
    extra = 0


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    inlines = [CatInline]
