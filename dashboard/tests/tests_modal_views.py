from django.contrib.auth.models import User, Group
from django.contrib.messages import get_messages

from .base import UnitTest, reverse, UserProfile

from dashboard.models import Post
from squalaetp.models import Xelon
from tools.models import TagXelon


class MixinsTest(UnitTest):

    def setUp(self):
        super(MixinsTest, self).setUp()
        xelon = Xelon.objects.create(numero_de_dossier='A123456789', vin=self.vin, modele_produit='produit',
                                     modele_vehicule='peugeot')
        user = User.objects.get(username='toto')
        user.groups.add(Group.objects.create(name="technician"))
        user.save()
        self.author = UserProfile.objects.get(user=user)
        Post.objects.create(title='test', overview='texte', author=self.author)
        self.xelonId = str(xelon.id)

    def test_TagXelonAjaxMixin(self):
        """
        Create TagXelon through BSModalCreateView.
        """
        self.login()

        # First post request = ajax request checking if form in view is valid
        response = self.client.post(
            reverse('tools:tag-xelon'),
            data={
                'xelon': 'wrong_xelon',
                'comments': ''
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Form has errors
        self.assertTrue(response.context_data['form'].errors)
        # No redirection
        self.assertEqual(response.status_code, 200)
        # Object is not created
        tags = TagXelon.objects.all()
        self.assertEqual(tags.count(), 0)

        # Second post request = non-ajax request creating an object
        response = self.client.post(
            reverse('tools:tag-xelon'),
            data={
                'xelon': 'A123456789',
                'comments': ''
            }
        )

        # redirection
        self.assertEqual(response.status_code, 302)
        # Object is not created
        tags = TagXelon.objects.all()
        self.assertEqual(tags.count(), 1)

    def test_LoginAjaxMixin(self):
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

    def test_PostAjaxMixin(self):
        """
        Create Post throught BSModalCreateView.
        """
        self.login()

        # Update object through BSModalUpdateView
        post = Post.objects.first()
        response = self.client.post(
            reverse('dashboard:update-post', kwargs={'pk': post.pk}),
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

    def test_DeleteMessageMixin(self):
        """
        Delete object through BSModalDeleteView.
        """
        self.login()
        # Request to delete view passes message to the response
        post = Post.objects.first()
        response = self.client.post(reverse('dashboard:delete-post', kwargs={'pk': post.pk}))
        messages = get_messages(response.wsgi_request)
        self.assertEqual(len(messages), 1)
