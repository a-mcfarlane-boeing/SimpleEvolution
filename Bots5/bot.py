from __future__ import annotations
import math
import random
from unittest import result
import brain
import copy
import visualiser
import simulator
import world
#import reward


# bot simulation constants
# breeding
Min_energy_to_breed = 10  # below this energy level the bot is too tired to breed
Min_breed_delay = 10  # seconds between "sessions"
Energy_lost_from_breeding = 2.5
Norm_neuron_max_change = 0.2
Mutation_neuron_max_change = Norm_neuron_max_change*3
Chance_of_mutation = 1/25.0

# apperance
Radius = 0.5  # unit (size of the bot)
# fractions of the 255 values
Colour_R = 0.5
Colour_G = 0.2
Colour_B = 0.1
Colour_RGB = [Colour_R, Colour_G, Colour_B]

# eating
Eat_delay = 7  # seconds between meals

# energy
Movement_energy_loss_rate = 0.05  # units per unit moved
Base_energy_loss_rate = 0.9  # units per second
Max_energy_reserve = 100

Boundry_damage = 8

# sight
Max_view_distance = 100
Max_view_angle = math.pi/2.0  # radians
# the number of segments of vision (note this will require adapatble number of neurons. Min 1)
Resolution_of_eye = 9
Eye_segment_angle = Max_view_angle/Resolution_of_eye

# Mobility
Max_turn_speed = math.pi/1.5  # radians per second
Max_speed = 3  # units per second

# brain variables
# neuron count
Num_of_neurons = 30
Num_of_connections = 5
Num_of_brain_inputs = 4+Resolution_of_eye*4

# ouput neurons
O_neuron_eat = "n0"
O_neuron_RFactor = "n1"
O_neuron_VFactor = "n2"

# input neurons
I_neuron_Clock = "i7"  # internal clock
I_neuron_Energy = "i0"  # energy percentage (1 when full, 0 when empty)
I_neuron_Xpos = "i1"# X position in world (0 when to the left, 1 when to the right)
I_neuron_YPos = "i2"  # Y position in world

# how long it takes for the clock input neuron go from 0 to 1 (simulated seconds)
internal_clock_range = 10.0


