from django.shortcuts import render, redirect, resolve_url
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Item, Region, District, Ward, Place, UserProfile
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import ItemForm, SignUpForm
from django.shortcuts import get_object_or_404


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
        if not phone:
            messages.error(request, 'Phone number is required.')
        elif form.is_valid():
            user = form.save()  # Auto-creates UserProfile via signal
            user.userprofile.phone_number = phone
            user.userprofile.save()

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

def item_detail(request, pk):
    """Show full details of a single item"""
    item = get_object_or_404(Item, pk=pk)
    return render(request, "tupie_app/item_detail.html", {"item": item})

@login_required(login_url='/login/')
def list_item(request):
    regions = Region.objects.all().order_by('region_name')

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user
            item.save()
            return redirect('home')
    else:
        form = ItemForm()

    context = {
        'form': form,
        'regions': regions,
    }
    return render(request, 'tupie_app/list_item.html', context)

def get_districts(request):
    region_id = request.GET.get('region')
    districts = District.objects.filter(region_id=region_id).order_by('district_name').values('district_code', 'district_name')
    return JsonResponse(list(districts), safe=False)

def get_wards(request):
    district_id = request.GET.get('district')
    wards = Ward.objects.filter(district_id=district_id).order_by('ward_name').values('ward_code', 'ward_name')
    return JsonResponse(list(wards), safe=False)

def get_places(request):
    ward_id = request.GET.get('ward')
    places = Place.objects.filter(ward_id=ward_id).order_by('place_name').values('id', 'place_name')
    return JsonResponse(list(places), safe=False)
