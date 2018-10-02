from .serializers import NodeRegistrationSerializer, UserRegistrationSerializer
from .models import NodeRegistration, UserRegistration
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'nodes': reverse('node-list', request=request, format=format),
        'users': reverse('user-list', request=request, format=format)
    })
class NodeListView(generics.ListCreateAPIView):
    queryset = NodeRegistration.objects.all()
    serializer_class = NodeRegistrationSerializer

class UserListView(generics.ListCreateAPIView):
    queryset = UserRegistration.objects.all()
    serializer_class = UserRegistrationSerializer

