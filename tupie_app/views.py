from django.shortcuts import render, redirect, resolve_url
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from .models import Item, Region
from .forms import ItemForm
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

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
            user = form.save()  # Create the user
            auth_login(request, user)  # ✅ Auto-login after registration
            messages.success(request, f"Welcome {user.username}, your account was created and you are now logged in!")
            return redirect('home')  # Go to home or any other page
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = UserCreationForm()

    return render(request, 'tupie_app/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        next_url = request.GET.get('next') or resolve_url('tupie_app:home')
        if user:
            auth_login(request, user)
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid Username or Password.')
    return render(request, 'tupie_app/login.html')

def logout_view(request):
    auth_logout(request)
    return redirect('home')

def listed_items(request):
    item_list = Item.objects.filter(available=True).order_by('-created_at')
    paginator = Paginator(item_list, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'tupie_app/listed_items.html', {'page_obj': page_obj})

@login_required(login_url='/login/')
def list_item(request):
    regions = Region.objects.all()

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user
            item.save()
            messages.success(request, 'Item added successfully!')
            return redirect('home')
    else:
        form = ItemForm()

    return render(request, 'tupie_app/list_item.html', {
        'form': form,
        'regions': regions
    })

def get_regions(request):
    regions = Region.objects.all().values('region_code', 'region_name').order_by('region_name')
    return JsonResponse(list(regions), safe=False)


# def get_regions(request):
#     regions = Region.objects.all().order_by('region_name')
#     return render(request, 'tupie_app/list_item.html', {'regions': regions, 'form': form})

