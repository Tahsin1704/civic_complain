from django import forms
from .models import User, Roles, Task
from .models import WorkerProfile


class CitizenSignupForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows':2}), required=False)
    photo = forms.ImageField(required=False)

    class Meta:
        model = User
        # <-- এখানে fields অবশ্যই দিতে হবে
        fields = ['email', 'first_name', 'last_name', 'address', 'photo']

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = Roles.CITIZEN
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class CitizenProfileForm(forms.ModelForm):
        class Meta:
            model = User
            fields = ['first_name', 'last_name', 'email', 'address', 'photo']

class CitizenProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'address', 'photo']

class WorkerCreateForm(forms.ModelForm):
    # WorkerProfile এর extra fields
    phone = forms.CharField(required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    skills = forms.CharField(widget=forms.Textarea, required=True)
    photo = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name"]  # User table এর ফিল্ড

    def save(self, commit=True):
        # প্রথমে User create করা হবে
        user = super().save(commit=False)
        user.role = "WORKER"  # default role worker
        user.set_password(self.cleaned_data["password"])  # password hash করা
        if commit:
            user.save()

            # WorkerProfile create করা হবে
            WorkerProfile.objects.create(
                user=user,
                phone=self.cleaned_data.get("phone"),
                address=self.cleaned_data.get("address"),
                skills=self.cleaned_data.get("skills"),
                photo=self.cleaned_data.get("photo"),
            )
        return user
#  Admin Creation Form (used by Superuser only)
class AdminCreateForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

    def save(self, commit=True, created_by_superuser=False):
        if not created_by_superuser:
            raise forms.ValidationError("Only superuser can create an admin.")
        user = super().save(commit=False)
        user.role = Roles.ADMIN
        user.is_staff = True
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

# 🟢 Task Submission Form (for Citizens)
class TaskSubmitForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title',
            'description',
            'category',
            'location',
            'instructions',
            'estimated_time',
            'task_photo',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'instructions': forms.Textarea(attrs={'rows': 2}),
        }

# Task Assignment Form (for Admin)
# Task Assignment Form (for Admin)
class TaskAssignForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(role=Roles.WORKER),
        label="Assign to Worker",
        required=False  # allow empty to show "Not assigned" if needed
    )
    priority = forms.ChoiceField(
        choices=Task.PRIORITY_CHOICES,
        label="Priority",
        required=False
    )

    class Meta:
        model = Task
        fields = [
            'assigned_to',
            'priority',
            'status',  # Usually 'new' when assigning
        ]



class TaskUpdateForm(forms.Form):
    STATUS_CHOICES = [

        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),

    ]

    status = forms.ChoiceField(choices=STATUS_CHOICES)
    progress = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 2 hours'})
    )
    work_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Describe what work was completed...'})
    )
    materials_used = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'List materials and equipment used'})
    )
    additional_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Any additional notes or observations...'})
    )
    before_photo = forms.ImageField(required=False)
    after_photo = forms.ImageField(required=False)


class TaskSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search tasks...',
            'class': 'form-control',
        })
    )
class WorkerProfileForm(forms.ModelForm):
    class Meta:
        model = WorkerProfile
        fields = ['phone', 'address', 'skills', 'photo']
