from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Lamp, UserProfile, Cart, CartItem, Order
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
        # Guest can view lamp list
        response = self.guest_client.get(reverse('catalog:lamp_list'))
        self.assertEqual(response.status_code, 200)

        # Guest can view lamp detail
        response = self.guest_client.get(reverse('catalog:lamp_detail', args=[self.lamp.id]))
        self.assertEqual(response.status_code, 200)

        # Guest cannot edit description
        response = self.guest_client.get(reverse('catalog:edit_lamp_description', args=[self.lamp.id]))
        self.assertEqual(response.status_code, 403)

        # Guest cannot create order
        response = self.guest_client.post(reverse('catalog:create_order'))
        self.assertEqual(response.status_code, 403)

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
        self.assertTrue(Order.objects.filter(sales_manager=self.sales_manager).exists())

        # Test order access
        order = Order.objects.get(sales_manager=self.sales_manager)
        response = self.sales_client.get(reverse('catalog:order_detail', args=[order.id]))
        self.assertEqual(response.status_code, 200)

        # Other sales manager cannot access the order
        other_sales = User.objects.create_user(username='other_sales', password='sales123')
        UserProfile.objects.create(user=other_sales, role='sales_manager')
        other_client = Client()
        other_client.login(username='other_sales', password='sales123')
        response = other_client.get(reverse('catalog:order_detail', args=[order.id]))
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
            price=1000,
            small_wholesale_price=900,
            small_wholesale_quantity=5,
            large_wholesale_price=800,
            large_wholesale_quantity=10
        )

    def test_price_calculation(self):
        cart = Cart.objects.create(user=self.user)
        
        # Test single item price
        CartItem.objects.create(cart=cart, lamp=self.lamp, quantity=1)
        self.assertEqual(cart.get_total_price(), 1000)

        # Test small wholesale price
        cart.items.all().delete()
        CartItem.objects.create(cart=cart, lamp=self.lamp, quantity=5)
        self.assertEqual(cart.get_total_price(), 4500)  # 5 * 900

        # Test large wholesale price
        cart.items.all().delete()
        CartItem.objects.create(cart=cart, lamp=self.lamp, quantity=10)
        self.assertEqual(cart.get_total_price(), 8000)  # 10 * 800

    def test_discount_calculation(self):
        cart = Cart.objects.create(user=self.user)
        
        # Test no discount
        CartItem.objects.create(cart=cart, lamp=self.lamp, quantity=1)
        self.assertEqual(cart.get_total_price_with_discount(), 1000)

        # Test 5% discount
        cart.items.all().delete()
        CartItem.objects.create(cart=cart, lamp=self.lamp, quantity=50)
        self.assertEqual(cart.get_total_price_with_discount(), 47500)  # 50000 * 0.95

        # Test 10% discount
        cart.items.all().delete()
        CartItem.objects.create(cart=cart, lamp=self.lamp, quantity=100)
        self.assertEqual(cart.get_total_price_with_discount(), 90000)  # 100000 * 0.9

