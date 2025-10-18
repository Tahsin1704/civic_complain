# accounts/urls.py
from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),

    path('home/', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
path('signup/', views.signup_citizen, name='signup'),

    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Dashboard (Role based redirect)
    path('dashboard/', views.dashboard, name='dashboard'),

    # Admin Dashboard
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),

    # Worker Dashboard
    path('worker/dashboard/', views.worker_dashboard, name='worker_dashboard'),
    path('worker/tasks/', views.worker_tasks, name='worker_tasks'),
# Worker search (Admin)
path('workers/search/', views.worker_search_admin, name='worker_search_admin'),
# worker preview
path('workers/preview/<int:user_id>/', views.worker_preview, name='worker_preview'),


    path('worker/search/', views.worker_search_task, name='worker_search_task'),
    path('worker/profile/', views.worker_profile, name='worker_profile'),

    # Worker management (Admin only)
    path('workers/create/', views.worker_create, name='worker_create'),
    path('workers/', views.worker_list, name='worker_list'),
    path('workers/<int:user_id>/delete/', views.worker_delete, name='worker_delete'),
path('worker/update/<int:pk>/', views.worker_update, name='worker_update'),


    # Task related (Worker)
    path('worker/task/<int:task_id>/', views.view_task, name='view_task'),
    path('worker/task/start/<int:task_id>/', views.start_task, name='start_task'),
    path('worker/task/update/<int:task_id>/', views.update_task_status, name='update_task_status'),

    # Signup (Citizen)
    path('signup/', views.signup_citizen, name='signup_citizen'),

    # Superuser-only
    path('admins/create/', views.admin_create, name='admin_create'),

    # Admin-only: Citizen moderation
    path('citizens/', views.citizen_list, name='citizen_list'),


    path('profile/', views.citizen_profile_view, name='citizen_profile_view'),
    path('profile/update/', views.citizen_profile_update, name='citizen_profile_update'),

    path('citizens/<int:user_id>/deactivate/', views.citizen_deactivate, name='citizen_deactivate'),
    path('citizens/<int:user_id>/delete/', views.citizen_delete, name='citizen_delete'),
# Citizen preview + search
path('citizens/search/', views.citizen_search_admin, name='citizen_search_admin'),
path('citizens/<int:user_id>/preview/', views.citizen_preview, name='citizen_preview'),
# urls.py example




    # Tasks (Citizen submit + Admin assigns)
    path('tasks/submit/', views.submit_task, name='submit_task'),
    path('tasks/admin/', views.admin_task_list, name='admin_task_list'),
    path('tasks/<int:task_id>/assign/', views.assign_task, name='assign_task'),
    path('tasks/<int:task_id>/delete/', views.task_delete, name='task_delete'),
path('tasks/search/', views.search_task_by_code, name='search_task_by_code'),
path('tasks/search-preview/', views.search_task_preview, name='search_task_preview'),

# Admin Task search + view
path('tasks/admin/search/', views.admin_task_search, name='admin_task_search'),

    path('tasks/<int:task_id>/preview/', views.task_preview, name='task_preview'),
path('tasks/<int:task_id>/view/', views.admin_task_view, name='admin_task_view'),
path('tasks/<int:task_id>/full/', views.admin_task_full_view, name='admin_task_full_view'),
path('tasks/<int:task_id>/detail/', views.citizen_task_detail, name='citizen_task_detail'),


# Citizen Dashboard
path('dashboard/citizen/', views.citizen_dashboard, name='citizen_dashboard'),




]