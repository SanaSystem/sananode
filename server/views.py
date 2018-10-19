from .serializers import NodeRegistrationSerializer, UserRegistrationSerializer, PermissionSerializer
from .models import NodeRegistration, UserRegistration, Permission
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'nodes': reverse('node-list', request=request, format=format),
        'users': reverse('user-list', request=request, format=format),
        'permissions':reverse('permission-list', request=request, format=format)
    })
class NodeListView(generics.ListCreateAPIView):
    queryset = NodeRegistration.objects.all()
    serializer_class = NodeRegistrationSerializer

class UserListView(generics.ListCreateAPIView):
    queryset = UserRegistration.objects.all()
    serializer_class = UserRegistrationSerializer

class PermissionsView(generics.ListCreateAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer