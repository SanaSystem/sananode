from rest_framework import serializers
from api.models import Profile, User, MedBlock, Key

# User Serializer
class UserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True)
    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], password=validated_data['password'])
        return user
    class Meta:
        model = User
        fields = ('id', 'profile', '')
# Profile Serializer
class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'user', 'phone', 'rsa_public_key', 'encrypted_rsa_private_key')