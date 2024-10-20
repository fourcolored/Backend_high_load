from rest_framework import serializers
# from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import User

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, data):
        user = User.objects.create(
            username = data['username'],
            email = data['email'],
            # password = data['password'],
        )
        user.set_password(data['password'])
        user.save()

        return user
    
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


