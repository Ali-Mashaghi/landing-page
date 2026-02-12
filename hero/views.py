from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Project
from .forms import ContactForm


def index(request):
    return render(request, 'index.html')


def projects(request):
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'projects.html', {'projects': projects})


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
