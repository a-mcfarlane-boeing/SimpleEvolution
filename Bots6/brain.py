import neuron
import random
import json
import math

Base_save_location = "BaseBrain.txt"
Input_expansion_factor = 2 # the number of decimal places the input will be seperated into
# there will be additional inputs for every main input
Brain_size = 10 #The height and width of the brain


class Brain:
    """Handles all the neurons
    each of the neurons will be placed in a field.
    the result of each neuron will come from it's neighbours
    the weights between each neuron will be based on its proximity"""

    def __init__(self,num_of_neurons = 1,file_name = None):
        self.num_of_neurons = num_of_neurons
        self.side_length = math.sqrt(self.num_of_neurons)
        self.range_of_neuron = neuron.Neuron().max_range_of_neuron

        self.num_of_inputs = 0
        self.num_of_outputs = 0

        self.neurons:list[neuron.Neuron] = []
        
        if file_name == None:
            # Create Neurons
            for _ in range(self.num_of_neurons): self.neurons.append(self._makeNewNeuron())

            #initialise neuron inputs from one another
            self.configureNeurons()
            
        else:
            self.load(file_name)

    def _makeNewNeuron(self):
        return neuron.Neuron(name="Neuron "+str(len(self.neurons)),location=[self.side_length*random.random(),self.side_length*random.random()])

    def configureNeurons(self):
        """initialise all the neurons inputs
        will select from surounding Neurons"""
        for N in self.neurons:
            N.findInputs(self.neurons, self.side_length)

    def resize(self, num_of_neurons):
        self.side_length = math.sqrt(num_of_neurons)

        for _ in range(num_of_neurons - self.num_of_neurons):
            self.neurons.insert(self.num_of_inputs, self._makeNewNeuron())

        self.num_of_neurons = num_of_neurons

    def think(self):
        # each neuron collects its inputs from the list on neurons
        for neuron in self.neurons:
            neuron.calculateValue()

    def setInput(self, name , input_function):
         # inputs go to first neurons
        self.neurons[self.num_of_inputs].name = name
        self.neurons[self.num_of_inputs].takeInput(input_function)
        self.num_of_inputs += 1

    def getOutput(self, name):
        # gets the outputs from the end of the list of neurons
        self.num_of_outputs+=1
        self.neurons[-self.num_of_outputs].name = name
        return self.neurons[-self.num_of_outputs].getOutput

    def copy(self):
        """returns a copy of the brain
        will not have the inputs or outputs assigned"""
        new_brain = Brain(num_of_neurons = self.num_of_neurons)
        
        new_brain.neurons = [N.copy() for N in self.neurons]

        return new_brain

    def save(self,file_location):
        brainFile = open(file_location,"w")

        brainFile.write(json.dumps(self.side_length)+"\n")
        brainFile.write(json.dumps(self.range_of_neuron)+"\n")
        brainFile.write(json.dumps(self.num_of_neurons)+"\n")
        
        for neuron in self.neurons:
            brainFile.write(json.dumps(neuron.name)+"\n")
            brainFile.write(json.dumps(neuron.location)+"\n")

        brainFile.write("~")
        brainFile.close()
    
    def load(self, file_name):
        # creates a brain from a file

        #wipe previous brain
        self.neurons = []
        self.num_of_neurons = 0

        # open file
        file_object = open(file_name, "r")

        # get base attributes
        self.side_length = float(file_object.readline())
        self.range_of_neuron = float(file_object.readline())
        self.num_of_neurons = int(file_object.readline())

        # collect data about neurons
        i=0
        while i < self.num_of_neurons:
            line = str(file_object.readline())
            if line != "~":
                name = json.loads(line)
                line = str(file_object.readline())
                location = json.loads(line)
                self.neurons.append(neuron.Neuron(name=name,location=location))
            i+=1
        
        self.configureNeurons()


def main():
    testBrain = Brain(128)
    testBrain.save("brains\starter_brain.txt")

    print("test")
    print(testBrain.__dict__)

    otherbrain = testBrain.copy()

    print("other")
    print(otherbrain.__dict__)

    otherbrain.resize(2)

    print("test")
    print(testBrain.__dict__)
    
    print("other")
    print(otherbrain.__dict__)

    
    

if __name__ == '__main__':
    main()