import copy
import unittest.mock as mock

import pytest

import tic_tac_toe.bot
from tic_tac_toe.game import Game


print(dir(tic_tac_toe.bot))
# from tic_tac_toe.bot import OptimalBot


DIAGONAL = [
    ((0, 0), (1, 1), (2, 2)),
    ((0, 2), (1, 1), (2, 0)),
]

HORIZONTAL = [tuple((i, j) for i in range(3)) for j in range(3)]
VERTICAL = [tuple((j, i) for i in range(3)) for j in range(3)]
LINES = DIAGONAL + HORIZONTAL + VERTICAL


def get_cell_coordinates(cell_number):
    return cell_number % 3, cell_number // 3


def get_positions_with_one_winning_move(grid_tmpl, turn, line):
    result = []
    for cell_1_number in range(9):
        for cell_2_number in range(cell_1_number+1, 9):
            cell_1 = get_cell_coordinates(cell_1_number)
            cell_2 = get_cell_coordinates(cell_2_number)
            if cell_1 in line or cell_2 in line:
                continue
            grid = copy.deepcopy(grid_tmpl)
            grid[cell_1[0]][cell_1[1]] = 1 - turn
            grid[cell_2[0]][cell_2[1]] = 1 - turn
            result.append(grid)
    return result


@pytest.fixture
def games_before_winning_move_and_moves():
    empty_grid = [[None]*3 for _ in range(3)]
    result = []
    for bot_turn in [0, 1]:
        for line in LINES:
            for free_cell_idx in range(3):
                winning_move = line[free_cell_idx]
                grid_with_winning_line = copy.deepcopy(empty_grid)
                for i in range(3):
                    if i != free_cell_idx:
                        grid_with_winning_line[line[i][0]][line[i][1]] = bot_turn
                for grid in get_positions_with_one_winning_move(
                        grid_with_winning_line, bot_turn, line):
                    game = Game()
                    game.grid = grid
                    game.human = 1 - bot_turn
                    result.append((game, winning_move))
    return result


def test_winning_move(games_before_winning_move_and_moves):
    for game, winning_move in games_before_winning_move_and_moves:
        bot = tic_tac_toe.bot.OptimalBot(game)
        assert bot.move() == winning_move, \
            "wrong move on grid {}. Expected {}".format(game.grid, winning_move)
