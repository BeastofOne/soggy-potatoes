from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    # Forum home
    path('', views.ForumHomeView.as_view(), name='home'),

    # Category
    path('c/<slug:slug>/', views.CategoryDetailView.as_view(), name='category'),

    # Thread
    path('c/<slug:category_slug>/new/', views.CreateThreadView.as_view(), name='create_thread'),
    path('c/<slug:category_slug>/<slug:thread_slug>/', views.ThreadDetailView.as_view(), name='thread'),
    path('c/<slug:category_slug>/<slug:thread_slug>/reply/', views.create_reply, name='create_reply'),

    # Reactions
    path('react/', views.toggle_reaction, name='toggle_reaction'),
]
