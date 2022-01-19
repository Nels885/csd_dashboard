from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils.translation import ugettext as _

from dashboard.tests.base import UnitTest

from volvo.models import SemRefBase, SemType, SemModel


class VolvoTestCase(UnitTest):

    def setUp(self):
        super(VolvoTestCase, self).setUp()

    def test_reman_ref_table_page(self):
        url = reverse('volvo:reman_ref_table')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        # Test if connected with permissions
        self.add_perms_user(SemRefBase, 'view_semrefbase')
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_sem_ref_table_page(self):
        url = reverse('reman:part_table')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
