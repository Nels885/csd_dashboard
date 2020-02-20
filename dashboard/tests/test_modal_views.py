from .base import UnitTest


class MixinsTest(UnitTest):

    def test_LoginAjaxMixin(self):
        """
        Login user through BSModalLoginView.
        """

        # First post request = ajax request checking if form in view is valid
        response = self.client.post(
            '/dashboard/login/',
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
            '/dashboard/login/',
            data={
                'username': 'toto',
                'password': 'totopassword'
            }
        )

        # Redirection
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/dashboard/charts/')
        # User is authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)
