from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from hero.models import Contact
from hero.services.email import send_contact_emails_parallel
from .serializers import ContactSerializer


@api_view(['GET', 'POST'])
def contact_api(request):
    if request.method == 'GET':
        if not request.user.is_staff:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        contacts = Contact.objects.all()
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    serializer = ContactSerializer(data=request.data)
    if serializer.is_valid():
        contact = serializer.save()
        send_contact_emails_parallel(contact)
        return Response(
            {'success': True, 'message': 'Your message has been sent successfully!'},
            status=status.HTTP_201_CREATED,
        )
    return Response(
        {'success': False, 'errors': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def contact_detail_api(request, pk):
    contact = get_object_or_404(Contact, pk=pk)

    if request.method == 'GET':
        serializer = ContactSerializer(contact)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = ContactSerializer(contact, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Contact updated successfully!'})
        return Response(
            {'success': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    contact.delete()
    return Response(
        {'success': True, 'message': 'Contact deleted successfully!'},
        status=status.HTTP_204_NO_CONTENT,
    )
