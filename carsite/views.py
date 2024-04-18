from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from .models import Product, Category
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


# Create your views here.


def main(request):
    context = {'category': Category.objects.all()}
    return render(request, 'carsite/base.html', context)


def sign_in(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/carsite')
        else:
            messages.info(request, 'username or password incorrect')
    context = {'category': Category.objects.all()}
    return render(request, 'carsite/sign_in.html', context)


def sign_up(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created ' + user)
            return redirect('login')

    context = {'form': form, 'category': Category.objects.all()}
    return render(request, 'carsite/sign_up.html', context)


def all_detail(request):
    context = {'products': Product.objects.all(), 'category': Category.objects.all()}
    return render(request, 'carsite/all_detail.html', context)


def detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    context = {'product': product, 'category': Category.objects.all()}
    return render(request, 'carsite/detail.html', context)


def categories(request):
    context = {'categories': Category.objects.all(), 'category': Category.objects.all()}
    return render(request, 'carsite/categories.html', context)


def category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    context = {'product': Product.objects.filter(category=category), 'category': Category.objects.all()}
    return render(request, 'carsite/category.html', context)
