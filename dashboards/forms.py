from django import forms
from blogs.models import Blog, Category
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CategoryForm(forms.ModelForm):
    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if self.instance.pk is None:
            self.instance.author = user

    class Meta:
        model = Category
        fields = ('category_name',)

    def clean_category_name(self):
        category_name = self.cleaned_data['category_name']
        existing_categories = Category.objects.filter(
            author=self.user,
            category_name=category_name,
        )
        if self.instance.pk:
            existing_categories = existing_categories.exclude(pk=self.instance.pk)
        if existing_categories.exists():
            raise forms.ValidationError('You already have a category with this name.')
        return category_name


class BlogPostForm(forms.ModelForm):
    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        if not user.is_superuser:
            categories = categories.filter(author=user)
        self.fields['category'].queryset = categories

    class Meta:
        model = Blog
        fields = ('title', 'category', 'featured_image', 'short_description', 'blog_body', 'status', 'is_featured')


class AddUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')


class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')