from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_root, name='api_root'),
    path('profile/', views.ProfileAPIView.as_view(), name='profile_api'),
    path('projects/', views.ProjectListCreateAPIView.as_view(), name='project_list_api'),
    path('projects/<int:pk>/', views.ProjectDetailAPIView.as_view(), name='project_detail_api'),
    path('skills/', views.SkillListCreateAPIView.as_view(), name='skill_list_api'),
    path('skills/<int:pk>/', views.SkillDetailAPIView.as_view(), name='skill_detail_api'),
    path('contact/', views.ContactListCreateAPIView.as_view(), name='contact_list_api'),
    path('contact/<int:pk>/', views.ContactDetailAPIView.as_view(), name='contact_detail_api'),
]
