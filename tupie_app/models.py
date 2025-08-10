from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Region model
class Region(models.Model):
    region_code = models.IntegerField(primary_key=True)
    region_name = models.TextField()
    country_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "regions"
        managed = False

    def __str__(self):
        return self.region_name

# Districts are subdivisions of regions
class District(models.Model):
    district_code = models.IntegerField(primary_key=True)
    district_name = models.TextField()
    region = models.ForeignKey(Region, on_delete=models.CASCADE, db_column="region_id")

    class Meta:
        db_table = "districts"
        managed = False

    def __str__(self):
        return self.district_name

# Wards are subdivisions of districts
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

# Place model
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
    
# Display a clean location string in templates
@property
def location_display(self):
    parts = [str(self.region), str(self.district), str(self.ward), str(self.place), self.street]
    return ", ".join(filter(None, parts))

# User verification status
VERIFICATION_CHOICES = [
    ('unverified', 'Unverified'),
    ('verified', 'Verified User'),
    ('organization', 'Verified Organization'),
    ('administrator', 'Administrator'),
]

#User Profile Model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    region = models.ForeignKey('Region', on_delete=models.SET_NULL, blank=True, null=True)
    district = models.ForeignKey('District', on_delete=models.SET_NULL, blank=True, null=True)
    ward = models.ForeignKey('Ward', on_delete=models.SET_NULL, blank=True, null=True)
    place = models.ForeignKey('Place', on_delete=models.SET_NULL, blank=True, null=True)
    
    id_document = models.ImageField(upload_to='verification_ids/', blank=True, null=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='unverified'
    )

    def __str__(self):
        return f"{self.user.username} - {self.verification_status} - {self.region}  - {self.district} - {self.ward} - {self.place}" if self.user else "Unlinked Profile"

# Item model
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
    created_at = models.DateTimeField(auto_now_add=True)
    available = models.BooleanField(default=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True, blank=True)
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, blank=True)
    street = models.CharField(max_length=255, blank=True, null=True)

    image1 = models.ImageField(upload_to='items/', blank=True, null=True) 
    image2 = models.ImageField(upload_to='items/', blank=True, null=True)
    image3 = models.ImageField(upload_to='items/', blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.owner.username} ({self.category})"

# Item Images
class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='items/')

    def __str__(self):
        return f"Image for {self.item.title}"
    
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
    
    def save(self, *args, **kwargs):
        if not self.owner:
            self.owner = self.item.owner
        super().save(*args, **kwargs)
    #Prevent duplicate requests for the same item by the same user
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['item', 'requester'], name='unique_item_request')
        ]


# Message model
class Conversation(models.Model):
    participants = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation between {[user.username for user in self.participants.all()]}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}"
    