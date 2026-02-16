from rest_framework import serializers
from hero.models import Contact, Project


class ContactSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required=True)
    
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'phone', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'image', 'repo_url', 'created_at']
        read_only_fields = ['id', 'created_at']
