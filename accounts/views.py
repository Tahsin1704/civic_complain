from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CitizenSignupForm, WorkerCreateForm, AdminCreateForm
from .models import User, Roles, AdminActionLog

# 🏠 Home page — shows login/signup options
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')  # ← send unauthenticated users to login page

# 🟢 Citizen signup view — public registration
def signup_citizen(request):
    if request.method == 'POST':
        form = CitizenSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login')
    else:
        form = CitizenSignupForm()
    return render(request, 'accounts/signup_citizen.html', {'form': form})

# 🧭 Dashboard — shown after login, varies by role
@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

# 🧑‍🔧 Worker list — visible only to Admins
@login_required
def worker_list(request):
    if request.user.role != Roles.ADMIN:
        return redirect('dashboard')
    workers = User.objects.filter(role=Roles.WORKER)
    return render(request, 'accounts/worker_list.html', {'workers': workers})

@login_required
def worker_create(request):
    if request.user.role != Roles.ADMIN:
        return redirect('dashboard')
    if request.method == 'POST':
        form = WorkerCreateForm(request.POST)
        if form.is_valid():
            worker = form.save()
            AdminActionLog.objects.create(admin=request.user, target_user=worker, action='CREATE_WORKER')
            messages.success(request, "Worker added.")
            return redirect('worker_list')
    else:
        form = WorkerCreateForm()
    return render(request, 'accounts/worker_form.html', {'form': form})
# ❌ Delete worker — Admin-only
@login_required
def worker_delete(request, user_id):
    if request.user.role != Roles.ADMIN:
        return redirect('dashboard')
    worker = get_object_or_404(User, id=user_id, role=Roles.WORKER)
    if request.method == 'POST':
        worker.delete()
        AdminActionLog.objects.create(admin=request.user, target_user=None, action='DELETE_WORKER', reason=f"Deleted {worker.email}")
        messages.success(request, "Worker deleted.")
        return redirect('worker_list')
    return render(request, 'accounts/confirm_delete.html', {'user': worker})

# 👥 Citizen list — Admin-only
@login_required
def citizen_list(request):
    if request.user.role != Roles.ADMIN:
        return redirect('dashboard')
    citizens = User.objects.filter(role=Roles.CITIZEN)
    return render(request, 'accounts/citizen_list.html', {'citizens': citizens})

# 🚫 Deactivate citizen — Admin-only
@login_required
def citizen_deactivate(request, user_id):
    if request.user.role != Roles.ADMIN:
        return redirect('dashboard')
    citizen = get_object_or_404(User, id=user_id, role=Roles.CITIZEN)
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        citizen.is_active = False
        citizen.save()
        AdminActionLog.objects.create(admin=request.user, target_user=citizen, action='DEACTIVATE_USER', reason=reason)
        messages.info(request, "Citizen deactivated.")
        return redirect('citizen_list')
    return render(request, 'accounts/citizen_deactivate.html', {'user': citizen})

# 🗑 Delete citizen — Admin-only
@login_required
def citizen_delete(request, user_id):
    if request.user.role != Roles.ADMIN:
        return redirect('dashboard')
    citizen = get_object_or_404(User, id=user_id, role=Roles.CITIZEN)
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        citizen.delete()
        AdminActionLog.objects.create(admin=request.user, target_user=None, action='DELETE_USER', reason=f"{reason} (Deleted {citizen.email})")
        messages.warning(request, "Citizen deleted.")
        return redirect('citizen_list')
    return render(request, 'accounts/confirm_delete.html', {'user': citizen})

# 🔐 Create admin — Superuser-only
@user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
def admin_create(request):
    if request.method == 'POST':
        form = AdminCreateForm(request.POST)
        if form.is_valid():
            form.save(created_by_superuser=True)
            messages.success(request, "Admin created.")
            return redirect('dashboard')
    else:
        form = AdminCreateForm()
    return render(request, 'accounts/admin_form.html', {'form': form})