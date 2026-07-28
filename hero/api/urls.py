from django.urls import path
from . import views

urlpatterns = [
    path('contact/', views.contact_api, name='contact_api'),
    path('contact/<int:pk>/', views.contact_detail_api, name='contact_detail_api'),
]
