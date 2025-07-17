from django.contrib import admin
from .models import Item

# Register your models here.
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'available', 'created_at')
    list_filter = ('category', 'available')
    search_fields = ('title', 'description')