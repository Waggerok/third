from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse
from .models import Lamp, Cart, CartItem, Order, UserProfile

def about(request):
    return render(request, 'catalog/about.html')

def has_role(role):
    def check_role(user):
        try:
            return user.userprofile.role == role
        except UserProfile.DoesNotExist:
            return False
    return check_role

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

@login_required
def add_to_cart(request, lamp_id):
    lamp = get_object_or_404(Lamp, id=lamp_id)
    quantity = int(request.POST.get('quantity', 1))

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        lamp=lamp,
        defaults={'quantity': quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    messages.success(request, 'Товар добавлен в корзину')
    return redirect('catalog:lamp_detail', pk=lamp_id)

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'catalog/cart_detail.html', {'cart': cart})

@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    return redirect('catalog:cart_detail')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Товар удален из корзины')
    return redirect('catalog:cart_detail')

@login_required
@user_passes_test(has_role('sales_manager'))
def create_order(request):
    cart = get_object_or_404(Cart, user=request.user)
    if not cart.items.exists():
        messages.error(request, 'Корзина пуста')
        return redirect('catalog:cart_detail')
    
    order = Order.objects.create(cart=cart, sales_manager=request.user)
    messages.success(request, 'Заказ успешно создан')
    return redirect('catalog:order_detail', pk=order.id)

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, id=pk)
    if not (request.user == order.sales_manager or request.user.userprofile.role == 'admin'):
        messages.error(request, 'У вас нет доступа к этому заказу')
        return redirect('catalog:lamp_list')
    
    return render(request, 'catalog/order_detail.html', {'order': order})

@login_required
@user_passes_test(has_role('admin'))
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'catalog/order_list.html', {'orders': orders})

@login_required
@user_passes_test(has_role('merchandiser'))
def edit_lamp_description(request, pk):
    lamp = get_object_or_404(Lamp, id=pk)
    if request.method == 'POST':
        lamp.description = request.POST.get('description', '')
        lamp.save()
        messages.success(request, 'Описание товара обновлено')
        return redirect('catalog:lamp_detail', pk=pk)
    
    return render(request, 'catalog/edit_lamp_description.html', {'lamp': lamp})
