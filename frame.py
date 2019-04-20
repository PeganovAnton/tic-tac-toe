import tkinter as tk


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