import tkinter as tk
import brain
import math



# Global Variables
Window_width_pixels = 600

# neuron size in units
Neuron_min_radius = 0.08
Neuron_max_radius = 0.2

def valueToNeuronRadius(value):
    """
    Figures out what the radius of the displayed neuron should be based on the value (0 to 1)
    based on the min an max radi set as global variables
    """
    new_radius = (Neuron_max_radius-Neuron_min_radius)*value +Neuron_min_radius
    return new_radius

class BrainDisplay:
    def __init__(self):
        #keeps a connection to the brain
        self.connected_brain:brain.Brain = None

        # work out how much space is required to show all the neurons
        # window should be a square
        self.vis_side_length = 15

        # calculate the size and layout of the window
        self.window_width_pixels = Window_width_pixels
        self.pixels_per_unit = self.window_width_pixels / self.vis_side_length
        self.window_height_pixels = self.vis_side_length * self.pixels_per_unit

        self.canvas_items = []

        # Create the main window
        self.window = tk.Tk()
        self.window.title("  Brain Visualiser")

        # Create canvas to show the environment
        self.canvas = tk.Canvas(self.window, bg='black', width=self.window_width_pixels, height=self.window_height_pixels)

        self.canvas.pack()

    def drawConnections(self,neuron):
        origin_X = self._convertToPixels(neuron["x"])
        origin_Y = self._convertToPixels(neuron["y"])
        connectionLines = []
        for name in neuron["connection list"]:
            i=0
            for other_neuron in self.canvas_items:
                if other_neuron["name"] == name:
                    destination_X = self._convertToPixels(other_neuron["x"])
                    destination_Y = self._convertToPixels(other_neuron["y"])
                    colour = "blue"
                    thickness = 7 * neuron["weights"][i]
                    if thickness < 0:
                        colour = "red"
                    connectionLines.append(self.canvas.create_line(origin_X,origin_Y,destination_X,destination_Y,width = abs(thickness), fill=colour,activewidth=5,arrow="first"))
                    i+=1
        return connectionLines

    def connectBrain(self, new_brain):
        #keeps a connection to the brain
        self.connected_brain:brain = new_brain

        # work out how much space is required to show all the neurons
        # window should be a square
        self.vis_side_length = self.connected_brain.side_length + 2

        # calculate the size and layout of the window
        self.window_width_pixels = Window_width_pixels
        self.pixels_per_unit = self.window_width_pixels / self.vis_side_length
        self.window_height_pixels = self.vis_side_length * self.pixels_per_unit

        self.canvas_items = []


    def _generateUnitLines(self, spacing, world_width, world_height, colour):
        # vertical
        items = []
        i=1
        while i <= world_width:
            items.append(self.canvas.create_line(self._convertToPixels(i), self._convertToPixels(0), self._convertToPixels(i), self._convertToPixels(world_height),fill=colour))
            i+=spacing

        # horizontal
        i=1
        while i <= world_height:
            items.append(self.canvas.create_line(self._convertToPixels(0), self._convertToPixels(i), self._convertToPixels(world_width), self._convertToPixels(i),fill=colour))
            i+=spacing

        return items

    def update(self):
        self.canvas.delete('all')

        self.canvas_items = []

        # draw lines to indicate the units
        # individual units
        self.canvas_items.extend(self._generateUnitLines(1,self.vis_side_length,self.vis_side_length, "light grey"))
        # 10s of units
        # these are done seperately so that they overlay the grey lines underneath
        self.canvas_items.extend(self._generateUnitLines(10,self.vis_side_length,self.vis_side_length, "light blue"))

        # draw the boundries of the brain
        self.canvas_items.append(self.canvas.create_rectangle(self._convertToPixels(1),self._convertToPixels(1),self._convertToPixels(self.vis_side_length-1),self._convertToPixels(self.vis_side_length-1),fill="",outline="red"))

        #  create the circles for the neurons
        for neuron in self.connected_brain.neurons:

            colour = "light blue"

            for i in range(9):
                if neuron.name == "Eye Segment"+str(int(i))+"R":
                    colour = "red"
                elif neuron.name == "Eye Segment"+str(int(i))+"G":
                    colour = "green"
                elif neuron.name == "Eye Segment"+str(int(i))+"B":
                    colour = "blue"
                elif neuron.name =="Eye Segment"+str(int(i))+"Dis":
                    colour = "purple"

            if neuron.name == "VF":
                colour = "yellow"
            elif neuron.name == "AVF":
                colour = "orange"
            elif neuron.name == "EA":
                colour = "red4"

            self.canvas_items.append(self.createNeuronCircle(neuron,colour))

        self.window.update()

    def createNeuronCircle(self, neuron : brain.neuron.Neuron, colour):
        '''
        Creates a circle with the centre in the x and y position and a radius
        returns the circle object.
        '''
        radius = valueToNeuronRadius(neuron.getOutput())
        # point 1
        UL_x = self._convertToPixels(neuron.location[0] - radius + 1)
        UL_y = self._convertToPixels(neuron.location[1] - radius + 1)
        # point 2
        LR_x = self._convertToPixels(neuron.location[0] + radius + 1)
        LR_y = self._convertToPixels(neuron.location[1] + radius + 1)

        return self.canvas.create_oval(UL_x,UL_y,LR_x,LR_y,fill=colour)

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

def main():
    testbrain = brain.Brain(100)
    window1 = BrainDisplay()

    class box:
        def __init__(self) -> None:
            self.val = 0.0

        def getVal(self):
            self.val = ((self.val+1)/100)%1
            return self.val

    thing = box()

    testbrain.neurons[0].takeInput(thing.getVal)
    window1.connectBrain(testbrain)
    window1.window.title("test brain")
    while True:
        testbrain.think()
        window1.update()

if __name__ == "__main__":
    main()