from django.contrib import admin
from .models import Product,Cart,Review,UserRegister,OfferPoster,ProductImage,Wishlist

# Register your models here.
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')
    search_fields = ('product__name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','price','is_new_arrival','offer_text','fabric','color','work')
    list_filter = ('is_new_arrival','fabric','color','work')
    search_fields = ('name','description','fabric','color')
    fieldsets = (
        ('Basic Info', {
            'fields': ('name','price','image','description')
        }),
        ('Saree Details', {
            'fields': ('fabric','color','work','occasion','length','blouse_piece')
        }),
        ('Additional Info', {
            'fields': ('wash_care','shipping_info','is_new_arrival','offer_text')
        }),
    )

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('username','product','quantity')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('username','product','rating','created_at')
    list_filter = ('rating',)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('username','product','added_at')

@admin.register(UserRegister)
class UserRegisterAdmin(admin.ModelAdmin):
    list_display = ('email','name')

@admin.register(OfferPoster)
class OfferPosterAdmin(admin.ModelAdmin):
    list_display = ('title','active')
    list_filter = ('active',)
