from django.db import models


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
    height_cm = models.PositiveIntegerField(verbose_name='Высота (см)', null=True, blank=True)
    color = models.CharField(max_length=50, verbose_name='Цвет')
    lamp_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Тип лампы')
    description = models.TextField(verbose_name='Описание', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
