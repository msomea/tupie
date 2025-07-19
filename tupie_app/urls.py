from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Home & static pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('donation/', views.donation, name='donation'),

    # Authentication
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Item listing
    path('list_item/', views.list_item, name='list_item'),
    path('listed_items/', views.listed_items, name='listed_items'),
    path("item/<int:pk>/", views.item_detail, name="item_detail"),
    path("item/<int:pk>/request/", views.request_item, name="request_item"),

    # AJAX API for Regions
    path("get_districts/", views.get_districts, name="get_districts"),
    path("get_wards/", views.get_wards, name="get_wards"),
    path("get_places/", views.get_places, name="get_places"),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
