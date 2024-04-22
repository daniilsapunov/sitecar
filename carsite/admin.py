from django.contrib import admin
from .models import Category, Product, CategoryForTopic, Topic, Comment, ChildComment
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
admin.site.register(Product)
admin.site.register(CategoryForTopic)
admin.site.register(Topic)
admin.site.register(ChildComment)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('author', 'email', 'body')


admin.site.register(Comment, CommentAdmin)


class ProductInline(admin.StackedInline):
    model = Product
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [ProductInline]
