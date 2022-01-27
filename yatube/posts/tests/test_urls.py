from django.test import Client, TestCase
from django.urls import reverse

from http import HTTPStatus

from ..models import Group, Post, User

USERNAME = 'tester'
SLUG = 'test-slug'
INDEX = reverse('posts:index')
GROUP = reverse('posts:group',
                kwargs={'slug': SLUG})
PROFILE = reverse('posts:profile',
                  kwargs={'username': USERNAME})
CREATE_POST = reverse('posts:post_create')

UNEXISTING = '/posts/unexisting/'


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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )

        cls.POST_DETAIL = reverse('posts:post_detail',
                                  kwargs={'post_id': cls.post.id})

        cls.EDITE_POST = reverse('posts:post_edit',
                                 kwargs={'post_id': cls.post.id})

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон для пользователя."""

        templates_url_names = [
            [INDEX, 'posts/index.html'],
            [GROUP, 'posts/group_list.html'],
            [PROFILE, 'posts/profile.html'],
            [self.POST_DETAIL, 'posts/post_detail.html'],
            [CREATE_POST, 'posts/create_post.html'],
            [self.EDITE_POST, 'posts/create_post.html'],
        ]
        for url, template in templates_url_names:
            with self.subTest(url=url):
                self.assertTemplateUsed(self.authorized_client.get(url), template)

    def test_urs_exists_at_desired_location_guest(self):
        """Страницы доступны любому пользователю."""
        templates_url_names = [
            [INDEX, self.guest_client.get(INDEX), HTTPStatus.OK],
            [GROUP, self.guest_client.get(GROUP), HTTPStatus.OK],
            [PROFILE, self.guest_client.get(PROFILE), HTTPStatus.OK],
            [self.POST_DETAIL, self.guest_client.get(self.POST_DETAIL), HTTPStatus.OK],
            [CREATE_POST, self.guest_client.get(CREATE_POST), HTTPStatus.FOUND],
            [CREATE_POST, self.authorized_client.get(CREATE_POST), HTTPStatus.OK],
            [self.EDITE_POST, self.authorized_client.get(self.EDITE_POST), HTTPStatus.OK],
            [self.EDITE_POST, self.guest_client.get(self.EDITE_POST), HTTPStatus.FOUND],
            [UNEXISTING, self.guest_client.get(UNEXISTING), HTTPStatus.NOT_FOUND],
            [UNEXISTING, self.authorized_client.get(UNEXISTING), HTTPStatus.NOT_FOUND]

        ]
        for url, user, answer in templates_url_names:
            # response_guest = self.guest_client.get(url)
            # response_authorized = self.authorized_client.get(url)
            with self.subTest(url=url):
                if answer == HTTPStatus.FOUND:
                    self.assertEqual(user.status_code,
                                     HTTPStatus.FOUND)
                    self.assertTrue(user, '/accounts/login/')
                elif answer == HTTPStatus.OK:
                    self.assertEqual(user.status_code,
                                     HTTPStatus.OK)
                elif answer == HTTPStatus.NOT_FOUND:
                    self.assertEqual(user.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_redirect(self):
        urls_names = [
            CREATE_POST,
            self.EDITE_POST
        ]
        for url in urls_names:
            with self.subTest(url=url):
                response_guest = self.guest_client.get(url)
                response_authorized = self.authorized_client.get(url)
                # self.assertTrue(response, '/accounts/login/')
                self.assertRedirects(response_guest, (f'/auth/login/?next={url}'))
                if url == HTTPStatus.FOUND:
                    self.assertRedirects(response_authorized, (f'/posts/{self.post.pk}/'))