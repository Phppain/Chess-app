# chess_engine.py

from copy import deepcopy

class InvalidMoveError(Exception):
    pass


class ChessGame:
    def __init__(self, board=None, current_turn='white'):
        self.board = board or self.default_board()
        self.current_turn = current_turn  # 'white' or 'black'
        self.move_history = []

    def default_board(self):
        return [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p'] * 8,
            [''] * 8,
            [''] * 8,
            [''] * 8,
            [''] * 8,
            ['P'] * 8,
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]

    def make_move(self, from_pos, to_pos):
        fx, fy = from_pos
        tx, ty = to_pos
        piece = self.board[fx][fy]

        if not piece:
            raise InvalidMoveError("No piece at the starting square")

        if self.current_turn == 'white' and piece.islower():
            raise InvalidMoveError("It's white's turn")
        if self.current_turn == 'black' and piece.isupper():
            raise InvalidMoveError("It's black's turn")

        # Add piece-specific rules later (pawns, castling, etc.)
        self.board[tx][ty] = piece
        self.board[fx][fy] = ''
        self.move_history.append(((fx, fy), (tx, ty)))

        self.current_turn = 'black' if self.current_turn == 'white' else 'white'

    def serialize(self):
        return {
            "board": deepcopy(self.board),
            "turn": self.current_turn,
            "history": deepcopy(self.move_history),
        }

    @staticmethod
    def deserialize(data):
        game = ChessGame()
        game.board = data['board']
        game.current_turn = data['turn']
        game.move_history = data['history']
        return game