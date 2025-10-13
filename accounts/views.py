from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CitizenSignupForm, WorkerCreateForm,CitizenProfileForm,AdminCreateForm, TaskSubmitForm,  CitizenProfileUpdateForm,TaskAssignForm, TaskUpdateForm, \
    WorkerProfileForm
from .models import WorkerProfile
from .forms import TaskSearchForm
from django.db.models import Q


from .models import User, Roles, AdminActionLog, Task

from django.utils import timezone

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
        form = CitizenSignupForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login')
    else:
        form = CitizenSignupForm()
    return render(request, 'accounts/signup_citizen.html', {'form': form})

# 🧭 Dashboard — shown after login, varies by role
# 🧭 Dashboard — shown after login, varies by role
# views.py

@login_required


@login_required
def dashboard(request):
    if request.user.role == Roles.CITIZEN:
        # Get all tasks submitted by this citizen
        tasks = Task.objects.filter(submitted_by=request.user).order_by('-id')

        # Counters
        new_count = tasks.filter(status='new').count()
        in_progress_count = tasks.filter(status='in_progress').count()
        completed_count = tasks.filter(status='completed').count()

        context = {
            'citizen': request.user,
            'my_tasks': tasks,
            'new_count': new_count,
            'in_progress_count': in_progress_count,
            'completed_count': completed_count,
        }
        return render(request, 'accounts/citizen_dashboard.html', context)

    elif request.user.role == Roles.WORKER:
        return redirect('worker_dashboard')

    elif request.user.role == Roles.ADMIN:
        # Admin dashboard logic
        total_complaints = Task.objects.count()
        pending_complaints = Task.objects.filter(status="new").count()
        resolved_complaints = Task.objects.filter(status="completed").count()
        active_workers = User.objects.filter(role=Roles.WORKER, is_active=True).count()
        recent_tasks = Task.objects.order_by('-id')[:10]

        context = {
            "total_complaints": total_complaints,
            "pending_complaints": pending_complaints,
            "resolved_complaints": resolved_complaints,
            "active_workers": active_workers,
            "recent_tasks": recent_tasks,
        }
        return render(request, "accounts/admin_dashboard.html", context)

@login_required
def citizen_task_detail(request, task_id):
    # Only allow the submitting citizen to view their own task
    task = get_object_or_404(Task, id=task_id, submitted_by=request.user)

    context = {
        'task': task
    }
    return render(request, 'accounts/citizen_task_detail.html', context)


@login_required
def worker_list(request):
    if request.user.role != "ADMIN":
        return redirect('dashboard')
    workers = User.objects.filter(role="WORKER").select_related("worker_profile")
    return render(request, 'accounts/worker_list.html', {'workers': workers})


@login_required
def worker_create(request):
    if request.user.role != "ADMIN":
        return redirect('dashboard')

    if request.method == "POST":
        form = WorkerCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Worker created successfully.")
            return redirect("worker_list")
    else:
        form = WorkerCreateForm()

    return render(request, "accounts/create_worker.html", {"form": form})
@login_required
def worker_delete(request, user_id):
    if request.user.role != Roles.ADMIN:
        messages.error(request, "You are not allowed to delete workers.")
        return redirect('dashboard')

    # First try to get the worker
    try:
        worker = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "Worker not found.")
        return redirect('worker_list')

    # Ensure it's actually a worker
    if worker.role != Roles.WORKER:
        messages.error(request, "You can only delete workers.")
        return redirect('worker_list')

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()

        if not reason:
            messages.error(request, "Please provide a reason for deletion.")
            return render(request, 'accounts/worker_delete.html', {'user': worker})

        # Log admin action
        AdminActionLog.objects.create(
            admin=request.user,
            target_user=worker,
            action='DELETE_USER',
            reason=reason
        )

        # Delete the worker
        worker.delete()
        messages.success(request, f"Worker '{worker.email}' deleted successfully.")
        return redirect('worker_list')

    # GET → show form with reason field
    return render(request, 'accounts/worker_delete.html', {'user': worker})



