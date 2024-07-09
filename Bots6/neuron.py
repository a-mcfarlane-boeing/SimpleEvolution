import math

class Neuron:
    """
    This neuron makes calculations based on its position relative to the neurons surrounding it    
    """

    def __init__(self,name='Blank Neuron',location=[0,0]):
        
        self.max_range_of_neuron = 1
        self.min_range_of_neuron = 0.05

        # the strength of the sigmoid function (initialy 10)
        self.sigmoid_multiplier = 5

        self.name = name
        self.location = location
        self.type = 'null'

        self.inputs = []
        self.input_weights = []
        
        # initialise the output of the neuron
        self.value = 0.0
    
    def findInputs(self, neuron_list : list['Neuron']):
        """
        searches through the other neurons to find neighbours.
        assigns their outputs to this neuron's inputs.
        also calculates their weight based on their distance
        """
        # wipes the previously held inputs
        self.inputs=[]
        self.input_weights = []
        i=0
        for other_neuron in neuron_list:
            x_dis = self.location[0] - other_neuron.location[0]
            y_dis = self.location[1] - other_neuron.location[1]
            distance = math.sqrt(x_dis**2 + y_dis**2)
            if distance <= self.max_range_of_neuron and distance >= self.min_range_of_neuron:
                distance_percent = 1.0 - (distance-self.min_range_of_neuron)/(self.max_range_of_neuron-self.min_range_of_neuron)
                #invert distance percent every second neuron
                if i%2 == 0:
                    distance_percent = -distance_percent

                self.inputs.append(other_neuron.getOutput)
                self.input_weights.append(distance_percent)
                i+=1
    
    def takeInput(self, input):
        self.inputs = [input]
        self.input_weights = []
        self.type = 'input'

    def calculateValue(self):
        """
        calculates the output of the neuron
        """
        if self.type == 'input':
            self.value = self.inputs[0]()
        elif len(self.input_weights) == 0:
            return
        else:
            total=0.0
            
            # adds up all the inputs
            i=0
            while i < len(self.inputs):
                total += self.inputs[i]()*self.input_weights[i]
                i+=1

            total_factor = min(max(total,-1),1)
            
            # the sigmoid function
            # TF = 0 -> O = 0.5
            # TF = 1 -> O = 1.0
            # TF = -1 -> O = 0.0
            self.value=1/(1+2.0**-(total_factor*self.sigmoid_multiplier))

    def getOutput(self):
        return self.value

    def copy(self):
        return Neuron(name= self.name, location=self.location)

def main():
    pass

if __name__ == '__main__':
    main()