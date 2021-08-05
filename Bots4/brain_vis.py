import tkinter as tk
import brain
import math
import neuron



# Global Variables
Window_width_pixels = 600

# neuron size in units
Neuron_min_radius = 0.1
Neuron_max_radius = 0.4

def valueToNeuronRadius(value):
    """
    Figures out what the radius of the displayed neuron should be based on the value (0 to 1) given
    """
    new_radius = (Neuron_max_radius-Neuron_min_radius)*value +Neuron_min_radius
    return new_radius

class Display:
    def __init__(self, input_brain:brain.Brain):
        #keeps a connection to the brain
        self.connected_brain = input_brain

        # how many neurons in the brain
        self.num_of_neurons = input_brain.num_of_neurons
        self.num_of_inputs = input_brain.num_of_inputs * input_brain.input_expansion_factor
        self.total_num_of_neurons = self.num_of_neurons + self.num_of_inputs

        # work out how much space is required to show all the neurons
        # window should be a square
        self.vis_side_length = math.ceil(math.sqrt(self.total_num_of_neurons)+1)
        self.lower_index = 1
        self.upper_index = self.vis_side_length

        # calculate the size and layout of the window
        self.pixels_per_unit = Window_width_pixels / self.vis_side_length
        self.window_width_pixels = Window_width_pixels
        self.window_height_pixels = self.vis_side_length * self.pixels_per_unit

        # neurons
        self.neurons = []


        # Create the main window
        self.window = tk.Tk()
        self.window.title("  Brain Visualiser")

        # Create canvas to show the environment
        self.canvas = tk.Canvas(self.window, bg='black', width=self.window_width_pixels, height=self.window_height_pixels)

        # draw lines to indicate the units
        # individual units
        self._generateUnitLines(1,self.vis_side_length,self.vis_side_length, "light grey")
        # 10s of units
        # these are done seperately so that they overlay the grey lines underneath
        self._generateUnitLines(10,self.vis_side_length,self.vis_side_length, "light blue")
        
        # create the circles for the inputs
        x=self.lower_index
        y=self.lower_index
        num_of_neuron_check=0
        while y < self.upper_index and num_of_neuron_check < self.num_of_inputs:
            while x < self.upper_index and num_of_neuron_check < self.num_of_inputs:
                self.neurons.append({"name":input_brain.input_names[num_of_neuron_check],"circle":self._createCircle(x,y,0.2,"light green"),"x":x,"y":y})
                x+=1
                num_of_neuron_check+=1
            x=self.lower_index
            y+=1

        # create the circles for the neurons
        num_of_neuron_check=0
        while y < self.upper_index and num_of_neuron_check < self.num_of_neurons:
            while x < self.upper_index and num_of_neuron_check < self.num_of_neurons:
                self.neurons.append({"name":input_brain.neuron_names[num_of_neuron_check],"circle":self._createCircle(x,y,0.2,"orange"),"x":x,"y":y,"connection list":input_brain.neurons[num_of_neuron_check].input_names,"weights":input_brain.neurons[num_of_neuron_check].weights})
                x+=1
                num_of_neuron_check+=1
            x=self.lower_index
            y+=1

        index_num= self.num_of_inputs
        while index_num < self.total_num_of_neurons:
            self.drawConnections(self.neurons[index_num])
            index_num+=1

        self.canvas.pack()


    def drawConnections(self,neuron):
        origin_X = self._convertToPixels(neuron["x"])
        origin_Y = self._convertToPixels(neuron["y"])
        connectionLines = []
        for name in neuron["connection list"]:
            i=0
            for other_neuron in self.neurons:
                if other_neuron["name"] == name:
                    destination_X = self._convertToPixels(other_neuron["x"])
                    destination_Y = self._convertToPixels(other_neuron["y"])
                    colour = "blue"
                    thickness = 7 * neuron["weights"][i]
                    if thickness < 0:
                        colour = "red"
                    connectionLines.append(self.canvas.create_line(origin_X,origin_Y,destination_X,destination_Y,width = abs(thickness), fill=colour,activewidth=5,arrow="first"))
                    i+=1
        neuron["connection lines"] = connectionLines


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
        self.neuronValueToSize()
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

    def _changeNeuronSize(self,neuron,new_radius):
        """
        Changes the size of a circle to a new radius
        """

        x = neuron["x"]
        y = neuron["y"]

        # point 1
        UL_x = self._convertToPixels(x - new_radius) + 1
        UL_y = self._convertToPixels(y - new_radius) + 1
        # point 2
        LR_x = self._convertToPixels(x + new_radius)
        LR_y = self._convertToPixels(y + new_radius)

        self.canvas.coords(neuron["circle"]["object"], UL_x, UL_y, LR_x, LR_y)
    
    def _changeLinksSizes(self, neuron):
        for i in range(0,len(neuron["connection list"])):
            width = abs(neuron["weight list"][i])
            neuron[i]["connection lines"].configure(width = width)



    def neuronValueToSize(self):
        for neuron in self.neurons:
            self._changeNeuronSize(neuron,valueToNeuronRadius(self.connected_brain.dict_all_values[neuron["name"]]))


        


if __name__ == "__main__":
    yellow_brain = brain.Brain(30,3,7,3)
    yellow_brain.loadBrain("brains/starter_brain_yellow.txt")
    blue_brain = brain.Brain(30,3,7,3)
    blue_brain.loadBrain("brains/starter_brain_blue.txt")
    window1 = Display(yellow_brain)
    window2 = Display(blue_brain)
    window1.window.title("yellow")
    while True:
        window1.update()
        window2.update()