class Bot:
    """ Defines a Bot with all its attributes """

    def __init__(self, simulator: simulator.Simulator, name="exampleBot", max_speed=Max_speed, max_view_angle=Max_view_angle, max_energy=Max_energy_reserve, colour_RGB=Colour_RGB):
        #simulator
        self.simulator = simulator

        # bot attributes
        self.attributes = Attributes()
        self.attributes.name = name
        self.attributes.maxSpeed = max_speed
        self.attributes.maxTurnSpeed = Max_turn_speed
        self.attributes.energyReserveLimit = max_energy

        self.resolution_of_eye = 9
        self.max_view_angle = max_view_angle
        self.max_view_distance = Max_view_distance

        self.attributes.colourRGB = colour_RGB
        self.attributes.assignRGBtoHEX()

        self.dead = False

        #history
        self.attributes.generation = 0
        self.attributes.familyHistory = "None"

        # bot internal variables
        self.energy_level = self.attributes.energyReserveLimit
        self.breeding_points = 0
        self.total_rewards_collected = 0
        self.time_since_last_child = 0.0
        self.time_since_last_meal = 0.0

        # world variables
        self.birth_time = self.simulator.simTime
        self.age = 0.0
        self.time_last = 0.0
        self.simulator.simTimeInterval = 0.0

        # bot enviromental variables
        self.position = [5, 5]  # x,y
        self.direction = 0.0  # angle from x axis, anti-clockwise, radians

        # bot circle
        self.circleObject = visualiser.CircleObject(self.simulator.worldWindow,self.attributes.colourHEX,self.position,self.attributes.radius)

        # outputs from the brain
        self.brain_outputs = []

        self.velocity_factor = 0  # -1 to 1, forward and reverse
        self.angular_velocity_factor = 0  # -1 to 1, anti & clockwise
        self.eat_action = 0  # 0 to 1, triggers eating when >= 0.5

        self.brain_outputs.append({"name":"VF","value":self.velocity_factor})
        self.brain_outputs.append({"name":"AVF","value":self.angular_velocity_factor})
        self.brain_outputs.append({"name":"EA","value":self.eat_action})

        # inputs to brain
        self.brain_inputs = [] # list of dictionaries of name value pairs {"name":,"value"}

        self.energy_percent = 1.0
        self.direction_percent = 0.0
        self.position_percent = [0.0, 0.0]
        self.eye_segments = []
        for i in range(Resolution_of_eye):
            self.eye_segments.append({"name":"Eye Segment"+str(int(i)),"s_angle": i*Eye_segment_angle, "e_angle": (
                i+1)*Eye_segment_angle, "distance_percent": 0.0, "colour_RGB": [0.0, 0.0, 0.0]})

        self.brain_inputs.append({"name":"EP","value":self.energy_percent})
        self.brain_inputs.append({"name":"DP","value":self.direction_percent})
        self.brain_inputs.append({"name":"PPx","value":self.position_percent[0]})
        self.brain_inputs.append({"name":"PPy","value":self.position_percent[1]})
        for segment in self.eye_segments:
            self.brain_inputs.append({"name":segment["name"]+"Dis","value":segment["distance_percent"]})
            self.brain_inputs.append({"name":segment["name"]+"R","value":segment["colour_RGB"][0]})
            self.brain_inputs.append({"name":segment["name"]+"G","value":segment["colour_RGB"][1]})
            self.brain_inputs.append({"name":segment["name"]+"B","value":segment["colour_RGB"][2]})

        # outputs to simulator
        # tells the simulator if the bot was successful at eating in the last simulation run
        self.eat_success = False


        # brain
        num_of_inputs_and_outputs = len(self.brain_inputs) + len(self.brain_outputs)

        self.net = brain.Brain(num_of_inputs_and_outputs*2)

        i=0
        for input in self.brain_inputs:
            self.net.neurons[i].name = input["name"]
            i+=1

        i=-1
        for j in range(len(self.brain_outputs)):
            self.net.neurons[i].name = self.brain_outputs[j]["name"]
            i -= 1

    def setAngularVelocity(self, a_velocity):
        self.angular_velocity_factor = a_velocity

    def setVelocity(self, velocity):
        self.velocity_factor = velocity

    def simulate(self):
        # determine the elapsed time
        self.calculateInternalVariables()
        # consider objects
        self.loopThroughObjects()
        # run calculations through the brain
        self.think()
        # move bot accoringly
        self.move()
        # calculate energy consumption
        self.calculate_energy()
        # if died
        if self.dead:
            print(self.attributes.name+" died")
            self.circleObject.delete()
            self.simulator.simObjects.remove(self)
    
    def calculateInternalVariables(self):
        # how long the bot has been alive
        self.age += self.simulator.simTimeInterval
        
        # updates internal clocks accordingly
        self.time_since_last_child += self.simulator.simTimeInterval
        self.time_since_last_meal += self.simulator.simTimeInterval

    def loopThroughObjects(self):
        for object in self.simulator.simObjects:
            self.see(object)
            self.eat(object)
            self.breed(object)
    
    def see(self,object):
        #resets all the view segments
        for eye_segment in self.eye_segments:
            eye_segment["distance_percent"] = 0.0
            eye_segment["colour_RGB"] = [0.0,0.0,0.0]

        #determine the global angle of the left view
        angle_of_left_view_g = (
            self.direction-self.max_view_angle/2) % (2*math.pi)

        #determine where the object is in comparison to self
        x_displacement = object.position[0] - self.position[0]
        y_displacement = self.position[1] - object.position[1]
        # check if too far away, if so, skip
        distance_to_object = math.sqrt(
            x_displacement**2 + y_displacement**2)
        
        if distance_to_object > self.max_view_distance:
            print("Too far "+distance_to_object)
            return
        #determine the angle to the object from self in global coords
        angle_to_object_g = math.atan2(y_displacement,x_displacement)
        #determine the angle from the left most side of the bots view
        angle_of_object_in_view = (
            angle_to_object_g-angle_of_left_view_g) % (2*math.pi)
        #if the object is outside the field of view skip it
        if angle_of_object_in_view > self.max_view_angle:
            return
        
        for i in range(Resolution_of_eye):
            if angle_of_object_in_view >= self.eye_segments[i]["s_angle"] and angle_of_object_in_view < self.eye_segments[i]["e_angle"]:
                distance_percent = 1.0 - distance_to_object/self.max_view_distance
                if self.eye_segments[i]["distance_percent"] <= distance_percent:     
                    self.eye_segments[i]["distance_percent"] = distance_percent
                    self.eye_segments[i]["colour_RGB"] = object.attributes.colourRGB
        
        for eye_segment in self.eye_segments:
            for input in self.brain_inputs:
                if input["name"] == eye_segment["name"]+"Dis":
                    input["value"] = eye_segment["distance_percent"]
                elif input["name"] == eye_segment["name"]+"R":
                    input["value"] = eye_segment["colour_RGB"][0]
                elif input["name"] == eye_segment["name"]+"G":
                    input["value"] = eye_segment["colour_RGB"][1]
                elif input["name"] == eye_segment["name"]+"B":
                    input["value"] = eye_segment["colour_RGB"][2]
                else:
                    pass

    def eat(self, object):
        """
        Bot will attempt to eat from the object. Will only succeed if close enough
        updates the bot's energy level
        Returns True if successfull, otherwise False.
        """
        import reward
        if object.__class__ != reward.Reward:
            return

        self.eat_success = False
        target_x_pos = object.position[0]
        target_y_pos = object.position[1]

        # check the distance from the object
        distance = math.sqrt(
            (self.position[0]-target_x_pos)**2+(self.position[1]-target_y_pos)**2)

        # will eat if;
        # - within range
        # - hasn't eaten recently
        # - wants to (neuron)
        if (distance <= Radius + 1) and self.time_since_last_meal >= Eat_delay and self.eat_action <= 0.8:
            print(self.attributes.name+" took a nibble")

            # adds an energy boost to the energy level upto the maximum energy level
            energy_boost = 30
            self.energy_level += energy_boost
            if self.energy_level > self.attributes.energyReserveLimit:
                self.energy_level = self.attributes.energyReserveLimit

            # makes the bot "age" and have less vitality
            if self.attributes.energyReserveLimit >= 30:
                self.attributes.energyReserveLimit -= 2

            # the rewards for getting a reward
            self.total_rewards_collected += 1
            self.breeding_points += 2
            self.time_since_last_meal = 0

            # flag for the simulator
            self.eat_success = True

            object.consumed()

        # eating will consume a bit of energy, decentivising the bots from attempting to eat continuously
        self.energy_level -= 0.001
    
    def willingToBreed(self) -> bool:
        # check if this bot is willing to breed
        result = self.breeding_points >= 1 and self.energy_level >= Min_energy_to_breed and self.time_since_last_child >= Min_breed_delay
        
        return result

    def sameSpecies(self, other:Bot) -> bool:
        # check if the bots are of the same species
        result = True
        for i in range(3):
            if self.attributes.colourRGB[i] <= other.attributes.colourRGB[i]+0.3 and self.attributes.colourRGB[i] >= other.attributes.colourRGB[i]-0.3 :
                result = result and True
            else:
                result = False
        
        return result

    def breed(self, other_bot: Bot):
        """
        the assigned bot will attempt to breed with the given bot providing they are both eligable
        returns the child bot of the two parents.
        """
        
        if isinstance(other_bot,Bot):
            # check if not trying to breed with self (eww)
            if self.attributes.name == other_bot.attributes.name:
                return
            
            #check if this bot is still willing (might not if mated with previous bot)
            if not self.willingToBreed():
                return

            #check if other bot is still willing (might not if mated with a previous bot)
            if not other_bot.willingToBreed():
                return

            # check if the two bots are of the same species
            if not self.sameSpecies(other_bot):
                return
            
            child_name = "bot"+str(self.simulator.totalNumOfObjects)

            print(self.attributes.name+" mated with " +
                  other_bot.attributes.name+" to create "+child_name)

            # reset breeding timers
            self.time_since_last_child = 0
            other_bot.time_since_last_child = 0
            # remove a breeding point
            self.breeding_points -= 1
            other_bot.breeding_points -= 1
            # remove some energy
            self.energy_level -= Energy_lost_from_breeding
            other_bot.energy_level -= Energy_lost_from_breeding
            # determine whos traits will dominate
            if self.total_rewards_collected > other_bot.total_rewards_collected:
                domBot = self  # dominate traits
                recBot = other_bot  # recessive traits
            else:
                recBot = self
                domBot = other_bot
            # make love (generate the child bot)
            childBot = Bot(name=child_name, simulator = self.simulator)
            # child comes from the dominate bot
            childBot.position = copy.deepcopy(domBot.position)
            childBot.direction = 2* math.pi * random.random()
            childBot.attributes.generation = copy.copy(domBot.attributes.generation) + 1
            # give the child a family history or genetic code
            childBot.attributes.familyHistory = domBot.attributes.ownFamilyHistory()
            #give child bot colour
            result_colour_RGB = []
            for i in range(3):
                result_colour_RGB.append(Combine2(domBot.attributes.colourRGB[i],recBot.attributes.colourRGB[i],1,0))
            childBot.attributes.colourRGB = result_colour_RGB
            childBot.attributes.assignRGBtoHEX()
            
            childBot.circleObject.colourHEX = childBot.attributes.colourHEX
            childBot.circleObject.changeColour()

            # create the brain for the child bot
            childBot.net = copy.deepcopy(domBot.net)

            i=0
            for neuron in childBot.net.neurons:
                neuron.location[0] = Combine2(neuron.location[0],recBot.net.neurons[i].location[0],9,1)
                neuron.location[1] = Combine2(neuron.location[1],recBot.net.neurons[i].location[1],9,1)
                i+=1

            childBot.attributes.maxSpeed = float(
                domBot.attributes.maxSpeed)+(random.random()*0.1-0.05)
            childBot.attributes.maxTurnSpeed = float(
                domBot.attributes.maxTurnSpeed)+(random.random()*0.1-0.05)

            self.simulator.addObject(childBot)

    def move(self):
        # find out the direction which the bot is facing (added onto the current direction)
        self.direction += self.angular_velocity_factor * \
            self.attributes.maxTurnSpeed*self.simulator.simTimeInterval
        # limit the angle to be within 2*Pi radians or 360 degrees
        self.direction = self.direction % (2*math.pi)
        # find out how far the bot has traveled
        displacement = self.velocity_factor*self.attributes.maxSpeed*self.simulator.simTimeInterval
        # find the displacement along the axis
        x_displacement = math.cos(self.direction)*displacement
        y_displacement = -math.sin(self.direction)*displacement
        # update the position
        self.position = [self.position[0]+x_displacement,
                         self.position[1]+y_displacement]
        
        # check if the bot has reached the boundry
        # Right boundry
        if self.position[0] > self.simulator.world.width - self.attributes.radius:
            self.energy_level -= Boundry_damage
            self.position[0] = self.simulator.world.width - self.attributes.radius*2
        # Bottom boundry
        if self.position[1] > self.simulator.world.height - self.attributes.radius:
            self.energy_level -= Boundry_damage
            self.position[1] = self.simulator.world.height - self.attributes.radius*2
        # Left boundry
        if self.position[0] < self.attributes.radius:
            self.energy_level -= Boundry_damage
            self.position[0] = self.attributes.radius*2
        # Top boundry
        if self.position[1] < self.attributes.radius:
            self.energy_level -= Boundry_damage
            self.position[1] = self.attributes.radius*2

        self.calculate_position_percent()
        self.circleObject.position = self.position
        self.circleObject.move()

    def calculate_position_percent(self):
        # calculates and returns the percent indicators of the position of the bot within the world
        self.position_percent = [
            self.position[0] / self.simulator.world.width, self.position[1] / self.simulator.world.height]

    def think(self):
        # gather inputs
        self.assign_brain_inputs()
        # think
        self.net.think()
        # assign to outputs
        self.assign_brain_outputs()

    def calculate_energy(self):
        # how much energy was used
        movement_energy_consumption = self.attributes.maxSpeed * \
            abs(self.velocity_factor) * \
            Movement_energy_loss_rate * self.simulator.simTimeInterval

        base_energy_consumption = Base_energy_loss_rate*self.simulator.simTimeInterval

        # take from resoviour
        self.energy_level -= movement_energy_consumption + base_energy_consumption

        # limits to 0
        self.dead = self. energy_level <= 0

        # limits above (shouldnt be possible but is somehow)
        if self.energy_level > self.attributes.energyReserveLimit:
            self.energy_level = self.attributes.energyReserveLimit
        
        self.energy_percent = self.energy_level/self.attributes.energyReserveLimit

    def assign_brain_inputs(self):
        '''
        grabs the inputs to the brain and assigns them to designated neurons
        '''

        for input in self.brain_inputs:
            if input['name']=='EP':
                input['value']= self.energy_percent
            elif input['name']=='DP':
                input['value']= self.direction_percent
            elif input['name']=='PPx':
                input['value']= self.position_percent[0]
            elif input['name']=='PPy':
                input['value']= self.position_percent[1]
            else:
                """ for segment in self.eye_segments:
                    if input['name']==segment["name"]+"Dis":
                        input['value'] = segment["distance_percent"]
                    self.brain_inputs.append({"name":segment["name"]+"R","value":segment["colour_RGB"][0]})
                    self.brain_inputs.append({"name":segment["name"]+"G","value":segment["colour_RGB"][1]})
                    self.brain_inputs.append({"name":segment["name"]+"B","value":segment["colour_RGB"][2]}) """


        for neuron in self.net.neurons:
            for input in self.brain_inputs:
                if neuron.name == input["name"]:
                    neuron.output = input["value"]

    def assign_brain_outputs(self):
        '''
        grabs the outputs for the brain then assigns them to designated neurons
        '''
        for neuron in self.net.neurons:
            for output in self.brain_outputs:
                if neuron.name == output["name"]:
                    output["value"] = neuron.output

                if output["name"]=="VF":
                    self.setVelocity(2*output["value"]-1)

                if output["name"]=="AVF":
                    self.setAngularVelocity(2*output["value"]-1)

    def saveBrain(self, file_location=None):
        if file_location == None:
            file_location = "brains/" + self.attributes.name+"_brain.txt"

        self.net.save(file_location)

    def takeEnergy(self, other_bot):
        """
        The two bots will share their energy if close enough.
        Takes some of the energy from the object bot
        """
        energy_transfered = 0.5
        self.energy_level += energy_transfered
        other_bot.energy_level -= energy_transfered

