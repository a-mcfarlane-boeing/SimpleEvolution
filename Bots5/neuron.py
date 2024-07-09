import math
from random import random

class Neuron:
    """
    This neuron makes calculations based on its position relative to the neurons surrounding it    
    """

    def __init__(self,name='blank',location=[0,0]):

        self.range_of_neuron = 1

        # the strength of the sigmoid function (initialy 10)
        self.sigmoid_multiplier = 10

        self.name = name
        self.location = location

        self.input_values = []
        self.input_weights = []
        
        # initialise the output of the neuron
        self.output = 0.0         

    def calculateInputs(self,neuron_list:list['Neuron']):
        """
        searches through the other neurons to find neighbours and grabs their output
        also calculates their weight based on their distance
        """
        # wipes the previously held inputs
        self.input_values=[]
        self.input_weights = []
        i=0
        for other_neuron in neuron_list:
            x_dis = self.location[0] - other_neuron.location[0]
            y_dis = self.location[1] - other_neuron.location[1]
            distance = math.sqrt(x_dis**2 + y_dis**2)
            if distance <= self.range_of_neuron and distance != 0:
                distance_percent = 1.0 - distance/self.range_of_neuron
                #invert distance percent every second neuron
                if i%2 == 0:
                    distance_percent = -distance_percent
                self.input_values.append(other_neuron.output)
                self.input_weights.append(distance_percent)
                i+=1
    
    def calculateOutput(self):
        """
        calculates the output of the neuron based on the current inputs held
        """
        if len(self.input_weights) == 0:
            self.output = 0.0
        else:
            total=0.0
            
            # adds up all the inputs
            i=0
            while i < len(self.input_values):
                total += self.input_values[i]*self.input_weights[i]
                i+=1

            total_factor = min(max(total,-1),1)
            
            # the sigmoid function
            # TF = 0 -> O = 0.5
            # TF = 1 -> O = 1.0
            # TF = -1 -> O = 0.0
            self.output=1/(1+2.0**-(total_factor*self.sigmoid_multiplier))

    def think(self, neuron_list):
        self.calculateInputs(neuron_list)
        self.calculateOutput()


def main():
    pass

if __name__ == '__main__':
    main()