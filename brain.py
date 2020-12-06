import neuron

class Brain:
    """ Handles all the neurons """
    def __init__(self,num_of_neurons,num_of_connections,num_of_inputs,num_of_outputs):
        self.num_of_neurons = num_of_neurons
        self.num_of_connections = num_of_connections
        self.num_of_inputs = num_of_inputs
        self.num_of_outputs = num_of_outputs

        self.neuron_names = []
        self.neurons = []
        self.neuron_outputs = {}

        i=0
        while i<num_of_neurons:
            self.neuron_names.append("n"+str(i))
            self.neuron_outputs[self.neuron_names[i]] = 0
            i+=1
        
        for x in self.neuron_names:
            self.neurons.append(neuron.Neuron(x))
        
        for x in self.num_of_connections:
            pass

    def getOutputs(self):
        i=0
        while i < self.num_of_neurons:
            self.neuron_outputs[self.neuron_names[i]] = self.neurons[i].calculateOutput()
            i+=1

    def main(self):
        net=Brain(10,3,3,3)
        print(net.neuron_names,net.neurons[2].weights)
        net.getOutputs()
        print(net.neuron_outputs)

if __name__ == '__main__':
    Brain.main(None)