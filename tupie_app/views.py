from django.shortcuts import render, redirect, resolve_url
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Item, Region, District, Ward, Place, UserProfile, ItemRequest
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import ItemForm, SignUpForm
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch


# Create your views here.
def home(request):
    items = Item.objects.filter(available=True).order_by('-created_at')[:8]
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
            return render(request, 'tupie_app/register.html', {'form': form})
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
    # If AJAX refresh -> return only grid fragment
    if request.GET.get("ajax"):
        return render(request, "tupie_app/_items_grid.html", {"page_obj": page_obj})
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
    
@login_required
def request_item(request, pk):
    item = get_object_or_404(Item, id=pk)

    # ✅ Prevent requesting your own item
    if item.owner == request.user:
        messages.error(request, "You cannot request your own item.")
        return redirect("item_detail", pk=item.id)

    # ✅ Check if item is already unavailable
    if not item.available:
        messages.warning(request, "This item is no longer available.")
        return redirect("item_detail", pk=item.id)

    # ✅ Prevent duplicate request from same user
    existing = ItemRequest.objects.filter(item=item, requester=request.user)
    if existing.exists():
        messages.info(request, "You have already requested this item.")
        return redirect("item_detail", pk=item.id)
    else:
        ItemRequest.objects.create(
            item=item,
            requester=request.user,
            owner=item.owner,
            message="Requesting this item."  # Can later add custom messages
        )
        messages.success(request, "✅ Your request has been sent to the owner!")
        return redirect("outgoing_requests_dashboard")

@login_required
def requests_dashboard(request):
    # Show only requests for the logged-in user's items
    my_requests = ItemRequest.objects.filter(owner=request.user).select_related('item', 'requester').order_by('-created_at')
    return render(request, "tupie_app/requests_dashboard.html", {"my_requests": my_requests})

@login_required
def update_request_status(request, request_id, action):
    item_request = get_object_or_404(ItemRequest, id=request_id, owner=request.user)

    if action == "accept":
        item_request.status = "accepted"
        item_request.item.available = False   # Mark as unavailable
        item_request.item.save()              # ✅ Save the item so it's removed from listings
        item_request.save()
        # Decline all other pending requests for the same item
        ItemRequest.objects.filter(item=item_request.item, status="pending").exclude(id=item_request.id).update(status="declined")
        messages.success(request, f"You accepted {item_request.requester.username}'s request for {item_request.item.title}.")
    elif action == "decline":
        item_request.status = "declined"
        item_request.save()
        messages.warning(request, f"You declined {item_request.requester.username}'s request.")
    else:
        messages.error(request, "Invalid action.")
        return redirect("requests_dashboard")
    
    return redirect("requests_dashboard")

@login_required
def outgoing_requests_dashboard(request):
    my_outgoing_requests = ItemRequest.objects.filter(
        requester=request.user
    ).select_related('item', 'owner').order_by('-created_at')

    return render(
        request,
        "tupie_app/outgoing_requests_dashboard.html",
        {"my_outgoing_requests": my_outgoing_requests}
    )


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
