from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from hero.models import Contact
from .serializers import ContactSerializer
import threading


def send_admin_email(contact):
    try:
        admin_subject = f'New Contact from {contact.name}'
        admin_message = f"""
New contact form submission:

Name: {contact.name}
Email: {contact.email}
Phone: {contact.phone}

Message: {contact.message}
"""
        send_mail(
            subject=admin_subject,
            message=admin_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Admin email error: {e}")


def send_user_email(contact):
    try:
        user_subject = 'We received your message!'
        user_message = f"""
Hi {contact.name},

Thank you for contacting us! We'll get back to you soon.

Best regards,
Ali Mashaghi
"""
        send_mail(
            subject=user_subject,
            message=user_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contact.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"User email error: {e}")





@api_view(['GET', 'PUT', 'DELETE'])
def contact_detail_api(request, pk):
    contact = get_object_or_404(Contact, pk=pk)

    if request.method == 'GET':
        serializer = ContactSerializer(contact)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = ContactSerializer(contact, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'success': True, 'message': 'Contact updated successfully!'}
            )
        return Response(
            {'success': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    if request.method == 'DELETE':
        contact.delete()
        return Response(
            {'success': True, 'message': 'Contact deleted successfully!'},
            status=status.HTTP_204_NO_CONTENT
        )
