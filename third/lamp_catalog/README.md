# Каталог ламп - Django проект

## Описание проекта
Проект представляет собой веб-приложение для каталогизации ламп. Приложение позволяет просматривать, добавлять, редактировать и удалять информацию о лампах через административную панель.

## Структура проекта
```
lamp_catalog/
├── catalog/                    # Основное приложение
│   ├── migrations/            # Миграции базы данных
│   ├── templates/             # HTML шаблоны
│   │   └── catalog/
│   │       ├── base.html     # Базовый шаблон
│   │       ├── lamp_list.html # Список ламп
│   │       ├── lamp_detail.html # Детальная информация о лампе
│   │       └── about.html    # Страница "О сервисе"
│   ├── admin.py              # Настройки админ-панели
│   ├── models.py             # Модели данных
│   ├── urls.py               # URL-маршруты приложения
│   └── views.py              # Представления (views)
├── lamp_catalog/             # Настройки проекта
│   ├── settings.py           # Основные настройки
│   ├── urls.py               # Корневые URL-маршруты
│   └── wsgi.py               # WSGI конфигурация
└── manage.py                 # Утилита управления Django
```

## Основные компоненты

### Модель Lamp (models.py)
```python
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
```

### Представления (views.py)
```python
class LampListView(ListView):
    model = Lamp
    template_name = 'catalog/lamp_list.html'
    context_object_name = 'lamps'
    paginate_by = 10

class LampDetailView(DetailView):
    model = Lamp
    template_name = 'catalog/lamp_detail.html'
    context_object_name = 'lamp'
```

### URL-маршруты (urls.py)
```python
urlpatterns = [
    path('', views.LampListView.as_view(), name='lamp_list'),
    path('about/', views.about, name='about'),
    path('lamp/<int:pk>/', views.LampDetailView.as_view(), name='lamp_detail'),
]
```

### Административная панель (admin.py)
```python
@admin.register(Lamp)
class LampAdmin(admin.ModelAdmin):
    list_display = ('article', 'brand', 'lamp_type', 'power_watts', 'price')
    list_filter = ('lamp_type', 'has_dimmer', 'color')
    search_fields = ('article', 'brand', 'description')
    ordering = ('-created_at',)
```

## Функциональность

### Основные возможности:
1. Просмотр списка ламп с пагинацией
2. Детальный просмотр информации о каждой лампе
3. Административная панель для управления данными
4. Фильтрация и поиск в административной панели
5. Страница "О сервисе"

### Особенности реализации:
1. Использование Bootstrap для стилизации
2. Адаптивный дизайн
3. Пагинация списка ламп
4. Хлебные крошки для навигации
5. Поддержка русского языка в интерфейсе

## Установка и запуск

1. Установите зависимости:
```bash
pip install django
```

2. Примените миграции:
```bash
python manage.py migrate
```

3. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

4. Запустите сервер разработки:
```bash
python manage.py runserver
```

5. Откройте в браузере:
- Каталог: http://127.0.0.1:8000/
- Админ-панель: http://127.0.0.1:8000/admin/

## Технические требования
- Python 3.8+
- Django 4.0+
- SQLite (встроенная база данных) 