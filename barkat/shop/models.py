from django.db import models

class Product(models.Model):
    name= models.CharField(max_length=100)
    price = models.IntegerField()
    image = models.FileField(upload_to='products/')
    description =models.TextField()

    def __str__(self):
        return self.name
    

class Cart(models.Model):
    username = models.CharField(max_length=100) 
    product = models.ForeignKey(Product,on_delete=models.CASCADE)    #! Why foreign key = one product can be in many cart
    quantity = models.IntegerField(default=1)


class Review(models.Model):
    username = models.CharField(max_length=50)
    product  = models.ForeignKey(Product,on_delete=models.CASCADE)
    comment = models.TextField()

class UserRegister(models.Model):
    name =models.CharField(max_length=100)
    email= models.EmailField()
    password = models.CharField(max_length=20)

    def __str__(self):
        return self.email  
