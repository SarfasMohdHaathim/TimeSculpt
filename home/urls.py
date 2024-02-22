from django.urls import path
from . import views

urlpatterns = [
    # api
    path('dashboard/watches/', views.list_watches, name='list_watches'),
    path('dashboard/orders/', views.list_orders, name='list_orders'),
    path('dashboard/users/', views.list_users, name='list_users'),
    path('dashboard/staff/', views.list_staffs, name='list_staffs'),
    path('dashboard/watches/create/', views.create_watch, name='create_watch'),
    path('dashboard/watches/<int:pk>/', views.watch_detail, name='watch_detail'),
    path('dashboard/watches/<int:pk>/delete/', views.delete_watch, name='delete_watch'),
    path('dashboard/watches/<int:pk>/edit/', views.edit_watch, name='edit_watch'),
    path('dashboard/watch/image/create/', views.WatchImageCreateAPIView.as_view(), name='watchimage-create'),
    path('dashboard/watch/image/delete/<int:pk>/', views.WatchImageDeleteAPIView.as_view(), name='watchimage-delete'),
    path('dashboard/watch/image/<int:pk>/', views.watch_image_list, name='watch_image_list'),

    # web    
    path('', views.HomeView.as_view(), name='home'),
    path('watch/', views.WatchView.as_view(), name='watch'),
    path('watch/<str:watch_name>/<int:watch_id>/', views.WatchDetailView.as_view(), name='watch_detail'),
    path('cart/', views.CartView.as_view(), name='cart_view'),
    path('cart/checkout/', views.CartView.as_view(), name='cart_checkout'),
    path('checkout/', views.CheckOut.as_view(), name='checkout'),
    path('add/address/', views.ShippingAddress.as_view(), name='add_address'),
    # path('register/', views.RegisterView.as_view(), name='register'),
    path('userlogin/', views.userlogin, name='userlogin'),
    path('userlogout', views.userlogout,name="userlogout"),
    path('add-to-cart/<int:pk>/', views.AddToCartView.as_view(), name='addCart'),
    path('payment/done/', views.payment_done, name='payment_done'),
    path('cart/delete/<int:pk>/', views.delete_cart_item, name='delete_cart_item'),
    path('orders/complete/', views.orders, name='orders'),
    path('orders/', views.orders_page, name='orders_page'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('account_address/', views.account_address, name='account_address'),
    path('wishlist', views.wishlist,name="wishlist"),
    path('brands', views.brands,name="brands"),
    path('stores', views.stores,name="stores"),
    path('offer', views.offers,name="offer"),
    path('add-to-wishlist/<int:pk>/', views.addtowishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:pk>/', views.removewishlist, name='remove_from_wishlist'),
]
