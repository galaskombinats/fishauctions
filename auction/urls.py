from django.urls import path
from . import views

app_name = 'auction'

urlpatterns = [
    path('', views.redirect_to_homepage, name='redirect_to_homepage'),
    path('list/', views.index, name='index'),
    path('<int:auction_id>/', views.auction_detail, name='auction_detail'),
    path('create/', views.create_auction, name='create_auction'),
    path('<int:auction_id>/bid/', views.place_bid, name='place_bid'),
    path('<int:auction_id>/end/', views.end_auction, name='end_auction'),
    path('<int:auction_id>/delete/', views.delete_auction, name='delete_auction'),
    path('fish/', views.fish_list, name='fish_list'),
    path('fish/add/', views.add_fish, name='add_fish'),
    path('fish/delete/<int:fish_id>/', views.delete_fish, name='delete_fish'),
    path('user_list/', views.user_list, name='user_list'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
]
