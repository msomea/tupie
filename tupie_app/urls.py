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

    # AJAX API for Regions
    path('get_regions/', views.get_regions, name='get_regions'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
