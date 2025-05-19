from django.test import TestCase
from django.urls import reverse
from django.db.models import Q
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
        self.lamp4 = Lamp.objects.create(
            article='D004',
            brand='Brand D',
            has_dimmer=False,
            power_watts=100,
            height_cm=60,
            color='Blue',
            lamp_type='ceiling',
            price=300.00,
            description='Test description 4'
        )
        self.lamp5 = Lamp.objects.create(
            article='E005',
            brand='Brand E',
            has_dimmer=True,
            power_watts=45,
            height_cm=35,
            color='Green',
            lamp_type='other',
            price=250.00,
            description='Test description 5'
        )

    def test_alphabetical_ordering(self):
        lamps = Lamp.objects.order_by('brand')
        self.assertEqual(list(lamps), [self.lamp1, self.lamp2, self.lamp3, self.lamp4, self.lamp5])

    def test_price_ordering(self):
        lamps = Lamp.objects.order_by('price')
        self.assertEqual(list(lamps), [self.lamp1, self.lamp2, self.lamp3, self.lamp5, self.lamp4])

    def test_power_ordering(self):
        lamps = Lamp.objects.order_by('power_watts')
        self.assertEqual(list(lamps), [self.lamp2, self.lamp5, self.lamp1, self.lamp3, self.lamp4])

    def test_height_ordering(self):
        lamps = Lamp.objects.order_by('height_cm')
        self.assertEqual(list(lamps), [self.lamp1, self.lamp5, self.lamp2, self.lamp3, self.lamp4])

    def test_lamp_type_filtering(self):
        table_lamps = Lamp.objects.filter(lamp_type='table')
        self.assertEqual(list(table_lamps), [self.lamp1])
        
        floor_lamps = Lamp.objects.filter(lamp_type='floor')
        self.assertEqual(list(floor_lamps), [self.lamp2])
        
        wall_lamps = Lamp.objects.filter(lamp_type='wall')
        self.assertEqual(list(wall_lamps), [self.lamp3])
        
        ceiling_lamps = Lamp.objects.filter(lamp_type='ceiling')
        self.assertEqual(list(ceiling_lamps), [self.lamp4])
        
        other_lamps = Lamp.objects.filter(lamp_type='other')
        self.assertEqual(list(other_lamps), [self.lamp5])

    def test_dimmer_filtering(self):
        dimmer_lamps = Lamp.objects.filter(has_dimmer=True)
        self.assertEqual(set(dimmer_lamps), {self.lamp1, self.lamp3, self.lamp5})
        
        non_dimmer_lamps = Lamp.objects.filter(has_dimmer=False)
        self.assertEqual(set(non_dimmer_lamps), {self.lamp2, self.lamp4})

    def test_power_range_filtering(self):
        # Тест диапазона мощности
        lamps_40_60 = Lamp.objects.filter(power_watts__gte=40, power_watts__lte=60)
        self.assertEqual(set(lamps_40_60), {self.lamp1, self.lamp2, self.lamp5})
        
        lamps_above_70 = Lamp.objects.filter(power_watts__gt=70)
        self.assertEqual(set(lamps_above_70), {self.lamp3, self.lamp4})
        
        lamps_below_50 = Lamp.objects.filter(power_watts__lt=50)
        self.assertEqual(set(lamps_below_50), {self.lamp2, self.lamp5})

    def test_height_range_filtering(self):
        # Тест диапазона высоты
        lamps_30_40 = Lamp.objects.filter(height_cm__gte=30, height_cm__lte=40)
        self.assertEqual(set(lamps_30_40), {self.lamp1, self.lamp2, self.lamp5})
        
        lamps_above_50 = Lamp.objects.filter(height_cm__gt=50)
        self.assertEqual(set(lamps_above_50), {self.lamp4})
        
        lamps_below_35 = Lamp.objects.filter(height_cm__lt=35)
        self.assertEqual(set(lamps_below_35), {self.lamp1})

    def test_price_range_filtering(self):
        # Тест диапазона цены
        lamps_100_200 = Lamp.objects.filter(price__gte=100, price__lte=200)
        self.assertEqual(set(lamps_100_200), {self.lamp1, self.lamp2, self.lamp3})
        
        lamps_above_250 = Lamp.objects.filter(price__gt=250)
        self.assertEqual(set(lamps_above_250), {self.lamp4})
        
        lamps_below_150 = Lamp.objects.filter(price__lt=150)
        self.assertEqual(set(lamps_below_150), {self.lamp1})

    def test_color_filtering(self):
        # Тест фильтрации по цвету
        white_lamps = Lamp.objects.filter(color='White')
        self.assertEqual(list(white_lamps), [self.lamp1])
        
        black_lamps = Lamp.objects.filter(color='Black')
        self.assertEqual(list(black_lamps), [self.lamp2])
        
        colored_lamps = Lamp.objects.filter(color__in=['Red', 'Blue', 'Green'])
        self.assertEqual(set(colored_lamps), {self.lamp3, self.lamp4, self.lamp5})

    def test_combined_filtering(self):
        # Тест комбинированной фильтрации
        # Лампы с диммером и мощностью выше 50 Вт
        dimmer_power_lamps = Lamp.objects.filter(has_dimmer=True, power_watts__gt=50)
        self.assertEqual(set(dimmer_power_lamps), {self.lamp1, self.lamp3})
        
        # Настольные и напольные лампы с ценой до 200
        type_price_lamps = Lamp.objects.filter(
            lamp_type__in=['table', 'floor'],
            price__lt=200
        )
        self.assertEqual(set(type_price_lamps), {self.lamp1, self.lamp2})
        
        # Лампы высотой от 30 до 50 см с диммером
        height_dimmer_lamps = Lamp.objects.filter(
            height_cm__gte=30,
            height_cm__lte=50,
            has_dimmer=True
        )
        self.assertEqual(set(height_dimmer_lamps), {self.lamp1, self.lamp3, self.lamp5})

    def test_search_functionality(self):
        # Тест поиска по артикулу
        article_search = Lamp.objects.filter(article__icontains='00')
        self.assertEqual(set(article_search), {self.lamp1, self.lamp2, self.lamp3, self.lamp4, self.lamp5})
        
        # Тест поиска по бренду
        brand_search = Lamp.objects.filter(brand__icontains='Brand')
        self.assertEqual(set(brand_search), {self.lamp1, self.lamp2, self.lamp3, self.lamp4, self.lamp5})
        
        # Тест поиска по описанию
        desc_search = Lamp.objects.filter(description__icontains='Test')
        self.assertEqual(set(desc_search), {self.lamp1, self.lamp2, self.lamp3, self.lamp4, self.lamp5})

    def test_complex_queries(self):
        # Сложные запросы с использованием Q объектов
        # Лампы с диммером ИЛИ мощностью выше 70 Вт
        dimmer_or_power = Lamp.objects.filter(
            Q(has_dimmer=True) | Q(power_watts__gt=70)
        )
        self.assertEqual(set(dimmer_or_power), {self.lamp1, self.lamp3, self.lamp4, self.lamp5})
        
        # Лампы с ценой от 150 до 300 И (с диммером ИЛИ высотой больше 40 см)
        complex_query = Lamp.objects.filter(
            Q(price__gte=150) & Q(price__lte=300) & (Q(has_dimmer=True) | Q(height_cm__gt=40))
        )
        self.assertEqual(set(complex_query), {self.lamp3, self.lamp4, self.lamp5})
