from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class LampType(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')

class Lamp(models.Model):
    TYPE_CHOICES = [
        ('table', 'Настольная'),
        ('floor', 'Напольная'),
        ('wall', 'Настенная'),
        ('ceiling', 'Потолочная'),
        ('other', 'Другая'),
    ]

    article = models.CharField(max_length=50, unique=True, verbose_name='Артикул')
    brand = models.CharField(max_length=100, verbose_name='Марка')
    has_dimmer = models.BooleanField(default=False, verbose_name='Поддержка диммера')
    power_watts = models.PositiveIntegerField(verbose_name='Мощность (Вт)')
    height_cm = models.PositiveIntegerField(blank=True, null=True, verbose_name='Высота (см)')
    color = models.CharField(max_length=50, verbose_name='Цвет')
    lamp_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Тип лампы')
    description = models.TextField(verbose_name='Описание', blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена за единицу')
    small_wholesale_price = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена мелкого опта', null=True, blank=True)
    small_wholesale_quantity = models.PositiveIntegerField(verbose_name='Количество для мелкого опта', null=True, blank=True)
    large_wholesale_price = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена крупного опта', null=True, blank=True)
    large_wholesale_quantity = models.PositiveIntegerField(verbose_name='Количество для крупного опта', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_price_for_quantity(self, quantity=1):
        if self.large_wholesale_price and self.large_wholesale_quantity and quantity >= self.large_wholesale_quantity:
            return self.large_wholesale_price
        elif self.small_wholesale_price and self.small_wholesale_quantity and quantity >= self.small_wholesale_quantity:
            return self.small_wholesale_price
        return self.price

    def __str__(self):
        return f"{self.brand} - {self.article}"

    def get_current_group_display(self):
        """
        Returns the display value for the current grouping field.
        This method is used in the template to display the group header.
        """
        if hasattr(self, '_current_group'):
            if self._current_group == 'lamp_type':
                return self.get_lamp_type_display()
            elif self._current_group == 'has_dimmer':
                return 'С диммером' if self.has_dimmer else 'Без диммера'
            elif self._current_group == 'color':
                return self.color
        return ''

    class Meta:
        verbose_name = 'Лампа'
        verbose_name_plural = 'Лампы'
        ordering = ['-created_at']

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('merchandiser', 'Товаровед'),
        ('sales_manager', 'Менеджер по продажам'),
        ('guest', 'Гость'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='guest')
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())
    
    def get_total_price_with_discount(self):
        total = self.get_total_price()
        if total >= Decimal('100000'):  # 10% discount for orders over 100,000
            return total * Decimal('0.9')
        elif total >= Decimal('50000'):  # 5% discount for orders over 50,000
            return total * Decimal('0.95')
        return total

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    lamp = models.ForeignKey(Lamp, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    
    def get_total_price(self):
        return self.lamp.get_price_for_quantity(self.quantity) * self.quantity

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает обработки'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]

    cart = models.OneToOneField(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    sales_manager = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_price(self):
        return self.cart.get_total_price_with_discount() if self.cart else 0
