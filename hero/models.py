from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from .managers import UserManager


class Contact(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    repo_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self) -> str:
        return self.title


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    bio = models.TextField(max_length=500, blank=True)
    about_me = models.TextField(max_length=500, blank=True)
    title = models.CharField(max_length=200, blank=True, help_text='e.g. Full Stack Developer')
    tagline = models.CharField(max_length=300, blank=True)
    location = models.CharField(max_length=200, blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    x_url = models.URLField(blank=True)
    telegram_url = models.URLField(blank=True)
    public_email = models.EmailField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    resume = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text='Only PDF files are allowed.',
    )

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()


class Skill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'
        ordering = ['order', 'id']

    def __str__(self):
        return self.name