class CatalogAccessTest(TestCase):
    def setUp(self):
        # Создаем тестовых пользователей с разными ролями
        self.guest_client = Client()
        
        self.admin_user = User.objects.create_user(username='admin', password='admin123')
        self.admin_profile = UserProfile.objects.create(user=self.admin_user, role='admin')
        self.admin_client = Client()
        self.admin_client.login(username='admin', password='admin123')
        
        self.manager_user = User.objects.create_user(username='manager', password='manager123')
        self.manager_profile = UserProfile.objects.create(user=self.manager_user, role='sales_manager')
        self.manager_client = Client()
        self.manager_client.login(username='manager', password='manager123')
        
        self.merchandiser_user = User.objects.create_user(username='merchandiser', password='merchandiser123')
        self.merchandiser_profile = UserProfile.objects.create(user=self.merchandiser_user, role='merchandiser')
        self.merchandiser_client = Client()
        self.merchandiser_client.login(username='merchandiser', password='merchandiser123')
        
        # Создаем тестовую лампу
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

    def test_guest_access(self):
        """Тест доступа гостя"""
        # Гость может просматривать каталог
        response = self.guest_client.get(reverse('catalog:lamp_list'))
        self.assertEqual(response.status_code, 200)
        
        # Гость не может добавлять в корзину
        response = self.guest_client.post(reverse('catalog:add_to_cart', args=[self.lamp.id]))
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа
        
        # Гость не может создавать заказы
        response = self.guest_client.post(reverse('catalog:create_order'))
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа

    def test_role_based_access(self):
        """Тест разграничения прав по ролям"""
        # Только менеджер и админ могут создавать заказы
        response = self.manager_client.post(reverse('catalog:create_order'))
        self.assertNotEqual(response.status_code, 403)  # Не должно быть запрещено
        
        response = self.admin_client.post(reverse('catalog:create_order'))
        self.assertNotEqual(response.status_code, 403)  # Не должно быть запрещено
        
        response = self.merchandiser_client.post(reverse('catalog:create_order'))
        self.assertEqual(response.status_code, 403)  # Должно быть запрещено

    def test_catalog_operations(self):
        """Тест операций с каталогом"""
        # Только товаровед может редактировать описания
        response = self.merchandiser_client.post(
            reverse('catalog:edit_lamp_description', args=[self.lamp.id]),
            {'description': 'New description'}
        )
        self.assertEqual(response.status_code, 200)
        self.lamp.refresh_from_db()
        self.assertEqual(self.lamp.description, 'New description')
        
        # Другие роли не могут редактировать описания
        response = self.manager_client.post(
            reverse('catalog:edit_lamp_description', args=[self.lamp.id]),
            {'description': 'Manager description'}
        )
        self.assertEqual(response.status_code, 403)

    def test_price_calculation(self):
        """Тест расчета цен"""
        # Создаем корзину для менеджера
        cart = Cart.objects.create(user=self.manager_user)
        
        # Тест обычной цены
        cart_item = CartItem.objects.create(cart=cart, lamp=self.lamp, quantity=1)
        self.assertEqual(cart_item.get_total_price(), Decimal('1000.00'))
        
        # Тест мелкого опта
        cart_item.quantity = 5
        cart_item.save()
        self.assertEqual(cart_item.get_total_price(), Decimal('4500.00'))  # 5 * 900
        
        # Тест крупного опта
        cart_item.quantity = 10
        cart_item.save()
        self.assertEqual(cart_item.get_total_price(), Decimal('8000.00'))  # 10 * 800
        
        # Тест скидок
        cart_item.quantity = 100  # Сумма заказа будет 80000 (10 * 800)
        cart_item.save()
        self.assertEqual(cart.get_total_price_with_discount(), Decimal('76000.00'))  # 80000 * 0.95 (скидка 5%)
        
        cart_item.quantity = 200  # Сумма заказа будет 160000 (20 * 800)
        cart_item.save()
        self.assertEqual(cart.get_total_price_with_discount(), Decimal('144000.00'))  # 160000 * 0.9 (скидка 10%)

    def test_order_creation(self):
        """Тест создания заказа"""
        # Создаем корзину с товарами
        cart = Cart.objects.create(user=self.manager_user)
        CartItem.objects.create(cart=cart, lamp=self.lamp, quantity=5)
        
        # Создаем заказ
        response = self.manager_client.post(reverse('catalog:create_order'))
        self.assertEqual(response.status_code, 302)  # Редирект на страницу заказа
        
        # Проверяем, что заказ создан
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.sales_manager, self.manager_user)
        
        # Проверяем, что старая корзина удалена и создана новая
        self.assertFalse(Cart.objects.filter(id=cart.id).exists())
        self.assertTrue(Cart.objects.filter(user=self.manager_user).exists())
        self.assertEqual(Cart.objects.filter(user=self.manager_user).count(), 1) 