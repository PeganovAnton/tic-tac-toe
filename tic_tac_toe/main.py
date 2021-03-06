import tkinter as tk

from tic_tac_toe.frame import MainFrame
from tic_tac_toe.game import Game


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
