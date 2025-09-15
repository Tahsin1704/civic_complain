from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone

# Define role choices
class Roles(models.TextChoices):
    CITIZEN = 'CITIZEN', 'Citizen'
    WORKER = 'WORKER', 'Worker'
    ADMIN = 'ADMIN', 'Admin'

# Custom user manager
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role=Roles.CITIZEN, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)

        # Prevent public creation of admin
        if role == Roles.ADMIN and not extra_fields.pop('created_by_superuser', False):
            raise ValueError("Admin must be created by superuser")

        user = self.model(email=email, role=role, is_active=True, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, role=Roles.ADMIN, created_by_superuser=True, **extra_fields)

# Custom user model
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.CITIZEN)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} ({self.role})"

# Admin action log model
class AdminActionLog(models.Model):
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='actions')
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='moderated')
    action = models.CharField(max_length=50)
    reason = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp} - {self.admin} -> {self.action} on {self.target_user}"