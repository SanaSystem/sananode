from .serializers import NodeRegistrationSerializer, UserRegistrationSerializer
from .models import NodeRegistration, UserRegistration
from rest_framework import generics
# Create your views here.

class NodeListView(generics.ListCreateAPIView):
    queryset = NodeRegistration.objects.all()
    serializer_class = NodeRegistrationSerializer

class UserListView(generics.ListCreateAPIView):
    queryset = UserRegistration.objects.all()
    serializer_class = UserRegistrationSerializer

