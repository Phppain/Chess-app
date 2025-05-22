from rest_framework import serializers
from .models import Game, Move, User
from django.contrib.auth import authenticate

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__' 


class MoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Move
        fields = '__all__'
        

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'nickname', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Неверные данные для входа")
