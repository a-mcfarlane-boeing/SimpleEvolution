import neurons
import random
import json


class Brain:
    """ Handles all the neurons """
    def __init__(self,num_of_neurons=0, num_of_connections_each=0, num_of_inputs=1, num_of_outputs=0, file_name = None):
        self.input_expansion_factor = 5

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

        self.outputs = {}
        
        if file_name == None:

            # create the names of the neurons
            i=0
            while i < self.num_of_neurons:
                self.neuron_names.append("n"+str(i))
                self.outputs[self.neuron_names[i]] = 0
                i+=1
        
            # create the neurons
            for x in self.neuron_names:
                self.neurons.append(neurons.Neuron3(x))
        
            # create the inputs
            i=0
            while i < self.num_of_inputs:
                name = "i"+str(i)
                self.input_names.append(name)
                self.outputs[name] = 0
                j = 0
                while j < self.input_expansion_factor:
                    name = "i"+str(i)+"_"+str(j)
                    self.input_names.append(name)
                    self.outputs[name] = 0
                    j+=1
                i+=1
        
            # link the neurons to eachother
            i=0
            while i < self.num_of_neurons:
                j=0
                connections = []
                while j < self.num_of_connections:
                    rand = random.random()
                    rand2 = random.random()
                    if rand <= self.chance_of_neuron_connection:
                        connections.append(self.neuron_names[int((self.num_of_neurons-1)*rand2)])
                    else:
                        connections.append(self.input_names[int((self.num_of_inputs*(self.input_expansion_factor+1))*rand2)])
                    j += 1
                self.neurons[i].input_names = connections
                self.neurons[i].createWeights(self.num_of_connections)
                i+=1

            # Create the outputs from the brain
            pass
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
                self.outputs[name] = 0
                j = 0
                while j < self.input_expansion_factor:
                    name = "i"+str(i)+"_"+str(j)
                    self.input_names.append(name)
                    self.outputs[name] = 0
                    j+=1
                i+=1

            # create the names of the neurons
            self.num_of_neurons = int(file_object.readline())
            i=0
            while i < self.num_of_neurons:
                self.neuron_names.append("n"+str(i))
                self.outputs[self.neuron_names[i]] = 0
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
                    self.neurons.append(neurons.Neuron3(neuron_name, connections, weights))
                i+=1
            
            

    def calculateInputs(self):
        i=0
        while i < self.num_of_inputs:
            input_name = 'i'+str(i)
            input_value = self.outputs[input_name]
            j=0
            while j < self.input_expansion_factor:
                input_name = 'i'+str(i)+"_"+str(j)
                input_value = (input_value*10)-int(input_value*10)
                self.outputs[input_name] = input_value
                j+=1
            i+=1


    def calculateOutputs(self):
        self.calculateInputs()

        i=0
        while i < self.num_of_neurons:
            self.neurons[i].getInputs(self.outputs)
            i+=1

        i=0
        while i < self.num_of_neurons:
            self.neurons[i].calculateOutput()
            self.outputs[self.neuron_names[i]] = self.neurons[i].output
            i+=1
    
    def summarise(self,file_name):
        brainFile = open(file_name,"w")
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
        # open file
        file_object = open(file_name, "r")
        # get first two rows
        self.num_of_inputs = int(file_object.readline())
        # create the inputs
        i=0
        while i < self.num_of_inputs:
            name = "i"+str(i)
            self.input_names.append(name)
            self.outputs[name] = 0
            j = 0
            while j < self.input_expansion_factor:
                name = "i"+str(i)+"_"+str(j)
                self.input_names.append(name)
                self.outputs[name] = 0
                j+=1
            i+=1

        # create the names of the neurons
        self.num_of_neurons = int(file_object.readline())
        i=0
        while i < self.num_of_neurons:
            self.neuron_names.append("n"+str(i))
            self.outputs[self.neuron_names[i]] = 0
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
                self.neurons.append(neurons.Neuron3(neuron_name, connections, weights))
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
                net.outputs["i0"] = i/100
                print("Change")

                text ="{:2.0f} neuron 0 : {:.3f} neuron 50 : {:.3f} neuron 51 : {:.3f}"
        
                print(text.format(i,net.neurons[0].output,net.neurons[24].output,net.neurons[49].output))
            i+=1

if __name__ == '__main__':
    main()