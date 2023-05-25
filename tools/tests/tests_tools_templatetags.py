from django.template import Context, Template

from dashboard.tests.base import UnitTest

from tools.models import ThermalChamber


class ToolsTemplateTagsTest(UnitTest):

    def setUp(self):
        super(ToolsTemplateTagsTest, self).setUp()
        self.tc = ThermalChamber.objects.create(
            operating_mode='CHAUD', start_time='1970-07-17 12:12:00+00:00', stop_time='1970-07-17 14:14:00+00:00',
            created_by=self.user
        )

    def test_past_time(self):
        context = Context({'test': None})
        template_to_render = Template(
            '{% load tools_extras %}'
            '{{ test|past_time }}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('---', rendered_template)

    def test_usage_time(self):
        context = Context({'test': None})
        template_to_render = Template(
            '{% load tools_extras %}'
            '{{ test|usage_time }}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('---', rendered_template)

        context = Context({'test': self.tc})
        rendered_template = template_to_render.render(context)
        self.assertInHTML('2:02:00', rendered_template)

    def test_suptech_msg(self):
        # If test is valid
        context = Context({'test': "{'msg': 'test'}"})
        template_to_render = Template(
            '{% load tools_extras %}'
            '{{ test|suptech_msg }}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('test', rendered_template)

        # If test is not valid
        context = Context({'test': ''})
        template_to_render = Template(
            '{% load tools_extras %}'
            '{{ test|suptech_msg }}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('', rendered_template)

    def test_suptech_type(self):
        # If test is valid
        context = Context({'test': "{'type': 'test'}"})
        template_to_render = Template(
            '{% load tools_extras %}'
            '{{ test|suptech_type }}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('Test:', rendered_template)

        # If test is not valid
        context = Context({'test': ''})
        template_to_render = Template(
            '{% load tools_extras %}'
            '{{ test|suptech_type }}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('Message:', rendered_template)
