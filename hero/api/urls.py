from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)

urlpatterns = [
    path('', views.api_root, name='api_root'),
    path('profile/', views.ProfileAPIView.as_view(), name='profile_api'),
    path('projects/', views.ProjectListCreateAPIView.as_view(), name='project_list_api'),
    path('projects/<int:pk>/', views.ProjectDetailAPIView.as_view(), name='project_detail_api'),
    path('skills/', views.SkillListCreateAPIView.as_view(), name='skill_list_api'),
    path('skills/<int:pk>/', views.SkillDetailAPIView.as_view(), name='skill_detail_api'),
    path('contact/', views.ContactListCreateAPIView.as_view(), name='contact_list_api'),
    path('contact/<int:pk>/', views.ContactDetailAPIView.as_view(), name='contact_detail_api'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('auth/google/', views.GoogleAuthAPIView.as_view(), name='google_auth_api'),
]
