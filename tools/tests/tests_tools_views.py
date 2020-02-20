from django.urls import reverse
from django.contrib.auth.models import User, Group

from dashboard.tests.base import UnitTest

from dashboard.models import CsdSoftware


class ToolsTestCase(UnitTest):

    def setUp(self):
        super(ToolsTestCase, self).setUp()
        self.form_data = {
            'jig': 'test', 'new_version': '1', 'link_download': 'test', 'status': 'En test',
        }
        user = User.objects.get(username='toto')
        user.groups.add(Group.objects.create(name="cellule"))
        user.save()

    def test_soft_list_page(self):
        response = self.client.get(reverse('tools:soft-list'))
        self.assertEqual(response.status_code, 200)

    def test_soft_add_page_is_disconnected(self):
        response = self.client.get(reverse('tools:soft-add'))
        self.assertRedirects(response, '/accounts/login/?next=/tools/soft/add/', status_code=302)

    def test_soft_add_page_is_connected(self):
        self.login()
        response = self.client.get(reverse('tools:soft-add'))
        self.assertEqual(response.status_code, 200)

    def test_soft_add_page_is_valid(self):
        self.login()
        old_soft = CsdSoftware.objects.count()
        response = self.client.post(reverse('tools:soft-add'), self.form_data)
        new_soft = CsdSoftware.objects.count()
        self.assertEqual(new_soft, old_soft + 1)
        self.assertEqual(response.status_code, 200)

    def test_tag_xelon_is_disconnected(self):
        response = self.client.get(reverse('tools:tag-xelon'))
        self.assertRedirects(response, '/accounts/login/?next=/tools/tag-xelon/', status_code=302)
