from django.contrib import admin
from .models import Product,Cart,Review,UserRegister,OfferPoster

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','price','is_new_arrival','offer_text')
    list_filter = ('is_new_arrival',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('username','product','quantity')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('username','product')

@admin.register(UserRegister)
class UserRegisterAdmin(admin.ModelAdmin):
    list_display = ('email','name')

@admin.register(OfferPoster)
class OfferPosterAdmin(admin.ModelAdmin):
    list_display = ('title','active')
    list_filter = ('active',)
