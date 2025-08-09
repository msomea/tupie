from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.urls import reverse_lazy

app_name = 'tupie_app'

urlpatterns = [
    # Accounts
    path('signup/', views.signup_view, name='signup'),
    path('profile/', views.update_profile, name='update_profile'),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path("resend-verification/", views.resend_verification, name="resend_verification"),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Password reset
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='tupie_app/accounts/password_reset.html',
        email_template_name='tupie_app/accounts/password_reset_email.html',
        subject_template_name='tupie_app/accounts/password_reset_subject.txt',
        success_url=reverse_lazy('tupie_app:password_reset_done')
    ), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='tupie_app/accounts/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='tupie_app/accounts/password_reset_confirm.html',
        success_url=reverse_lazy('tupie_app:password_reset_complete')
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='tupie_app/accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Home & static pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('donation/', views.donation, name='donation'),

    # Profile view
    path("owner/<int:user_id>/", views.owner_profile, name="owner_profile"),

    # Item listing
    path('add_item/', views.add_item, name='add_item'),
    path('listed_items/', views.listed_items, name='listed_items'),
    path("item/<int:pk>/", views.item_detail, name="item_detail"),
    path("item/<int:pk>/request/", views.request_item, name="request_item"),

    # Item Request
    path("requests_dashboard/", views.requests_dashboard, name="requests_dashboard"),
    path("update_request/<int:request_id>/<str:action>/", views.update_request_status, name="update_request_status"),
    path("my-requests/", views.outgoing_requests_dashboard, name="outgoing_requests_dashboard"),


    # AJAX API for Regions
    path("get_districts/", views.get_districts, name="get_districts"),
    path("get_wards/", views.get_wards, name="get_wards"),
    path("get_places/", views.get_places, name="get_places"),

    # Search for items
    path("search-items/", views.search_items, name="search_items"),

    # Message URLs
    path('messages/', views.inbox, name='inbox'),
    path('messages/start/<int:user_id>/', views.start_conversation, name='start_conversation'),
    path('messages/<int:conversation_id>/', views.conversation, name='conversation'),
    path('messages/ajax-send-fetch/<int:conversation_id>/', views.ajax_send_fetch_message, name='ajax_send_fetch_message'),



]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
