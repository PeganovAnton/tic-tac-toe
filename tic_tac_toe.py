import tkinter as tk
from tkinter import ttk


class Game:
    def save(self):
        pass  # TODO

    def load(self):
        pass  # TODO


class MainFrame(tk.Frame):
    def __init__(self, root, game):
        super().__init__()
        self.grid(row=0, column=0, sticky=(tk.S, tk.E, tk.N, tk.W))
        self._game = game
        self._add_menu()
        self._add_canvas()

    def _add_menu(self):
        menu_bar = tk.Menu(self.master)
        self.master.config(menu=menu_bar)
        file_menu = tk.Menu(menu_bar)
        file_menu.add_command(label="save", command=self._game.save)
        file_menu.add_command(label="load", command=self._game.load)
        menu_bar.add_cascade(label="file", menu=file_menu)

    def _draw_grid(self, canvas):
        canvas.create_line((101, 10, 101, 290))
        canvas.create_line((195, 10, 195, 290))
        canvas.create_line((10, 101, 290, 101))
        canvas.create_line((10, 195, 290, 195))

    def _add_cell_highlighting(self):
        pass  # TODO

    def _add_mark_placing(self):
        pass  # TODO

    def _add_event_processing(self):
        self._add_cell_highlighting()
        self._add_mark_placing()

    def _add_canvas(self):
        canvas = tk.Canvas(self, width=300, height=300, background='white')
        canvas.grid(column=0, row=0, padx=5, pady=5)
        self._draw_grid(canvas)
        self._add_event_processing()
        pass


def add_game_over_window():
    pass  # TODO


def add_save_game_window():
    pass  # TODO


def add_load_game_window():
    pass  # TODO


def set_window(root):
    root.title('tic tac toe')
    root.geometry('310x310+200+200')
    root.resizable(False, False)


if __name__ == '__main__':
    game = Game()

    root = tk.Tk()
    set_window(root)
    frame = MainFrame(root, game)
    add_save_game_window()
    add_load_game_window()
    add_game_over_window()
    root.mainloop()
