class Board:
    def __init__(self):
        self.white_killed_pieces = []
        self.black_killed_pieces = []
        self._board_position = self.initialize_board()

    @property
    def board_position(self):
        return self._board_position  

    @board_position.setter
    def board_position(self, new_position_piece):
        self._board_position[new_position_piece[0]] = new_position_piece[1]
    
    def get_id_board_position(self, position):
        return self._board_position.get(position, None)

    def initialize_board(self):
        board = {}

        for row in range(8):
            for col in range(8):
                board[(row, col)] = None

        # Пешки
        for col in range(8):
            board[(1, col)] = Pawn('white', (1, col), self)
            board[(6, col)] = Pawn('black', (6, col), self)
        
        # Ладьи
        board[(0, 0)] = Rook('white', (0, 0), self)
        board[(0, 7)] = Rook('white', (0, 7), self)
        board[(7, 0)] = Rook('black', (7, 0), self)
        board[(7, 7)] = Rook('black', (7, 7), self)

        # Слоны
        board[(0, 2)] = Bishop('white', (0, 2), self)
        board[(0, 5)] = Bishop('white', (0, 5), self)
        board[(7, 2)] = Bishop('black', (7, 2), self)
        board[(7, 5)] = Bishop('black', (7, 5), self)

        # Кони
        board[(0, 1)] = Knight('white', (0, 1), self)
        board[(0, 6)] = Knight('white', (0, 6), self)
        board[(7, 1)] = Knight('black', (7, 1), self)
        board[(7, 6)] = Knight('black', (7, 6), self)

        # Короли
        board[(0, 3)] = King('white', (0, 3), self)
        board[(7, 3)] = King('black', (7, 3), self)

        # Ферзи
        board[(0, 4)] = Queen('white', (0, 4), self)
        board[(7, 4)] = Queen('black', (7, 4), self)

        return board

    def serialize(self):
        """Для сохранения в базу"""
        result = {}
        for position, piece in self._board_position.items():
            if piece:
                result[str(position)] = {
                    "type": piece.__class__.__name__,
                    "color": piece.color,
                    "position": piece.position,
                }
        return result

    def deserialize(self, data):
        """Для восстановления доски из базы"""
        self._board_position = {}
        for pos_str, piece_data in data.items():
            row, col = eval(pos_str)  # (0, 1) как строка → tuple
            piece_type = piece_data['type']
            color = piece_data['color']
            position = tuple(piece_data['position'])

            piece_class = globals()[piece_type]
            self._board_position[(row, col)] = piece_class(color, position, self)

    def board_position_as_dict(self):
        """Аналог serialize — просто удобное имя"""
        return self.serialize()

    def load_position(self, data):
        """Аналог deserialize — просто удобное имя"""
        self.deserialize(data)


class Piece:
    price = 1

    def __init__(self, color, position, board):
        self.color = color
        self._position = position
        self.board = board  # Ссылка на объект Board
    
    @property
    def position(self):
        return self._position

    def can_move(self, new_position):
        board = self.board.board_position
        piece = board.get(new_position)

        if piece is None:
            return new_position
        elif piece.color != self.color:
            self.attack(piece, piece.price, piece.color)
            return new_position

        return None

    def possible_moves(self):
        pass
        
    def attack(self, attacked_piece, price, color):
        if color == 'black':
            self.board.white_killed_pieces.append(attacked_piece)
        else:
            self.board.black_killed_pieces.append(attacked_piece)


class Pawn(Piece):
    def possible_moves(self):
        moves = []

        if self.color == 'white':
            if self.position[0] == 1:
                move = self.can_move((self.position[0] + 2, self.position[1]))
                moves.append(move)
        
            move = self.can_move((self.position[0] + 1, self.position[1]))

        else:
            if self.position[0] == 6:
                move = self.can_move((self.position[0] - 2, self.position[1]))
                moves.append(move)
        
            move = self.can_move((self.position[0] - 1, self.position[1]))

        moves.append(move)

        return moves
    

class Rook(Piece):
    price = 5

    def possible_moves(self):
        moves = []
        board = self.board.board_position

        for row in range(8):
            if self.position[0] == row:
                continue
            move = self.can_move((row, self.position[1]))
            moves.append(move)
        
        for col in range(8):
            if self.position[1] == col:
                continue
            move = self.can_move((self.position[0], col))
            moves.append(move)
        
        return moves


class Bishop(Piece):
    price = 3

    def possible_moves(self):
        moves = []
        board = self.board.board_position

        for diagonal in range(1, 8):
            move1 = self.can_move((self.position[0] + diagonal, self.position[1] + diagonal))
            move2 = self.can_move((self.position[0] - diagonal, self.position[1] - diagonal))

            moves.append(move1)
            moves.append(move2)

        return moves


class Knight(Piece):
    price = 3

    def possible_moves(self):
        board = self.board.board_position

        moves = [
            (2, -1), (2, 1), (-2, 1), (-2, -1),
            (1, -2), (1, 2), (-1, 2), (-1, -2)
        ]

        valid_moves = [
            (self.position[0] + dx, self.position[1] + dy) 
            for dx, dy in moves
            if self.can_move((self.position[0] + dx, self.position[1] + dy))
        ]
        return valid_moves


class Queen(Piece):
    price = 8

    def possible_moves(self):
        moves = []

        board = self.board.board_position

        for row in range(8):
            if self.position[0] == row:
                continue
            move = self.can_move((row, self.position[1]))
            moves.append(move)
        
        for col in range(8):
            if self.position[1] == col:
                continue
            move = self.can_move((self.position[0], col))
            moves.append(move)
        
        for diagonal in range(1, 8):
            move1 = self.can_move((self.position[0] + diagonal, self.position[1] + diagonal))
            move2 = self.can_move((self.position[0] - diagonal, self.position[1] - diagonal))

            moves.append(move1)
            moves.append(move2)
        
        return moves


class King(Piece):
    def possible_moves(self):
        moves = []


        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in directions:
            moves.append(self.can_move((self.position[0] + dx, self.position[1] + dy)))
        
        return moves
