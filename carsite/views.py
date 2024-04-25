from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from .forms import CommentForm, ChildCommentForm
from .models import Product, Category, Order, OrderEntry, Profile, Topic, ChildComment, CategoryForTopic, Comment, \
    Service, Engine
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import json
from django.http import JsonResponse, HttpResponseNotFound
from django.core.mail import send_mail
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


def main(request):
    user = request.user
    context = {'category': Category.objects.all(), '1': 1, 'user': user}
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
    engines = product.engines.all()
    context = {'product': product, 'engines': engines}
    return render(request, 'carsite/detail.html', context)


def categories(request):
    context = {'categories': Category.objects.all(), 'category': Category.objects.all()}
    return render(request, 'carsite/categories.html', context)


def category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    context = {'product': Product.objects.filter(category=category), 'category': Category.objects.all()}
    return render(request, 'carsite/category.html', context)


@login_required
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST['id']
        engine_id = request.POST['id1']
        product = get_object_or_404(Product, id=product_id)
        engine = get_object_or_404(Engine, id=engine_id)
        try:
            profile = Profile.objects.get(user=request.user)
            profile.save()
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=request.user)
            profile.save()
        if not profile.shopping_cart:
            profile.shopping_cart = Order.objects.create(profile=profile)
            profile.save()
        try:
            order_entry = OrderEntry.objects.get(order=profile.shopping_cart, product=product, engine=engine)
        except OrderEntry.DoesNotExist:
            order_entry = OrderEntry.objects.create(order=profile.shopping_cart, product=product, engine=engine)
        # for i in profile.shopping_cart.order.all():
        #     if i.product == product:
        #         i.product.engine = engine
        #         i.save()

        order_entry.count = 1
        order_entry.save()
        return redirect('carsite:detail', product_id)


@login_required(redirect_field_name='login')
def shopping_cart(request):
    try:
        profile = Profile.objects.get(user=request.user)
        profile.save()
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
        profile.save()
    order_entry = OrderEntry.objects.filter(order=profile.shopping_cart).order_by('product')
    t = 0
    for i in OrderEntry.objects.filter(order=profile.shopping_cart):
        t += i.engine.price * i.count
    context = {'order_entry': order_entry, 't': t}

    return render(request, 'carsite/shopping_cart.html', context)


def clear_order(request):
    profile = Profile.objects.get(user=request.user)
    OrderEntry.objects.filter(order=profile.shopping_cart).delete()
    return redirect('carsite:shopping_cart')


def clear_concrete_order(request):
    product_id = request.POST['id']
    profile = Profile.objects.get(user=request.user)
    OrderEntry.objects.filter(order=profile.shopping_cart, product=product_id).delete()
    return redirect('carsite:shopping_cart')


def update_count(request):
    if request.method == 'POST':
        count = request.POST['new']
        id = request.POST['id']
        if int(count) > 0:
            order = OrderEntry.objects.get(id=id)
            order.count = count
            order.save()
        else:
            order = OrderEntry.objects.get(id=id)
            order.delete()
    return redirect('carsite:shopping_cart')


@csrf_exempt
def make_order(request):
    if request.method == 'POST':
        profile = Profile.objects.get(user=request.user)
        if profile.shopping_cart.order.exists():
            email = request.user.email
            print(email)
            profile.shopping_cart.status = 'COMPLETED'
            profile.shopping_cart.save()
            profile.shopping_cart = Order.objects.create(profile=profile)
            profile.save()
            send_mail(
                'Новое сообщение от компании',
                f'Сообщение: Успешн00о заказано!',
                'sapunowdany@yandex.ru',
                [f'{email}'],  # Замените на вашу почту для получения сообщений
                fail_silently=False,
            )
            return redirect('carsite:shopping_cart')
        else:
            return redirect('carsite:shopping_cart')


@login_required(redirect_field_name='login')
def success_order(request):
    return render(request, 'carsite/success_order.html')


@login_required(redirect_field_name='login')
def account(request):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
        profile.save()
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)
        profile.save()
    first_name = user.first_name
    last_name = user.last_name
    email = user.email
    if 'first_name' in request.POST:
        first_name = request.POST['first_name']
        user.first_name = first_name
        user.save()
    if 'last_name' in request.POST:
        last_name = request.POST['last_name']
        user.last_name = last_name
        user.save()
    if 'email' in request.POST:
        email = request.POST['email']
        user.email = email
        user.save()
    order_entry = Order.objects.filter(profile=profile).filter(status='COMPLETED').order_by('-id')[:5]
    for i in order_entry:
        entries = i.order.all()
        amount = sum(j.count for j in entries)
        i.amount = amount
        # count = sum(k.product.price * k.count for k in entries)
        # i.count = count
        i.save()
    context = {'first_name': first_name, 'last_name': last_name, 'email': email, 'order': order_entry}
    return render(request, 'carsite/account.html', context)


