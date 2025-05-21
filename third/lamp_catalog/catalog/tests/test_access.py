from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Lamp, Cart, CartItem, Order, UserProfile
from decimal import Decimal

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

    # def test_role_based_access(self):
    #     """Тест разграничения прав по ролям"""
    #     # Создаем корзину для менеджера
    #     cart = Cart.objects.create(user=self.manager_user)
    #     CartItem.objects.create(cart=cart, lamp=self.lamp, quantity=5)
        
    #     # Только менеджер и админ могут создавать заказы
    #     response = self.manager_client.post(reverse('catalog:create_order'))
    #     self.assertEqual(response.status_code, 302)  # Редирект на страницу заказа
        
    #     response = self.admin_client.post(reverse('catalog:create_order'))
    #     self.assertEqual(response.status_code, 302)  # Редирект на страницу заказа
        
    #     response = self.merchandiser_client.post(reverse('catalog:create_order'))
    #     self.assertEqual(response.status_code, 403)  # Должно быть запрещено

    def test_catalog_operations(self):
        """Тест операций с каталогом"""
        # Только товаровед может редактировать описания
        response = self.merchandiser_client.post(
            reverse('catalog:edit_lamp_description', args=[self.lamp.id]),
            {'description': 'New description'}
        )
        self.assertEqual(response.status_code, 302)  # Редирект после успешного обновления
        self.lamp.refresh_from_db()
        self.assertEqual(self.lamp.description, 'New description')
        
        # Другие роли не могут редактировать описания
        response = self.manager_client.post(
            reverse('catalog:edit_lamp_description', args=[self.lamp.id]),
            {'description': 'Manager description'}
        )
        self.assertEqual(response.status_code, 403)  # Должно быть запрещено

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
