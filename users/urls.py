from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/photo/<int:photo_id>/delete/', views.delete_pet_photo, name='delete_pet_photo'),
    path('u/<str:username>/', views.public_profile_view, name='public_profile'),
]
