from django.shortcuts import render
from rest_framework import viewsets
from .serializers import ProfileSerializer, UserSerializer
from .models import Profile, User
# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    lookup_field = 'phone'