class Attributes:
    """
    Defines and handles all a bots internal and external attributes.
    """
    def __init__(self):
        self.name = ""
        self.generation = 0
        self.familyHistory = ""
        self.maxSpeed = Max_speed
        self.maxTurnSpeed = Max_turn_speed
        self.colourRGB = Colour_RGB
        self.assignRGBtoHEX()
        self.maxEnergyReserve = Max_energy_reserve
        self.energyReserveLimit = self.maxEnergyReserve
        self.radius = Radius
    
    def save(self, file_location=None):
        if file_location == None:
            file_location = "attributes/"+self.name+"_attributes.txt"

        attributeFile = open(file_location, "w")

        attributeFile.write("Name: "+self.name+"\n")
        attributeFile.write("Generation: "+str(self.generation)+"\n")
        attributeFile.write("Family History: " +self.ownFamilyHistory()+"\n")
        attributeFile.write("Max Speed: "+str(self.maxSpeed)+"\n")
        attributeFile.write("Max Turn Speed: "+str(self.maxTurnSpeed)+"\n")
        attributeFile.write("Colour: "+self.colourHEX+"\n")
        attributeFile.write("Energy Reserve: "+str(self.maxEnergyReserve))

        attributeFile.close()

    def load(self, file_location):
        attributeFile = open(file_location, "r")

        name = attributeFile.readline()
        generation = attributeFile.readline()
        family_history = attributeFile.readline()
        max_speed = attributeFile.readline()
        max_turn_speed = attributeFile.readline()
        colour = attributeFile.readline()
        energy_reserve = attributeFile.readline()

        name = name.strip()
        generation = generation.strip()
        family_history = family_history.strip()
        max_speed = max_speed.strip()
        max_turn_speed = max_turn_speed.strip()
        colour = colour.strip()
        energy_reserve = energy_reserve.strip()

        name = name.lstrip("Name: ")
        generation = generation.lstrip("Generation: ")
        family_history = family_history.lstrip("Family History: ")
        max_speed = max_speed.lstrip("Max Speed: ")
        max_turn_speed = max_turn_speed.lstrip("Max Turn Speed: ")
        colour = colour.lstrip("Colour: ")
        energy_reserve = energy_reserve.lstrip("Energy Reserve: ")

        self.name = name
        self.generation = int(generation)
        self.familyHistory = family_history
        self.maxSpeed = float(max_speed)
        self.maxTurnSpeed = float(max_turn_speed)
        self.colourHEX = colour
        self.assignHEXtoRGB()
        self.maxEnergyReserve = float(energy_reserve)

        attributeFile.close()

    def ownFamilyHistory(self):
        return self.familyHistory + " ~> (N:"+self.name+" G:"+str(self.generation)+")"

    def mutate(self):
        """
        Mutates the attributes for the bot 
        """
        self.maxSpeed = self.maxSpeed + (random.random()-0.5)*0.3
        self.maxTurnSpeed = self.maxTurnSpeed + (random.random()-0.5)*0.3
        self.maxEnergyReserve = self.maxEnergyReserve + (random.random()-0.5)*0.3
        self.energyReserveLimit = self.maxEnergyReserve

        for i in range(3):
            self.colourRGB[i] = max(min(self.colourRGB[i] + (random.random()-0.5)*0.3,1),0)
        self.assignRGBtoHEX()

    def assignRGBtoHEX(self):
        self.colourHEX = visualiser.RGBtoHEX(self.colourRGB)
        
    def assignHEXtoRGB(self):
        self.colourRGB = visualiser.HEXtoRGB(self.colourHEX)
        
        


    
