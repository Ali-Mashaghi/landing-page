from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('projects/', views.projects, name='projects'),
    path('contact/', views.contact, name='contact'),
    path('resume/', views.resume, name='resume'),
    path('dashboard/login/', views.admin_login, name='admin_login'),
    path('dashboard/logout/', views.admin_logout, name='admin_logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/profile/', views.dashboard_profile, name='dashboard_profile'),
    path('dashboard/projects/', views.dashboard_projects, name='dashboard_projects'),
    path('dashboard/projects/add/', views.dashboard_project_create, name='dashboard_project_create'),
    path('dashboard/projects/<int:pk>/edit/', views.dashboard_project_edit, name='dashboard_project_edit'),
    path('dashboard/projects/<int:pk>/delete/', views.dashboard_project_delete, name='dashboard_project_delete'),
    path('dashboard/contacts/', views.dashboard_contacts, name='dashboard_contacts'),
    path('dashboard/contacts/<int:pk>/', views.dashboard_contact_detail, name='dashboard_contact_detail'),
]
