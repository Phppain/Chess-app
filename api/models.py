# models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, nickname, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        if not nickname:
            raise ValueError("Ник обязателен")

        email = self.normalize_email(email)
        user = self.model(email=email, nickname=nickname, **extra_fields)
        user.set_password(password)  # 🔐 тут хеширование
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nickname, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, nickname, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    avatar_img = models.ImageField(upload_to="avatars/", blank=True, null=True)
    rank = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    def __str__(self):
        return f'{self.nickname} ({self.email})'


class Move(models.Model):
    game = models.ForeignKey('Game', on_delete=models.CASCADE, related_name='moves')
    move_number = models.IntegerField()
    move = models.CharField(max_length=10)
    moved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Moves – {self.game_id}'


class Game(models.Model):
    class Result(models.TextChoices):
        IN_PROGRESS = 'INP', 'In progress'
        CHECKMATE = 'CM', 'Checkmate'
        STALEMATE = 'SM', 'Stalemate'
        DRAW = 'DW', 'Draw'
        PERPETUAL_CHECK = 'PPC', 'Perpetual check'
        INSUFFICIENT_MATERIAL = 'ISFCM', 'Insufficient material'
        THREEFOLD_REPETITION = 'TFRP', 'Threefold repetition'
        FIFTY_MOVE_RULE = 'FMR', 'Fifty-move rule'

    player_white = models.ForeignKey(User, on_delete=models.CASCADE, related_name='white_games')
    player_black = models.ForeignKey(User, on_delete=models.CASCADE, related_name='black_games')
    result = models.CharField(max_length=100, choices=Result.choices)
    winner_id = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='win_games')
    created_at = models.DateTimeField(auto_now_add=True)

    current_turn = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='current_turn_games')
    board_state = models.JSONField(default=dict)  # requires PostgreSQL, or switch to TextField if SQLite
    is_active = models.BooleanField(default=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Game – {self.result}'
