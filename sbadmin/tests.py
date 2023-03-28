from django.urls import reverse
from django.utils.translation import gettext as _

from dashboard.tests.base import UnitTest

from prog.models import Raspeedi, UnlockProduct, ToolStatus
from squalaetp.models import Xelon


class SbadminTestCase(UnitTest):

    def setUp(self):
        super(SbadminTestCase, self).setUp()

    def test_get_progress_view(self):
        response = self.client.get(reverse('progress'))
        self.assertEqual(response.status_code, 200)

    def test_download_file_view(self):
        response = self.client.get(reverse('download'))
        self.assertEqual(response.status_code, 404)
