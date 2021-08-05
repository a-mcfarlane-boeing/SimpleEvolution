import math
import tkinter as tk


# Global Variables
Window_width_pixels = 500

class Display:
    def __init__(self, world_width, world_height):
        
        #variables
        self.pixels_per_unit = Window_width_pixels / world_width
        self.window_width_pixels = Window_width_pixels
        self.window_height_pixels = world_height * self.pixels_per_unit

        # Create the main window
        self.window = tk.Tk()
        self.window.title("  Simple Evolution")

        # Create canvas to show the environment
        self.canvas = tk.Canvas(self.window, bg='green3', width=self.window_width_pixels, height=self.window_height_pixels)

        # draw lines to indicate the units
        # individual units
        self._generateUnitLines(1,world_width,world_height, "light grey")
        # 10s of units
        # these are done seperately so that they overlay the grey lines underneath
        self._generateUnitLines(10,world_width,world_height, "orange red")
        
        self.canvas.pack()





    def _generateUnitLines(self, spacing, world_width, world_height, colour):
        # vertical
        i=spacing
        while i <= world_width:
            self.canvas.create_line(self._convertToPixels(i), self._convertToPixels(0), self._convertToPixels(i), self._convertToPixels(world_height),fill=colour)
            i+=spacing
        
        # horizontal
        i=spacing
        while i <= world_height:
            self.canvas.create_line(self._convertToPixels(0), self._convertToPixels(i), self._convertToPixels(world_width), self._convertToPixels(i),fill=colour)
    
            i+=spacing


    def update(self):
        self.window.update()

    def moveCircleFromCenter(self, circle_object, x_pos, y_pos):
        radius = circle_object['radius']
        self.canvas.moveto(circle_object['object'], self._convertToPixels(x_pos - radius), self._convertToPixels(y_pos - radius))

    def moveBot(self, bot):
        self.moveCircleFromCenter(bot['circle_object'],bot['bot'].getPosition()[0],bot['bot'].getPosition()[1])

    def deleteObject(self, object_to_delete):
        '''
        removes the object from the view space
        '''
        self.canvas.delete(object_to_delete['object'])

    def _convertToPixels(self, value) -> int:
        '''converts a position in the world to a pixel position on the window
        index 0 and 1 are outside of the range of the canvas
        a position of 0 should not show, however a position of 0.01 will
        decimals are rounded to the nearest whole number, 0.4 -> 0, 0.5 -> 1
        2 is the first index which will show on the canvas
        calculated pixel -> index -> pixel number
        0.1-1 -> 2 -> 1, 1.1-2 -> 3 -> 2 and so on.
        '''

        return math.ceil(value*self.pixels_per_unit) + 1



    def _createCircle(self, x_pos, y_pos, radius, colour):
        '''
        Creates a circle with the centre in the x and y position and a radius
        returns the circle object.
        '''
        # point 1
        UL_x = self._convertToPixels(x_pos - radius) + 1
        UL_y = self._convertToPixels(y_pos - radius) + 1
        # point 2
        LR_x = self._convertToPixels(x_pos + radius)
        LR_y = self._convertToPixels(y_pos + radius)

        circle = self.canvas.create_oval(UL_x,UL_y,LR_x,LR_y,fill=colour)
        circle_object = {'object': circle, 'radius':radius}
        return circle_object

    

if __name__ == "__main__":
    window = Display(20,20)
    circle = window._createCircle(5,5,1,'yellow')
    i=0
    while True:
        i+=0.001
        window.moveCircleFromCenter(circle, i+5,math.sin(i*5)+5)
        if i>10:
            window.deleteObject(circle)
        window.update()