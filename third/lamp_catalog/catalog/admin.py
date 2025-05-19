from django.contrib import admin
from .models import Lamp, LampType

@admin.register(LampType)
class LampTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Lamp)
class LampAdmin(admin.ModelAdmin):
    list_display = ('article', 'brand', 'lamp_type', 'power_watts', 'price')
    list_filter = ('lamp_type', 'has_dimmer', 'color')
    search_fields = ('article', 'brand', 'description')
    ordering = ('-created_at',)
