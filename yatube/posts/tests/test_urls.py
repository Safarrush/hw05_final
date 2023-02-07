from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовый текст',
        )
        cls.user = User.objects.create_user(username='auth')
        cls.author = User.objects.create_user(username='author')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.client_author = Client()
        self.client_author.force_login(self.author)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': 'test_slug'
            }): ('posts/group_list.html'),
            reverse('posts:profile', kwargs={
                'username': 'auth'
            }): ('posts/profile.html'),
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.id
            }): ('posts/post_detail.html'),
            reverse('posts:post_create'): ('posts/create_post.html'),
            reverse('posts:edit', kwargs={
                'post_id': self.post.id
            }): ('posts/create_post.html'),
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.client_author.get(address)
                self.assertTemplateUsed(response, template)

    def test_unauthorised_user(self):
        fields = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_list', kwargs={
                'slug': 'test_slug'}): HTTPStatus.OK,
            reverse('posts:profile', kwargs={
                'username': 'auth'}): HTTPStatus.OK,
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.id
            }): HTTPStatus.OK,
        }
        for url, response_code in fields.items():
            with self.subTest(url=url):
                status_code = self.guest_client.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_edit_post_page(self):
        """Страница редактирования поста доступна только автору."""
        response = self.client_author.get(reverse(
            'posts:edit', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_none_author(self):
        response = self.authorized_client.get(
            reverse('posts:edit', kwargs={
                'post_id': self.post.id}), follow=True
        )
        self.assertRedirects(response, (reverse(
            'posts:post_detail', kwargs={
                'post_id': self.post.id})))

    def test_about_url_exists_at_desired_location(self):
        """ Несуществующая страница выдает ошибку 404."""
        response = self.guest_client.get(reverse('posts:group_list', kwargs={
            'slug': 'none_page'}))
        self.assertEqual(response.status_code, 404)

    def test_create_url_exists_at_desired_location(self):
        """Страница create доступна только авторизованному пользователю."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
