from django.contrib import admin
from .models import Item, UserProfile

# Register your models here.
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'available', 'created_at')
    list_filter = ('category', 'available')
    search_fields = ('title', 'description')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'verification_status')
    list_filter = ('verification_status',)