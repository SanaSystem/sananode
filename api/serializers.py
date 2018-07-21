from rest_framework import serializers
from api.models import Profile, User, MedBlock, Key

class MedBlockSerializer(serializers.ModelSerializer):
    signature = serializers.CharField(write_only=True)
    class Meta:
        model = MedBlock
        url = serializers.HyperlinkedIdentityField(view_name='medblock-detail')
        read_only_fields = ('last_synced',)
        fields = ('url','last_synced', 'format', 'data', 'user','signature')
    def validate(self, data):
        # Verify signature
        if not data.get('signature') == '123':
            raise serializers.ValidationError("Invalid Signature", "203")
        return data

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('phone', 'rsa_public_key', 'encrypted_rsa_private_key')

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='user-detail', lookup_field='username')
    profile = ProfileSerializer(required=False)
    password = serializers.CharField(write_only=True)
    medblocks = MedBlockSerializer(many=True, read_only=True)
    class Meta:
        model = User
        fields = ('url','profile', 'first_name', 'last_name','password', 'profile', 'medblocks')

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create(username=profile_data.get('phone'), **validated_data)
        user.profile.phone = profile_data.get('phone')
        user.profile.rsa_public_key = profile_data.get('rsa_public_key')
        user.profile.encrypted_rsa_private_key = profile_data.get('encrypted_rsa_public_key')
        user.save()
        return user
    
    def update(self, validated_data):
        pass

