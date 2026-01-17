from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
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

    # Password Reset (Django's built-in views)
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset.html',
             email_template_name='users/emails/password_reset_email.html',
             subject_template_name='users/emails/password_reset_subject.txt',
             success_url=reverse_lazy('users:password_reset_done')
         ), name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'
         ), name='password_reset_done'),

    path('password-reset/confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html',
             success_url=reverse_lazy('users:password_reset_complete')
         ), name='password_reset_confirm'),

    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'
         ), name='password_reset_complete'),

    # =============================================
    # SUPERUSER ADMIN DASHBOARD URLS
    # =============================================
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/products/', views.admin_products, name='admin_products'),
    path('admin-dashboard/badges/', views.admin_badges, name='admin_badges'),
    path('admin-dashboard/reports/', views.admin_reports, name='admin_reports'),
    path('admin-dashboard/reports/<int:report_id>/', views.handle_report, name='handle_report'),

    # Badge management
    path('u/<str:username>/award-badge/', views.award_badge, name='award_badge'),
    path('u/<str:username>/remove-badge/<int:badge_id>/', views.remove_badge, name='remove_badge'),
    path('u/<str:username>/badges/', views.get_user_badges, name='get_user_badges'),

    # User moderation
    path('u/<str:username>/ban/', views.ban_user, name='ban_user'),
    path('u/<str:username>/unban/', views.unban_user, name='unban_user'),

    # Content moderation
    path('mod/thread/<int:thread_id>/delete/', views.delete_thread, name='delete_thread'),
    path('mod/post/<int:post_id>/delete/', views.delete_post, name='delete_post'),

    # Reporting (for all users)
    path('report/post/<int:post_id>/', views.report_post, name='report_post'),
    path('report/thread/<int:thread_id>/', views.report_thread, name='report_thread'),
]
