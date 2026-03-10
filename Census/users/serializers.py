from rest_framework import serializers
from .models import Users

# Serializer for Users
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Users
        fields = '__all__'
        extra_kwargs = {
            'avatar_url': {'required': False}
        }
