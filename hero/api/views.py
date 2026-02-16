from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from hero.models import Contact
from .serializers import ContactSerializer
from hero.sms_service import send_sms
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


def send_user_sms(contact):
    print(f"[SMS] Starting for {contact.phone}")
    try:
        phone = contact.phone.replace('+98', '').replace(' ', '').replace('-', '')
        if not phone.startswith('0'):
            phone = '0' + phone
            
        message = f"Ali Mashaghi: Hi {contact.name}, we received your message! We'll contact you soon."
        print(f"[SMS] Sending to {phone}")
        success, result = send_sms(phone, message)
        print(f"[SMS] Result: {success}, {result}")
        if not success:
            print(f"SMS error: {result}")
    except Exception as e:
        print(f"SMS exception: {e}")


@api_view(['GET', 'POST'])
def contact_list_api(request):
    if request.method == 'GET':
        contacts = Contact.objects.all().order_by('-created_at')
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.save()

            # Get phone before starting thread (to avoid DB connection issues)
            phone = contact.phone
            name = contact.name

            # Send SMS synchronously (threading has DB connection issues on Django)
            send_user_sms(contact)

            # Send emails in background using threading
            threading.Thread(target=send_admin_email, args=(contact,)).start()
            threading.Thread(target=send_user_email, args=(contact,)).start()

            return Response(
                {'success': True, 'message': 'Your message has been sent successfully!'},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'success': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


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
