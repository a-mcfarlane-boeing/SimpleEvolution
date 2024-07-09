#This file contains a number of different versions of neurons, each with their own parameters for inputs and outputs
import random

class Neuron1:
    """ Neuron in a neural network
    
    weights between 0 and 1 """

    def __init__(self,name='blank',input_names=None,weights=None):
        # sort out name
        self.name=name

        # sort out inputs
        self.input_names = input_names
        if input_names == None:
            self.input_names = []
            self.num_of_inputs = 3
            i=0
            while i < self.num_of_inputs:
                self.input_names.append('blank'+str(i))
                i+=1
        else:
            self.num_of_inputs = len(input_names)

        #sort out weights
        self.weights = weights
        if weights == None:
            self.createWeights(self.num_of_inputs)
        
        # sort out output
        self.output = 0.0            

    def getInputs(self,dictionary_of_outputs):
        self.input_values=[]
        for key in dictionary_of_outputs:
            for input_id in self.input_names:
                if key == input_id:
                    self.input_values+=[dictionary_of_outputs[key]]
    
    def calculateOutput(self):
        i=0
        results=0
        total=0.0
        while i < len(self.input_values):
            total += self.input_values[i]*self.weights[i]
            i+=1
        total += self.weights[-1]
        results=total/self.sum_of_weights
        #results=total
        self.output=abs(results)
    
    def createWeights(self,number_of_weights):
        """ fills the weights list """
        self.sum_of_weights = 0
        self.weights = []
        i=0
        while i < number_of_weights:
            self.weights.append(random.random())
            i+=1
        self.weights.append(random.random())

        self.sum_of_weights = sum(self.weights)

class Neuron2:
    """ Neuron in a neural network
    
    Positive and negative weights """\

    def __init__(self,name='blank',input_names=None,weights=None):
        # sort out name
        self.name=name

        # sort out inputs
        self.input_names = input_names
        if input_names == None:
            self.input_names = []
            self.num_of_inputs = 3
            i=0
            while i < self.num_of_inputs:
                self.input_names.append('blank'+str(i))
                i+=1
        else:
            self.num_of_inputs = len(input_names)

        #sort out weights
        self.weights = weights
        if weights == None:
            self.weights = []
            self.createWeights(self.num_of_inputs)
        
        # sort out output
        self.output = 0.0            

    def getInputs(self,dictionary_of_outputs):
        self.input_values=[]
        for key in dictionary_of_outputs:
            for input_id in self.input_names:
                if key == input_id:
                    self.input_values+=[dictionary_of_outputs[key]]
    
    def calculateOutput(self):
        i=0
        results=0
        total=0.0
        while i < len(self.input_values):
            total += self.input_values[i]*self.weights[i]
            i+=1
        total += self.weights[-1]
        if total >= 0:
            results=total/self.sum_of_weights_pos
        else:          
            results=total/self.sum_of_weights_neg
        self.output=abs(results)
    
    def createWeights(self,number_of_weights):
        """ fills the weights list """
        self.sum_of_weights = 0
        self.sum_of_weights_pos = 0
        self.sum_of_weights_neg = 0
        i=0
        while i < number_of_weights:
            self.weights.append(random.random()*2-1)
            i+=1
        self.weights.append((random.random()*2-1)/3.0)

        max_pos = 0
        max_neg = 0
        for x in self.weights:
            if x >=0:
                max_pos += x
            else:
                max_neg += x
            
            self.sum_of_weights_pos = max_pos
            self.sum_of_weights_neg = max_neg

