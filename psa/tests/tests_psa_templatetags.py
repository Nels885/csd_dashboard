from django.template import Context, Template

from dashboard.tests.base import UnitTest

from psa.models import CorvetChoices


class PsaTemplateTagsTest(UnitTest):

    def test_get_corvet(self):
        context = Context({'test': '01'})
        template_to_render = Template(
            '{% load i18n corvet_tags %}'
            '{{ test|get_corvet:"DON_LIN_PROD" }}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('* 01 *', rendered_template)

        CorvetChoices.objects.create(key='01', value='new_test', column='DON_LIN_PROD')
        rendered_template = template_to_render.render(context)
        self.assertInHTML('new_test', rendered_template)
