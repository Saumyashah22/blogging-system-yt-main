from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Blog, Category


class PublicPostAccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='writer',
            password='password',
        )
        self.category = Category.objects.create(
            category_name='Stories',
            author=self.user,
        )
        self.post = Blog.objects.create(
            title='A published story',
            slug='a-published-story',
            category=self.category,
            author=self.user,
            featured_image='test.jpg',
            short_description='A short description',
            blog_body='The full story',
            status='Published',
            is_featured=True,
        )

    def test_guest_post_request_redirects_to_registration(self):
        response = self.client.get(reverse('blogs', args=[self.post.slug]))

        self.assertRedirects(response, reverse('register'))

    def test_guest_homepage_hides_category_bar(self):
        response = self.client.get(reverse('home'))

        self.assertNotContains(response, 'category-bar')

    def test_authenticated_user_can_open_post_and_see_category_bar(self):
        self.client.force_login(self.user)

        post_response = self.client.get(reverse('blogs', args=[self.post.slug]))
        home_response = self.client.get(reverse('home'))

        self.assertEqual(post_response.status_code, 200)
        self.assertContains(home_response, 'category-bar')
