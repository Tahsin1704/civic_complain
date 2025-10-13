from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, AdminActionLog,Task

# 🔐 Custom admin panel for User model
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('email',)
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_active', 'is_staff'),
        }),
    )

    filter_horizontal = ('groups', 'user_permissions',)

# 📋 Admin action log viewer
@admin.register(AdminActionLog)
class AdminActionLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'admin', 'action', 'target_user', 'reason')
    list_filter = ('action', 'timestamp')
    search_fields = ('admin__email', 'target_user__email', 'reason')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'task_code', 'title', 'category', 'priority', 'status', 'assigned_to', 'citizen_name')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('task_code', 'title', 'category', 'location')
    readonly_fields = ('task_code',)