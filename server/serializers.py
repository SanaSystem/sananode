from rest_framework import serializers
from django.db import IntegrityError
from .models import NodeRegistration, UserRegistration, Permission
class NodeRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeRegistration
        fields = ('ipAddress','couchReplication','ipfsReplication')

class UserRegistrationSerializer(serializers.ModelSerializer):
    permissions = serializers.SlugRelatedField(slug_field='medblockId',many=True, read_only=True)
    class Meta:
        model = UserRegistration
        fields = ('name','email','publicKey','permissions')

class PermissionSerializer(serializers.Serializer):
    email = serializers.EmailField()
    medblockId = serializers.CharField()


    def validate_email(self, value):
        if len(UserRegistration.objects.filter(email=value)) == 0:
            raise serializers.ValidationError("Email not registered")
        return value
    def create(self, validated_data):
        print(validated_data)
        user = UserRegistration.objects.get(email=validated_data['email'])
        print(user)
        try:
            return Permission.objects.create(medblockId=validated_data['medblockId'], user=user)
        except IntegrityError:
            raise serializers.ValidationError("Combination of email and medblock id already exists")
    