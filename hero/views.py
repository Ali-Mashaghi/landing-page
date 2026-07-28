from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from functools import wraps

from .models import Project, Contact
from .forms import ContactForm, LoginForm, ProfileForm, ProjectForm, SignupForm
from .services.email import send_contact_emails


def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access the admin panel.')
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return wrapper


def index(request):
    return render(request, 'index.html')


def projects(request):
    project_list = Project.objects.all().order_by('-created_at')
    return render(request, 'projects.html', {'projects': project_list})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            try:
                send_contact_emails(contact_message)
            except Exception:
                messages.warning(
                    request,
                    'Your message was saved, but email delivery failed. Please try again later.',
                )
            else:
                messages.success(request, 'Your message has been sent successfully.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


def resume(request):
    return render(request, 'resume.html')


def admin_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard' if request.user.is_staff else 'index')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, 'Welcome back!')
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        return redirect('dashboard' if user.is_staff else 'index')

    return render(request, 'dashboard/login.html', {'form': form})


def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard' if request.user.is_staff else 'index')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Your account was created successfully.')
            return redirect('index')
    else:
        form = SignupForm()

    return render(request, 'dashboard/signup.html', {'form': form})


@require_POST
def admin_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('index')


@staff_required
def dashboard(request):
    contacts_count = Contact.objects.count()
    recent_contacts = Contact.objects.all()[:5]
    return render(request, 'dashboard/index.html', {
        'contacts_count': contacts_count,
        'recent_contacts': recent_contacts,
    })


@staff_required
def dashboard_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('dashboard_profile')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'dashboard/profile.html', {'form': form})


@staff_required
def dashboard_contacts(request):
    contacts = Contact.objects.all()
    return render(request, 'dashboard/contacts.html', {'contacts': contacts})


@staff_required
def dashboard_contact_detail(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    return render(request, 'dashboard/contact_detail.html', {'contact': contact})


@staff_required
def dashboard_projects(request):
    project_list = Project.objects.all().order_by('-created_at')
    return render(request, 'dashboard/projects.html', {'projects': project_list})


@staff_required
def dashboard_project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project created successfully.')
            return redirect('dashboard_projects')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = ProjectForm()
    return render(request, 'dashboard/project_form.html', {
        'form': form,
        'page_title': 'Add Project',
    })


@staff_required
def dashboard_project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully.')
            return redirect('dashboard_projects')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'dashboard/project_form.html', {
        'form': form,
        'page_title': 'Edit Project',
        'project': project,
    })


@require_POST
@staff_required
def dashboard_project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.delete()
    messages.success(request, 'Project deleted successfully.')
    return redirect('dashboard_projects')
