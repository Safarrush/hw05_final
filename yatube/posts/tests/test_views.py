import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовый текст',
        )
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): ('posts/index.html'),
            reverse('posts:group_list', kwargs={
                'slug': 'test_slug'
            }): ('posts/group_list.html'),
            reverse('posts:profile', kwargs={
                'username': 'auth'
            }): ('posts/profile.html'),
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.id
            }): ('posts/post_detail.html'),
            reverse('posts:edit', kwargs={
                'post_id': self.post.id
            }): ('posts/create_post.html'),
            reverse('posts:post_create'): ('posts/create_post.html'),
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_info(self, post):
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group.id, self.post.group.id)

    def test_index_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        single_post = response.context['page_obj'][0]
        self.check_info(single_post)
        self.assertEqual(single_post.image, self.post.image)

    def test_group_list_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test_slug'}))
        single_post = response.context['page_obj'][0]
        self.assertEqual(response.context['group'], self.group)
        self.check_info(single_post)
        self.assertEqual(single_post.image, self.post.image)

    def test_profile_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'auth'}))
        single_post = response.context['page_obj'][0]
        self.check_info(single_post)
        self.assertEqual(single_post.image, self.post.image)
        self.assertEqual(response.context['author'], self.user)

    def test_detail_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        comment_count = Comment.objects.count()
        form_data = {
            'post': self.post.id,
            'author': self.user,
            'text': 'комментарий',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        single_post = response.context['post']
        self.assertEqual(single_post.image, self.post.image)
        self.check_info(single_post)

    def test_create_show_correct_context(self):
        templates_pages_names = {
            reverse('posts:post_create'),
            reverse('posts:edit', kwargs={'post_id': self.post.id}),
        }
        for template in templates_pages_names:
            with self.subTest(template=template):
                response = self.authorized_client.get(template)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], PostForm)

    def test_cache(self):
        posts = Post.objects.create(
            text='Кэш',
            author=self.user,
        )
        response = self.authorized_client.get(
            reverse('posts:index')).content
        posts.delete()
        response_delete = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertEqual(response, response_delete)
        cache.clear()
        response_clear = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(response, response_clear)

    def test_error(self):
        response = self.authorized_client.get('/non_page/')
        template = 'core/404.html'
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, template)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='auth',
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовый текст',
        )
        posts = [Post(
            text=f'Текст {i}',
            author=cls.user,
            group=cls.group,
        ) for i in range(13)
        ]
        cls.post = Post.objects.bulk_create(posts)

    def setUp(self):
        self.client = Client()

    def test_first_page_contains_ten_records(self):
        post_first_page = 10
        post_second_page = 3
        templates_pages_names = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'}),
        }
        for reversing in templates_pages_names:
            with self.subTest(reversing=reversing):
                self.assertEqual(len(self.client.get(reversing).context.get(
                    'page_obj')), post_first_page
                )
                self.assertEqual(len(
                    self.client.get(
                        reversing + '?page=2').context.get(
                            'page_obj')), post_second_page)


class FollowNest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='auth',
        )
        cls.post = Post.objects.create(
            text='Подписка',
            author=cls.user,
        )
        cls.follower = User.objects.create(
            username='follower',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)

    def test_follow_authorized(self):
        count_follow = Follow.objects.count()
        new_author = User.objects.create(username='new_author')
        self.authorized_client.post(reverse(
            'posts:profile_follow', kwargs={'username': new_author}
        )
        )
        self.assertIs(
            Follow.objects.filter(
                user=self.user, author=new_author
            ).exists(), True
        )
        self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': self.user}
        )
        )
        self.assertEqual(Follow.objects.count(), count_follow + 1)

    def test_post_none_likes(self):
        new_author = User.objects.create(username='new_author')
        new_client = User.objects.create(username='new_user')
        self.follower_client.force_login(new_client)
        self.assertIs(
            Follow.objects.filter(
                user=new_client, author=new_author
            ).exists(), False
        )

    def test_unfollow(self):
        Follow.objects.create(
            user=self.user,
            author=self.follower,
        )
        count_follow = Follow.objects.count()
        self.authorized_client.post(reverse(
            'posts:profile_unfollow', kwargs={'username': self.follower}
        )
        )
        self.assertEqual(Follow.objects.count(), count_follow - 1)

    def test_follow_posts(self):
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response.context['page_obj']), 0)
