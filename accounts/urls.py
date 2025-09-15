from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='home'),                        # Home page
    path('dashboard/', views.dashboard, name='dashboard'),     # Role-based dashboard

    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup_citizen, name='signup_citizen'),

    # Superuser-only
    path('admins/create/', views.admin_create, name='admin_create'),

    # Admin-only: Worker management
    path('workers/', views.worker_list, name='worker_list'),
    path('workers/create/', views.worker_create, name='worker_create'),
    path('workers/<int:user_id>/delete/', views.worker_delete, name='worker_delete'),

    # Admin-only: Citizen moderation
    path('citizens/', views.citizen_list, name='citizen_list'),
    path('citizens/<int:user_id>/deactivate/', views.citizen_deactivate, name='citizen_deactivate'),
    path('citizens/<int:user_id>/delete/', views.citizen_delete, name='citizen_delete'),
]