import random

class Neuron1:
    """ Neuron in a neural network
    
    weights between 0 and 1 """\

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
    """ Neuron in a neural network
    
    Sigmoid function """\

    def __init__(self,name='blank',input_names=None,weights=None):
        # sort out name
        self.name=name

        # sort out inputs
        self.input_names = input_names
        if input_names == None: 
            self.input_names = []
        self.num_of_inputs = len(self.input_names)

        #sort out weights
        self.weights = weights
        if weights == None: 
            self.weights = []
        self.num_of_weights = len(self.weights)
        
        self.sum_of_weights_pos = 1
        self.sum_of_weights_neg = -1
        for x in self.weights:
            if x >= 0:
                self.sum_of_weights_pos += x
            else:
                self.sum_of_weights_neg += x
        
        # sort out output
        self.output = 0.0            

    def getInputs(self,dictionary_of_outputs):
        self.input_values=[]
        for input_id in self.input_names:
            self.input_values+=[dictionary_of_outputs[input_id]]
    
    def createWeights(self,number_of_weights):
        """ fills the weights list """
        self.num_of_weights = number_of_weights
        self.weights = []
        i=0
        while i < self.num_of_weights:
            self.weights.append(random.random()*2-1)
            i+=1
        self.weights.append((random.random()*2-1)/(number_of_weights+1))

        for x in self.weights:
            if x >= 0:
                self.sum_of_weights_pos += x
            else:
                self.sum_of_weights_neg += x
    
    def calculateOutput(self):
        results=0
        total=0.0
        i=0
        while i < len(self.input_values):
            total += self.input_values[i]*self.weights[i]
            i+=1
        total += self.weights[-1]

        if total >= 0:
            total = total / self.sum_of_weights_pos
        else:
            total = -(total / self.sum_of_weights_neg)

        results = 1/(1+2.0**(-(total*10)))

        self.output=abs(results)


def main():
    n=Neuron3('Neuron',['input0','input1','input2'])
    n.createWeights(3)
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

if __name__ == '__main__':
    main()