from rest_framework import serializers
from hero.models import Contact, Project, Skill, User


class ContactSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required=True)

    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'phone', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        for field in ('name', 'phone', 'message'):
            value = attrs.get(field)
            if isinstance(value, str):
                attrs[field] = value.strip()
                if not attrs[field]:
                    raise serializers.ValidationError({field: 'This field may not be blank.'})
        return attrs


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'image', 'repo_url', 'created_at']
        read_only_fields = ['id', 'created_at']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'order']
        read_only_fields = ['id']

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Skill name may not be blank.')
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    skills = SkillSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'full_name',
            'bio',
            'about_me',
            'title',
            'tagline',
            'location',
            'public_email',
            'profile_image',
            'resume',
            'github_url',
            'linkedin_url',
            'x_url',
            'telegram_url',
            'skills',
            'updated_date',
        ]
        read_only_fields = ['id', 'full_name', 'updated_date']

    def update(self, instance, validated_data):
        skills_data = validated_data.pop('skills', None)
        instance = super().update(instance, validated_data)

        if skills_data is not None:
            instance.skills.all().delete()
            Skill.objects.bulk_create([
                Skill(
                    user=instance,
                    name=skill['name'],
                    order=skill.get('order', index),
                )
                for index, skill in enumerate(skills_data)
            ])

        return instance
