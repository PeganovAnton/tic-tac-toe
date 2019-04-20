import random


class Bot:
    def __init__(self, game):
        self._game = game

    def _move_randomly(self):
        free_cells = self._game.get_free_cells()
        if free_cells:
            return random.choice(free_cells)

    def move(self):
        return self._move_randomly()