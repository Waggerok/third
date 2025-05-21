from django.contrib import admin
from .models import Lamp, LampType, UserProfile, Cart, CartItem, Order

@admin.register(LampType)
class LampTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Lamp)
class LampAdmin(admin.ModelAdmin):
    list_display = ('article', 'brand', 'lamp_type', 'power_watts', 'price')
    list_filter = ('lamp_type', 'has_dimmer', 'color')
    search_fields = ('article', 'brand', 'description')
    ordering = ('-created_at',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'lamp', 'quantity')
    search_fields = ('cart__user__username', 'lamp__article')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('cart', 'sales_manager', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('cart__user__username', 'sales_manager__username')
