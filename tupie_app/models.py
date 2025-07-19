from django.db import models

# Country
class Country(models.Model):
    id = models.AutoField(primary_key=True)
    iso = models.CharField(max_length=2, null=False)
    name = models.TextField(max_length=100, null=False)
    nicename = models.TextField(max_length=100, null=False)
    iso3 = models.CharField(max_length=3, null=True)
    numcode = models.IntegerField(null=True)
    phonecode = models.IntegerField(null=False)

    class Meta:
        db_table = 'countries'
        managed = False

    def __str__(self):
        return self.name

# Region
class Region(models.Model):
    region_name = models.TextField(max_length=100, unique=True)
    region_code = models.IntegerField(primary_key=True)
    country_id = models.ForeignKey(Country, on_delete=models.CASCADE, db_column='country_id', null=True)

    class Meta:
        db_table = 'regions'
        managed = False

    def __str__(self):
        return self.region_name
    
# Street   
class Street(models.Model):
    name = models.TextField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name or "No Street"



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
    owner = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    image = models.ImageField(upload_to='items/', blank=True, null=True)
    created_at =models.DateTimeField(auto_now_add=True)
    available = models.BooleanField(default=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    street = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title