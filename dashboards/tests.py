from django.contrib.auth.models import User
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase
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

    def test_dashboard_counts_shared_categories_and_only_current_users_posts(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.context['category_count'], 2)
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

    def test_post_form_offers_categories_shared_by_all_users(self):
        form = BlogPostForm(user=self.user, instance=self.post)

        self.assertEqual(
            set(form.fields['category'].queryset),
            {self.category, self.other_category},
        )

    def test_category_names_are_unique_case_insensitively_across_all_users(self):
        for duplicate_name in ('My category', '  MY CATEGORY  '):
            with self.subTest(category_name=duplicate_name):
                form = CategoryForm(
                    {'category_name': duplicate_name},
                    user=self.other_user,
                )

                self.assertFalse(form.is_valid())
                self.assertIn('category_name', form.errors)

        new_category_form = CategoryForm(
            {'category_name': '  Shared category  '},
            user=self.other_user,
        )
        self.assertTrue(new_category_form.is_valid(), new_category_form.errors)
        new_category = new_category_form.save()
        self.assertEqual(new_category.author, self.other_user)
        self.assertEqual(new_category.category_name, 'Shared category')

    def test_creator_cannot_delete_a_category_used_by_another_writer(self):
        shared_post = self.create_post(
            'Shared category post',
            'shared-category-post',
            self.category,
            self.other_user,
        )

        response = self.client.get(
            reverse('delete_category', args=[self.category.pk]),
            follow=True,
        )

        self.assertRedirects(response, reverse('categories'))
        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())
        self.assertTrue(Blog.objects.filter(pk=shared_post.pk).exists())
        self.assertContains(response, 'This category is used by another writer')

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


class SharedCategoryMigrationTests(TransactionTestCase):
    migrate_from = [('blogs', '0005_category_author')]
    migrate_to = [('blogs', '0006_shared_categories')]

    def setUp(self):
        super().setUp()
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        old_apps = executor.loader.project_state(self.migrate_from).apps
        User = old_apps.get_model('auth', 'User')
        Category = old_apps.get_model('blogs', 'Category')
        Blog = old_apps.get_model('blogs', 'Blog')

        first_user = User.objects.create(username='migration-writer-one')
        second_user = User.objects.create(username='migration-writer-two')
        first_category = Category.objects.create(
            category_name='Sports',
            author=first_user,
        )
        second_category = Category.objects.create(
            category_name='Sports',
            author=second_user,
        )
        Blog.objects.create(
            title='First sports story',
            slug='first-sports-story',
            category=first_category,
            author=first_user,
            featured_image='first.jpg',
            short_description='First story',
            blog_body='First story body',
        )
        Blog.objects.create(
            title='Second sports story',
            slug='second-sports-story',
            category=second_category,
            author=second_user,
            featured_image='second.jpg',
            short_description='Second story',
            blog_body='Second story body',
        )

        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_to)
        new_apps = executor.loader.project_state(self.migrate_to).apps
        self.Category = new_apps.get_model('blogs', 'Category')
        self.Blog = new_apps.get_model('blogs', 'Blog')

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_duplicate_categories_merge_without_losing_posts(self):
        category = self.Category.objects.get(category_name='Sports')
        posts = self.Blog.objects.filter(
            slug__in=['first-sports-story', 'second-sports-story'],
        )

        self.assertEqual(self.Category.objects.filter(category_name='Sports').count(), 1)
        self.assertEqual(posts.count(), 2)
        self.assertEqual(
            set(posts.values_list('category_id', flat=True)),
            {category.pk},
        )
