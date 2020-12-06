import random

class Neuron:
    """ Neuron in a neural network """
    def __init__(self,_name='blank',_links=[],_weights=[]):
        self.name=_name

        if len(_links)==0:
            self.num_of_inputs = 3
            self.input_values = [0]*3
        else:
            self.num_of_inputs = len(_links)
            self.input_values = [0]*len(_links)
        
        self.input_IDs = _links
        self.weights = _weights

        self.output = 0.0

        if _weights == []:
            i=0
            while i < self.num_of_inputs:
                self.weights.append(random.random())
                i+=1
        
        if _links == []:
            i=0
            while i < self.num_of_inputs:
                self.input_IDs.append('blank')
                i+=1
            

    def getInputs(self,i):
        self.input_values=i
    
    def calculateOutput(self):
        i=0
        results=0
        total=0.0
        while i < self.num_of_inputs:
            total += self.weights[i]*self.input_values[i]
            i+=1
        total=total/self.num_of_inputs

        if total >= 0.5:
            total = 1
        else:
            total = 0

        self.output=results
        return self.output

    def main(self):
        n=Neuron()
        print("weights: "+str(n.weights)+"   input names: " + str(n.input_IDs))

if __name__ == '__main__':
    Neuron.main(None)

