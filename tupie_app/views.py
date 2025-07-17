from django.shortcuts import render
from .models import Item

# Create your views here.
def home(request):
    items = Item.objects.filter(available=True).order_by('-created_at')[:8]
    return render(request, 'tupie_app/home.html', {'items': items})

def list_item(request):
    return render(request, 'tupie_app/list_item.html')

def about(request):
    return render(request, 'tupie_app/about.html')

def donation(request):
    return render(request, 'tupie_app/donation.html')