def Combine(dom_value, sub_value, max_value, min_value):

    mutation_chance = 0.2
    sub_pull = 0.2
    mut_pull = 0.5

    mutation_factor = random.random()
    if mutation_factor <= mutation_chance:
        #mutation occurs
        difference = dom_value - ((max_value-min_value)*random.random()+min_value)
        return min(max(dom_value-mut_pull*difference,min_value),max_value)
    else:
        #combine
        difference = dom_value - sub_value
        return min(max(dom_value-sub_pull*difference,min_value),max_value)

def Combine2(dom_value, sub_value, max_value, min_value):

    mutation_chance = 0.2
    sub_pull = 0.2
    mut_pull = 0.5

    midpoint = (max_value-min_value)/2.0

    mutation_value = ((max_value-min_value)*random.random()+min_value)
    
    mutation_factor = random.random()
    if mutation_factor <= mutation_chance:
        #mutation occurs
        difference = mutation_value - midpoint
        return min(max(dom_value + mut_pull * difference,min_value),max_value)
    else:
        #combine
        difference = sub_value - midpoint
        return min(max(dom_value + sub_pull * difference,min_value),max_value)

class eye:
    def __init__(self, bot : Bot):
        self.bot = bot

    def see(self, object):
        pass


def main():
    import bot
    plane = world.World(10,10)
    sim = simulator.Simulator(1,0.1,plane)
    for i in range(1):
        sim.addObject(bot.Bot(sim))
    sim.minNumOfBots = 1
    sim.run()
    
if __name__ == "__main__":
    main()
