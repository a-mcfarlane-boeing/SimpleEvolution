import random
import tkinter as tk
import math

Reward_radius = 1.0 #units
Boarder_width = 2 #units
Max_slices = 5


class Reward:
    def __init__(self, w_width, w_height, canvas, pixels_per_unit):
        self.position = [0,0]
        self.slices = Max_slices

        self.x_max = w_width - (2 * (Boarder_width + Reward_radius))
        self.y_max = w_height - (2 * (Boarder_width + Reward_radius))

        self.x_min = Boarder_width + Reward_radius
        self.y_min = self.x_min

        self.pixels_per_unit = pixels_per_unit

        self.position[0] = random.random()*self.x_max + self.x_min
        self.position[1] = random.random()*self.y_max + self.y_min

        self.canvas = canvas

        self.oval_object = self.canvas.create_oval(0, 0, Reward_radius * 2 * self.pixels_per_unit, Reward_radius * 2 * self.pixels_per_unit, fill="red")

        self.move()

    def move(self):
        self.position[0] = random.random()*self.x_max + self.x_min
        self.position[1] = random.random()*self.y_max + self.y_min 

        self.canvas.moveto(self.oval_object,round((self.position[0]-Reward_radius)*self.pixels_per_unit),round((self.position[1]-Reward_radius)*self.pixels_per_unit))
    
    def isNear(self, obj):
        is_close = False

        x_distance = abs(self.position[0] - obj.position[0])
        y_distance = abs(self.position[1] - obj.position[1])

        distance = math.sqrt(pow(x_distance,2)+pow(y_distance,2))

        if distance < Reward_radius:
            is_close = True
              
        return is_close
    
    def consumed(self):
        self.slices -= 1
        if self.slices == 0:
            self.move()
            self.slices = Max_slices


def main():
    pass

if __name__ == "__main__":
    main()