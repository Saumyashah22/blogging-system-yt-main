from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from blogs.models import Blog, Category
from .forms import BlogPostForm, CategoryForm


class DashboardOwnershipTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='writer', password='password')
        self.other_user = User.objects.create_user(
            username='other-writer',
            password='password',
        )
        self.category = Category.objects.create(
            category_name='My category',
            author=self.user,
        )
        self.other_category = Category.objects.create(
            category_name='Other category',
            author=self.other_user,
        )
        self.post = self.create_post(
            'My post',
            'my-post',
            self.category,
            self.user,
        )
        self.other_post = self.create_post(
            'Other post',
            'other-post',
            self.other_category,
            self.other_user,
        )
        self.client.force_login(self.user)

    @staticmethod
    def create_post(title, slug, category, author):
        return Blog.objects.create(
            title=title,
            slug=slug,
            category=category,
            author=author,
            featured_image='test.jpg',
            short_description='Description',
            blog_body='Body',
        )

    def test_dashboard_counts_only_current_users_content(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.context['category_count'], 1)
        self.assertEqual(response.context['blogs_count'], 1)

    def test_category_list_only_shows_current_users_categories(self):
        response = self.client.get(reverse('categories'))

        self.assertEqual(list(response.context['categories']), [self.category])
        self.assertContains(response, self.category.category_name)
        self.assertNotContains(response, self.other_category.category_name)

    def test_post_list_only_shows_current_users_posts(self):
        response = self.client.get(reverse('posts'))

        self.assertEqual(list(response.context['posts']), [self.post])

    def test_user_cannot_edit_another_users_category_or_post(self):
        category_response = self.client.get(
            reverse('edit_category', args=[self.other_category.pk])
        )
        post_response = self.client.get(
            reverse('edit_post', args=[self.other_post.pk])
        )

        self.assertEqual(category_response.status_code, 404)
        self.assertEqual(post_response.status_code, 404)

    def test_user_can_edit_their_own_category_and_post(self):
        category_response = self.client.get(
            reverse('edit_category', args=[self.category.pk])
        )
        post_response = self.client.get(reverse('edit_post', args=[self.post.pk]))

        self.assertEqual(category_response.status_code, 200)
        self.assertEqual(post_response.status_code, 200)

    def test_post_form_only_offers_current_users_categories(self):
        form = BlogPostForm(user=self.user, instance=self.post)

        self.assertEqual(
            list(form.fields['category'].queryset),
            [self.category],
        )

    def test_category_names_are_unique_per_user(self):
        form = CategoryForm(
            {'category_name': 'My category'},
            user=self.other_user,
        )

        self.assertTrue(form.is_valid(), form.errors)
        category = form.save()
        self.assertEqual(category.author, self.other_user)

        duplicate_form = CategoryForm(
            {'category_name': 'My category'},
            user=self.user,
        )
        self.assertFalse(duplicate_form.is_valid())

    def test_superuser_can_view_and_edit_every_users_content(self):
        admin = User.objects.create_superuser(
            username='admin',
            password='password',
            email='admin@example.com',
        )
        self.client.force_login(admin)

        dashboard_response = self.client.get(reverse('dashboard'))
        categories_response = self.client.get(reverse('categories'))
        posts_response = self.client.get(reverse('posts'))
        edit_category_response = self.client.get(
            reverse('edit_category', args=[self.other_category.pk])
        )
        edit_post_response = self.client.get(
            reverse('edit_post', args=[self.other_post.pk])
        )
        post_form = BlogPostForm(user=admin)

        self.assertEqual(dashboard_response.context['category_count'], 2)
        self.assertEqual(dashboard_response.context['blogs_count'], 2)
        self.assertEqual(
            set(categories_response.context['categories']),
            {self.category, self.other_category},
        )
        self.assertContains(categories_response, self.other_category.category_name)
        self.assertEqual(
            set(posts_response.context['posts']),
            {self.post, self.other_post},
        )
        self.assertContains(posts_response, self.other_post.title)
        self.assertEqual(edit_category_response.status_code, 200)
        self.assertEqual(edit_post_response.status_code, 200)
        self.assertEqual(
            set(post_form.fields['category'].queryset),
            {self.category, self.other_category},
        )

    def test_superuser_can_update_and_delete_other_users_content(self):
        admin = User.objects.create_superuser(
            username='admin',
            password='password',
            email='admin@example.com',
        )
        self.client.force_login(admin)

        category_response = self.client.post(
            reverse('edit_category', args=[self.other_category.pk]),
            {'category_name': 'Updated other category'},
        )
        post_response = self.client.post(
            reverse('edit_post', args=[self.other_post.pk]),
            {
                'title': 'Updated other post',
                'category': self.other_category.pk,
                'short_description': 'Updated description',
                'blog_body': 'Updated body',
                'status': 'Draft',
            },
        )

        self.assertEqual(category_response.status_code, 302)
        self.assertEqual(post_response.status_code, 302)
        self.other_category.refresh_from_db()
        self.other_post.refresh_from_db()
        self.assertEqual(self.other_category.category_name, 'Updated other category')
        self.assertEqual(self.other_post.title, 'Updated other post')
        self.assertEqual(self.other_post.author, self.other_user)

        post_delete_response = self.client.get(
            reverse('delete_post', args=[self.other_post.pk])
        )
        category_delete_response = self.client.get(
            reverse('delete_category', args=[self.other_category.pk])
        )

        self.assertEqual(post_delete_response.status_code, 302)
        self.assertEqual(category_delete_response.status_code, 302)
        self.assertFalse(Blog.objects.filter(pk=self.other_post.pk).exists())
        self.assertFalse(Category.objects.filter(pk=self.other_category.pk).exists())
