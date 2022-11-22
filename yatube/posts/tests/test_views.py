import shutil
import tempfile
from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from posts.models import Post, Group, User, Comment, Follow
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
TEST_ID_100 = 100


class PostModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Artyom')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',)
        cls.post = Post.objects.create(
            id=TEST_ID_100,
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'Artyom'}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': TEST_ID_100}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': TEST_ID_100}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        post_list = response.context.get('page_obj').object_list
        post_list_expected = list(Post.objects.all())
        self.assertEqual(post_list, post_list_expected)

    def test_group_list_shows_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        post_list = response.context.get('page_obj').object_list
        post_list_expected = list(Post.objects.filter(group=self.group))
        self.assertEqual(post_list, post_list_expected)

    def test_profile_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Artyom'})
        )
        post_list = response.context.get('page_obj').object_list
        post_list_expected = list(Post.objects.filter(author=self.user))
        self.assertEqual(post_list, post_list_expected)

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом:"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': TEST_ID_100})
        )
        post = response.context.get('post')
        post_list_expected = Post.objects.get(id=TEST_ID_100)
        self.assertEqual(post, post_list_expected)

    def test_post_edit_correct_context(self):
        """Шаблон post_create имеет форму с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': TEST_ID_100})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for field, expected in form_fields.items():
            with self.subTest():
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, expected)

    def test_create_post_correct_context(self):
        """Шаблон create_post имеет форму с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for field, expected in form_fields.items():
            with self.subTest():
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Artyom')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',)

        posts_list = []
        for i in range(13):
            posts_list.append(Post(
                text=f'Текстовый текст {i}',
                author=cls.user,
                group=cls.group,
            ))
        cls.post = Post.objects.bulk_create(posts_list)

    def setUp(self):
        self.user = PaginatorViewsTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_first_page_contains_ten_records(self):
        """Проверка, паджинатор выводит 10 записей на страницу index"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_two_records(self):
        """Проверка, паджинатор выводит 4 записи на 2ю страницу index"""
        response = self.authorized_client.get(
            (reverse('posts:index') + '?page=2')
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_first_page_contains_ten_records(self):
        """Проверка, паджинатор выводит 10 записей на страницу group_list"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_second_page_contains_two_records(self):
        """Проверка, паджинатор выводит 4 записи на 2ю страницу group_list"""
        response = self.authorized_client.get(
            (reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
            + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_contains_ten_records(self):
        """Проверка, паджинатор выводит 10 записей на страницу profile"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Artyom'})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page_contains_two_records(self):
        """Проверка, паджинатор выводит 4 записи на 2ю страницу profile"""
        response = self.authorized_client.get(
            (
                reverse('posts:profile', kwargs={'username': 'Artyom'})
                + '?page=2'
            )
        )
        self.assertEqual(len(response.context['page_obj']), 3)


class PostRelatedGroupTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Artyom')
        cls.group1 = Group.objects.create(
            title='Тестовая группа1',
            slug='test-slug1',
            description='Тестовое описание1',)
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание2',)
        cls.post1 = Post.objects.create(
            id=TEST_ID_100,
            text='Тестовый пост1',
            author=cls.user,
            group=cls.group1,)

    def setUp(self):
        self.user = PostRelatedGroupTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_created_post_appears_on_related_pages(self):
        """
        При создании поста с укзанием группы он появляется на связанных
        с ним страницах
        """
        url_list = {
            'posts:index': None,
            'posts:group_list': {'slug': 'test-slug1'},
            'posts:profile': {'username': 'Artyom'},
        }

        for key, value in url_list.items():
            with self.subTest():
                response = self.authorized_client.get(
                    reverse(key, kwargs=value)
                )
                expected_post = Post.objects.get(id=TEST_ID_100)
                self.assertContains(response, expected_post)

    def test_no_created_post_on_non_related_pages(self):
        """
        При создании поста с укзанием группы он не появляется на
        не связанных с ним страницах
        """
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug2'})
        )
        post_100 = Post.objects.get(id=TEST_ID_100)
        self.assertNotContains(response, post_100)


# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ShowPicturesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Для тестирования загрузки изображений
        # берём байт-последовательность картинки,
        # состоящей из двух пикселей: белого и чёрного
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

        cls.author = User.objects.create(username='Artyom')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group,
            image=uploaded,
        )
        # создаем тестовую запись с картинкой
        cls.post_with_picture = Post.objects.create(
            text='Text and picture',
            author=cls.author,
            group=cls.group,
            image=uploaded,
        )
        # создаем тестовую запись без картинки
        cls.post_without_pic = Post.objects.create(
            text='Text and all',
            author=cls.author,
            group=cls.group
        )
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок и
        # файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pictures_on_pages_list_posts(self):
        '''Проверка передачи картинки в context index/group_list/profile'''
        reverse_context = {
            reverse('posts:index'): Post.objects.all(),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                Group.objects.get(slug='group').posts.all(),
            reverse('posts:profile', kwargs={'username':
                    self.author.username}):
                        User.objects.get(username='Artyom').posts.all()
        }
        for adress, passed_posts in reverse_context.items():
            with self.subTest(adress=adress):
                nums_passed_posts = passed_posts.count()
                response = self.authorized_author.get(adress)
                objs_on_page = list(response.context['page_obj'].object_list)
                self.assertEqual(nums_passed_posts, len(objs_on_page))

    def test_picture_on_page_post_detail(self):
        '''Проверка передачи картинки в context post_detail'''
        passed_post = self.post_with_picture
        adress = reverse(
            'posts:post_detail', kwargs={'post_id': passed_post.id})
        response = self.authorized_author.get(adress)
        self.assertEqual(passed_post.image, response.context['post'].image)

    def test_comment_in_page_detail_context(self):
        """Комментарии передаются в контекст страницы page_detail
        авторизованным пользователем"""
        response = self.authorized_author.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'}))
        first_object = response.context['post']
        comment_0 = first_object.comments
        self.assertEqual(comment_0, self.post.comments)

    def test_comment_in_correct_page(self):
        """Комментарий появляется на нужной странице"""
        form_data = {
            'text': 'Добавил комментарий',
        }
        self.authorized_author.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True)
        self.assertTrue(Comment.objects.filter(id=self.post.id).exists())


class CacheViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_author'),
            text='Тестовая запись')

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_cache_index(self):
        """Тест кэширования страницы index.html"""
        initial_state = self.authorized_client.get(reverse('posts:index'))
        post = Post.objects.get(pk=1)
        post.text = 'Измененная тестовая запись'
        post.save()
        changed_state = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(initial_state.content, changed_state.content)
        cache.clear()
        changed_state_2 = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(initial_state.content, changed_state_2.content)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_follower = User.objects.create_user(
            username='user_follower')
        cls.author_following = User.objects.create_user(
            username='author_following')
        cls.post = Post.objects.create(
            author=cls.author_following,
            text='Тестирование подписок/отписок',
        )

    def setUp(self):
        self.client_user_follower = Client()
        self.client_author_following = Client()
        self.client_user_follower.force_login(self.user_follower)
        self.client_author_following.force_login(self.author_following)

    def test_auth_user_follow(self):
        """Авторизованный пользователь может подписываться на других
        пользователей"""
        follow_count = Follow.objects.count()
        self.client_user_follower.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.author_following.username}))
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_auth_user_unfollow(self):
        """Авторизованный пользователь может удалять подписки на других"""
        self.client_user_follower.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.author_following.username}))
        follow_count = Follow.objects.count()
        self.client_user_follower.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.author_following.username}))
        self.assertEqual(Follow.objects.count(), follow_count - 1)

    def test_subscribe_feed(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех,
        кто не подписан"""
        post = self.post
        Follow.objects.create(
            user=self.user_follower,
            author=self.author_following
        )
        response = self.client_user_follower.get(
            reverse('posts:follow_index'))
        obj = response.context['page_obj'].object_list
        self.assertIn(post, obj)
        response = self.client_author_following.get(
            reverse('posts:follow_index'))
        obj = response.context['page_obj'].object_list
        self.assertNotIn(post, obj)
