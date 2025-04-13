from rest_framework import viewsets, serializers
from .models import Game, User, Move
from .serializer import GameSerializer, UserSerializer, MoveSerializer, LoginSerializer, RegisterSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password, check_password
from rest_framework import status
from .game import Board

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    @action(detail=False, methods=['post'])
    def start_new(self, request):
        try:
            player_white = User.objects.get(id=request.data.get("player_white"))
            player_black = User.objects.get(id=request.data.get("player_black"))

            board = Board()
            game = Game.objects.create(
                player_white=player_white, 
                player_black=player_black, 
                result=request.data.get("result"),
                board_state=board.serialize(),  # сохраняем начальное состояние доски
            )

            return Response({
                "game": GameSerializer(game).data,
                "pieces": board.serialize()
            }, status=status.HTTP_201_CREATED)
        
        except User.DoesNotExist:
            return Response({"error": "Игрок не найден"}, status=status.HTTP_400_BAD_REQUEST)

class MoveViewSet(viewsets.ModelViewSet):
    queryset = Move.objects.all()
    serializer_class = MoveSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname', 'first_name', 'last_name', 'email', 'avatar_img', 'rank']

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'])
    def get_users(self, request):
        users = User.objects.all()
        return Response(UserSerializer(users, many=True).data)
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        data = request.data

        # Валидация данных
        if not data.get('nickname') or not data.get('email') or not data.get('password') or not data.get('firstName') or not data.get('lastName'):
            return Response({"error": "Nickname, email and password are required"}, status=400)

        # Проверка на существование пользователя с таким ником или email
        if User.objects.filter(nickname=data['nickname']).exists():
            return Response({"error": "Nickname is already taken"}, status=400)

        if User.objects.filter(email=data['email']).exists():
            return Response({"error": "Email is already taken"}, status=400)

        # Хэширование пароля
        hashed_password = make_password(data['password'])

        # Создание нового пользователя
        user = User.objects.create(
            nickname=data['nickname'],
            first_name=data.get('firstName', ''),
            last_name=data.get('lastName', ''),
            email=data['email'],
            password=hashed_password,
            avatar_img=data.get('avatar_img', None),
            rank=500  # или как ты хочешь задать начальный рейтинг
        )

        return Response(UserSerializer(user).data, status=201)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        data = request.data

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            print(email)
            return Response({"error": "User does not exist"}, status=400)

        if not check_password(password, user.password):
            return Response({"error": "Incorrect password"}, status=400)

        return Response({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "nickname": user.nickname,
                "email": user.email,
                "rank": user.rank
            }
        })
