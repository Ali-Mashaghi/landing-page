from django.shortcuts import get_object_or_404
from django.contrib import messages
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from hero.models import Contact
from hero.forms import ContactForm
from .serializers import ContactSerializer


@api_view(['GET', 'POST'])
def contact_list_api(request):
    if request.method == 'GET':
        contacts = Contact.objects.all().order_by('-created_at')
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)
    
    if request.method == 'POST':
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
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
