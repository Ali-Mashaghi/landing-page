from django.http import Http404
from rest_framework import status
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from hero.models import Contact, Project, Skill, User
from hero.services.email import send_contact_emails
from hero.services.google_auth import (
    GoogleAuthError,
    get_or_create_user_from_google,
    verify_google_id_token,
)
from .permissions import IsAdminOrReadOnly
from .serializers import (
    ContactSerializer,
    ProjectSerializer,
    SkillSerializer,
    UserProfileSerializer,
)
from .throttles import ContactSubmissionThrottle


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        'profile': reverse('profile_api', request=request),
        'projects': reverse('project_list_api', request=request),
        'skills': reverse('skill_list_api', request=request),
        'contact': reverse('contact_list_api', request=request),
        'token': reverse('token_obtain_pair', request=request),
        'token_refresh': reverse('token_refresh', request=request),
        'google_auth': reverse('google_auth_api', request=request),
    })


class GoogleAuthAPIView(APIView):
    """Exchange a Google ID token for SimpleJWT access/refresh tokens."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        id_token_value = (
            request.data.get('id_token')
            or request.data.get('credential')
            or ''
        )
        try:
            payload = verify_google_id_token(id_token_value)
            user, created = get_or_create_user_from_google(payload)
        except GoogleAuthError as exc:
            return Response(
                {'detail': str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'created': created,
                'user': {
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_staff': user.is_staff,
                },
            },
            status=status.HTTP_200_OK,
        )


class ContactListCreateAPIView(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    throttle_classes = [ContactSubmissionThrottle]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAdminUser()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        contact = serializer.save()
        try:
            send_contact_emails(contact)
        except Exception:
            return Response(
                {
                    'success': False,
                    'message': (
                        'Your message was saved, but email delivery failed. '
                        'Please try again later.'
                    ),
                    'contact_id': contact.pk,
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(
            {
                'success': True,
                'message': 'Your message has been sent successfully!',
                'contact_id': contact.pk,
            },
            status=status.HTTP_201_CREATED,
        )


class ContactDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAdminUser]


class ProjectListCreateAPIView(generics.ListCreateAPIView):
    queryset = Project.objects.all().order_by('-created_at')
    serializer_class = ProjectSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [JSONParser, FormParser, MultiPartParser]


class ProjectDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [JSONParser, FormParser, MultiPartParser]


class SkillListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = SkillSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = Skill.objects.select_related('user')
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return queryset
        return queryset.filter(user__is_active=True, user__is_staff=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SkillDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SkillSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = Skill.objects.select_related('user')
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return queryset
        return queryset.filter(user__is_active=True, user__is_staff=True)


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_object(self):
        if self.request.method in ('PUT', 'PATCH'):
            return self.request.user
        profile = (
            User.objects.filter(is_staff=True, is_active=True)
            .prefetch_related('skills')
            .order_by('id')
            .first()
        )
        if profile is None:
            raise Http404
        return profile
