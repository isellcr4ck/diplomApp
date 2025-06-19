from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('account/', views.account_view, name='account'),
    path('catalog/', views.catalog, name='catalog'),
    path('account/edit/', views.edit_profile, name='edit_profile'),
    path('cart/', views.cart_view, name='cart'),
    path('catalog/<int:currency_id>/', views.currency_detail, name='currency_detail'),
    path('cart/add/<int:currency_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('contacts/', views.contacts, name='contacts'),
    path('reviews/', views.reviews, name='reviews'),
    path('exchange/', views.exchange_view, name='exchange'),
]