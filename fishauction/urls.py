# fishauction/urls.py
from django.contrib import admin
from django.urls import path, include
from auction import views as auction_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', auction_views.homepage, name='homepage'),
    path('accounts/login/', auction_views.user_login, name='login'),
    path('accounts/logout/', auction_views.user_logout, name='logout'),
    path('accounts/register/', auction_views.register, name='register'),
    path('auction/', include('auction.urls', namespace='auction')),
    path('fish/', auction_views.fish_list, name='fish_list'),
    path('fish/add/', auction_views.add_fish, name='add_fish'),
    path('fish/delete/<int:fish_id>/', auction_views.delete_fish, name='delete_fish'),
    path('users/', auction_views.user_list, name='user_list'),
    path('users/edit/<int:user_id>/', auction_views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', auction_views.delete_user, name='delete_user'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
