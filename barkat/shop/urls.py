
from django.urls import path
from .import views

urlpatterns = [
    path('', views.home), 
    path('product/<int:id>/',views.product),
    path('cart/',views.cart),
    path('add_cart/<int:id>/',views.add_cart),
    path('remove_cart/<int:id>/',views.remove_cart),
    path('increase/<int:id>/',views.increase_qty),
    path('decrease/<int:id>/',views.decrease_qty),
    path('register/',views.register),
    path('login/',views.login),
    path('login_check/',views.login_check),
    path('logout/',views.logout),
]