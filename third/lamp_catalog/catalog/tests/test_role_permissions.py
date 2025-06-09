from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Lamp, Cart, CartItem, Order, UserProfile
from decimal import Decimal

class RolePermissionsTest(TestCase):
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

    def test_admin_permissions(self):
        """Test admin permissions"""
        # Admin can view all orders
        response = self.admin_client.get(reverse('catalog:order_list'))
        self.assertEqual(response.status_code, 200)

        # Admin can view merchandiser product list
        response = self.admin_client.get(reverse('catalog:merchandiser_product_list'))
        self.assertEqual(response.status_code, 200)

        # Admin can edit lamp descriptions
        response = self.admin_client.post(
            reverse('catalog:edit_lamp_description', args=[self.lamp.id]),
            {'description': 'Admin edited description'}
        )
        self.assertEqual(response.status_code, 302)
        self.lamp.refresh_from_db()
        self.assertEqual(self.lamp.description, 'Admin edited description')

        # Admin can create orders
        cart = Cart.objects.create(user=self.admin_user)
        CartItem.objects.create(cart=cart, lamp=self.lamp, quantity=5)
        response = self.admin_client.post(reverse('catalog:create_order'))
        self.assertEqual(response.status_code, 302)

    def test_merchandiser_permissions(self):
        """Test merchandiser permissions"""
        # Merchandiser can view merchandiser product list
        response = self.merchandiser_client.get(reverse('catalog:merchandiser_product_list'))
        self.assertEqual(response.status_code, 200)

        # Merchandiser can edit lamp descriptions
        response = self.merchandiser_client.post(
            reverse('catalog:edit_lamp_description', args=[self.lamp.id]),
            {'description': 'Merchandiser edited description'}
        )
        self.assertEqual(response.status_code, 302)
        self.lamp.refresh_from_db()
        self.assertEqual(self.lamp.description, 'Merchandiser edited description')

        # Merchandiser cannot create orders
        cart = Cart.objects.create(user=self.merchandiser)
        CartItem.objects.create(cart=cart, lamp=self.lamp, quantity=5)
        response = self.merchandiser_client.post(reverse('catalog:create_order'))
        self.assertEqual(response.status_code, 302)  # Forbidden

        # Merchandiser cannot view order list
        response = self.merchandiser_client.get(reverse('catalog:order_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_sales_manager_permissions(self):
        """Test sales manager permissions"""
        # Sales manager can view order list
        response = self.sales_client.get(reverse('catalog:order_list'))
        self.assertEqual(response.status_code, 200)

        # Sales manager can create orders
        cart = Cart.objects.create(user=self.sales_manager)
        CartItem.objects.create(cart=cart, lamp=self.lamp, quantity=5)
        response = self.sales_client.post(reverse('catalog:create_order'))
        self.assertEqual(response.status_code, 302)

        # Sales manager cannot edit lamp descriptions
        response = self.sales_client.post(
            reverse('catalog:edit_lamp_description', args=[self.lamp.id]),
            {'description': 'Sales manager edited description'}
        )
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Sales manager cannot view merchandiser product list
        response = self.sales_client.get(reverse('catalog:merchandiser_product_list'))
        self.assertEqual(response.status_code, 302)  # Forbidden

    def test_guest_permissions(self):
        """Test guest permissions"""
        # Guest can view lamp list
        response = self.guest_client.get(reverse('catalog:lamp_list'))
        self.assertEqual(response.status_code, 200)

        # Guest can view lamp detail
        response = self.guest_client.get(reverse('catalog:lamp_detail', args=[self.lamp.id]))
        self.assertEqual(response.status_code, 200)

        # Guest cannot edit lamp descriptions
        response = self.guest_client.post(
            reverse('catalog:edit_lamp_description', args=[self.lamp.id]),
            {'description': 'Guest edited description'}
        )
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Guest cannot create orders
        cart = Cart.objects.create(user=self.guest)
        CartItem.objects.create(cart=cart, lamp=self.lamp, quantity=5)
        response = self.guest_client.post(reverse('catalog:create_order'))
        self.assertEqual(response.status_code, 302)  # Forbidden

        # Guest cannot view order list
        response = self.guest_client.get(reverse('catalog:order_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Guest cannot view merchandiser product list
        response = self.guest_client.get(reverse('catalog:merchandiser_product_list'))
        self.assertEqual(response.status_code, 302)  # Forbidden

    def test_cross_role_access(self):
        """Test access to other users' resources"""
        # Create an order by sales manager
        cart = Cart.objects.create(user=self.sales_manager)
        CartItem.objects.create(cart=cart, lamp=self.lamp, quantity=5)
        self.sales_client.post(reverse('catalog:create_order'))
        order = Order.objects.first()

        # Test order access
        # Admin can access any order
        response = self.admin_client.get(reverse('catalog:order_detail', args=[order.id]))
        self.assertEqual(response.status_code, 200)

        # Sales manager can access their own order
        response = self.sales_client.get(reverse('catalog:order_detail', args=[order.id]))
        self.assertEqual(response.status_code, 200)

        # Other sales manager cannot access the order
        other_sales = User.objects.create_user(username='other_sales', password='sales123')
        UserProfile.objects.create(user=other_sales, role='sales_manager')
        other_client = Client()
        other_client.login(username='other_sales', password='sales123')
        response = other_client.get(reverse('catalog:order_detail', args=[order.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Merchandiser cannot access the order
        response = self.merchandiser_client.get(reverse('catalog:order_detail', args=[order.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Guest cannot access the order
        response = self.guest_client.get(reverse('catalog:order_detail', args=[order.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login 