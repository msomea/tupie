from django.shortcuts import render, redirect, resolve_url, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.models import User
from .models import Item, Region, District, Ward, Street, Place,ItemRequest, Message, Conversation, User, UserProfile
from .forms import SignUpForm, UserProfileUpdateForm, ItemForm, MessageForm
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import ItemForm, MessageForm
from django.template.loader import render_to_string
from django.db.models import Q
from django.db import IntegrityError
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

#Account managements
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            next_url = request.GET.get('next') or resolve_url('tupie_app:home')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'tupie_app/accounts/login.html', {'form': form})


def logout_view(request):
    auth_logout(request)
    return redirect('tupe_app:home')

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        phone_number = request.POST.get('phone_number', '').strip()
        email = request.POST.get('email', '').strip().lower()

        # Validate phone number
        if not phone_number:
            messages.error(request, 'Phone number is required.')
            return render(request, 'tupie_app/accounts/signup.html', {'form': form})

        if UserProfile.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'Phone number is already registered.')
            return render(request, 'tupie_app/accounts/signup.html', {'form': form})

        # Validate email
        if not email:
            messages.error(request, 'Email is required.')
            return render(request, 'tupie_app/accounts/signup.html', {'form': form})

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already in use. Please use a different email.')
            return render(request, 'tupie_app/accounts/signup.html', {'form': form})

        # Validate form
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.email = email
                user.is_active = False  # Deactivate until email verification
                user.save()

                # Ensure profile exists
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.phone_number = phone_number
                profile.save()

                # Prepare email verification
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                verify_url = request.build_absolute_uri(
                    reverse('tupie_app:verify_email', kwargs={'uidb64': uid, 'token': token})
                )

                subject = 'Verify your email address'
                message = render_to_string('tupie_app/accounts/email_verification.html', {
                    'user': user,
                    'verify_url': verify_url
                })

                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

                messages.success(request, 'Account created. Please check your email to verify your account.')
                return redirect('tupie_app:login')

            except IntegrityError:
                messages.error(request, 'Something went wrong. Please try again.')

        else:
            messages.error(request, 'Please correct the errors in the form.')

    else:
        form = SignUpForm()

    return render(request, 'tupie_app/accounts/signup.html', {'form': form})

def verify_email(request, uidb64, token):
    UserModel = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Email verified! You can now log in.')
        return redirect('tupie_app:login')
    else:
        messages.error(request, 'Verification link is invalid or expired.')
        return redirect('tupie_app:login')


@login_required
def update_profile(request):
    profile = request.user.userprofile
    if request.method == "POST":
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)

            if 'id_document' in request.FILES:
                profile.verification_status = 'pending'
                messages.info(request, "Your verification is now pending review.")

            profile.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('tupie_app:update_profile')
    else:
        form = UserProfileUpdateForm(instance=profile)

    return render(request, 'tupie_app/accounts/profile_update.html', {'form': form})

# Other views
def home(request):
    items = Item.objects.filter(available=True).order_by('-created_at')[:6]
    return render(request, 'tupie_app/home.html', {'items': items})

def about(request):
    return render(request, 'tupie_app/about.html')

def donation(request):
    return render(request, 'tupie_app/donation.html')


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
        return render(request, "tupie_app/partials/_items_grid.html", {"page_obj": page_obj, 'categories': categories })
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
            return redirect('tupie_app:home')
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
    
    convo_data = []
    for convo in conversations:
        other_users = convo.participants.exclude(id=request.user.id)
        unread_count = convo.messages.filter(is_read=False, receiver=request.user).count()
        convo_data.append({
            'conversation': convo,
            'other_users': other_users,
            'unread_count': unread_count,
        })

    unread_total = Message.objects.filter(receiver=request.user, is_read=False).count()

    return render(request, 'tupie_app/messages/inbox.html', {
        'convo_data': convo_data,
        'unread_count': unread_total,
    })

# AJAX for messages
@login_required
def start_conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    # Prevent chatting with self
    if other_user == request.user:
        messages.warning(request, "You cannot start a conversation with yourself.")
        return redirect('inbox')

    # Get existing conversation or create new
    conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()

    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.set([request.user, other_user])

    return redirect('tupie_app:conversation', conversation_id=conversation.id)

# Conversation view
@login_required
def conversation(request, conversation_id):
    conversation = get_object_or_404(
        Conversation.objects.prefetch_related('messages__sender', 'messages__receiver'), 
        id=conversation_id
    )

    if request.user not in conversation.participants.all():
        messages.error(request, "You are not a participant in this conversation.")
        return redirect('tupie_app:inbox')

    # Identify the other participant
    other_user = conversation.participants.exclude(id=request.user.id).first()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = other_user
            message.conversation = conversation
            message.save()

            if request.is_ajax():  # If sent via AJAX
                return JsonResponse({
                    'success': True,
                    'message_id': message.id,
                    'content': message.content,
                    'sender': request.user.username,
                    'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                })

            return redirect('tupie_app:conversation', conversation_id=conversation.id)
    else:
        form = MessageForm()

    # Mark unread messages as read
    conversation.messages.filter(is_read=False, receiver=request.user).update(is_read=True)

    unread_total = Message.objects.filter(receiver=request.user, is_read=False).count()

    return render(request, 'tupie_app/messages/conversation.html', {
        'conversation': conversation,
        'other_user': other_user,
        'form': form,
        'unread_count': unread_total
    })

# AJAX Send and Fetch messages
@login_required
def ajax_send_fetch_message(request, conversation_id):
    conversation = get_object_or_404(
        Conversation.objects.prefetch_related('messages__sender', 'messages__receiver'),
        id=conversation_id
    )

    if request.user not in conversation.participants.all():
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # Handle sending new message
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            other_user = conversation.participants.exclude(id=request.user.id).first()
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                receiver=other_user,
                content=content
            )

    # Fetch all messages and mark unread as read
    conversation.messages.filter(is_read=False, receiver=request.user).update(is_read=True)

    messages_html = render_to_string(
        'tupie_app/messages/_messages_partial.html',
        {'conversation': conversation, 'request': request}
    )

    unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()

    return JsonResponse({
        'html': messages_html,
        'unread_count': unread_count
    })

