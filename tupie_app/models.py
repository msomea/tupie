from django.db import models

# Create your models here.

class Item(models.Model):
    CATEGORY_CHOICES = [
        ("books", 'Books'),
        ('clothing', 'Clothing'),
        ('electronic', 'Electronic'),
        ('food', 'Food'),
        ('furniture', 'Furniture'),
        ('home_appliance', 'Home Appliance'),
        ('kitchenware', 'Kitchenware'),
        ('office_supplies', 'Office Supplies'),
        ('personal_hygiene', 'Personal Hygiene'),
        ('shoes', 'Shoes'),
        ('toys_and_games', 'Toys and Games'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    image = models.ImageField(upload_to='items/', blank=True, null=True)
    created_at =models.DateTimeField(auto_now_add=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.title