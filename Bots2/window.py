import tkinter as tk
import time


# Global Variables
window_width = 500
window_height = 500
frame_rate = 24
frame_interval = 1 / frame_rate

class Display:
    def __init__(self):
        # Create the main window
        self.window = tk.Tk()
        self.window.title("  Simple Evolution")
        # Create canvas to show the environment
        self.canvas = tk.Canvas(self.window, bg='white', width=window_width, height=window_height)
        self.canvas.pack()

    def update(self):
        self.window.update()

if __name__ == "__main__":
    window = Display()
    while True:
        window.update()