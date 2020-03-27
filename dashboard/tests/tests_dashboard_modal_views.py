from django.contrib.messages import get_messages

from .base import UnitTest, reverse, UserProfile

from dashboard.models import Post


class MixinsTest(UnitTest):

    def setUp(self):
        super(MixinsTest, self).setUp()
        self.add_perms_user(Post, 'add_post', 'change_post', 'delete_post')
        self.add_group_user("technician")
        self.author = UserProfile.objects.get(user=self.user)
        Post.objects.create(title='test', overview='texte', author=self.author)

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
        self.login()
        # Request to delete view passes message to the response
        post = Post.objects.first()
        response = self.client.post(reverse('dashboard:delete_post', kwargs={'pk': post.pk}))
        messages = get_messages(response.wsgi_request)
        self.assertEqual(len(messages), 1)
