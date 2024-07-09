import neuron
import random
import json

Input_expansion_factor = 2 # the number of decimal places the input will be seperated into
# there will be additional inputs for every main input

class Brain:
    """ Handles all the neurons """
    def __init__(self,num_of_neurons=0, num_of_connections_each=0, num_of_inputs=1, num_of_outputs=0, file_name = None):
        self.input_expansion_factor = Input_expansion_factor

        self.num_of_neurons = num_of_neurons
        self.num_of_connections = num_of_connections_each
        self.num_of_inputs = num_of_inputs
        self.num_of_outputs = num_of_outputs

        self.chance_of_neuron_connection = 0.8

        if num_of_connections_each > num_of_neurons:
            print('There are too many connections for the number of neurons!')

        self.neuron_names = []
        self.input_names = []
        self.neurons = []

        self.dict_all_values = {}
        
        if file_name == None:

            # create the names of the neurons
            i=0
            while i < self.num_of_neurons:
                self.neuron_names.append("n"+str(i))
                self.dict_all_values[self.neuron_names[i]] = 0
                i+=1
        
            # create the neurons
            for x in self.neuron_names:
                self.neurons.append(neuron.Neuron3(x))
        
            # create the inputs
            i=0
            while i < self.num_of_inputs:
                # for each input
                name = "i"+str(i)
                self.input_names.append(name)
                self.dict_all_values[name] = 0
                j = 0
                while j < self.input_expansion_factor:
                    #expand the input by this factor
                    #segmetents the input values so that there is a larger array of inputs
                    # eg. input 1_0 = 0.9837 -> input 1_1 = 0.837 -> input 1_2 = 0.37
                    # this, in theory, allows the brain to have higher precision with the inputs
                    name = "i"+str(i)+"_"+str(j)
                    self.input_names.append(name)
                    self.dict_all_values[name] = 0
                    j+=1
                i+=1
        
            # link the neurons to each other
            i=0
            while i < self.num_of_neurons:
                # for each neuron
                j=0
                connections = []
                while j < self.num_of_connections:
                    # connect to either, another neuron, or an input

                    #chance of connecting to another neuron
                    rand = random.random()

                    # randomises which input/neuron to connect to
                    rand2 = random.random()


                    if rand <= self.chance_of_neuron_connection:
                        connections.append(self.neuron_names[int((self.num_of_neurons-1)*rand2)])
                    else:
                        connections.append(self.input_names[int((self.num_of_inputs*(self.input_expansion_factor+1))*rand2)])
                    j += 1

                # assigns this list of inputs to the neuron
                self.neurons[i].input_names = connections
                # makes the neuron generate weights for each of these connections
                self.neurons[i].createWeights(self.num_of_connections)
                i+=1

        else:
            # creates a brain from a file
            # open file
            file_object = open(file_name, "r")
            # get first two rows
            self.num_of_inputs = int(file_object.readline())
            # create the inputs
            i=0
            while i < self.num_of_inputs:
                name = "i"+str(i)
                self.input_names.append(name)
                self.dict_all_values[name] = 0
                j = 0
                while j < self.input_expansion_factor:
                    name = "i"+str(i)+"_"+str(j)
                    self.input_names.append(name)
                    self.dict_all_values[name] = 0
                    j+=1
                i+=1

            # create the names of the neurons
            self.num_of_neurons = int(file_object.readline())
            i=0
            while i < self.num_of_neurons:
                self.neuron_names.append("n"+str(i))
                self.dict_all_values[self.neuron_names[i]] = 0
                i+=1

            # collect data about neurons
            i=0
            while i < self.num_of_neurons:
                neuron_name = "n"+str(i)
                line = str(file_object.readline())
                if line != "~":
                    connections = json.loads(line)
                    line = str(file_object.readline())
                    weights = json.loads(line)
                    file_object.readline()
                    self.neurons.append(neuron.Neuron3(neuron_name, connections, weights))
                i+=1

    def buildFromFile(self,file_name):
        # creates a brain from a file

        # wipe any previous values
        self.input_expansion_factor = 5

        self.num_of_neurons = 0
        self.num_of_connections = 0
        self.num_of_inputs = 0
        self.num_of_outputs = 0

        self.chance_of_neuron_connection = 0.8

        self.neuron_names = []
        self.input_names = []
        self.neurons = []

        self.dict_all_values = {}

        # open file
        file_object = open(file_name, "r")
        # get first two rows
        self.num_of_inputs = int(file_object.readline())
        # create the inputs
        i=0
        while i < self.num_of_inputs:
            name = "i"+str(i)
            self.input_names.append(name)
            self.dict_all_values[name] = 0
            j = 0
            while j < self.input_expansion_factor:
                name = "i"+str(i)+"_"+str(j)
                self.input_names.append(name)
                self.dict_all_values[name] = 0
                j+=1
            i+=1

        # find how many neurons there are
        self.num_of_neurons = int(file_object.readline())

        # create the names of the neurons
        i=0
        while i < self.num_of_neurons:
            self.neuron_names.append("n"+str(i))
            self.dict_all_values[self.neuron_names[i]] = 0
            i+=1
        # collect data about neurons
        i=0
        while i < self.num_of_neurons:
            neuron_name = "n"+str(i)
            line = str(file_object.readline())
            if line != "~":
                connections = json.loads(line)
                line = str(file_object.readline())
                weights = json.loads(line)
                file_object.readline()
                #build the neuron
                self.neurons.append(neuron.Neuron3(neuron_name, connections, weights))
            i+=1


    def calculateInputs(self):
        #segmetents the input values so that there is a larger array of inputs
        # eg. input 1_0 = 0.9837 -> input 1_1 = 0.837 -> input 1_2 = 0.37
        # this, in theory, allows the brain to have higher precision with the inputs
        i=0
        while i < self.num_of_inputs:
            # cycle through each parent input
            input_name = 'i'+str(i)
            # get the value from the list of outputs (this should have been reassinged externaly)
            input_value = self.dict_all_values[input_name]
            j=0
            while j < self.input_expansion_factor:
                # calculate each of the child inputs
                input_name = 'i'+str(i)+"_"+str(j)
                input_value = (input_value*10)-int(input_value*10)
                # assing the results to the list of outputs
                self.dict_all_values[input_name] = input_value
                j+=1
            i+=1

    def calculateOutputs(self):
        self.calculateInputs()

        # each neuron collects its inputs from the dictionary of all output values
        i=0
        while i < self.num_of_neurons:
            self.neurons[i].getInputs(self.dict_all_values)
            i+=1

        # each neuron calculates its output and assigns it back to the dictionary
        i=0
        while i < self.num_of_neurons:
            self.neurons[i].calculateOutput()
            self.dict_all_values[self.neuron_names[i]] = self.neurons[i].output
            i+=1
    
    def saveBrain(self,file_location):
        brainFile = open(file_location,"w")
        brainFile.write(json.dumps(self.num_of_inputs)+"\n")
        brainFile.write(json.dumps(self.num_of_neurons)+"\n")
        
        i=0
        while i<self.num_of_neurons:
            brainFile.write(json.dumps(self.neurons[i].input_names)+"\n")
            brainFile.write(json.dumps(self.neurons[i].weights)+"\n")
            brainFile.write(".\n")
            i+=1
        brainFile.write("~")
        brainFile.close()
    
    def loadBrain(self, file_name):
        # creates a brain from a file

        #wipe previous brain
        self.neurons = []
        self.neuron_names = []
        self.input_names = []
        self.num_of_connections = 10

        # open file
        file_object = open(file_name, "r")
        # get first two rows
        self.num_of_inputs = int(file_object.readline())
        # create the inputs
        i=0
        while i < self.num_of_inputs:
            name = "i"+str(i)
            self.input_names.append(name)
            self.dict_all_values[name] = 0
            j = 0
            while j < self.input_expansion_factor:
                name = "i"+str(i)+"_"+str(j)
                self.input_names.append(name)
                self.dict_all_values[name] = 0
                j+=1
            i+=1

        # create the names of the neurons
        self.num_of_neurons = int(file_object.readline())
        i=0
        while i < self.num_of_neurons:
            self.neuron_names.append("n"+str(i))
            self.dict_all_values[self.neuron_names[i]] = 0
            i+=1

        # collect data about neurons
        i=0
        while i < self.num_of_neurons:
            neuron_name = "n"+str(i)
            line = str(file_object.readline())
            if line != "~":
                connections = json.loads(line)
                line = str(file_object.readline())
                weights = json.loads(line)
                file_object.readline()
                self.neurons.append(neuron.Neuron3(neuron_name, connections, weights))
                self.num_of_connections = len(connections)
            i+=1
    
    def randomiseNeuronWeights(self):
        i=0
        while i < self.num_of_neurons:
            self.neurons[i].createWeights(self.num_of_connections)
            i+=1


def main():
        #net= Brain(50,4)
        net=Brain(file_name="Brain.txt")

        #print(net.num_of_inputs)
        #net.summarise("Brain.txt")
        
        #print(net.num_of_connections)
        #print(net.num_of_neurons)
        #print(net.neurons[0].weights)
        i=0
        while i < 100:
            net.calculateOutputs()
            if i%10==0:
                net.dict_all_values["i0"] = i/100
                print("Change")

                text ="{:2.0f} neuron 0 : {:.3f} neuron 50 : {:.3f} neuron 51 : {:.3f}"
        
                print(text.format(i,net.neurons[0].output,net.neurons[24].output,net.neurons[49].output))
            i+=1

if __name__ == '__main__':
    main()