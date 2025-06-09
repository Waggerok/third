from django.test import TestCase, Client
from django.urls import reverse
from ..models import Lamp
from decimal import Decimal

class SortingTests(TestCase):
    def setUp(self):
        # Create test lamps with different values
        self.lamp1 = Lamp.objects.create(
            article='TEST001',
            brand='A Brand',
            has_dimmer=True,
            power_watts=60,
            height_cm=30,
            color='White',
            lamp_type='table',
            price=Decimal('1000.00'),
            small_wholesale_price=Decimal('900.00'),
            small_wholesale_quantity=5,
            large_wholesale_price=Decimal('800.00'),
            large_wholesale_quantity=10
        )
        
        self.lamp2 = Lamp.objects.create(
            article='TEST002',
            brand='B Brand',
            has_dimmer=False,
            power_watts=40,
            height_cm=40,
            color='Black',
            lamp_type='floor',
            price=Decimal('2000.00'),
            small_wholesale_price=Decimal('1800.00'),
            small_wholesale_quantity=5,
            large_wholesale_price=Decimal('1600.00'),
            large_wholesale_quantity=10
        )
        
        self.lamp3 = Lamp.objects.create(
            article='TEST003',
            brand='C Brand',
            has_dimmer=True,
            power_watts=80,
            height_cm=50,
            color='Red',
            lamp_type='wall',
            price=Decimal('1500.00'),
            small_wholesale_price=Decimal('1350.00'),
            small_wholesale_quantity=5,
            large_wholesale_price=Decimal('1200.00'),
            large_wholesale_quantity=10
        )

        self.client = Client()

    def test_sort_by_brand_ascending(self):
        """Test sorting by brand in ascending order"""
        response = self.client.get(reverse('catalog:lamp_list'), {'sort_by': 'brand', 'sort_order': 'asc'})
        lamps = response.context['lamps']
        self.assertEqual(list(lamps), [self.lamp1, self.lamp2, self.lamp3])

    def test_sort_by_brand_descending(self):
        """Test sorting by brand in descending order"""
        response = self.client.get(reverse('catalog:lamp_list'), {'sort_by': 'brand', 'sort_order': 'desc'})
        lamps = response.context['lamps']
        self.assertEqual(list(lamps), [self.lamp3, self.lamp2, self.lamp1])

    def test_sort_by_price_ascending(self):
        """Test sorting by price in ascending order"""
        response = self.client.get(reverse('catalog:lamp_list'), {'sort_by': 'price', 'sort_order': 'asc'})
        lamps = response.context['lamps']
        self.assertEqual(list(lamps), [self.lamp1, self.lamp3, self.lamp2])

    def test_sort_by_price_descending(self):
        """Test sorting by price in descending order"""
        response = self.client.get(reverse('catalog:lamp_list'), {'sort_by': 'price', 'sort_order': 'desc'})
        lamps = response.context['lamps']
        self.assertEqual(list(lamps), [self.lamp2, self.lamp3, self.lamp1])

    def test_sort_by_power_ascending(self):
        """Test sorting by power in ascending order"""
        response = self.client.get(reverse('catalog:lamp_list'), {'sort_by': 'power_watts', 'sort_order': 'asc'})
        lamps = response.context['lamps']
        self.assertEqual(list(lamps), [self.lamp2, self.lamp1, self.lamp3])

    def test_sort_by_power_descending(self):
        """Test sorting by power in descending order"""
        response = self.client.get(reverse('catalog:lamp_list'), {'sort_by': 'power_watts', 'sort_order': 'desc'})
        lamps = response.context['lamps']
        self.assertEqual(list(lamps), [self.lamp3, self.lamp1, self.lamp2])

    def test_sort_by_height_ascending(self):
        """Test sorting by height in ascending order"""
        response = self.client.get(reverse('catalog:lamp_list'), {'sort_by': 'height_cm', 'sort_order': 'asc'})
        lamps = response.context['lamps']
        self.assertEqual(list(lamps), [self.lamp1, self.lamp2, self.lamp3])

    def test_sort_by_height_descending(self):
        """Test sorting by height in descending order"""
        response = self.client.get(reverse('catalog:lamp_list'), {'sort_by': 'height_cm', 'sort_order': 'desc'})
        lamps = response.context['lamps']
        self.assertEqual(list(lamps), [self.lamp3, self.lamp2, self.lamp1])

    def test_sort_by_color_ascending(self):
        """Test sorting by color in ascending order"""
        response = self.client.get(reverse('catalog:lamp_list'), {'sort_by': 'color', 'sort_order': 'asc'})
        lamps = response.context['lamps']
        self.assertEqual(list(lamps), [self.lamp2, self.lamp3, self.lamp1])

    def test_sort_by_color_descending(self):
        """Test sorting by color in descending order"""
        response = self.client.get(reverse('catalog:lamp_list'), {'sort_by': 'color', 'sort_order': 'desc'})
        lamps = response.context['lamps']
        self.assertEqual(list(lamps), [self.lamp1, self.lamp3, self.lamp2])

    def test_sort_by_lamp_type_ascending(self):
        """Test sorting by lamp type in ascending order"""
        response = self.client.get(reverse('catalog:lamp_list'), {'sort_by': 'lamp_type', 'sort_order': 'asc'})
        lamps = response.context['lamps']
        # floor -> table -> wall
        self.assertEqual(list(lamps), [self.lamp2, self.lamp1, self.lamp3])

    def test_sort_by_lamp_type_descending(self):
        """Test sorting by lamp type in descending order"""
        response = self.client.get(reverse('catalog:lamp_list'), {'sort_by': 'lamp_type', 'sort_order': 'desc'})
        lamps = response.context['lamps']
        # wall -> table -> floor
        self.assertEqual(list(lamps), [self.lamp3, self.lamp1, self.lamp2])

    def test_sort_with_grouping(self):
        """Test sorting with grouping"""
        response = self.client.get(reverse('catalog:lamp_list'), {
            'sort_by': 'price',
            'sort_order': 'asc',
            'group_by': 'lamp_type'
        })
        lamps = response.context['lamps']
        # Should be grouped by lamp_type but still sorted by price within groups
        # floor (lamp2) -> table (lamp1) -> wall (lamp3)
        self.assertEqual(list(lamps), [self.lamp2, self.lamp1, self.lamp3])

    def test_sort_with_filtering(self):
        """Test sorting with filtering"""
        response = self.client.get(reverse('catalog:lamp_list'), {
            'sort_by': 'price',
            'sort_order': 'asc',
            'has_dimmer': 'true'
        })
        lamps = response.context['lamps']
        # Should only show lamps with dimmer, sorted by price
        self.assertEqual(list(lamps), [self.lamp1, self.lamp3]) 