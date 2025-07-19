from django.shortcuts import render, redirect, resolve_url
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Item, Region, UserProfile
from .forms import ItemForm, CustomUserCreationForm
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
        username = request.POST.get('username')
        phone = request.POST.get('phone_number')
        password = request.POST.get('password1')

        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # This triggers UserProfile auto-create
            # Update phone number
            user.userprofile.phone_number = phone
            user.userprofile.save()

            # ✅ Auto-login new user
            auth_login(request, user)
            messages.success(request, 'Account created & logged in!')
            return redirect('home')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = UserCreationForm()

    return render(request, 'tupie_app/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            next_url = request.GET.get('next') or resolve_url('home')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'tupie_app/login.html', {'form': form})

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

