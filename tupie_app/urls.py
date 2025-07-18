from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import signup

urlpatterns = [
    path('', views.home, name='home'),
    path('list-item', views.list_item, name='list_item'),
    path('about', views.about, name='about'),
    path('donation', views.donation, name='donation'),
    path('list_item', views.list_item, name='list_item'),
    path('listed_items', views.listed_items, name='listed_items'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('tupie_app.urls')),
]

urlpatterns += [
    path('signup/', signup, name='signup'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)