@login_required(redirect_field_name='login')
def order_history(request):
    profile = Profile.objects.get(user=request.user)
    order = Order.objects.filter(profile=profile).filter(status='COMPLETED').order_by('-id')[:5]
    '''contact_list = Order.objects.filter(profile=profile).filter(status='COMPLETED').order_by('-id')[:5]
    paginator = Paginator(contact_list, 2)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)'''
    page_obj = Order.objects.filter(profile=profile).filter(status='COMPLETED').order_by('-id')[:5]
    total = 0
    for i in page_obj:
        entries = i.order.all()
        i.count = total
        for g in entries:
            print(g.engine)
            total += g.engine.price
            print(total)

        # count = sum(k.order.engine.price * k.count for k in entries)
        # i.count = count
        # amount = sum(j.count for j in entries)
        # i.amount = amount
    context = {'order': order, "page_obj": page_obj, 'total': total}
    return render(request, 'carsite/order_history.html', context)


@login_required(redirect_field_name='login')
def repeat_order(request):
    if request.method == 'POST':

        profile = Profile.objects.get(user=request.user)
        OrderEntry.objects.filter(order=profile.shopping_cart).delete()

        id = request.POST['new_id']
        order = Order.objects.get(id=id)
        entry = OrderEntry.objects.filter(order=order)

        for i in entry:
            try:
                order_entry = OrderEntry.objects.get(order=profile.shopping_cart, product=i.product)
                order_entry.count = i.count
                order_entry.save()
            except OrderEntry.DoesNotExist:
                order_entry = OrderEntry.objects.create(order=profile.shopping_cart, product=i.product)
                order_entry.count = i.count
                order_entry.save()

        t = 0
        for i in OrderEntry.objects.filter(order=profile.shopping_cart):
            t += i.product.price * i.count

    return redirect('carsite:shopping_cart')


def forum_main(request):
    user = request.user

    if request.method == 'POST':
        title1 = request.POST['title']
        content1 = request.POST['content']
        category1 = request.POST['category']
        f = CategoryForTopic.objects.get(id=category1)
        Topic.objects.create(title=title1, content=content1, category=f, author=user)
    topics = Topic.objects.filter(status='Approved').order_by('created_at')
    context = {'topics': topics, 'category': category}
    return render(request, 'carsite/forum.html', context)


def add_topic(request):
    user = request.user
    category = CategoryForTopic.objects.all()

    context = {'user': user, 'category': category}
    return render(request, 'carsite/thread.html', context)


def topic_detail(request, thread_id):
    topic = Topic.objects.get(id=thread_id)
    return render(request, 'carsite/topic_view.html', {'topic': topic})


def comment_create(request, thread_id):
    topic = Topic.objects.get(id=thread_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        print(form)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post_id = thread_id
            comment.save()
            return redirect('carsite:thread_view', thread_id=thread_id)
    else:
        form = CommentForm()
    return render(request, 'carsite/comment_create_form.html', {'form': form, 'topic': topic})


def child_comment_create(request, comment_id):
    try:
        parent_comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return HttpResponseNotFound('Parent comment not found')

    if request.method == 'POST':
        form = ChildCommentForm(request.POST)
        if form.is_valid():
            child_comment = form.save(commit=False)
            child_comment.author = request.user
            child_comment.parent_comment = parent_comment
            child_comment.save()

            return redirect('carsite:thread_view', thread_id=child_comment.parent_comment.post_id)
    else:
        form = ChildCommentForm()

    return render(request, 'carsite/child_comment_create_form.html', {'form': form, 'parent_comment': parent_comment})


def support(request):
    return render(request, 'carsite/support.html')


@csrf_exempt
def send_email(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        print(name, email, message)

        # Отправка письма
        send_mail(
            'Новое сообщение от пользователя',
            f'Имя: {name}\nEmail: {email}\nСообщение: {message}',
            'sapunowdany@yandex.ru',
            ['sapunowdany@yandex.ru'],  # Замените на вашу почту для получения сообщений
            fail_silently=False,
        )
    return render(request, 'carsite/support.html')


def service(request):
    services = Service.objects.all()
    return render(request, 'carsite/service.html', {'services': services})
