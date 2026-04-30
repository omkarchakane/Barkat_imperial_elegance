from django.db import models
from django.conf import settings

# Use Cloudinary storage if configured
if settings.CLOUDINARY_URL:
    from cloudinary_storage.storage import MediaCloudinaryStorage
    storage = MediaCloudinaryStorage()
else:
    from django.core.files.storage import default_storage
    storage = default_storage

class ProductImage(models.Model):
    product = models.ForeignKey('Product', related_name='images', on_delete=models.CASCADE)
    image = models.FileField(upload_to='products/', storage=storage)
    
    def __str__(self):
        return f"Image for {self.product.name}"

class Product(models.Model):
    name= models.CharField(max_length=100)
    price = models.IntegerField()
    image = models.FileField(upload_to='products/', storage=storage)
    description =models.TextField()
    is_new_arrival = models.BooleanField(default=False)
    offer_text = models.CharField(max_length=100, blank=True, null=True)
    
    # Additional saree details
    fabric = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Silk, Cotton, Chiffon")
    color = models.CharField(max_length=50, blank=True, null=True)
    work = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Zari, Embroidery, Print")
    occasion = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Wedding, Festival, Casual")
    blouse_piece = models.BooleanField(default=True, help_text="Blouse piece included")
    wash_care = models.TextField(blank=True, null=True)
    shipping_info = models.TextField(blank=True, null=True)
    length = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 5.5 meters")


class OfferPoster(models.Model):
    title = models.CharField(max_length=150)
    image = models.FileField(upload_to='posters/', storage=storage)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    

class Cart(models.Model):
    username = models.CharField(max_length=100) 
    product = models.ForeignKey(Product,on_delete=models.CASCADE)    #! Why foreign key = one product can be in many cart
    quantity = models.IntegerField(default=1)


class Review(models.Model):
    username = models.CharField(max_length=50)
    product  = models.ForeignKey(Product,on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.IntegerField(default=5)  # 1-5 stars
    created_at = models.DateTimeField(auto_now_add=True)

class Wishlist(models.Model):
    username = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('username', 'product')  # Prevent duplicate wishlist items

    def __str__(self):
        return f"{self.username} - {self.product.name}"

class UserRegister(models.Model):
    name =models.CharField(max_length=100)
    email= models.EmailField()
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.email


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('upi', 'UPI'),
        ('phonepay', 'PhonePay'),
        ('googlepay', 'Google Pay'),
    ]
    
    username = models.CharField(max_length=100)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.IntegerField()
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    
    # Shipping Details
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='India')
    
    def __str__(self):
        return f"Order #{self.id} - {self.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField()  # Price at time of order
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
