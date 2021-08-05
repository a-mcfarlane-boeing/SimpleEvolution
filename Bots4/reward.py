import random
import tkinter as tk
import math

Radius = 1.0 #units
Colour = "red"
Boarder_width = 2 #units
Max_slices = 10


class Reward:
    def __init__(self, w_width, w_height):
        self.position = [0,0]
        self.slices = Max_slices

        self.x_max = w_width - (Boarder_width + Radius)
        self.y_max = w_height - (Boarder_width + Radius)

        self.x_min = Boarder_width + Radius
        self.y_min = self.x_min

        self.move()

    def move(self):
        """
        moves the reward to a new random location
        """
        print("the reward moved")
        self.position[0] = random.random()*(self.x_max-self.x_min) + self.x_min
        self.position[1] = random.random()*(self.y_max-self.y_min) + self.y_min
    
    def isNear(self, obj):
        """
        checks if the reward is near another object
        """
        is_close = False

        x_distance = abs(self.position[0] - obj.position[0])
        y_distance = abs(self.position[1] - obj.position[1])

        distance = math.sqrt(pow(x_distance,2)+pow(y_distance,2))

        if distance < Radius:
            is_close = True
              
        return is_close
    
    def consumed(self):
        '''
        removes a slice from the reward.
        if there are no more slices the reward will move and the slices reset 
        '''
        self.slices -= 1
        print(str(self.slices)+" slices left")
        if self.slices <= 0:
            self.move()
            self.slices = Max_slices
    
    def getPosition(self):
        """
        Returns the [x,y] position of the reward
        """
        return self.position

def main():
    pass

if __name__ == "__main__":
    main()