from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from .forms import PasswordResetConfirmForm, PasswordResetRequestForm
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('projects/', views.projects, name='projects'),
    path('contact/', views.contact, name='contact'),
    path('resume/', views.resume, name='resume'),
    path('card/', views.business_card, name='business_card'),
    path('card/<uuid:token>/', views.business_card_public, name='business_card_public'),
    path('dashboard/login/', views.admin_login, name='admin_login'),
    path('dashboard/login/google/', views.google_login, name='google_login'),
    path('signup/', views.signup, name='signup'),
    path(
        'dashboard/password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='dashboard/password_reset_form.html',
            email_template_name='dashboard/password_reset_email.txt',
            subject_template_name='dashboard/password_reset_subject.txt',
            form_class=PasswordResetRequestForm,
            success_url=reverse_lazy('password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'dashboard/password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='dashboard/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'dashboard/password-reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='dashboard/password_reset_confirm.html',
            form_class=PasswordResetConfirmForm,
            success_url=reverse_lazy('password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'dashboard/password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='dashboard/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
    path('dashboard/logout/', views.admin_logout, name='admin_logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/profile/', views.dashboard_profile, name='dashboard_profile'),
    path(
        'dashboard/profile/regenerate-card-token/',
        views.dashboard_regenerate_card_token,
        name='dashboard_regenerate_card_token',
    ),
    path('dashboard/projects/', views.dashboard_projects, name='dashboard_projects'),
    path('dashboard/projects/add/', views.dashboard_project_create, name='dashboard_project_create'),
    path('dashboard/projects/<int:pk>/edit/', views.dashboard_project_edit, name='dashboard_project_edit'),
    path('dashboard/projects/<int:pk>/delete/', views.dashboard_project_delete, name='dashboard_project_delete'),
    path('dashboard/contacts/', views.dashboard_contacts, name='dashboard_contacts'),
    path('dashboard/contacts/<int:pk>/', views.dashboard_contact_detail, name='dashboard_contact_detail'),
]