class Neuron3:
    """
    -This type of neuron takes values from 0 to 1 as the input and returns the same range as the output.
    -Incorportates positive and negative weights so some inputs can overpower others and reverse the value of the output.
    -The sigmoid function applied, pushes the outputs futher to the edges of the range.
    -Need to have one extra weight than the number of inputs.
    """

    def __init__(self,name='blank',input_names=[],weights=[]):

        # the strength of the sigmoid function (initialy 10)
        self.sigmoid_multiplier = 10

        # assign name
        self.name=name

        # assign inputs
        self.input_names = input_names
        self.num_of_inputs = len(self.input_names)
        self.input_values = []

        # assign weights
        self.weights = weights
        self.num_of_weights = len(self.weights)
        
        self.sum_of_weights_pos = 0
        self.sum_of_weights_neg = 0
        for x in self.weights:
            if x >= 0:
                self.sum_of_weights_pos += x
            else:
                self.sum_of_weights_neg += x
        
        # initialise the output of the neuron
        self.output = 0.0  

        # position of the neuron in the brain between 0 and 1
        self.x = 0.5
        self.y = 0.5          

    def getInputs(self,dict_inputs):
        """
        searches for the values which correspond with the inputs to the neuron
        """
        # wipes the previously held inputs
        self.input_values=[]
        # searches through the values of the dictionary to find the values which correspond with the inputs
        # adds these inputs to the input list
        for input_id in self.input_names:
            self.input_values+=[abs(dict_inputs[input_id])]
    
    def createWeights(self,number_of_weights):
        """
        fills the weights list
        has a weight for each of the inputs plus an additional weight as the baseline of the neuron
        """

        self.num_of_weights = number_of_weights
        # wipes any previous weights
        self.weights = []

        # generates new weights with values between -1 and 1
        i=0
        while i < self.num_of_weights:
            self.weights.append(random.random()*2-1)
            i+=1
        # generates the additional baseline weight to be added to the end of the array
        # This baseline is less and less effective the more inputs are present
        self.weights.append((random.random()*2-1)/(number_of_weights+1))

        # finds the max and min values which the neruon can output
        # these limits are reached when all the poisitive inputs are 1 and all the negative inputs are 0 or,
        # when all the negative inputs are 1 and all the positive inputs are 0.
        self.calculateWeightTotals()
    
    def calculateOutput(self):
        """
        calculates the output of the neuron based on the current inputs held
        """
        result=0.0
        total=0.0
        
        # adds up all the inputs
        i=0
        while i < len(self.input_values):
            total += self.input_values[i]*self.weights[i]
            i+=1
        # includes the baseline value
        total += self.weights[-1]

        # determines how close to the edges of the range the inputs reached
        # one in the positve direction and one in the negative depending on the sign of the total
        # pulls the total back into the range of -1 to 1
        if total >= 0:
            # returns a positive
            # makes output closer to 0
            total = total / self.sum_of_weights_pos
        else:
            # returns a negative ->  - (-t / -w)
            # makes output closer to 1
            total = -total / self.sum_of_weights_neg

        # the sigmoid function
        result = 1/(1+2.0**(total*self.sigmoid_multiplier))

        self.output=result

    def calculateWeightTotals(self):
        """
        Recalculates the Positive and Negative maximums which the total can reach
        """
        # finds the max and min values which the neruon can output
        # these limits are reached when all the poisitive inputs are 1 and all the negative inputs are 0 or,
        # when all the negative inputs are 1 and all the positive inputs are 0.
        for x in self.weights:
            if x >= 0:
                self.sum_of_weights_pos += x
            else:
                self.sum_of_weights_neg += x

    def setWeights(self, new_weights):
        """
        Assigns the given weights to the stored weight vector.
        Also recalculates the weight totals which limit the inputs.
        """
        self.weights = new_weights
        self.calculateWeightTotals()


def main():
    n=Neuron3('Neuron',['input0','input1','input2'])
    n.createWeights(3)
    print(n.sum_of_weights_pos," and ",n.sum_of_weights_neg)
    print(n.weights)
    for a in [0,1]:
        for b in [0,1]:
            for c in [0,1]:
                dic = {'input0':a,'input1':b,'input2':c}
                n.getInputs(dic)
                n.calculateOutput()
                text ="input values:  "+str(n.input_values)+"   output: {:.3f}"
                print(text.format(n.output))

    dic = {'input0':random.random(),'input1':random.random(),'input2':random.random()}
    n.getInputs(dic)
    n.calculateOutput()
    text ="input values:  "+str(n.input_values)+"   output: {:.3f}"
    print(text.format(n.output))

    dic = {'input0':random.random(),'input1':random.random(),'input2':random.random()}
    n.getInputs(dic)
    n.calculateOutput()
    text ="input values:  "+str(n.input_values)+"   output: {:.3f}"
    print(text.format(n.output))

    dic = {'input0':1.1,'input1':-0.1,'input2':0}
    n.getInputs(dic)
    n.calculateOutput()
    text ="input values:  "+str(n.input_values)+"   output: {:.3f}"
    print(text.format(n.output))

if __name__ == '__main__':
    main()