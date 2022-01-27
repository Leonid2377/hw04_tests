from django.test import TestCase, Client
from django.urls import reverse

from ..models import User, Post, Group
from ..settings import NUMBER_POSTS_ON_PAGE

USERNAME = 'tester'
SLUG = 'test-slug'
SLUG_1 = 'test-slug_1'
INDEX = reverse('posts:index')
GROUP = reverse('posts:group',
                kwargs={'slug': SLUG})
GROUP_1 = reverse('posts:group',
                  kwargs={'slug': SLUG_1})
PROFILE = reverse('posts:profile',
                  kwargs={'username': USERNAME})


class PostUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug=SLUG,
            description='Тестовое описание',
        )
        cls.group_1 = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug_1',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )
        cls.POST_DETAIL = reverse('posts:post_detail',
                                  kwargs={'post_id': cls.post.id})

    def setUp(self):
        self.guest_client = Client()  # Гость
        self.user = self.user
        self.authorized_client = Client()  # Авторизованный
        self.authorized_client.force_login(self.user)

    def test_post_not_in_another_group(self):
        '''Проверяем что пост не в другой группе'''
        response = self.authorized_client.get(GROUP_1)
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_post_in_group(self):
        '''Проверяем что пост в нужной группе,
        появился на главной странице, '''
        responses = [
            [INDEX, 'page_obj'],
            [GROUP, 'page_obj'],
            [PROFILE, 'page_obj'],
            [self.POST_DETAIL, 'post'],
        ]
        for url, obj in responses:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                if obj == 'page_obj':
                    context = response.context[obj]
                    self.assertEqual(len(context), 1)
                    self.assertIn(self.post, response.context['page_obj'])
                    context = context[0]
                    for post in response.context[obj]:
                        self.assertEqual(post.group, self.group)
                        self.assertEqual(post.author, self.user)
                elif obj == 'post':
                    context = response.context['post']
                self.assertEqual(context.text, self.post.text)
                self.assertEqual(context.author, self.post.author)
                self.assertEqual(context.group, self.post.group)
                self.assertEqual(context.pk, self.post.pk)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester')
        cls.i = 15
        Post.objects.bulk_create([
            Post(
                text='Тестовый текст',
                author=cls.user,
            ) for i in range(cls.i)
        ])

    def test_first_page_contains_records(self):
        response = self.client.get(INDEX)
        self.assertEqual(len(response.context['page_obj']),
                         NUMBER_POSTS_ON_PAGE)

    def test_second_page_contains_records(self):
        response = self.client.get(f'{INDEX}?page=2')
        self.assertEqual(len(response.context['page_obj']),
                         NUMBER_POSTS_ON_PAGE - (self.i - 10))
