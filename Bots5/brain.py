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

    def __init__(self,num_of_neurons = 100,file_name = None):
        self.num_of_neurons = num_of_neurons
        self.size = math.sqrt(self.num_of_neurons)+2
        self.range_of_neuron = neuron.Neuron().range_of_neuron

        self.neurons:list[neuron.Neuron] = []
        
        if file_name == None:
            # Create Neurons
            for i in range(self.num_of_neurons):
                self.neurons.append(neuron.Neuron(name="N"+str(i),location=[1+(self.size-2)*random.random(),1+(self.size-2)*random.random()]))

        else:
            self.load(file_name)

    def think(self):
        # each neuron collects its inputs from the list on neurons
        for neuron in self.neurons:
            neuron.think(self.neurons)
    
    def save(self,file_location):
        brainFile = open(file_location,"w")

        brainFile.write(json.dumps(self.size)+"\n")
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
        self.size = int(file_object.readline())
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


def main():
    testBrain = Brain()

    testBrain.neurons[5].output = 0.8

    for i in range(10):
        print("cycle " + str(i))
        for n in testBrain.neurons:
            if n.name == "N1":
                print(n.output,n.input_values,n.input_weights)
        
        testBrain.think()


    testBrain.saveBrain("testbrain.txt")

if __name__ == '__main__':
    main()