import json
import os
from tkinter import filedialog
from tkinter import messagebox

from bot import Bot


SAVE_DIR = '~/tic-tac-toe/save'


class Game:
    def __init__(self):
        self.turn = 0
        # A move is a tuple of 2 elements. The first element is
        # a number of a player. The number of a player can be either
        # 0 or 1. A player with number 0 is the one who made the first move
        # in a game.
        # The second element in move tuple is a tuple of 2
        # elements and contains  coordinates of a cell with
        # a mark. Coordinates can be equal to 0, 1, or 2.
        # Axes start in upper left angle of a field. Vertical axis Y
        # is directed down and horizontal axis X is directed to the right.
        # The first coordinate is X coordinate and the second is Y coordinate.
        # Example of attribute contents:
        # `[(0, (1, 1)), (1, (1, 0))]` corresponds to a game position
        #      | O |
        #   ---|---|---
        #      | X |
        #   ---|---|---
        #      |   |
        # The player who makes the first move is always playing with crosses
        self.moves = []
        self.bot = Bot(self)
        self.frame = None
        # A matrix 3x3 with moves of players. Each COLUMN
        # in matrix corresponds to row in the drawn field
        # The grid corresponding to the position above will be
        # `[[None, None, None], [1, 0, None], [None, None, None]]`
        self.grid = [[None]*3 for _ in range(3)]
        # Blocks canvas reaction while bot makes his move or game is loaded.
        self.lock = False
        self.finished = False
        self.human = 0
        self.victory_line = None

    def get_free_cells(self):
        free_cells = []
        for r_idx, row in enumerate(self.grid):
            for c_idx, cell in enumerate(row):
                if cell is None:
                    free_cells.append((r_idx, c_idx))
        return free_cells

    def _get_save_file_name(self):
        initialdir = os.path.expanduser(SAVE_DIR)
        if not os.path.exists(initialdir):
            os.makedirs(initialdir)
        save_file_name = filedialog.asksaveasfilename(
            initialdir=initialdir,
            title='Save game',
            filetypes=(("json files", "*.json"), ("all files", "*.*"))
        )
        if save_file_name in [(), '']:
            return None
        return save_file_name

    def save(self):
        old_lock = self.lock
        self.lock = True
        save_file_name = self._get_save_file_name()
        if save_file_name is not None:
            saved_game = {
                "turn": self.turn,
                "moves": self.moves,
                "bot_class_name": self.bot.__class__.__name__,
                "grid": self.grid,
                "lock": old_lock,
                "finished": self.finished,
                "human": self.human,
                "victory_line": self.victory_line,
            }
            with open(save_file_name, 'w') as f:
                json.dump(saved_game, f)
        self.lock = old_lock

    def _get_load_file_name(self):
        initialdir = os.path.expanduser(SAVE_DIR)
        if not os.path.exists(initialdir):
            initialdir = os.path.expanduser('~')
        save_file_name = filedialog.askopenfilename(
            initialdir=initialdir,
            filetypes=(("json files", "*.json"), ("all files", "*.*"))
        )
        if save_file_name in [(), '']:
            return None
        return save_file_name

    def _init_atributes_with_loaded_values(self, saved_game):
        self.turn = saved_game['turn']
        self.moves = saved_game['moves']
        self.bot = eval(saved_game['bot_class_name'] + '(self)')
        self.grid = saved_game['grid']
        self.finished = saved_game['finished']
        self.human = saved_game['human']
        self.victory_line = saved_game['victory_line']
        return saved_game['lock']

    def _redraw(self, moves, victory_line):
        old_lock = self.lock
        self.frame.reset_canvas()
        self.lock = True
        for move in moves:
            if move[0] == 0:
                self.frame.draw_cross(move[1])
            else:
                self.frame.draw_circle(move[1])
        if victory_line is not None:
            self.frame.draw_victory(victory_line)
        self.lock = old_lock

    def load(self):
        self.lock = True
        load_file_name = self._get_load_file_name()
        if load_file_name is not None:
            with open(load_file_name) as f:
                saved_game = json.load(f)
            saved_lock = self._init_atributes_with_loaded_values(saved_game)
            self._redraw(self.moves, self.victory_line)
            self.lock = saved_lock
            if self.human != self.turn and not self.finished:
                self._move_bot()

    def _move_bot(self):
        old_lock = self.lock
        self.lock = True
        if self.human != self.turn:
            cell_pos = self.bot.move()
            finished = self._process_player_move(cell_pos)
            if finished:
                self.finished = True
        self.lock = old_lock

    def start_new_game(self):
        answer = messagebox.askyesno("New game", "Bot makes the first move in the game?")
        self.lock = True
        self.turn = 0
        self.human = int(answer)
        self.moves = []
        self.grid = [[None]*3 for _ in range(3)]
        self.finished = False
        self.frame.reset_canvas()
        self._move_bot()
        self.lock = False
        self.victory_line = None

    def _get_diagonal_lines(self, cell_pos):
        cell_pos = (int(cell_pos[0]), int(cell_pos[1]))
        diags = [((0, 0), (1, 1), (2, 2)), ((0, 2), (1, 1), (2, 0))]
        ret = []
        if cell_pos in diags[0]:
            ret.append(diags[0])
        if cell_pos in diags[1]:
            ret.append(diags[1])
        return ret

    def _get_all_lines_to_check(self, cell_pos):
        lines = [((cell_pos[0], 0), (cell_pos[0], 1), (cell_pos[0], 2))]
        lines.append(((0, cell_pos[1]), (1, cell_pos[1]), (2, cell_pos[1])))
        lines += self._get_diagonal_lines(cell_pos)
        return lines

    def _select_victory_lines(self, lines):
        victory_lines = []
        for line in lines:
            victory = True
            for cell in line:
                if self.grid[cell[0]][cell[1]] != self.turn:
                    victory = False
            if victory:
                victory_lines.append(line)
        return victory_lines

    def _get_victory_line(self, cell_pos):
        lines = self._get_all_lines_to_check(cell_pos)
        victory_lines = self._select_victory_lines(lines)
        if victory_lines:
            return victory_lines[0]

    def _add_move_to_grid(self, cell_pos):
        self.grid[cell_pos[0]][cell_pos[1]] = self.turn

    def _open_game_over_window(self, winner):
        if winner is not None:
            if winner == self.human:
                result = 'Victory!'
            else:
                result = 'Defeat'
        else:
            result = 'Draw'
        messagebox.showinfo("Result", result)

    def _launch_mark_drawing(self, cell_pos):
        if self.turn:
            self.frame.draw_circle(cell_pos)
        else:
            self.frame.draw_cross(cell_pos)

    def _process_player_move(self, cell_pos):
        """
        Adds move of th current player to moves list
        and into grid. Initiates mark drawing. Checks
        if the game has finished, draws victory line,
        opens game over window. Switches turn.
        `cell_pos` is a position of cell where a player
        places his mark. The first element of the tuple is
        X coordinate of the cell and the second is Y
        coordinate of the cell. The axes origin is in the
        upper left angle of the field and Y axes is
        directed down.
        Args:
            cell_pos: A tuple of 2 integers

        Returns:
            `True` if the game has finished and `False`
            otherwise.
        """
        self.moves.append((self.turn, cell_pos))
        self._add_move_to_grid(cell_pos)
        self._launch_mark_drawing(cell_pos)
        victory_line = self._get_victory_line(cell_pos)
        if victory_line is not None:
            self.victory_line = victory_line
            self.frame.draw_victory(victory_line)
            self._open_game_over_window(self.turn)
            return True
        if len(self.moves) == 9:
            self._open_game_over_window(None)
            return True
        elif len(self.moves) > 9:
            raise ValueError("number of made moves exceeds 9")
        self.turn = 1 - self.turn
        return False

    def get_bot_move(self):
        return self.bot.move()

    def add_frame(self, frame):
        self.frame = frame

    def _is_cell_free(self, cell_pos):
        return self.grid[cell_pos[0]][cell_pos[1]] is None

    def receive_move(self, cell_pos):
        if not self.lock and not self.finished:
            self.lock = True
            if self._is_cell_free(cell_pos):
                finished = self._process_player_move(cell_pos)
                if finished:
                    self.finished = True
                    return
                cell_pos = self.bot.move()
                if cell_pos is None:
                    self._open_game_over_window(None)
                else:
                    finished = self._process_player_move(cell_pos)
                    if finished:
                        self.finished = True
            self.lock = False