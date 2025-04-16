import chess

# Простой материал-бейст оценщик позиции
def evaluate_board(board):
    values = {
        chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
        chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0
    }
    eval = 0
    for piece in values:
        eval += len(board.pieces(piece, chess.WHITE)) * values[piece]
        eval -= len(board.pieces(piece, chess.BLACK)) * values[piece]
    return eval

# Minimax с глубиной и alpha-beta pruning
def minimax(board, depth, alpha, beta, is_maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    best_move = None

    if is_maximizing:
        max_eval = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            eval, _ = minimax(board, depth - 1, alpha, beta, False)
            board.pop()

            if eval > max_eval:
                max_eval = eval
                best_move = move

            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move

    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval, _ = minimax(board, depth - 1, alpha, beta, True)
            board.pop()

            if eval < min_eval:
                min_eval = eval
                best_move = move

            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

# Получить ход бота
def get_bot_move(board, depth=2):
    _, move = minimax(board, depth, float('-inf'), float('inf'), board.turn)
    return move