from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

class ProductImage(models.Model):
    product = models.ForeignKey('Product', related_name='images', on_delete=models.CASCADE)
    image = models.FileField(upload_to='products/')
    
    def save(self, *args, **kwargs):
        # Compress image before saving to reduce memory usage
        if self.image:
            self._compress_image()
        super().save(*args, **kwargs)
    
    def _compress_image(self):
        """Compress image to reduce file size and memory usage"""
        try:
            img = Image.open(self.image)
            
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            # Resize if too large (max 1200px width)
            max_width = 1200
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Compress and save
            img_io = BytesIO()
            img.save(img_io, format='JPEG', quality=75, optimize=True)
            img_io.seek(0)
            
            # Replace the file
            file_name = self.image.name.split('/')[-1].split('.')[0]
            self.image.save(f'{file_name}.jpg', ContentFile(img_io.getvalue()), save=False)
        except Exception as e:
            print(f"Error compressing image: {e}")
    
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
    
    def save(self, *args, **kwargs):
        # Compress main image before saving
        if self.image:
            self._compress_image()
        super().save(*args, **kwargs)
    
    def _compress_image(self):
        """Compress image to reduce file size and memory usage"""
        try:
            img = Image.open(self.image)
            
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            # Resize if too large (max 1200px width)
            max_width = 1200
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Compress and save
            img_io = BytesIO()
            img.save(img_io, format='JPEG', quality=75, optimize=True)
            img_io.seek(0)
            
            # Replace the file
            file_name = self.image.name.split('/')[-1].split('.')[0]
            self.image.save(f'{file_name}.jpg', ContentFile(img_io.getvalue()), save=False)
        except Exception as e:
            print(f"Error compressing image: {e}")


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
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.email  
