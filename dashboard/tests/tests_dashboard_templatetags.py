from django.template import Context, Template
from django.contrib.auth.models import Group

from dashboard.tests.base import UnitTest


class DashboardTemplateTagsTest(UnitTest):

    def setUp(self):
        super(DashboardTemplateTagsTest, self).setUp()
        group_1 = Group.objects.create(name="group_1")
        group_2 = Group.objects.create(name="group_2")
        self.user.groups.add(group_1, group_2)
        self.user.save()

    def test_has_group(self):
        context = Context({'user': self.user})
        template_to_render = Template(
            '{% load user_tags %}'
            '{{ user|has_group:"group_1" }}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('True', rendered_template)

    def test_has_groups(self):
        context = Context({'user': self.user})
        template_to_render = Template(
            '{% load user_tags %}'
            '{{ user|has_groups:"group" }}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('True', rendered_template)
