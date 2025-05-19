from django.test import TestCase
from ..models import Lamp

class ContentTests(TestCase):
    def setUp(self):
        # Create test lamps with different attributes
        self.lamp1 = Lamp.objects.create(
            article='A001',
            brand='Brand A',
            has_dimmer=True,
            power_watts=60,
            height_cm=30,
            color='White',
            lamp_type='table',
            price=100.00,
            description='Test description 1'
        )
        self.lamp2 = Lamp.objects.create(
            article='B002',
            brand='Brand B',
            has_dimmer=False,
            power_watts=40,
            height_cm=40,
            color='Black',
            lamp_type='floor',
            price=150.00,
            description='Test description 2'
        )
        self.lamp3 = Lamp.objects.create(
            article='C003',
            brand='Brand C',
            has_dimmer=True,
            power_watts=75,
            height_cm=50,
            color='Red',
            lamp_type='wall',
            price=200.00,
            description='Test description 3'
        )

    def test_alphabetical_ordering(self):
        lamps = Lamp.objects.order_by('brand')
        self.assertEqual(list(lamps), [self.lamp1, self.lamp2, self.lamp3])

    def test_price_ordering(self):
        lamps = Lamp.objects.order_by('price')
        self.assertEqual(list(lamps), [self.lamp1, self.lamp2, self.lamp3])

    def test_power_ordering(self):
        lamps = Lamp.objects.order_by('power_watts')
        self.assertEqual(list(lamps), [self.lamp2, self.lamp1, self.lamp3])

    def test_height_ordering(self):
        lamps = Lamp.objects.order_by('height_cm')
        self.assertEqual(list(lamps), [self.lamp1, self.lamp2, self.lamp3])

    def test_lamp_type_filtering(self):
        table_lamps = Lamp.objects.filter(lamp_type='table')
        self.assertEqual(list(table_lamps), [self.lamp1])

    def test_dimmer_filtering(self):
        dimmer_lamps = Lamp.objects.filter(has_dimmer=True)
        self.assertEqual(set(dimmer_lamps), {self.lamp1, self.lamp3}) 