"""
Views for User API
"""

from rest_framework import generics

from user.serializers import UserSerializer

class CreateUserSerializer(generics.CreateAPIView):
    serializer_class = UserSerializer