from django.contrib.messages import get_messages

from .base import UnitTest, reverse

from dashboard.models import Post, WebLink, UserProfile


class MixinsTest(UnitTest):

    def setUp(self):
        super(MixinsTest, self).setUp()
        self.author = UserProfile.objects.get(user=self.user)
        Post.objects.create(title='test', overview='texte', author=self.author)
        WebLink.objects.create(title='test', url='http://test.com/', type='AUTRES', description='test')

    def test_Login_ajax_mixin(self):
        """
        Login user through BSModalLoginView.
        """

        # First post request = ajax request checking if form in view is valid
        response = self.client.post(
            reverse('dashboard:login'),
            data={
                'username': 'toto',
                # Wrong value
                'password': 'wrong_password'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Form has errors
        self.assertTrue(response.context_data['form'].errors)
        # No redirection
        self.assertEqual(response.status_code, 200)
        # User is anonymous
        self.assertTrue(response.wsgi_request.user.is_anonymous)

        # Second post request = non-ajax request logging the user in
        response = self.client.post(
            reverse('dashboard:login'),
            data={
                'username': 'toto',
                'password': 'totopassword'
            }
        )

        # Redirection
        self.assertRedirects(response, reverse('dashboard:charts'), status_code=302)
        # User is authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_create_post_ajax_mixin(self):
        """
        Create Post throught BSModalCreateView.
        """
        self.add_perms_user(Post, 'add_post')
        self.login()

        # First post request = ajax request checking if form in view is valid
        response = self.client.post(
            reverse('dashboard:create_post'),
            data={
                'title': 'test1',
                'overview': 'texte',
                'author': self.author.id,
            },
        )
        # Redirection
        self.assertRedirects(response, reverse('index'), status_code=302)
        # Object is created
        posts = Post.objects.all()
        self.assertEqual(posts.count(), 2)

    def test_update_post_ajax_mixin(self):
        """
        Update Post throught BSModalCreateView.
        """
        self.add_perms_user(Post, 'change_post')
        self.login()

        # Update object through BSModalUpdateView
        post = Post.objects.first()
        response = self.client.post(
            reverse('dashboard:update_post', kwargs={'pk': post.pk}),
            data={
                'title': 'test2',
                'overview': 'texte',
                'author': self.author.id,
            }
        )
        # redirection
        self.assertRedirects(response, reverse('index'), status_code=302)
        # Object is updated
        post = Post.objects.first()
        self.assertEqual(post.title, 'test2')

    def test_Delete_post_ajax_mixin(self):
        """
        Delete object through BSModalDeleteView.
        """
        self.add_perms_user(Post, 'delete_post')
        self.login()

        # Request to delete view passes message to the response
        post = Post.objects.first()
        response = self.client.post(reverse('dashboard:delete_post', kwargs={'pk': post.pk}))
        messages = get_messages(response.wsgi_request)
        self.assertEqual(len(messages), 1)

    def test_create_weblink_ajax_mixin(self):
        """
        Create web link throught BSModalCreateView.
        """
        self.add_perms_user(WebLink, 'add_weblink')
        self.login()

        # First post request = ajax request checking if form in view is valid
        response = self.client.post(
            reverse('dashboard:create_weblink'),
            data={
                'title': 'test1',
                'url': 'http://test1.com/',
                'type': 'AUTRES',
                'description': 'test1',
            },
        )
        # Redirection
        self.assertRedirects(response, reverse('index'), status_code=302)
        # Object is created
        links = WebLink.objects.all()
        self.assertEqual(links.count(), 2)

    def test_update_weblink_ajax_mixin(self):
        """
        Update web link throught BSModalCreateView.
        """
        self.add_perms_user(WebLink, 'change_weblink')
        self.login()

        # Update object through BSModalUpdateView
        link = WebLink.objects.first()
        response = self.client.post(
            reverse('dashboard:update_weblink', kwargs={'pk': link.pk}),
            data={
                'title': 'test2',
                'url': 'http://test1.com/',
                'type': 'AUTRES',
                'description': 'test1',
            },
        )
        # redirection
        self.assertRedirects(response, reverse('index'), status_code=302)
        # Object is updated
        link = WebLink.objects.first()
        self.assertEqual(link.title, 'test2')
