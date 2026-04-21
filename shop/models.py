from django.db import models

class ProductImage(models.Model):
    product = models.ForeignKey('Product', related_name='images', on_delete=models.CASCADE)
    image = models.FileField(upload_to='products/')
    
    def __str__(self):
        return f"Image for {self.product.name}"

class Product(models.Model):
    name= models.CharField(max_length=100)
    price = models.IntegerField()
    image = models.FileField(upload_to='products/')
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
    image = models.FileField(upload_to='posters/')
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
    password = models.CharField(max_length=20)

    def __str__(self):
        return self.email  
