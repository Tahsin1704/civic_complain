from django.conf import settings
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
    address = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.CITIZEN)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} ({self.role})"

# Admin action log
class AdminActionLog(models.Model):
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='actions')
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='moderated')
    action = models.CharField(max_length=50)
    reason = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp} - {self.admin} -> {self.action} on {self.target_user}"



class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In_Progress'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    task_code = models.CharField(max_length=20, unique=True, blank=True, null=True)

    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    citizen_name = models.CharField(max_length=100, blank=True)
    instructions = models.TextField(blank=True,null=True)
    estimated_time = models.CharField(max_length=50,null=True, blank=True)
    pending_reason = models.TextField(blank=True, null=True, help_text="Reason for pending")
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_tasks'
    )
    reopen_reason = models.TextField(blank=True, null=True)
    is_reopened = models.BooleanField(default=False)
    started_at = models.DateField(null=True, blank=True)
    completed_at = models.DateField(null=True, blank=True)

    before_photo = models.ImageField(upload_to='task_photos/before/', null=True, blank=True)
    after_photo = models.ImageField(upload_to='task_photos/after/', null=True, blank=True)
    task_photo = models.ImageField(upload_to='tasks/photos/', blank=True, null=True)
    progress = models.CharField(max_length=255, blank=True, null=True)
    work_description = models.TextField(blank=True, null=True)
    materials_used = models.TextField(blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):



        if not self.task_code:
            last_task = Task.objects.order_by("-id").first()
            if last_task and last_task.task_code:
                try:
                    last_number = int(last_task.task_code.replace("TASK-", ""))
                except ValueError:
                    last_number = 0
            else:
                last_number = 0
            new_number = last_number + 1
            self.task_code = f"TASK-{new_number:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class WorkerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="worker_profile")
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to="worker_profiles/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
