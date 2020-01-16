from django.test import TestCase
from django.urls import reverse


class DemoTestCase(TestCase):

    def test_animations_page(self):
        response = self.client.get(reverse('demo:animation'))
        self.assertEqual(response.status_code, 200)

    def test_blank_page(self):
        response = self.client.get(reverse('demo:blank'))
        self.assertEqual(response.status_code, 200)

    def test_border_page(self):
        response = self.client.get(reverse('demo:border'))
        self.assertEqual(response.status_code, 200)

    def test_buttons_page(self):
        response = self.client.get(reverse('demo:buttons'))
        self.assertEqual(response.status_code, 200)

    def test_cards_page(self):
        response = self.client.get(reverse('demo:cards'))
        self.assertEqual(response.status_code, 200)

    def test_charts_page(self):
        response = self.client.get(reverse('demo:charts'))
        self.assertEqual(response.status_code, 200)

    def test_colors_page(self):
        response = self.client.get(reverse('demo:colors'))
        self.assertEqual(response.status_code, 200)

    def test_password_page(self):
        response = self.client.get(reverse('demo:password'))
        self.assertEqual(response.status_code, 200)

    def test_other_page(self):
        response = self.client.get(reverse('demo:other'))
        self.assertEqual(response.status_code, 200)

    def test_register_page(self):
        response = self.client.get(reverse('demo:register'))
        self.assertEqual(response.status_code, 200)

    def test_tables_page(self):
        response = self.client.get(reverse('demo:tables'))
        self.assertEqual(response.status_code, 200)
