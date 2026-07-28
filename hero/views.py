from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.views.decorators.http import require_POST
from functools import wraps

from .models import Project, Contact
from .forms import ContactForm, LoginForm, ProfileForm


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
            form.save()
            messages.success(request, 'Your message has been sent successfully.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


def resume(request):
    return render(request, 'resume.html')


def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, 'Welcome back!')
        next_url = request.GET.get('next', 'dashboard')
        return redirect(next_url)

    return render(request, 'dashboard/login.html', {'form': form})


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
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('dashboard_profile')

    return render(request, 'dashboard/profile.html', {'form': form})


@staff_required
def dashboard_contacts(request):
    contacts = Contact.objects.all()
    return render(request, 'dashboard/contacts.html', {'contacts': contacts})


@staff_required
def dashboard_contact_detail(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    return render(request, 'dashboard/contact_detail.html', {'contact': contact})
