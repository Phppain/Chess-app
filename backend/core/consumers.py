import json
from channels.generic.websocket import AsyncWebsocketConsumer
from api.models import Game
from importlib import import_module
import api.game
from asgiref.sync import sync_to_async
from types import SimpleNamespace


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_group_name = f'game_{self.game_id}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        self.game = await sync_to_async(Game.objects.get)(id=self.game_id)
        self.board = self.game.board_state

        # if self.game.board_state:
        #     self.board.load_position(self.game.board_state)

        await self.send_board_state()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("type")

        if action == "move":
            await self.handle_move(data)
        elif action == "get_possible_moves":
            await self.handle_possible_moves(data)

    async def handle_move(self, data):
        old_pos = tuple(data["from"])
        new_pos = tuple(data["to"])

        piece = self.board.get_id_board_position(old_pos)

        if not piece:
            await self.send(text_data=json.dumps({"error": "No piece at the given position"}))
            return

        if piece.can_move(new_pos):
            # Проверка на шах, если ход приведет к шаху, отклоняем его
            temp_board = self.board.copy()  # Создаём копию доски для проверки
            temp_board.move_piece(old_pos, new_pos)
            if temp_board.is_check(piece.color):
                await self.send(text_data=json.dumps({"error": "Move places the king in check"}))
                return

            # Выполняем ход
            self.board.move_piece(old_pos, new_pos)
            await self.save_board_state()

            # Проверка на мат или пат
            if self.board.is_checkmate(piece.color):
                await self.send(text_data=json.dumps({"message": "Checkmate!"}))
            elif self.board.is_stalemate(piece.color):
                await self.send(text_data=json.dumps({"message": "Stalemate!"}))

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_board_state"
                }
            )
        else:
            await self.send(text_data=json.dumps({"error": "Invalid move"}))

    async def handle_possible_moves(self, data):
        from_pos = data.get("from")
        piece = data.get('board')[from_pos]

        print(piece)
        if piece:
            # print(data.get('board'))
            module = import_module("api.game")
            PieceClass = getattr(module, piece["type"], None)
            piece = PieceClass(color=piece["color"], position=piece["position"], board=self.board)

            moves =  piece.possible_moves()
            print(moves)
            await self.send(text_data=json.dumps({
                "type": "possible_moves",
                "moves": moves
            }))
        else:
            await self.send(text_data=json.dumps({
                "type": "possible_moves",
                "moves": []
            }))

    async def send_board_state(self, event=None):
        pieces = []
        # print(self.game.board_state)
        for position, piece in self.game.board_state.items():
            pieces.append({
                "type": piece['type'],
                "color": piece['color'],
                "position": piece['position']
            })

        await self.send(text_data=json.dumps({
            "type": "board_state",
            "pieces": pieces
        }))

    @sync_to_async
    def save_board_state(self):
        self.game.board_state = self.board.board_position_as_dict()
        self.game.save()
