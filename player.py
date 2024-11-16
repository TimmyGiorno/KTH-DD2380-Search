#!/usr/bin/env python3

"""
Code for KTH DD2380 HT24 Assignment: Fishing Derby Search.

Members：Bingchu Zhao (Timmy), Yiyao Zhang
Email：bingchu@kth.se, yiyaoz@kth.se
"""

import math
import random
import time

from fishing_game_core.game_tree import Node
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR, TYPE_TO_SCORE

# Requirement from Kattis.
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
        self.start_time = 0
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

    def minimax(
        self,
        node: Node,
        depth: int,
        player: int,
        alpha: float,
        beta: float,
    ) -> float:
        # Leave 0.15s for message sending.
        if time.time() - self.start_time > TIME_LIMIT - 0.15:
            raise TimeoutError

        # Make caches for the same situations.
        hooks_positions = node.state.get_hook_positions()
        fish_positions = node.state.get_fish_positions()
        key = str(hooks_positions) + str(fish_positions)
        if self.cache.get(key) is not None:
            return self.cache[key]

        # No children found, then calculate the heuristic value.
        if depth == 0 or len(node.compute_and_get_children()) == 0:
            return self.heuristic_func(node)

        # Max Player (Player 0).
        if player == 0:
            max_eval = float('-inf')
            for child in node.compute_and_get_children():
                eval_score = self.minimax(child, depth - 1, 1, alpha, beta)
                if eval_score > max_eval:
                    max_eval = eval_score
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            self.cache[key] = max_eval
            return max_eval

        # Min Player (Player 1).
        else:
            min_eval = float('inf')
            for child in node.compute_and_get_children():
                eval_score = self.minimax(child, depth - 1, 0, alpha, beta)
                if eval_score < min_eval:
                    min_eval = eval_score
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            self.cache[key] = min_eval
            return min_eval

    def heuristic_func(
        self,
        node: Node,
    ) -> float:

        hooks_positions = node.state.get_hook_positions()
        fish_positions = node.state.get_fish_positions()
        fish_positions_keys = fish_positions.keys()
        hook_position = hooks_positions[node.state.get_player()]
        fish_scores = node.state.get_fish_scores()

        weighted_fish_scores = []

        for fish_position_key in fish_positions_keys:

            fish_score = fish_scores[fish_position_key]
            distance = self.euclidean_distance(hook_position, fish_positions[fish_position_key])

            # There is a fish on the hook right now.
            if distance == 0 and node.state.fish_scores[fish_position_key] > 0:
                return float("inf")

            # One fish left, hustle for it.
            if len(fish_positions) == 1:
                return fish_score / math.pow(distance, 10)

            # Higher value, closer fish have higher value.
            # e^(-x), linear tried but not worked.
            weighted_fish_scores.append(fish_score / math.pow(distance, 10))

        # No fish left. Nothing to do.
        if len(weighted_fish_scores) == 0:
            best_fish = 0
        else:
            best_fish = max(weighted_fish_scores)

        # Parameter adjustment is a long and boring process.
        return 10 * (node.state.player_scores[0] - node.state.player_scores[1]) + best_fish

    def search_best_next_move(self, initial_tree_node):

        children = initial_tree_node.compute_and_get_children()
        best_move = 0
        depth = 1

        while True:
            try:
                scores = []
                for child in children:
                    score = self.minimax(
                        child, depth, 1, float("-inf"), float("inf"),
                    )
                    scores.append(score)
                best_move = children[scores.index(max(scores))].move
                depth += 1
            except TimeoutError:
                break

        return ACTION_TO_STR[best_move]