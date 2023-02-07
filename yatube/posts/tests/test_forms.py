import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовый текст',
        )
        cls.author = User.objects.create_user(username='author')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_author_create_post(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(
            response,
            reverse(
                'posts:profile', kwargs={'username': self.author.username}
            )
        )
        self.assertTrue(
            Post.objects.filter(
                text='Текст поста',
                group=self.group,
                author=self.author,
                image='posts/small.gif',
            ).exists()
        )

    def test_author_edit_post(self):
        post = Post.objects.create(
            text='Текст поста',
            group=self.group,
            author=self.author,
        )
        form_data = {
            'text': 'Текст поста после редактирования',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:edit',
                args=[post.id],
            ),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail', kwargs={'post_id': post.id}
            )
        )
        self.assertTrue(
            Post.objects.filter(
                text='Текст поста после редактирования',
                group=self.group,
                author=self.author,
            ).exists()
        )

    def test_auth_comment(self):
        comment_count = Comment.objects.count()
        form_data = {
            'post': self.post.id,
            'author': self.author,
            'text': 'комментарий',
        }
        response = self.authorized_client.post(reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.id}
        ), data=form_data, follow=True,
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='комментарий',
                post=self.post,
                author=self.author,
            ).exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_non_auth_comment(self):
        comment_count = Comment.objects.count()
        form_data = {
            'post': self.post.id,
            'author': self.author,
            'text': 'комментарий',
        }
        response = self.guest_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        redirect = reverse('login') + '?next=' + reverse(
            'posts:add_comment', kwargs={'post_id': self.post.id}
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, redirect)
        self.assertEqual(Comment.objects.count(), comment_count)
