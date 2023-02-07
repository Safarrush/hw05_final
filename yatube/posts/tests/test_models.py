from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовый текст',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        self.assertEqual(self.post.text[:15], str(self.post))

    def test_post_verbose_name(self):
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                verbose_name = self.post._meta.get_field(field).verbose_name
                self.assertEqual(verbose_name, expected_value)

    def test_post_help_text(self):
        field_help_text = {
            'text': 'Текст поста',
            'group': 'Группа поста',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                help_text = self.post._meta.get_field(field).help_text
                self.assertEqual(help_text, expected_value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test_slug',
        )

    def test_group_str(self):
        self.assertEqual(self.group.title, str(self.group))

    def test_group_verbose_name(self):
        field_verboses = {
            'title': 'Заголовок',
            'slug': 'Слаг',
            'description': 'Записи группы',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                verbose_name = self.group._meta.get_field(field).verbose_name
                self.assertEqual(verbose_name, expected_value)
