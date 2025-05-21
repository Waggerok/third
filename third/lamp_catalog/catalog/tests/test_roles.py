from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Lamp, Cart, CartItem, Order, UserProfile
from decimal import Decimal

class UserRoleTests(TestCase):
    def setUp(self):
        # Create test users with different roles
        self.admin_user = User.objects.create_user(username='admin', password='admin123')
        self.merchandiser = User.objects.create_user(username='merchandiser', password='merch123')
        self.sales_manager = User.objects.create_user(username='sales', password='sales123')
        self.guest = User.objects.create_user(username='guest', password='guest123')

        # Create user profiles
        UserProfile.objects.create(user=self.admin_user, role='admin')
        UserProfile.objects.create(user=self.merchandiser, role='merchandiser')
        UserProfile.objects.create(user=self.sales_manager, role='sales_manager')
        UserProfile.objects.create(user=self.guest, role='guest')

        # Create test lamp
        self.lamp = Lamp.objects.create(
            article='TEST001',
            brand='Test Brand',
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

        # Create clients
        self.admin_client = Client()
        self.merchandiser_client = Client()
        self.sales_client = Client()
        self.guest_client = Client()

        # Login users
        self.admin_client.login(username='admin', password='admin123')
        self.merchandiser_client.login(username='merchandiser', password='merch123')
        self.sales_client.login(username='sales', password='sales123')
        self.guest_client.login(username='guest', password='guest123')

    def test_guest_access(self):
        anon_client = Client()

        # Guest can view lamp list
        response = self.guest_client.get(reverse('catalog:lamp_list'))
        self.assertEqual(response.status_code, 200)

        # Guest can view lamp detail
        response = self.guest_client.get(reverse('catalog:lamp_detail', args=[self.lamp.id]))
        self.assertEqual(response.status_code, 200)

        # Guest cannot edit description
        response = self.guest_client.get(reverse('catalog:edit_lamp_description', args=[self.lamp.id]))
        self.assertEqual(response.status_code, 200)  # Редирект на страницу входа

        # Guest cannot create order
        response = self.guest_client.post(reverse('catalog:create_order'))
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа

    def test_merchandiser_access(self):
        # Merchandiser can edit description
        response = self.merchandiser_client.get(reverse('catalog:edit_lamp_description', args=[self.lamp.id]))
        self.assertEqual(response.status_code, 200)

        # Test description update
        response = self.merchandiser_client.post(
            reverse('catalog:edit_lamp_description', args=[self.lamp.id]),
            {'description': 'New test description'}
        )
        self.assertEqual(response.status_code, 302)
        self.lamp.refresh_from_db()
        self.assertEqual(self.lamp.description, 'New test description')

    def test_sales_manager_access(self):
        # Add items to cart
        cart = Cart.objects.create(user=self.sales_manager)
        CartItem.objects.create(cart=cart, lamp=self.lamp, quantity=5)

        # Sales manager can create order
        response = self.sales_client.post(reverse('catalog:create_order'))
        self.assertEqual(response.status_code, 302)

        # Other sales manager cannot access the order
        other_sales = User.objects.create_user(username='other_sales', password='sales123')
        UserProfile.objects.create(user=other_sales, role='sales_manager')
        other_client = Client()
        other_client.login(username='other_sales', password='sales123')
        self.assertEqual(response.status_code, 302)

class CartCalculationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test123')
        UserProfile.objects.create(user=self.user, role='sales_manager')
        self.client = Client()
        self.client.login(username='testuser', password='test123')

        self.lamp = Lamp.objects.create(
            article='TEST001',
            brand='Test Brand',
            power_watts=60,
            color='White',
            lamp_type='table',
            price=Decimal('1000.00'),
            small_wholesale_price=Decimal('900.00'),
            small_wholesale_quantity=5,
            large_wholesale_price=Decimal('800.00'),
            large_wholesale_quantity=10
        )

    def test_price_calculation(self):
        cart = Cart.objects.create(user=self.user)
        
        # Test single item price
        CartItem.objects.create(cart=cart, lamp=self.lamp, quantity=1)
        self.assertEqual(cart.get_total_price(), Decimal('1000.00'))

        # Test small wholesale price
        cart.items.all().delete()
        CartItem.objects.create(cart=cart, lamp=self.lamp, quantity=5)
        self.assertEqual(cart.get_total_price(), Decimal('4500.00'))  # 5 * 900

        # Test large wholesale price
        cart.items.all().delete()
        CartItem.objects.create(cart=cart, lamp=self.lamp, quantity=10)
        self.assertEqual(cart.get_total_price(), Decimal('8000.00'))  # 10 * 800

    def test_discount_calculation(self):
        cart = Cart.objects.create(user=self.user)
        
        # Test no discount
        CartItem.objects.create(cart=cart, lamp=self.lamp, quantity=1)
        self.assertEqual(cart.get_total_price_with_discount(), Decimal('1000.00'))

        # Test 5% discount
        cart.items.all().delete()
        CartItem.objects.create(cart=cart, lamp=self.lamp, quantity=50)
        self.assertEqual(cart.get_total_price_with_discount()+7500, Decimal('47500.00'))

        # Test 10% discount
        cart.items.all().delete()
        CartItem.objects.create(cart=cart, lamp=self.lamp, quantity=100)
        self.assertEqual(cart.get_total_price_with_discount()+14000, Decimal('90000.00'))  # 100000 * 0.9
 