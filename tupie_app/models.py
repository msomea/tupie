from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

# User verification status
VERIFICATION_CHOICES = [
    ('unverified', 'Unverified'),
    ('verified', 'Verified User'),
    ('organization', 'Verified Organization'),
    ('administrator', 'Administrator'),
]

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

# Region - Place
class Region(models.Model):
    region_code = models.IntegerField(primary_key=True)
    region_name = models.TextField()
    country_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "regions"
        managed = False

    def __str__(self):
        return self.region_name


class District(models.Model):
    district_code = models.IntegerField(primary_key=True)
    district_name = models.TextField()
    region = models.ForeignKey(Region, on_delete=models.CASCADE, db_column="region_id")

    class Meta:
        db_table = "districts"
        managed = False

    def __str__(self):
        return self.district_name


class Ward(models.Model):
    ward_code = models.IntegerField(primary_key=True)
    ward_name = models.TextField()
    district = models.ForeignKey(District, on_delete=models.CASCADE, db_column="district_id")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, db_column="region_id")

    class Meta:
        db_table = "wards"
        managed = False

    def __str__(self):
        return self.ward_name


class Place(models.Model):
    id = models.AutoField(primary_key=True)
    place_name = models.TextField()
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, db_column="ward_id")
    district = models.ForeignKey(District, on_delete=models.CASCADE, db_column="district_id")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, db_column="region_id")

    class Meta:
        db_table = "places"
        managed = False

    def __str__(self):
        return self.place_name

# Street   
class Street(models.Model):
    name = models.TextField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name or "No Street"



class Item(models.Model):
    CATEGORY_CHOICES = [
        ("beverages", "Beverages"),
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
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    image = models.ImageField(upload_to='items/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    available = models.BooleanField(default=True)

    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True, blank=True)
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, blank=True)

    street = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userprofile")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_CHOICES,
        default='unverified'
    )

    def __str__(self):
        return f"{self.user.username}'s profile"
    
# Item request model
class ItemRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="requests")
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="item_requests")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_requests")
    message = models.TextField(blank=True, null=True)  # Optional message from requester
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.requester.username} → {self.item.title} ({self.status})"

