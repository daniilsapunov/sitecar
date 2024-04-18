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


]