# 👥 Citizen list — Admin-only
@login_required
def citizen_deactivate(request, user_id):
    if request.user.role != Roles.ADMIN:
        return redirect('dashboard')

    citizen = get_object_or_404(User, id=user_id, role=Roles.CITIZEN)

    if request.method == 'POST':
        reason = request.POST.get('reason', '')

        if citizen.is_active:
            # Deactivate
            citizen.is_active = False
            action = 'DEACTIVATE_USER'
            messages.info(request, "Citizen deactivated.")
        else:
            # Reactivate
            citizen.is_active = True
            action = 'REACTIVATE_USER'
            messages.success(request, "Citizen reactivated.")

        citizen.save()

        # Log the action
        AdminActionLog.objects.create(
            admin=request.user,
            target_user=citizen,
            action=action,
            reason=reason
        )

        return redirect('citizen_list')

    # Pass citizen to template
    return render(request, 'accounts/citizen_deactive.html', {'user': citizen})

@login_required
def citizen_list(request):
    if request.user.role != Roles.ADMIN:
        return redirect('dashboard')
    citizens = User.objects.filter(role=Roles.CITIZEN)
    return render(request, 'accounts/citizen_list.html', {'citizens': citizens})

# 🚫 Deactivate citizen — Admin-only



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



@login_required
def submit_task(request):
    if request.user.role != Roles.CITIZEN:
        return redirect('dashboard')

    if request.method == 'POST':
        form = TaskSubmitForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.citizen_name = f"{request.user.first_name} {request.user.last_name}"
            task.save()
            messages.success(request, "Your task has been submitted.")
            return redirect('dashboard')
    else:
        form = TaskSubmitForm()

    return render(request, 'accounts/submit_task.html', {'form': form})

from .forms import TaskAssignForm

@login_required
def assign_task(request, task_id):
    if request.user.role != Roles.ADMIN:
        return redirect('dashboard')

    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskAssignForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, f"Task '{task.title}' assigned to {task.assigned_to.email}.")
            return redirect('admin_dashboard')
    else:
        form = TaskAssignForm(instance=task)

    return render(request, 'accounts/assign_task.html', {'form': form, 'task': task})
from django.shortcuts import render
from .models import Task

def admin_task_list(request):
    tasks = Task.objects.all()  # all tasks for admin
    return render(request, 'accounts/admin_task_list.html', {'tasks': tasks})

@login_required
def task_delete(request, task_id):
    if request.user.role != Roles.ADMIN:
        return redirect('dashboard')

    task = get_object_or_404(Task, id=task_id)

    # Admin can delete any task from preview
    if request.method == 'POST':
        task.delete()
        messages.success(request, "Task deleted.")
        return redirect('admin_dashboard')

    return render(request, 'accounts/confirm_delete.html', {'task': task})
@login_required
def task_preview(request, task_id):
    if request.user.role != Roles.ADMIN:
        return redirect('dashboard')
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'accounts/task_preview.html', {'task': task})

