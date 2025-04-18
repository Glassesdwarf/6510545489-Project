"""
The main module, responsible for creating a root window containing the game's
main component.
"""
from typing import Final
import tkinter as tk
from dragon_slaying import KillTheDragon

SCREEN_WIDTH: Final = 800
SCREEN_HEIGHT: Final = 500

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Turtle's Adventure")
    root.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    root.resizable(False, False) # games usually have fixed window size
    game = KillTheDragon(root, SCREEN_WIDTH, SCREEN_HEIGHT, level=1)
    game.start()
    root.mainloop()
