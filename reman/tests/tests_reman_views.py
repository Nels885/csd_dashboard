from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group


class RemanTestCase(TestCase):

    def setUp(self):
        user = User.objects.create_user(username='toto', email='toto@bibi.com', password='totopassword')
        user.groups.add(Group.objects.create(name="cellule"))
        user.save()
        self.redirectUrl = reverse('index')

    def test_reman_table_page(self):
        response = self.client.get(reverse('reman:reman-table'))
        self.assertEqual(response.status_code, 200)

    def test_reman_create_page_is_disconnected(self):
        response = self.client.get(reverse('reman:new-folder'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/reman/add/')

    def test_reman_create_page_is_connected(self):
        self.client.login(username='toto', password='totopassword')
        response = self.client.get(reverse('reman:new-folder'))
        self.assertEqual(response.status_code, 200)
