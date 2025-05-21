from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse
from .models import Lamp, Cart, CartItem, Order, UserProfile
from .forms import UserRegistrationForm

def about(request):
    return render(request, 'catalog/about.html')

def has_role(role):
    def check_role(user):
        try:
            return user.userprofile.role == role
        except UserProfile.DoesNotExist:
            return False
    return check_role

def has_role_or_admin(roles):
    def check_role(user):
        try:
            return user.userprofile.role in roles or user.userprofile.role == 'admin'
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
@user_passes_test(lambda u: u.userprofile.role in ['sales_manager', 'admin'])
def create_order(request):
    cart = get_object_or_404(Cart, user=request.user)
    if not cart.items.exists():
        messages.error(request, 'Корзина пуста')
        return redirect('catalog:cart_detail')
    
    # Создаем заказ
    order = Order.objects.create(cart=cart, sales_manager=request.user)
    
    # Создаем новую корзину для пользователя
    new_cart = Cart.objects.create(user=request.user)
    
    # Удаляем старую корзину
    cart.delete()
    
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
def order_list(request):
    if request.user.userprofile.role == 'admin':
        orders = Order.objects.all().order_by('-created_at')
    elif request.user.userprofile.role == 'sales_manager':
        orders = Order.objects.filter(sales_manager=request.user).order_by('-created_at')
    else:
        messages.error(request, 'У вас нет доступа к списку заказов')
        return redirect('catalog:lamp_list')
    return render(request, 'catalog/order_list.html', {'orders': orders})

@login_required
def edit_lamp_description(request, pk):
    lamp = get_object_or_404(Lamp, id=pk)

    if request.method == 'POST':
        if not (request.user.userprofile.role in ['merchandiser', 'admin']):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        lamp.description = request.POST.get('description', '')
        lamp.save()
        messages.success(request, 'Описание товара обновлено')
        return redirect('catalog:lamp_detail', pk=pk)

    return render(request, 'catalog/edit_lamp_description.html', {'lamp': lamp})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация успешна! Теперь вы можете войти.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
@user_passes_test(has_role_or_admin(['merchandiser']))
def merchandiser_product_list(request):
    lamps = Lamp.objects.all().order_by('-created_at')
    return render(request, 'catalog/merchandiser_product_list.html', {'lamps': lamps})

@login_required
@user_passes_test(has_role_or_admin(['merchandiser']))
def edit_lamp(request, pk):
    lamp = get_object_or_404(Lamp, id=pk)
    if request.method == 'POST':
        try:
            lamp.brand = request.POST.get('brand', lamp.brand)
            lamp.article = request.POST.get('article', lamp.article)
            lamp.has_dimmer = request.POST.get('has_dimmer') == 'on'
            lamp.power_watts = int(request.POST.get('power_watts', lamp.power_watts))
            height_cm = request.POST.get('height_cm')
            lamp.height_cm = int(height_cm) if height_cm else None
            lamp.color = request.POST.get('color', lamp.color)
            lamp.lamp_type = request.POST.get('lamp_type', lamp.lamp_type)
            lamp.description = request.POST.get('description', lamp.description)
            lamp.price = float(request.POST.get('price', lamp.price))
            
            small_wholesale_price = request.POST.get('small_wholesale_price')
            lamp.small_wholesale_price = float(small_wholesale_price) if small_wholesale_price else None
            
            small_wholesale_quantity = request.POST.get('small_wholesale_quantity')
            lamp.small_wholesale_quantity = int(small_wholesale_quantity) if small_wholesale_quantity else None
            
            large_wholesale_price = request.POST.get('large_wholesale_price')
            lamp.large_wholesale_price = float(large_wholesale_price) if large_wholesale_price else None
            
            large_wholesale_quantity = request.POST.get('large_wholesale_quantity')
            lamp.large_wholesale_quantity = int(large_wholesale_quantity) if large_wholesale_quantity else None
            
            lamp.save()
            messages.success(request, 'Товар успешно обновлен')
            return redirect('catalog:merchandiser_product_list')
        except (ValueError, TypeError) as e:
            messages.error(request, f'Ошибка при сохранении данных: {str(e)}')
    return render(request, 'catalog/edit_lamp.html', {'lamp': lamp})
