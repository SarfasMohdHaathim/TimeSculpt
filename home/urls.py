from django.urls import path
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('watch/<str:watch_name>/<int:watch_id>/', WatchDetailView.as_view(), name='watch_detail'),
    path('watch/', WatchView.as_view(), name='watch_detail'),
    path('cart/', CartView.as_view(), name='cart_view'),
    path('cart/checkout/', CartView.as_view(), name='cart_checkout'),
    path('checkout/', CheckOut.as_view(), name='checkout'),
    path('add/address/', ShippingAddress.as_view(), name='add_address'),
    path('userlogin/', RegisterView.as_view(), name='user_login'),
    path('userlogout',userlogout,name="userlogout"),
    path('add-to-cart/<int:pk>/', AddToCartView.as_view(), name='addCart'),
    path('payment/done/', payment_done, name='payment_done'),
    path('cart/delete/<int:pk>/', delete_cart_item, name='delete_cart_item'),
    path('orders/complete/', orders, name='orders'),
    path('orders/', orders_page, name='orders_page'),
]