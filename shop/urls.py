
from django.urls import path
from .import views

urlpatterns = [
    path('', views.home), 
    path('product/<int:id>/',views.product),
    path('product_reviews/<int:id>/', views.product_reviews, name='product_reviews'),
    path('cart/',views.cart),
    path('add_cart/<int:id>/',views.add_cart),
    path('buy_now/<int:id>/',views.buy_now, name='buy_now'),
    path('remove_cart/<int:id>/',views.remove_cart),
    path('increase/<int:id>/',views.increase_qty),
    path('decrease/<int:id>/',views.decrease_qty),
    path('register/',views.register),
    path('login/',views.login),
    path('login_check/',views.login_check),
    path('logout/',views.logout),
    path('profile/', views.profile, name='profile'),
    # Checkout flow
    path('checkout/order-summary/', views.checkout_order_summary, name='checkout_order_summary'),
    path('checkout/shipping/', views.checkout_shipping, name='checkout_shipping'),
    path('checkout/payment/', views.checkout_payment, name='checkout_payment'),
    path('checkout/success/<int:order_id>/', views.checkout_success, name='checkout_success'),
    # Quick view and wishlist
    path('quick_view/<int:id>/', views.quick_view, name='quick_view'),
    path('add_wishlist/<int:id>/', views.add_wishlist, name='add_wishlist'),
    path('remove_wishlist/<int:id>/', views.remove_wishlist, name='remove_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
]