@login_required
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)

    if request.method == 'POST':
        form = TaskUpdateForm(request.POST, request.FILES)

        if form.is_valid():
            status = form.cleaned_data['status']

            # যদি already completed থাকে → আর update হবে না
            if task.status == 'completed':
                messages.warning(request, "This task is already completed. You cannot update it further.")
                return redirect('worker_dashboard')

            # In Progress এ update করলে → প্রতিবার latest save হবে
            if status == 'in_progress':
                task.status = 'in_progress'
                task.progress = form.cleaned_data.get('progress')
                task.work_description = form.cleaned_data.get('work_description')
                task.materials_used = form.cleaned_data.get('materials_used')
                task.additional_notes = form.cleaned_data.get('additional_notes')
                task.pending_reason = form.cleaned_data.get('pending_reason')
                if request.FILES.get('before_photo'):
                    task.before_photo = request.FILES['before_photo']

                if not task.started_at:
                    task.started_at = timezone.now()

            # Completed → final save, locked
            elif status == 'completed':
                task.status = 'completed'
                task.progress = None
                task.work_description = form.cleaned_data.get('work_description')
                task.materials_used = form.cleaned_data.get('materials_used')
                task.additional_notes = form.cleaned_data.get('additional_notes')

                if request.FILES.get('before_photo'):
                    task.before_photo = request.FILES['before_photo']
                if request.FILES.get('after_photo'):
                    task.after_photo = request.FILES['after_photo']

                task.completed_at = timezone.now()

            task.save()
            messages.success(request, f"Task updated to {task.status}.")
            return redirect('worker_dashboard')

    else:
        # এখানে আগের saved ডেটা দেখানোর জন্য initial সেট করা
        form = TaskUpdateForm(initial={
            'status': task.status,
            'progress': task.progress,
            'work_description': task.work_description,
            'materials_used': task.materials_used,
            'additional_notes': task.additional_notes,
        })

    return render(request, 'accounts/update_task_status.html', {
        'form': form,
        'task': task
    })



@login_required

@login_required
@login_required
def worker_dashboard(request):
    user = request.user

    # Tasks assigned to this worker
    new_tasks = Task.objects.filter(assigned_to=user, status='new')
    in_progress_tasks = Task.objects.filter(assigned_to=user, status='in_progress')
    completed_tasks = Task.objects.filter(assigned_to=user, status='completed')
    high_priority_tasks = Task.objects.filter(assigned_to=user, priority='high')



    context = {
        'new_tasks': new_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'high_priority_tasks': high_priority_tasks,

    }

    return render(request, 'accounts/worker_dashboard.html', context)

def worker_tasks(request):
    worker = request.user
    query = request.GET.get('query', '')
    filter_status = request.GET.get('filter', '')

    tasks = Task.objects.filter(assigned_to=worker)

    # Filter by status
    if filter_status in ['new', 'in_progress', 'completed']:
        tasks = tasks.filter(status=filter_status)

    # Search by title or category
    if query:
        tasks = tasks.filter(title__icontains=query) | tasks.filter(category__icontains=query)

    context = {
        'tasks': tasks,
        'query': query,
        'filter_status': filter_status,
    }
    return render(request, 'accounts/worker_tasks.html', context)
def worker_search(request):
    query = request.GET.get('query', '')
    tasks = Task.objects.filter(title__icontains=query)  # title এ search
    context = {
        'tasks': tasks,
        'query': query,
    }
    return render(request, 'accounts/worker_search.html', context)


def worker_filter(request):
    filter_option = request.GET.get('filter', 'all')  # 'all', 'new', 'in_progress', 'completed'

    if filter_option == 'new':
        tasks = Task.objects.filter(status='new')
    elif filter_option == 'in_progress':
        tasks = Task.objects.filter(status='in_progress')
    elif filter_option == 'completed':
        tasks = Task.objects.filter(status='completed')
    else:
        tasks = Task.objects.all()

    context = {
        'tasks': tasks,
        'current_filter': filter_option,
    }
    return render(request, 'accounts/worker_filter.html', context)
@login_required
def citizen_dashboard(request):

    # Make sure only citizens can access
    if request.user.role != "CITIZEN":
        messages.error(request, "Access denied.")
        return redirect("dashboard")

 # Start with all tasks submitted by this citizen
    my_tasks = Task.objects.filter(submitted_by=request.user)

    my_tasks = my_tasks.order_by('-id')

    # Optional: highlight recently submitted task
    submitted_task = None
    submitted_task_id = request.session.pop('submitted_task_id', None)
    if submitted_task_id:
        try:
            submitted_task = Task.objects.get(id=submitted_task_id)
        except Task.DoesNotExist:
            submitted_task = None

    # Count tasks by status
    new_count = my_tasks.filter(status='new').count()
    in_progress_count = my_tasks.filter(status='in_progress').count()
    completed_count = my_tasks.filter(status='completed').count()

    context = {
        "citizen": request.user,
        "my_tasks": my_tasks,
        "submitted_task": submitted_task,
        "new_count": new_count,
        "in_progress_count": in_progress_count,
        "completed_count": completed_count,

    }

    return render(request, "accounts/citizen_dashboard.html", context)

