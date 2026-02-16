from django.contrib import admin
from django.utils.html import format_html
from .models import Contact, Project


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    readonly_fields = ('created_at',)
    fields = ('title', 'description', 'image', 'repo_url')
