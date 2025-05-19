from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.LampListView.as_view(), name='lamp_list'),
    path('about/', views.about, name='about'),
    path('lamp/<int:pk>/', views.LampDetailView.as_view(), name='lamp_detail'),
] 