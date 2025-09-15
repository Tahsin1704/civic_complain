from django import forms
from .models import User, Roles

# 🟢 Citizen Signup Form
class CitizenSignupForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password1') != cleaned.get('password2'):
            raise forms.ValidationError("Passwords do not match")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = Roles.CITIZEN
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

# 🟡 Worker Creation Form (used by Admin)
class WorkerCreateForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = Roles.WORKER
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

# 🔴 Admin Creation Form (used by Superuser only)
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