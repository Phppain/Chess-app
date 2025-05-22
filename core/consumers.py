import json
from channels.generic.websocket import AsyncWebsocketConsumer
from api.models import Game
from importlib import import_module
import api.game as gm
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
        old_pos = str(data["from"])
        new_pos = str(data["to"])

        module = import_module("api.game")
        board = gm.Board()
        board.deserialize(self.board)
        piece = board.get_id_board_position(old_pos)

        print('PIECE', piece)

        if not piece:
            await self.send(text_data=json.dumps({"error": "No piece at the given position"}))
            return



        if piece.can_move(new_pos):
            temp_board = self.board.copy()
            temp_board[new_pos] = {'type': piece.__class__.__name__, 'color': piece.color, 'position': piece.position}
            temp_board[old_pos] = {'type': None, 'color': None, 'position': old_pos}
            class_temp_board = gm.Board()
            class_temp_board.deserialize(temp_board)
            print(class_temp_board)
            if class_temp_board.is_check(piece.color):
                await self.send(text_data=json.dumps({"error": "Move places the king in check"}))

            # Выполняем ход
            self.board[new_pos] = {'type': piece.__class__.__name__, 'color': piece.color, 'position': piece.position}
            self.board[old_pos] = {'type': None, 'color': None, 'position': old_pos}
            await self.save_board_state()

            print(self.board)

            # Проверка на мат или пат
            if board.is_checkmate(piece.color):
                await self.send(text_data=json.dumps({"message": "Checkmate!"}))
            elif board.is_stalemate(piece.color):
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
            board = gm.Board()
            board.deserialize(data['board'])
            piece = PieceClass(color=piece["color"], position=piece["position"], board=board)

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
        print(self.game.board_state)
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
        self.game.board_state = self.board
        # self.game.save()
