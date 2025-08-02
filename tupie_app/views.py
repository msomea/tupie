from django.shortcuts import render, redirect, resolve_url, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Item, Region, District, Ward, Place, UserProfile, ItemRequest, Message, Conversation, User
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import ItemForm, SignUpForm, UserProfileUpdateForm, MessageForm
from django.db.models import Prefetch
from django.template.loader import render_to_string
from django.db.models import Q
from django.db import IntegrityError



# Create your views here.
def home(request):
    items = Item.objects.filter(available=True).order_by('-created_at')[:6]
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

        #  Validate phone number is provided
        if not phone:
            messages.error(request, 'Phone number is required.')
            return render(request, 'tupie_app/register.html', {'form': form})

        #  Check if phone already exists before saving user
        if UserProfile.objects.filter(phone_number=phone).exists():
            messages.error(request, 'This phone number is already registered. Please use another one.')
            return render(request, 'tupie_app/register.html', {'form': form})

        if form.is_valid():
            try:
                #  Create user normally
                user = form.save()  # Auto-creates UserProfile via signal
                user.userprofile.phone_number = phone
                user.userprofile.save()

                #  Auto login
                auth_login(request, user)
                messages.success(request, 'Account created & logged in!')
                return redirect('home')

            except IntegrityError:
                #  Fallback: If race condition still triggers DB unique error
                messages.error(request, 'This phone number is already registered.')
                return render(request, 'tupie_app/register.html', {'form': form})

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


def owner_profile(request, user_id):
    owner = get_object_or_404(UserProfile, user__id=user_id)
    return render(request, 'tupie_app/owner_profile.html', {'owner': owner})

def listed_items(request):
    item_list = Item.objects.filter(available=True).order_by('-created_at')
    paginator = Paginator(item_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    #  Get category choices from model
    categories = Item._meta.get_field("category").choices 
    # If AJAX refresh -> return only grid fragment
    if request.GET.get("ajax"):
        return render(request, "tupie_app/_items_grid.html", {"page_obj": page_obj, 'categories': categories })
    return render(request, 'tupie_app/listed_items.html', {'page_obj': page_obj, 'categories': categories })
  

def item_detail(request, pk):
    #Show full details of a single item
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

    #   Prevent requesting your own item
    if item.owner == request.user:
        messages.error(request, "You cannot request your own item.")
        return redirect("item_detail", pk=item.id)

    #   Check if item is already unavailable
    if not item.available:
        messages.warning(request, "This item is no longer available.")
        return redirect("item_detail", pk=item.id)

    #   Prevent duplicate request from same user
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
        messages.success(request, "  Your request has been sent to the owner!")
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
        item_request.item.save()              #   Save the item so it's removed from listings
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

# AJAX Search for items
def get_districts(request):
    region_id = request.GET.get('region')
    districts = District.objects.filter(region_id=region_id).order_by('district_name').values('district_code', 'district_name')
    return JsonResponse(list(districts), safe=False)

def get_wards(request):
    district_id = request.GET.get('district')
    wards = Ward.objects.filter(district_id=district_id).order_by('ward_name').values('ward_code', 'ward_name')
    return JsonResponse(list(wards), safe=False)

def get_places(request):
    ward_id = request.GET.get("ward")
    if not ward_id:
        return JsonResponse([], safe=False)

    # Get all places for that ward
    places = Place.objects.filter(ward_id=ward_id).values("id", "place_name")

    unique_places = []
    seen_names = set()

    for p in places:
        if p["place_name"] not in seen_names:
            seen_names.add(p["place_name"])
            unique_places.append(p)  # Keep the first occurrence (valid id)

    return JsonResponse(unique_places, safe=False)

def search_items(request):
    query = request.GET.get("q", "").strip()
    category_filter = request.GET.get("category", "").strip()

    items = Item.objects.filter(available=True)

    if query:
        items = items.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(region__region_name__icontains=query) |
            Q(district__district_name__icontains=query) |
            Q(ward__ward_name__icontains=query)
        )

    if category_filter:
        items = items.filter(category=category_filter)

    items = items.order_by("-created_at")[:30]  # Limit for AJAX

    # Render only the grid part
    html = render_to_string("tupie_app/partials/items_grid.html", {"items": items})
    return HttpResponse(html)

@login_required
def user_profile_update(request):
    profile = request.user.userprofile
    
    if request.method == "POST":
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            updated_profile = form.save(commit=False)

            # If user uploads an ID, set status to pending
            if 'id_document' in request.FILES:
                updated_profile.verification_status = 'pending'
                messages.info(request, "Your verification is now pending review.")

            updated_profile.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('user_profile_update')  # reload page after save
    else:
        form = UserProfileUpdateForm(instance=profile)

    return render(request, 'tupie_app/user_profile_update.html', {'form': form})

@login_required
def send_message(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.save()
            return redirect('inbox')
    else:
        form = MessageForm()
    return render(request, 'tupie_app/messages/send_message.html', {'form': form, 'receiver': receiver})

@login_required
def start_conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    # Avoid chatting with self
    if other_user == request.user:
        return redirect('inbox')

    # Check if conversation exists
    conversation = Conversation.objects.filter(participants=request.user).filter(participants=other_user).first()
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.set([request.user, other_user])

    return redirect('conversation', conversation_id=conversation.id)


@login_required
def inbox(request):
    conversations = Conversation.objects.filter(participants=request.user)

    # Mark all unread messages as read except those sent by the user
    for convo in conversations:
        convo.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()

    # Prepare a list of conversations along with their other participants
    convo_data = []
    for convo in conversations:
        other_users = convo.participants.exclude(id=request.user.id)
        convo_data.append({
            'conversation': convo,
            'other_users': other_users,
        })

    context = {
        'convo_data': convo_data,
        'unread_count': unread_count,
    }
    return render(request, 'tupie_app/messages/inbox.html', context)



@login_required
def send_message(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)

    # Find or create a conversation
    conversation = Conversation.objects.filter(participants=request.user).filter(participants=receiver).first()
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.set([request.user, receiver])

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.conversation = conversation
            message.save()
            return redirect('conversation', conversation_id=conversation.id)
    else:
        form = MessageForm()

    return render(request, 'tupie_app/messages/send_message.html', {'form': form, 'receiver': receiver})

@login_required
def conversation(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)

    if request.user not in conversation.participants.all():
        return redirect('inbox')

    # Get the other participant
    other_user = conversation.participants.exclude(id=request.user.id).first()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.receiver = other_user
            message.save()
            return redirect('conversation', conversation_id=conversation.id)
    else:
        form = MessageForm()

    # Mark all messages from the other user as read
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()

    return render(request, 'tupie_app/messages/conversation.html', {
        'conversation': conversation,
        'form': form,
        'other_user': other_user,
        'unread_count': unread_count,
    })

