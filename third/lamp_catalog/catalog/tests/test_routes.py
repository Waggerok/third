from django.test import TestCase, Client
from django.urls import reverse
from ..models import Lamp

class RouteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.lamp = Lamp.objects.create(
            article='TEST001',
            brand='Test Brand',
            has_dimmer=True,
            power_watts=60,
            color='White',
            lamp_type='table',
            price=100.00,
            description='Test description'
        )

    def test_catalog_page(self):
        response = self.client.get(reverse('catalog:lamp_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/lamp_list.html')

    def test_lamp_detail_page(self):
        response = self.client.get(reverse('catalog:lamp_detail', args=[self.lamp.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/lamp_detail.html')

    def test_about_page(self):
        response = self.client.get(reverse('catalog:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/about.html') 