from django.contrib import admin
from .models import Product,Cart,Review,UserRegister,OfferPoster,ProductImage,Wishlist,Order,OrderItem

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


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'order_date', 'total_amount', 'status', 'payment_method')
    list_filter = ('status', 'payment_method', 'order_date')
    search_fields = ('username', 'email', 'phone')
    readonly_fields = ('order_date',)
    inlines = [OrderItemInline]

    fieldsets = (
        ('Order Info', {
            'fields': ('username', 'order_date', 'total_amount', 'status', 'payment_method')
        }),
        ('Customer Details', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('address', 'city', 'state', 'postal_code', 'country')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ('order__id', 'product__name')