@login_required
def submit_task(request):
    if request.user.role != "CITIZEN":
        messages.error(request, "Only citizens can submit tasks.")
        return redirect("dashboard")

    if request.method == "POST":
        form = TaskSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.submitted_by = request.user  # ✅ very important
            task.status = "new"
            task.save()

            # Save to session (for highlight)
            request.session['submitted_task_id'] = task.id

            messages.success(request, "Your complaint has been submitted successfully.")
            return redirect("citizen_dashboard")  # ✅ redirect to citizen dashboard
    else:
        form = TaskSubmitForm()

    return render(request, "accounts/submit_task.html", {"form": form})

@login_required
def worker_profile(request):
    if request.user.role != "WORKER":
        messages.error(request, "You are not allowed to access worker profile.")
        return redirect("dashboard")

    profile = request.user.worker_profile

    # Tasks assigned to this worker
    total_tasks = Task.objects.filter(assigned_to=request.user).count()

    # Pending → New tasks not yet started
    pending = Task.objects.filter(assigned_to=request.user, status='new').count()

    # In Progress → started but not completed and not pending
    in_progress = Task.objects.filter(
        assigned_to=request.user,
        status='in_progress',
        pending_reason__isnull=True
    ).count()

    # Completed tasks
    completed = Task.objects.filter(assigned_to=request.user, status='completed').count()

    context = {
        "profile": profile,
        "total_tasks": total_tasks,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
    }

    return render(request, "accounts/worker_profile.html", context)

from django.db.models.functions import Lower, Trim

@login_required
def admin_dashboard(request):
    if request.user.role != Roles.ADMIN:
        return redirect('dashboard')

    tasks = Task.objects.all()  # clean DB, so simple query works


    total_complaints = tasks.count()
    pending_complaints = tasks.filter(status='new').count()

    resolved_complaints = tasks.filter(status='completed').count()
    active_workers = User.objects.filter(role=Roles.WORKER, is_active=True).count()

    query = request.GET.get('q', '').strip()
    if query:
        recent_tasks = tasks.filter(task_code__icontains=query).order_by('-id')[:10]
    else:
        recent_tasks = tasks.order_by('-id')[:10]

    context = {
        "total_complaints": total_complaints,
        "pending_complaints": pending_complaints,

        "resolved_complaints": resolved_complaints,
        "active_workers": active_workers,
        "recent_tasks": recent_tasks,
    }

    return render(request, "accounts/admin_dashboard.html", context)


@login_required
def view_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # শুধুমাত্র assigned worker দেখতে পারবে
    if request.user.role == "WORKER" and task.assigned_to != request.user:
        return redirect("worker_dashboard")

    # ------------------------
    # NEW TASK → view only + start button
    # ------------------------
    if task.status == "new":
        if request.method == "POST" and "start_task" in request.POST:
            task.status = "in_progress"
            task.save()
            messages.success(request, "Task started and moved to In Progress.")
            return redirect("worker_dashboard")

        context = {"task": task, "new_task": True}  # template-এ check করার জন্য
        return render(request, "accounts/view_task.html", context)

    # ------------------------
    # IN PROGRESS → update task
    # ------------------------
    if task.status == "in_progress":
        if request.method == "POST":
            form = TaskUpdateForm(request.POST, request.FILES)
            if form.is_valid():
                task.progress = form.cleaned_data.get('progress')
                task.work_description = form.cleaned_data.get('work_description')
                task.materials_used = form.cleaned_data.get('materials_used')
                task.additional_notes = form.cleaned_data.get('additional_notes')

                status = form.cleaned_data.get('status')
                task.status = status

                # After photo only if completed
                if status == "completed" and request.FILES.get("after_photo"):
                    task.after_photo = request.FILES["after_photo"]
                    task.completed_at = timezone.now()

                task.save()
                messages.success(request, "Task updated successfully.")
            return redirect('worker_dashboard')
        else:
            form = TaskUpdateForm(initial={
                "status": task.status,
                "progress": task.progress,
                "work_description": task.work_description,
                "materials_used": task.materials_used,
                "additional_notes": task.additional_notes,
            })

        context = {"task": task, "form": form}
        return render(request, "accounts/view_task.html", context)

    # ------------------------
    # COMPLETED → only view photos
    # ------------------------
    context = {"task": task}
    return render(request, "accounts/view_task.html", context)







