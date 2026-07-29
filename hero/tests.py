from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Contact, Project, Skill


class PublicAPITests(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='StrongTestPassword123!',
            first_name='Admin',
            last_name='User',
        )
        self.project = Project.objects.create(
            title='Portfolio',
            description='A sample project.',
            repo_url='https://example.com/project',
        )
        Skill.objects.create(user=self.admin, name='Django', order=1)

    def test_api_root_lists_available_resources(self):
        response = self.client.get(reverse('api_root'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('profile', response.data)
        self.assertIn('projects', response.data)
        self.assertIn('skills', response.data)
        self.assertIn('contact', response.data)

    def test_public_profile_includes_skills_without_auth_fields(self):
        response = self.client.get(reverse('profile_api'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Admin User')
        self.assertEqual(response.data['skills'][0]['name'], 'Django')
        self.assertNotIn('password', response.data)
        self.assertNotIn('is_superuser', response.data)

    def test_projects_are_public_but_writes_require_staff(self):
        list_response = self.client.get(reverse('project_list_api'))
        create_response = self.client.post(
            reverse('project_list_api'),
            {'title': 'Blocked project'},
            format='json',
        )

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data['results'][0]['title'], 'Portfolio')
        self.assertIn(
            create_response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    @patch('hero.api.views.send_contact_emails')
    def test_contact_can_be_submitted_publicly_but_list_is_private(self, send_emails):
        payload = {
            'name': 'Visitor',
            'email': 'visitor@example.com',
            'phone': '+123456789',
            'message': 'I would like to discuss a project.',
        }

        create_response = self.client.post(reverse('contact_list_api'), payload, format='json')
        list_response = self.client.get(reverse('contact_list_api'))

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(create_response.data['success'])
        self.assertTrue(Contact.objects.filter(email='visitor@example.com').exists())
        send_emails.assert_called_once()
        self.assertIn(
            list_response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    @patch('hero.api.views.send_contact_emails', side_effect=OSError('SMTP unavailable'))
    def test_contact_reports_email_delivery_failure(self, send_emails):
        response = self.client.post(
            reverse('contact_list_api'),
            {
                'name': 'Visitor',
                'email': 'visitor@example.com',
                'phone': '+123456789',
                'message': 'Please contact me.',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertFalse(response.data['success'])
        self.assertTrue(Contact.objects.filter(email='visitor@example.com').exists())
        send_emails.assert_called_once()

    def test_staff_can_manage_projects_and_update_profile_skills(self):
        self.client.force_authenticate(self.admin)

        project_response = self.client.post(
            reverse('project_list_api'),
            {
                'title': 'New project',
                'description': 'Created via API.',
                'repo_url': 'https://example.com/new',
            },
            format='json',
        )
        profile_response = self.client.patch(
            reverse('profile_api'),
            {
                'first_name': 'Updated',
                'skills': [
                    {'name': 'Python', 'order': 0},
                    {'name': 'PostgreSQL', 'order': 1},
                ],
            },
            format='json',
        )

        self.assertEqual(project_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.first_name, 'Updated')
        self.assertEqual(
            list(self.admin.skills.values_list('name', flat=True)),
            ['Python', 'PostgreSQL'],
        )


class AdminAppearanceTests(TestCase):
    def test_admin_login_loads_custom_font_styles(self):
        response = self.client.get(reverse('admin:login'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'css/admin.css')
        self.assertContains(response, 'fonts/fonts.css')


class DashboardProjectTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            email='dashboard@example.com',
            password='StrongTestPassword123!',
            first_name='Dashboard',
            last_name='Admin',
        )
        self.client.force_login(self.admin)

    def test_staff_can_create_edit_and_delete_project(self):
        create_response = self.client.post(reverse('dashboard_project_create'), {
            'title': 'New dashboard project',
            'description': 'Created from the dashboard.',
            'repo_url': 'https://example.com/new-project',
        })
        project = Project.objects.get(title='New dashboard project')

        edit_response = self.client.post(
            reverse('dashboard_project_edit', args=[project.pk]),
            {
                'title': 'Updated dashboard project',
                'description': 'Updated from the dashboard.',
                'repo_url': 'https://example.com/updated-project',
            },
        )
        project.refresh_from_db()

        delete_response = self.client.post(
            reverse('dashboard_project_delete', args=[project.pk])
        )

        self.assertRedirects(create_response, reverse('dashboard_projects'))
        self.assertRedirects(edit_response, reverse('dashboard_projects'))
        self.assertEqual(project.title, 'Updated dashboard project')
        self.assertRedirects(delete_response, reverse('dashboard_projects'))
        self.assertFalse(Project.objects.filter(pk=project.pk).exists())


class ProfileFallbackTests(TestCase):
    def test_anonymous_homepage_uses_lorem_even_when_profile_exists(self):
        get_user_model().objects.create_superuser(
            email='hidden@example.com',
            password='StrongHiddenPassword123!',
            first_name='Hidden',
            last_name='Profile',
            title='Hidden title',
        )

        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Lorem ipsum dolor sit amet')
        self.assertNotContains(response, 'Hidden Profile')
        self.assertNotContains(response, 'Hidden title')
        self.assertNotContains(response, 'assets/profile.png')
        self.assertNotContains(response, 'assets/profile 2.png')

    def test_authenticated_pages_use_logged_in_users_profile(self):
        user = get_user_model().objects.create_user(
            email='visible@example.com',
            password='StrongVisiblePassword123!',
            first_name='Visible',
            last_name='Member',
            title='Product Designer',
            bio='Authenticated profile biography.',
            about_me='Authenticated about text.',
            location='Shiraz',
        )
        self.client.force_login(user)

        homepage = self.client.get(reverse('index'))
        resume_page = self.client.get(reverse('resume'))
        card_page = self.client.get(reverse('business_card'))

        self.assertContains(homepage, 'Visible Member')
        self.assertContains(homepage, 'Authenticated profile biography.')
        self.assertContains(homepage, 'Authenticated about text.')
        self.assertContains(resume_page, 'Visible Member')
        self.assertContains(resume_page, 'Product Designer')
        self.assertContains(card_page, 'Visible Member')
        self.assertContains(card_page, 'Shiraz')


class UserRegistrationTests(TestCase):
    def test_login_page_links_to_signup(self):
        response = self.client.get(reverse('admin_login'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, reverse('signup'))

    def test_visitor_can_create_account_and_is_logged_in(self):
        response = self.client.post(reverse('signup'), {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'visitor@example.com',
            'password1': 'StrongRegistrationPassword123!',
            'password2': 'StrongRegistrationPassword123!',
        })

        user = get_user_model().objects.get(email='visitor@example.com')
        self.assertRedirects(response, reverse('index'))
        self.assertFalse(user.is_staff)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_regular_user_login_redirects_to_homepage(self):
        get_user_model().objects.create_user(
            email='member@example.com',
            password='StrongLoginPassword123!',
            first_name='Site',
            last_name='Member',
        )

        response = self.client.post(reverse('admin_login'), {
            'username': 'member@example.com',
            'password': 'StrongLoginPassword123!',
        })

        self.assertRedirects(response, reverse('index'))


class BusinessCardTests(TestCase):
    def setUp(self):
        self.profile = get_user_model().objects.create_superuser(
            email='card@example.com',
            password='StrongCardPassword123!',
            first_name='Card',
            last_name='Owner',
            title='Software Engineer',
            tagline='Building useful products',
            location='Tehran',
            public_email='hello@example.com',
            github_url='https://github.com/example',
            bio='This bio must not appear on the business card.',
            about_me='This about text must not appear on the business card.',
        )

    def test_business_card_uses_contact_details_without_bio(self):
        self.client.force_login(self.profile)
        response = self.client.get(reverse('business_card'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Card Owner')
        self.assertContains(response, 'Software Engineer')
        self.assertContains(response, 'hello@example.com')
        self.assertContains(response, 'https://github.com/example')
        self.assertNotContains(response, self.profile.bio)
        self.assertNotContains(response, self.profile.about_me)

    def test_navigation_links_to_business_card(self):
        response = self.client.get(reverse('index'))

        self.assertContains(response, reverse('business_card'))
