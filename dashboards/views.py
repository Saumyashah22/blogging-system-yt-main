from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from blogs.models import Blog, Category
from django.contrib.auth.decorators import login_required

from .forms import AddUserForm, BlogPostForm, CategoryForm, EditUserForm
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User


@login_required(login_url='login')
def dashboard(request):
    category_count = Category.objects.count()
    if request.user.is_superuser:
        blogs_count = Blog.objects.count()
    else:
        blogs_count = Blog.objects.filter(author=request.user).count()

    context = {
        'category_count': category_count,
        'blogs_count': blogs_count,
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required(login_url='login')
def categories(request):
    categories = Category.objects.all()
    if not request.user.is_superuser:
        categories = categories.filter(author=request.user)
    return render(request, 'dashboard/categories.html', {'categories': categories})


@login_required(login_url='login')
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('categories')
    else:
        form = CategoryForm(user=request.user)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/add_category.html', context)


@login_required(login_url='login')
def edit_category(request, pk):
    categories = Category.objects.all()
    if not request.user.is_superuser:
        categories = categories.filter(author=request.user)
    category = get_object_or_404(categories, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('categories')
    else:
        form = CategoryForm(instance=category, user=request.user)
    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'dashboard/edit_category.html', context)


@login_required(login_url='login')
def delete_category(request, pk):
    categories = Category.objects.all()
    if not request.user.is_superuser:
        categories = categories.filter(author=request.user)
    category = get_object_or_404(categories, pk=pk)
    if (
        not request.user.is_superuser
        and Blog.objects.filter(category=category).exclude(author=request.user).exists()
    ):
        messages.error(
            request,
            'This category is used by another writer and cannot be deleted.',
        )
        return redirect('categories')
    category.delete()
    return redirect('categories')


@login_required(login_url='login')
def posts(request):
    posts = Blog.objects.all()
    if not request.user.is_superuser:
        posts = posts.filter(author=request.user)
    posts = posts.select_related('category', 'author')
    context = {
        'posts': posts,
    }
    return render(request, 'dashboard/posts.html', context)


@login_required(login_url='login')
def add_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            post = form.save(commit=False) # temporarily saving the form
            post.author = request.user
            post.save()
            title = form.cleaned_data['title']
            post.slug = slugify(title) + '-'+str(post.id)
            post.save()
            return redirect('posts')
        else:
            print('form is invalid')
            print(form.errors)
    else:
        form = BlogPostForm(user=request.user)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/add_post.html', context)


@login_required(login_url='login')
def edit_post(request, pk):
    posts = Blog.objects.all()
    if not request.user.is_superuser:
        posts = posts.filter(author=request.user)
    post = get_object_or_404(posts, pk=pk)
    if request.method == 'POST':
        form = BlogPostForm(
            request.POST,
            request.FILES,
            instance=post,
            user=request.user,
        )
        if form.is_valid():
            post = form.save()
            title = form.cleaned_data['title']
            post.slug = slugify(title) + '-'+str(post.id)
            post.save()
            return redirect('posts')
    else:
        form = BlogPostForm(instance=post, user=request.user)
    context = {
        'form': form,
        'post': post
    }
    return render(request, 'dashboard/edit_post.html', context)


@login_required(login_url='login')
def delete_post(request, pk):
    posts = Blog.objects.all()
    if not request.user.is_superuser:
        posts = posts.filter(author=request.user)
    post = get_object_or_404(posts, pk=pk)
    post.delete()
    return redirect('posts')


def users(request):
    users = User.objects.all()
    context = {
        'users': users,
    }
    return render(request, 'dashboard/users.html', context)


def add_user(request):
    if request.method == 'POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users')
        else:
            print(form.errors)
    form = AddUserForm()
    context = {
        'form': form,
    }
    return render(request, 'dashboard/add_user.html', context)


def edit_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('users')
    form = EditUserForm(instance=user)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/edit_user.html', context)


def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    return redirect('users')