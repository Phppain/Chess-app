import json
from channels.generic.websocket import AsyncWebsocketConsumer
from api.game import Board
from api.models import Game, User
from asgiref.sync import sync_to_async
from django.utils import timezone


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_group_name = f'game_{self.game_id}'

        # Присоединение к группе
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Загрузка состояния игры
        self.game = await sync_to_async(Game.objects.get)(id=self.game_id)
        self.board = Board()
        if self.game.board_state:
            self.board.load_position(self.game.board_state)  # метод load_position ты можешь реализовать сам

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "move":
            await self.handle_move(data)

    async def handle_move(self, data):
        old_pos = tuple(data["from"])
        new_pos = tuple(data["to"])
        user_id = data.get("user_id")

        piece = self.board.get_id_board_position(old_pos)

        if piece and piece.can_move(new_pos):
            # Обновление позиции
            self.board.board_position[old_pos] = None
            self.board.board_position[new_pos] = piece

            # Сохраняем состояние доски
            await self.save_board_state()

            # Отправляем новое состояние всем участникам
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_board_state"
                }
            )
        else:
            await self.send(text_data=json.dumps({"error": "Invalid move"}))

    async def send_board_state(self, event=None):
        pieces = []
        for (row, col), piece in self.board.board_position.items():
            if piece:
                pieces.append({
                    "type": piece.__class__.__name__.lower(),
                    "color": piece.color,
                    "position": [row, col]
                })

        await self.send(text_data=json.dumps({"pieces": pieces}))

    @sync_to_async
    def save_board_state(self):
        self.game.board_state = self.board.board_position_as_dict()
        self.game.save()