from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from . import views


class LoginViewNEW(LoginView):
    template_name = "login.html"


app_name = 'carsite'
urlpatterns = [
    path('', views.main, name='main'),
    path('sign_in', views.sign_in, name='sign_in'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('all_detail', views.all_detail, name='all_detail'),
    path('detail/<int:product_id>', views.detail, name='detail'),
    path('accounts/login/', LoginViewNEW.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('categories', views.categories, name='categories'),
    path('category/<int:category_id>', views.category, name='category'),
    path('add_to_cart', views.add_to_cart, name='add_to_cart'),
    path('shopping_cart', views.shopping_cart, name='shopping_cart'),
    path('clear_order', views.clear_order, name='clear_order'),
    path('clear_concrete_order', views.clear_concrete_order, name='clear_concrete_order'),
    path('update_count', views.update_count, name='update_count'),
    path('make_order', views.make_order, name='make_order'),
    path('success_order', views.success_order, name='success_order'),
    path('account', views.account, name='account'),
    path('order_history', views.order_history, name='order_history'),
    path('repeat_order', views.repeat_order, name='repeat_order'),
    path('forum', views.forum_main, name='forum'),
    path('thread', views.add_topic, name='thread'),
    path('thread/<int:thread_id>', views.topic_detail, name='thread_view'),
    path('comment-create/<int:thread_id>', views.comment_create, name='comment-create'),
    path('child-comment-create/<int:comment_id>', views.child_comment_create, name='child-comment-create')

]
