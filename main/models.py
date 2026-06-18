from django.db import models

class Admin(models.Model):
    Username=models.CharField(max_length=120)
    Password=models.CharField(max_length=120)

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Bharatnatyam', 'Bharatnatyam'),
        ('Kuchipudi', 'Kuchipudi'),
        ('Mohiniyattam', 'Mohiniyattam'),
        ('Jewellery','Jewellery'),
        ('Antique Jewellery','Antique Jewellery'),
        ('Hair & Floral','Hair & Floral Accessories'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.CharField(max_length=50) 
    description = models.TextField()
    sizes = models.CharField(max_length=200)
    image = models.ImageField(upload_to='product_images/',null=True,blank=True)

class Inquiry(models.Model):
    customer_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    product_interest = models.CharField(max_length=200)
    status = models.CharField(max_length=50, default='Pending') # Pending, Shipped, Resolved
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.product_interest}"


# Create your models here.
