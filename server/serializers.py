from rest_framework import serializers
from .models import NodeRegistration, UserRegistration
class NodeRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeRegistration
        fields = ('ipAddress','couchReplication','ipfsReplication')

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRegistration
        fields = ('name','email','publicKey')