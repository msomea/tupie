from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    return render(request, 'tupie_app/home.html')

def list_item(request):
    return render(request, 'tupie_app/list_item.html')

def about(request):
    return render(request, 'tupie_app/about.html')

def donation(request):
    return render(request, 'tupie_app/donation.html')

