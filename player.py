#!/usr/bin/env python3
import math
import random
import time

from fishing_game_core.game_tree import Node
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR, TYPE_TO_SCORE

# Requirement from Kattis
TIME_LIMIT = 0.075

class PlayerControllerHuman(PlayerController):
    def player_loop(self):
        """
        Function that generates the loop of the game. In each iteration
        the human plays through the keyboard and send
        this to the game through the sender. Then it receives an
        update of the game through receiver, with this it computes the
        next movement.
        :return:
        """

        while True:
            # send message to game that you are ready
            msg = self.receiver()
            if msg["game_over"]:
                return


class PlayerControllerMinimax(PlayerController):

    def __init__(self):
        super(PlayerControllerMinimax, self).__init__()
        self.start_time = None
        self.cache = dict()

    def player_loop(self):
        """
        Main loop for the minimax next move search.
        :return:
        """

        # Generate first message (Do not remove this line!)
        first_msg = self.receiver()

        while True:
            msg = self.receiver()

            # Create the root node of the game tree
            node = Node(message=msg, player=0)

            # Possible next moves: "stay", "left", "right", "up", "down"
            self.start_time = time.time()
            best_move = self.search_best_next_move(initial_tree_node=node)

            # Execute next action
            self.sender({"action": best_move, "search_time": None})

    @staticmethod
    def euclidean_distance(pt1, pt2):
        x = abs(pt2[0] - pt1[0])
        x = min(x, 20-x)
        return math.sqrt(math.pow(x, 2) + math.pow(pt2[1] - pt1[1], 2))

    @staticmethod
    def manhattan_distance(pt1, pt2):
        x = abs(pt2[0] - pt1[0])
        return min(x, 20 - x) + abs(pt2[1] - pt1[1])

    def heuristic_func(
        self,
        current_node: Node,
    ) -> float:

        current_player = current_node.state.get_player()
        hooks_positions = current_node.state.get_hook_positions()
        hook_position = hooks_positions[current_player]

        caught = current_node.state.get_caught()
        player_scores = current_node.state.get_player_scores()

        fish_positions = current_node.state.get_fish_positions()
        fish_scores = current_node.state.get_fish_scores()


    def minimax(
        self,
        node: Node,
        depth: int,
        player: int,
        alpha: float = -999999,
        beta: float = 999999,
    ):
        if depth == 0 or len(node.compute_and_get_children()) == 0:
            return self.heuristic_func(node), None

        if player == 0:
            max_eval = float('-inf')
            best_action = None
            for child in node.compute_and_get_children():
                eval_score, _ = self.minimax(child, depth - 1, 1, alpha, beta)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_action = child.move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_action

        else:
            min_eval = float('inf')
            for child in node.compute_and_get_children():
                eval_score, _ = self.minimax(child, depth - 1, 0, alpha, beta)
                if eval_score < min_eval:
                    min_eval = eval_score
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, None


    def search_best_next_move(self, initial_tree_node):

        children = initial_tree_node.compute_and_get_children()

        if len(children) == 0:
            return ACTION_TO_STR[0]

        max_eval = float('-inf')
        best_action = ACTION_TO_STR[0]

        for child in children:
            child_eval, _ = self.minimax(child, depth=5, player=1)
            if child_eval > max_eval:
                max_eval = child_eval
                move = child.move if child.move is not None else 0
                best_action = ACTION_TO_STR[move]

        return best_action