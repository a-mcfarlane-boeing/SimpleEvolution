import random
import tkinter as tk

Reward_diameter = 1 #unit

class Reward:
    def __init__(self, w_width, w_height, canvas, pixels_per_unit):
        self.position = [0,0]

        self.x_max = w_width
        self.y_max = w_height
        self.pixels_per_unit = pixels_per_unit

        self.position[0] = random.random()*self.x_max
        self.position[1] = random.random()*self.y_max

        self.canvas = canvas

        self.oval_object = self.canvas.create_oval(0, 0, Reward_diameter * pixels_per_unit, Reward_diameter * pixels_per_unit, fill="red")

        self.move()

    def move(self):
        self.position[0] = random.random()*self.x_max
        self.position[1] = random.random()*self.y_max

        self.canvas.moveto(self.oval_object,round(self.position[0]*self.pixels_per_unit),round(self.position[1]*self.pixels_per_unit))
    
    def near(self, x_pos, y_pos):
        is_close = False
        min_distance = 2

        x_distance = abs(x_pos - self.position[0])
        y_distance = abs(y_pos - self.position[1])

        if x_distance < min_distance and y_distance < min_distance:
            self.move()
            is_close = True
        
        return is_close

def main():
    
    print(reward.position)

if __name__ == "__main__":
    main()