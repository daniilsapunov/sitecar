from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from .forms import CommentForm, ChildCommentForm
from .models import Product, Category, Order, OrderEntry, Profile, Topic, ChildComment, CategoryForTopic, Comment
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import json
from django.http import JsonResponse


def main(request):
    context = {'category': Category.objects.all(), '1': 1}
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


@login_required
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST['id']
        product = get_object_or_404(Product, id=product_id)
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
            order_entry = OrderEntry.objects.get(order=profile.shopping_cart, product=product)
        except OrderEntry.DoesNotExist:
            order_entry = OrderEntry.objects.create(order=profile.shopping_cart, product=product)
        order_entry.count += 1
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
        t += i.product.price * i.count
    context = {'order_entry': order_entry, 'total': t}

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


def make_order(request):
    if request.method == 'POST':
        profile = Profile.objects.get(user=request.user)
        if profile.shopping_cart.order.exists():
            profile.shopping_cart.status = 'COMPLETED'
            profile.shopping_cart.save()
            profile.shopping_cart = Order.objects.create(profile=profile)
            profile.save()
            return redirect('carsite:success_order')
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
        count = sum(k.product.price * k.count for k in entries)
        i.count = count
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
    for i in page_obj:
        entries = i.order.all()
        i.entries = entries
        count = sum(k.product.price * k.count for k in entries)
        i.count = count
        amount = sum(j.count for j in entries)
        i.amount = amount
    context = {'order': order, "page_obj": page_obj}
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


# def topic_view(request, thread_id):
#     topic = Topic.objects.get(id=thread_id)
#     if request.method == 'POST':
#         if 'reply_comment_id' in request.POST:  # Проверка, является ли это ответом на комментарий
#             parent_comment_id = request.POST.get('reply_comment_id')
#             parent_comment = Comment.objects.get(id=parent_comment_id)
#             form = ChildCommentForm(data=request.POST)
#             if form.is_valid():
#                 child_comment = form.save(commit=False)
#                 child_comment.parent_comment = parent_comment
#                 child_comment.author = request.user
#                 child_comment.save()
#         else:  # Обычный комментарий
#             form = CommentForm(data=request.POST)
#             if form.is_valid():
#                 comment = form.save(commit=False)
#                 comment.post = topic
#                 comment.author = request.user
#                 comment.save()
#     else:
#         form = CommentForm()
#
#     t = Comment.objects.filter(post=thread_id).order_by('-created')
#     context = {'topic': topic, 't': t, 'form': form,
#                }
#     return render(request, 'carsite/topic_view.html', context)


def topic_detail(request, thread_id):
    topic = Topic.objects.get(id=thread_id)
    return render(request, 'carsite/topic_view.html', {'topic': topic})


# def comment_create(request, thread_id):
#     topic = Topic.objects.get(id=thread_id)
#     if request.method == 'POST':
#         form = CommentForm(request.POST)
#         if form.is_valid():
#             comment = form.save(commit=False)
#             comment.author = request.user
#             comment.post_id = thread_id
#             comment.save()
#             comments = Comment.objects.filter(post_id=thread_id).order_by('-created')
#             return render(request, 'carsite/topic_view.html',
#                           {'thread_id': thread_id, 'comments': comments, 'topic': topic})
#     else:
#         form = CommentForm()
#     return render(request, 'carsite/comment_create_form.html', {'form': form})


# def child_comment_create(request, comment_id):
#     if request.method == 'POST':
#         form = ChildCommentForm(request.POST)
#         if form.is_valid():
#             child_comment = form.save(commit=False)
#             child_comment.author = request.user
#             child_comment.parent_comment_id = comment_id
#             child_comment.save()
#
#             # Извлечение всех дочерних комментариев для родительского комментария
#             parent_comment = Comment.objects.get(id=comment_id)
#             child_comments = parent_comment.child_comments.all().order_by('-created_at')
#
#             return render(request, 'carsite/topic_view.html',
#                           {'thread_id': parent_comment.post.id, 'comments': child_comments})
#     else:
#         form = ChildCommentForm()
#     return render(request, 'carsite/child_comment_create_form.html', {'form': form})
def comment_create(request, thread_id):
    topic = Topic.objects.get(id=thread_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
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
    comment = Comment.objects.get(id=comment_id)
    if request.method == 'POST':
        form = ChildCommentForm(request.POST)
        if form.is_valid():
            print('asdasda')
            child_comment = form.save(commit=False)
            child_comment.author = request.user
            child_comment.parent_comment_id = comment_id
            child_comment.save()

            parent_comment = Comment.objects.get(id=comment_id)
            parent_comment.child_posts.add(child_comment)  # Связываем родительский комментарий с дочерним

            return redirect('carsite:thread_view', thread_id=parent_comment.post_id)
    else:
        form = ChildCommentForm()
    return render(request, 'carsite/child_comment_create_form.html', {'form': form, 'comment': comment})


