import os
import random
import json
import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import filedialog


SAVE_DIR = '~/tic-tac-toe/save'


class Bot:
    def __init__(self, game):
        self._game = game

    def _move_randomly(self):
        free_cells = self._game.get_free_cells()
        if free_cells:
            return random.choice(free_cells)

    def move(self):
        return self._move_randomly()


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

    def _init_fields_with_loaded_values(self, saved_game):
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
            saved_lock = self._init_fields_with_loaded_values(saved_game)
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
        answer = tk.messagebox.askyesno("New game", "Bot makes the first move in the game?")
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
        tk.messagebox.showinfo("Result", result)

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


class MainFrame(tk.Frame):
    def __init__(self, root, game):
        super().__init__()
        self._canvas = None
        self.grid(row=0, column=0, sticky=(tk.S, tk.E, tk.N, tk.W))
        self._game = game
        self._game.add_frame(self)
        self._add_menu()
        self._add_canvas()

    def _add_menu(self):
        menu_bar = tk.Menu(self.master)
        self.master.config(menu=menu_bar)
        file_menu = tk.Menu(menu_bar)
        game_menu = tk.Menu(menu_bar)

        file_menu.add_command(label="save", command=self._game.save)
        file_menu.add_command(label="load", command=self._game.load)

        game_menu.add_command(label='new', command=self._game.start_new_game)

        menu_bar.add_cascade(label="file", menu=file_menu)
        menu_bar.add_cascade(label='game', menu=game_menu)

    @staticmethod
    def _draw_grid(canvas):
        canvas.create_line((101, 10, 101, 290))
        canvas.create_line((195, 10, 195, 290))
        canvas.create_line((10, 101, 290, 101))
        canvas.create_line((10, 195, 290, 195))

    @staticmethod
    def _get_cell_pos(x, y):
        x_idx = (x - 9) // 94
        y_idx = (y - 9) // 94
        if x_idx < 0 or x_idx > 2:
            x_idx = None
        if y_idx < 0 or y_idx > 2:
            y_idx = None
        return x_idx, y_idx

    @staticmethod
    def _get_mark_bounding_box(cell_pos):
        x0 = 19 + cell_pos[0] * 94
        y0 = 19 + cell_pos[1] * 94
        x1 = 9 + (cell_pos[0] + 1) * 94 - 10
        y1 = 9 + (cell_pos[1] + 1) * 94 - 10
        return x0, y0, x1, y1

    def draw_circle(self, cell_pos):
        x0, y0, x1, y1 = self._get_mark_bounding_box(cell_pos)
        self._canvas.create_arc(x0, y0, x1, y1, start=0, extent=359.999, width=12, outline='blue', style='arc')

    def draw_cross(self, cell_pos):
        x0, y0, x1, y1 = self._get_mark_bounding_box(cell_pos)
        self._canvas.create_line(x0, y0, x1, y1, width=12, fill='red')
        self._canvas.create_line(x0, y1, x1, y0, width=12, fill='red')

    def _classify_line(self, line):
        start, end = line[0], line[2]
        if start[0] == end[0]:
            descr = (0, start[0])
        elif start[1] == end[1]:
            descr = (1, start[1])
        else:
            if start[0] != start[1]:
                descr = 2
            else:
                descr = 3
        return descr

    def _draw_victory_line(self, descr):
        if isinstance(descr, tuple):
            if descr[0] == 0:
                x = 9 + 94 * descr[1] + 47
                self._canvas.create_line(x, 9, x, 291, width=8)
            else:
                y = 9 + 94 * descr[1] + 47
                self._canvas.create_line(9, y, 291, y, width=8)
        else:
            if descr == 2:
                self._canvas.create_line(9, 291, 291, 9, width=8)
            else:
                self._canvas.create_line(9, 9, 291, 291, width=8)

    def draw_victory(self, victory_line):
        line_descr = self._classify_line(victory_line)
        self._draw_victory_line(line_descr)

    def _process_mouse_click(self, canvas, event):
        cell_pos = self._get_cell_pos(event.x, event.y)
        if cell_pos[0] is not None and cell_pos[1] is not None:
            self._game.receive_move(cell_pos)

    def _add_event_processing(self, canvas):
        canvas.bind("<Button-1>", lambda e: self._process_mouse_click(canvas, e))

    def _add_canvas(self):
        canvas = tk.Canvas(self, width=300, height=300, background='white')
        canvas.grid(column=0, row=0, padx=5, pady=5)
        self._draw_grid(canvas)
        self._add_event_processing(canvas)
        self._canvas = canvas
        pass

    def reset_canvas(self):
        self._canvas.delete('all')
        self._draw_grid(self._canvas)


def set_window(root):
    root.title('tic-tac-toe')
    root.geometry('310x310+200+200')
    root.resizable(False, False)


if __name__ == '__main__':
    game = Game()

    root = tk.Tk()
    set_window(root)
    frame = MainFrame(root, game)
    root.mainloop()
