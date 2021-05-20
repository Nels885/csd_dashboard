from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from utils.django.decorators import group_required


class DjangoDecoratorTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='foo', password='bar')
        self.group = Group.objects.create(name='test')
        self.factory = RequestFactory()

    def test_group_required_pass(self):
        self.user.groups.add(self.group)
        @group_required('test')
        def a_view(request):
            return HttpResponse()
        request = self.factory.get('/foo')
        request.user = self.user
        resp = a_view(request)
        self.assertEqual(resp.status_code, 200)
