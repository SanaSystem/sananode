from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .serializers import UserSerializer, MedBlockSerializer
from .models import User, MedBlock
from rest_framework.decorators import api_view
# Create your views here.

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'medblocks': reverse('medblock-list', request=request, format=format)
    })

class UserListView(generics.ListCreateAPIView):
    """
    GET: Return a list of all existing users

    POST: Create a new user instance
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetailView(generics.RetrieveDestroyAPIView):
    """
    GET: Return the details of user
    
    DELETE: Delete user
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'username'

class MedBlockListView(generics.ListCreateAPIView):
    """
    GET: Return a list of all existing medblocks

    POST: Create a new medblock instance (signature is RSA signature of data)
    """
    queryset = MedBlock.objects.all()
    serializer_class = MedBlockSerializer

class MedBlockDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = MedBlockSerializer
    queryset = MedBlock.objects.all()