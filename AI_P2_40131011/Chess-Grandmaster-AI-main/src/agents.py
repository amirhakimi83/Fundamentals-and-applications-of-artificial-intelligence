import datetime
import random

import chess

import utiles


class Agent:
    """
        Base class for agents.
    """

    def __init__(self, board: chess.Board, next_player) -> None:
        self.board = board
        self.next_player = next_player

    def get_action(self):
        """
            This method receives a GameState object and returns an action based on its strategy.
        """
        pass

    """
            get possible moves : 
                possibleMoves = board.legal_moves

            create a move object from possible move : 
                move = chess.Move.from_uci(str(possible_move))

            push the move : 
                board.push(move)

            pop the last move:
                board.pop(move)
    """


class RandomAgent(Agent):
    def __init__(self, board: chess.Board, next_player):
        super().__init__(board, next_player)

    def get_action(self):
        return self.random()

    def random(self):
        possible_moves_list = list(self.board.legal_moves)

        random_move = random.choice(possible_moves_list)
        return chess.Move.from_uci(str(random_move))


class MinimaxAgent(Agent):
    def __init__(self, board: chess.Board, next_player, depth):
        self.depth = depth
        super().__init__(board, next_player)

    def get_action(self):
        next_player = self.next_player
        return self.minimax(0, next_player, True)[1]

    def minimax(self, depth, turn, is_maximizing):
        if self.depth == depth:
            my_tuple = (evaluate_board_state(self.board, turn), None)
            return my_tuple
        if is_maximizing:
            alpha = (-float("inf"), None)
            for move in self.board.legal_moves:
                self.board.push(move)
                if self.minimax(depth + 1, turn, not is_maximizing)[0] > alpha[0]:
                    alpha = (self.minimax(depth + 1, turn, not is_maximizing)[0], move)
                self.board.pop()
            return alpha
        else:
            beta = (float("inf"), None)
            for move in self.board.legal_moves:
                self.board.push(move)
                if self.minimax(depth + 1, turn, not is_maximizing)[0] < beta[0]:
                    beta = (self.minimax(depth + 1, turn, not is_maximizing)[0], move)
                self.board.pop()
            return beta

class AlphaBetaAgent(Agent):
    def __init__(self, board: chess.Board, next_player, depth):
        self.depth = depth
        super().__init__(board, next_player)

    def get_action(self):
        next_player = self.next_player
        return self.alpha_beta(0, next_player, True, -float('inf'), float('inf'))[1]

    def terminal_state_check(self, depth, turn):
        if depth == self.depth:
            utility = evaluate_board_state(self.board, turn)
            return (utility, None)

    def maximize(self, depth, turn, alpha, beta):
        max_move = (-float("inf"), None)
        for move in self.board.legal_moves:
            self.board.push(move)
            utility, _ = self.alpha_beta(depth + 1, turn, False, alpha, beta)
            self.board.pop()

            if utility > max_move[0]:
                max_move = (utility, move)
                alpha = max(alpha, utility)

            if max_move[0] >= beta:
                return max_move
        return max_move

    def minimize(self, depth, turn, alpha, beta):
        min_move = (float("inf"), None)
        for move in self.board.legal_moves:
            self.board.push(move)
            utility, _ = self.alpha_beta(depth + 1, turn, True, alpha, beta)
            self.board.pop()

            if utility < min_move[0]:
                min_move = (utility, move)
                beta = min(beta, utility)
            if min_move[0] <= alpha:
                return min_move
        return min_move

    def alpha_beta(self, depth, turn, is_maximizing, alpha, beta):
        if depth == self.depth:
            return self.terminal_state_check(depth, turn)

        if is_maximizing:
            return self.maximize(depth, turn, alpha, beta)
        else:
            return self.minimize(depth, turn, alpha, beta)


class ExpectimaxAgent(Agent):
    def __init__(self, board: chess.Board, next_player, depth):
        self.depth = depth
        super().__init__(board, next_player)

    def get_action(self):
        next_player = self.next_player
        return self.expectimax(0, next_player, True)[1]

    def terminal_state_check(self, depth, turn):
        if depth == self.depth:
            utility = evaluate_board_state(self.board, turn)
            return (utility, None)

    def maximize(self, depth, turn):
        max_move = (-float("inf"), None)
        for move in self.board.legal_moves:
            self.board.push(move)
            utility, _ = self.expectimax(depth + 1, turn, False)
            self.board.pop()

            if utility > max_move[0]:
                max_move = (utility, move)
        return max_move

    def expect(self, depth, turn):
        utility = 0
        for move in self.board.legal_moves:
            self.board.push(move)
            utility += self.expectimax(depth + 1, turn, True)[0]
            self.board.pop()
        try:
            utility /= self.board.legal_moves.count()
        except ZeroDivisionError:
            utility = 0
        return (utility, None)

    def expectimax(self, depth, turn, is_maximizing):
        if depth == self.depth:
            return self.terminal_state_check(depth, turn)

        if is_maximizing:
            return self.maximize(depth, turn)
        else:
            return self.expect(depth, turn)


def evaluate_board_state(board, turn):
    node_evaluation = 0
    node_evaluation += utiles.check_status(board, turn)
    node_evaluation += utiles.evaluationBoard(board)
    node_evaluation += utiles.checkmate_status(board, turn)
    node_evaluation += utiles.good_square_moves(board, turn)
    if turn == 'white':
        return node_evaluation
    return -node_evaluation

