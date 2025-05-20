from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.LampListView.as_view(), name='lamp_list'),
    path('about/', views.about, name='about'),
    path('lamp/<int:pk>/', views.LampDetailView.as_view(), name='lamp_detail'),
    path('lamp/<int:pk>/edit-description/', views.edit_lamp_description, name='edit_lamp_description'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:lamp_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/create-order/', views.create_order, name='create_order'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('merchandiser/products/', views.merchandiser_product_list, name='merchandiser_product_list'),
    path('merchandiser/products/<int:pk>/edit/', views.edit_lamp, name='edit_lamp'),
] 