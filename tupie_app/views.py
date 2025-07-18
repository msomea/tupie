from django.shortcuts import render, redirect
from .models import Item
from .forms import ItemForm
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# Create your views here.
def home(request):
    items = Item.objects.filter(available=True).order_by('-created_at')[:12]
    return render(request, 'tupie_app/home.html', {'items': items})

def about(request):
    return render(request, 'tupie_app/about.html')

def donation(request):
    return render(request, 'tupie_app/donation.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def list_item(request):
    if request.method == 'POST':
        form =  ItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            print("Item listed successfully")
            return redirect('home')
        else:
            print("Form is not valid")
            print(form.errors)
    else:
        form = ItemForm()
    return render(request, 'tupie_app/list_item.html', {'form': form})

def listed_items(request):
    item_list = Item.objects.filter(available=True).order_by('-created_at')
    paginator = Paginator(item_list, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'tupie_app/listed_items.html', {'page_obj': page_obj})