def start_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    # status update করে In Progress এ পাঠাচ্ছি
    task.status = "in_progress"
    task.save()
    return redirect("dashboard")

@login_required
def worker_search_task(request):
    if request.user.role != "WORKER":
        return redirect("dashboard")

    query = request.GET.get('query', '').strip()
    task = None

    # এখন task_code দিয়ে খুঁজবে
    if query:
        try:
            task = Task.objects.get(task_code__iexact=query, assigned_to=request.user)
        except Task.DoesNotExist:
            task = None

    context = {
        "query": query,
        "task": task
    }
    return render(request, "accounts/worker_search_result.html", context)
@login_required
def search_task_by_code(request):
    if request.user.role != Roles.ADMIN:
        return redirect('dashboard')

    query = request.GET.get('q', '').strip()

    if not query:
        messages.warning(request, "Please enter a Task Code to search.")
        return redirect('admin_dashboard')

    # ✅ Task খুঁজে পাওয়া গেলে task_preview পেজে redirect করবে
    try:
        task = Task.objects.get(task_code__iexact=query)
        return redirect('task_preview', task_id=task.id)
    except Task.DoesNotExist:
        messages.error(request, "No task found with that Task Code.")
        return redirect('admin_dashboard')


@login_required
def search_task_preview(request):
    if request.user.role != Roles.ADMIN:
        return redirect('dashboard')

    query = request.GET.get('q', '').strip()

    if not query:
        messages.warning(request, "Please enter a Task Code to search.")
        return redirect('admin_dashboard')

    try:
        task = Task.objects.get(task_code__iexact=query)
        # এই page এ শুধুমাত্র preview দেখাবে
        return render(request, 'accounts/search_task_preview.html', {'task': task})
    except Task.DoesNotExist:
        messages.error(request, "No task found with that Task Code.")
        return redirect('admin_dashboard')

from django.db.models import Q

@login_required
def worker_preview(request, user_id=None):
    if request.user.role != Roles.ADMIN:
        return redirect('dashboard')

    # user_id থাকলে সেই worker দেখাবে
    worker = get_object_or_404(User, id=user_id, role=Roles.WORKER)
    # Delete action
    if request.method == "POST":
        worker.delete()
        messages.success(request, f"Worker '{worker.email}' deleted successfully.")
        return redirect('worker_list')
    context = {
        'worker': worker
    }
    return render(request, 'accounts/worker_preview.html', context)


@login_required
def worker_search_admin(request):
    if request.user.role != Roles.ADMIN:
        return redirect('dashboard')

    query = request.GET.get('q', '').strip()
    if query:
        try:
            worker = User.objects.get(email__iexact=query, role=Roles.WORKER)
            # সরাসরি preview page এ redirect
            return redirect('worker_preview', user_id=worker.id)
        except User.DoesNotExist:
            messages.error(request, "No worker found with this email.")

    # query না থাকলে বা worker না পাওয়া গেলে full list দেখাবে
    workers = User.objects.filter(role=Roles.WORKER)
    context = {
        'workers': workers,
        'query': query
    }
    return render(request, 'accounts/worker_list.html', context)
