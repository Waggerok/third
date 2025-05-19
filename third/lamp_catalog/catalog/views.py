from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Lamp

def about(request):
    return render(request, 'catalog/about.html')

class LampListView(ListView):
    model = Lamp
    template_name = 'catalog/lamp_list.html'
    context_object_name = 'lamps'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Получаем параметры фильтрации из GET-запроса
        lamp_type = self.request.GET.get('lamp_type')
        has_dimmer = self.request.GET.get('has_dimmer')
        min_power = self.request.GET.get('min_power')
        max_power = self.request.GET.get('max_power')
        search_query = self.request.GET.get('search')
        sort_by = self.request.GET.get('sort_by', 'brand')  # По умолчанию сортируем по бренду
        sort_order = self.request.GET.get('sort_order', 'asc')  # По умолчанию сортируем по возрастанию
        group_by = self.request.GET.get('group_by')  # Параметр для группировки
        
        # Применяем фильтры
        if lamp_type:
            queryset = queryset.filter(lamp_type=lamp_type)
        if has_dimmer:
            queryset = queryset.filter(has_dimmer=True)
        if min_power:
            queryset = queryset.filter(power_watts__gte=min_power)
        if max_power:
            queryset = queryset.filter(power_watts__lte=max_power)
        
        # Применяем поиск
        if search_query:
            queryset = queryset.filter(
                Q(article__icontains=search_query) |
                Q(brand__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Применяем сортировку
        if sort_by in ['brand', 'price', 'power_watts', 'height_cm', 'color', 'lamp_type']:
            if sort_order == 'desc':
                sort_by = f'-{sort_by}'
            queryset = queryset.order_by(sort_by)
        
        # Применяем группировку
        if group_by in ['lamp_type', 'has_dimmer', 'color']:
            queryset = queryset.order_by(group_by)
            # Устанавливаем текущую группу для каждого объекта
            for lamp in queryset:
                lamp._current_group = group_by
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Добавляем текущие значения фильтров в контекст
        context['current_lamp_type'] = self.request.GET.get('lamp_type', '')
        context['current_has_dimmer'] = self.request.GET.get('has_dimmer', '')
        context['current_min_power'] = self.request.GET.get('min_power', '')
        context['current_max_power'] = self.request.GET.get('max_power', '')
        context['current_search'] = self.request.GET.get('search', '')
        context['current_sort'] = self.request.GET.get('sort_by', 'brand')
        context['current_sort_order'] = self.request.GET.get('sort_order', 'asc')
        context['current_group'] = self.request.GET.get('group_by', '')
        
        # Добавляем типы ламп в контекст
        context['lamp_types'] = Lamp.TYPE_CHOICES
        
        # Добавляем доступные поля для сортировки
        context['sort_fields'] = [
            ('brand', 'По бренду'),
            ('price', 'По цене'),
            ('power_watts', 'По мощности'),
            ('height_cm', 'По высоте'),
            ('color', 'По цвету'),
            ('lamp_type', 'По типу')
        ]
        
        # Добавляем доступные поля для группировки
        context['group_fields'] = [
            ('lamp_type', 'По типу лампы'),
            ('has_dimmer', 'По наличию диммера'),
            ('color', 'По цвету')
        ]
        
        return context

class LampDetailView(DetailView):
    model = Lamp
    template_name = 'catalog/lamp_detail.html'
    context_object_name = 'lamp'
