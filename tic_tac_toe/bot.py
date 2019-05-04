import random
import copy


DIAGONAL = [
    ((0, 0), (1, 1), (2, 2)),
    ((0, 2), (1, 1), (2, 0)),
]

HORIZONTAL = [tuple((i, j) for i in range(3)) for j in range(3)]
VERTICAL = [tuple((j, i) for i in range(3)) for j in range(3)]
LINES = DIAGONAL + HORIZONTAL + VERTICAL


class Bot:
    def __init__(self, game):
        self._game = game

    def _move_randomly(self):
        free_cells = self._game.get_free_cells()
        if free_cells:
            return random.choice(free_cells)

    def move(self):
        return self._move_randomly()


# class OptimalBot(Bot):
#     def move(self):
#         free_cells = self._game.get_free_cells()
#         bot_turn = 1 - self._game.human
#         for cell in free_cells:
#             grid = copy.deepcopy(self._game.grid)
#             grid[cell[0]][cell[1]] = bot_turn
#             for line in LINES:
#                 win = True
#                 for c in line:
#                     if grid[c[0]][c[1]] != bot_turn:
#                         win = False
#                 if win:
#                     return cell
#         return self._move_randomly()