@login_required
def citizen_preview(request, user_id=None):
    if request.user.role != Roles.ADMIN:
        return redirect('dashboard')

    citizen = get_object_or_404(User, id=user_id, role=Roles.CITIZEN)
    # Delete action
    if request.method == "POST":
        citizen.delete()
        messages.success(request, f"Citizen '{citizen.email}' deleted successfully.")
        return redirect('citizen_list')

    return render(request, 'accounts/citizen_preview.html', {'citizen': citizen})


@login_required
def citizen_search_admin(request):
    if request.user.role != Roles.ADMIN:
        return redirect('dashboard')

    query = request.GET.get('q', '').strip()
    if query:
        try:
            citizen = User.objects.get(email__iexact=query, role=Roles.CITIZEN)
            return redirect('citizen_preview', user_id=citizen.id)
        except User.DoesNotExist:
            messages.error(request, "No citizen found with this email.")

    # query না থাকলে বা না পাওয়া গেলে full list দেখাবে
    citizens = User.objects.filter(role=Roles.CITIZEN)
    return render(request, 'accounts/citizen_list.html', {'citizens': citizens, 'query': query})

@login_required
def admin_task_search(request):
    if request.user.role != Roles.ADMIN:
        return redirect('dashboard')

    query = request.GET.get('q', '').strip()

    if not query:
        messages.warning(request, "Please enter a Task Code to search.")
        return redirect('admin_dashboard')

    try:
        task = Task.objects.get(task_code__iexact=query)
        # Redirect to task_preview page
        return redirect('task_preview', task_id=task.id)
    except Task.DoesNotExist:
        messages.error(request, "No task found with that Task Code.")
        return redirect('admin_dashboard')


@login_required
def admin_task_view(request, task_id):
    if request.user.role != Roles.ADMIN:
        return redirect('dashboard')

    task = get_object_or_404(Task, id=task_id)
    return render(request, 'accounts/admin_task_view.html', {'task': task})


@login_required
def admin_task_full_view(request, task_id):
    if request.user.role != Roles.ADMIN:
        return redirect('dashboard')

    task = get_object_or_404(Task, id=task_id)
    return render(request, 'accounts/admin_task_full_view.html', {'task': task})
@login_required
def task_preview(request, task_id):
    if request.user.role != Roles.ADMIN:
        return redirect('dashboard')

    task = get_object_or_404(Task, id=task_id)

    return render(request, 'accounts/task_preview.html', {'task': task})


@login_required
def citizen_profile(request):
    user = request.user
    if request.method == 'POST':
        form = CitizenProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('citizen_profile')
    else:
        form = CitizenProfileUpdateForm(instance=user)
    return render(request, 'accounts/citizen_profile.html', {'form': form})
@login_required
def citizen_profile_view(request):
    """View-only profile page"""
    user = request.user
    return render(request, 'accounts/citizen_profile_view.html', {'user': user})

@login_required
def citizen_profile_update(request):
    """Profile update page"""
    user = request.user
    if request.method == 'POST':
        form = CitizenProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('citizen_profile_view')  # back to view-only page
    else:
        form = CitizenProfileForm(instance=user)

    return render(request, 'accounts/citizen_profile_update.html', {'form': form, 'user': user})

@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.submitted_by = request.user  # link user directly
            task.save()
            return redirect('dashboard')
    else:
        form = TaskSubmitForm()
    return render(request, 'accounts/create_task.html', {'form': form})


def worker_update(request, pk):
    worker = get_object_or_404(User, id=pk, role='WORKER')
    profile = worker.worker_profile

    if request.method == 'POST':
        form = WorkerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('worker_list')
    else:
        form = WorkerProfileForm(instance=profile)

    return render(request, 'accounts/worker_update.html', {'form': form, 'worker': worker})

