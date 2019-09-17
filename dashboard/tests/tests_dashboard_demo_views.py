from django.test import TestCase
from django.urls import reverse


class DashboardDemoTestCase(TestCase):

    def test_animations_page(self):
        response = self.client.get(reverse('dashboard:animation'))
        self.assertEqual(response.status_code, 200)

    def test_blank_page(self):
        response = self.client.get(reverse('dashboard:blank'))
        self.assertEqual(response.status_code, 200)

    def test_border_page(self):
        response = self.client.get(reverse('dashboard:border'))
        self.assertEqual(response.status_code, 200)

    def test_buttons_page(self):
        response = self.client.get(reverse('dashboard:buttons'))
        self.assertEqual(response.status_code, 200)

    def test_cards_page(self):
        response = self.client.get(reverse('dashboard:cards'))
        self.assertEqual(response.status_code, 200)

    def test_charts_page(self):
        response = self.client.get(reverse('dashboard:charts'))
        self.assertEqual(response.status_code, 200)

    def test_colors_page(self):
        response = self.client.get(reverse('dashboard:colors'))
        self.assertEqual(response.status_code, 200)

    def test_password_page(self):
        response = self.client.get(reverse('dashboard:password'))
        self.assertEqual(response.status_code, 200)

    def test_other_page(self):
        response = self.client.get(reverse('dashboard:other'))
        self.assertEqual(response.status_code, 200)

    # def test_register_page(self):
    #     response = self.client.get(reverse('dashboard:register'))
    #     self.assertEqual(response.status_code, 200)

    def test_tables_page(self):
        response = self.client.get(reverse('dashboard:tables'))
        self.assertEqual(response.status_code, 200)
