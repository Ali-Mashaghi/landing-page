from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from captcha.fields import CaptchaField
from .models import Contact, Project, User, Skill


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your message', 'rows': 6}),
        }
        labels = {
            'name': 'Full Name',
            'email': 'Email Address',
            'phone': 'Phone Number',
            'message': 'Message',
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'image', 'repo_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png,image/webp,image/gif',
            }),
            'repo_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/project',
            }),
        }


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'admin@example.com',
            'autofocus': True,
        }),
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        }),
    )
    captcha = CaptchaField(label='Captcha')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['captcha'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter the characters shown',
            'autocomplete': 'off',
        })


class SignupForm(UserCreationForm):
    captcha = CaptchaField(label='Captcha')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name',
                'autofocus': True,
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'you@example.com',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password',
        })
        self.fields['captcha'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter the characters shown',
            'autocomplete': 'off',
        })


class PasswordResetRequestForm(PasswordResetForm):
    captcha = CaptchaField(label='Captcha')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = 'Email'
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'you@example.com',
            'autofocus': True,
            'autocomplete': 'email',
        })
        self.fields['captcha'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter the characters shown',
            'autocomplete': 'off',
        })


class PasswordResetConfirmForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'New password',
            'autocomplete': 'new-password',
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password',
        })


class ProfileForm(forms.ModelForm):
    profile_image = forms.ImageField(
        required=False,
        label='Profile Photo',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/jpeg,image/png,image/webp,image/gif',
        }),
    )
    resume = forms.FileField(
        required=False,
        label='Resume (PDF)',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'application/pdf,.pdf',
        }),
    )
    skills_text = forms.CharField(
        required=False,
        label='Skills',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Python\nDjango\nHTML/CSS',
        }),
        help_text='One skill per line. Shown in the My Skills section on the homepage.',
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'bio',
            'about_me',
            'title',
            'tagline',
            'location',
            'public_email',
            'profile_image',
            'github_url',
            'linkedin_url',
            'x_url',
            'telegram_url',
            'resume',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'about_me': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'tagline': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'I build websites that',
            }),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'public_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control'}),
            'x_url': forms.URLInput(attrs={'class': 'form-control'}),
            'telegram_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://t.me/username',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['skills_text'].initial = '\n'.join(
                self.instance.skills.values_list('name', flat=True)
            )

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            skill_names = [
                line.strip()
                for line in self.cleaned_data.get('skills_text', '').splitlines()
                if line.strip()
            ]
            user.skills.all().delete()
            Skill.objects.bulk_create([
                Skill(user=user, name=name, order=index)
                for index, name in enumerate(skill_names)
            ])
        return user

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if not image or getattr(image, '_committed', False):
            return image

        filename = image.name.lower()
        allowed_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
        if not any(filename.endswith(ext) for ext in allowed_extensions):
            raise forms.ValidationError('Profile photo must be JPG, PNG, WEBP, or GIF.')

        content_type = getattr(image, 'content_type', '')
        if content_type and not content_type.startswith('image/'):
            raise forms.ValidationError('Profile photo must be JPG, PNG, WEBP, or GIF.')

        return image

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if not resume or getattr(resume, '_committed', False):
            return resume

        filename = resume.name.lower()
        content_type = getattr(resume, 'content_type', '')

        if not filename.endswith('.pdf'):
            raise forms.ValidationError('Resume file must be a PDF.')

        if content_type and content_type not in ('application/pdf', 'application/x-pdf'):
            raise forms.ValidationError('Resume file must be a PDF.')

        return resume
