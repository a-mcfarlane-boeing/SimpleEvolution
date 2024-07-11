import math
import random
import brain
import visualiser
import simulator


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
Colour_B = 0.8
Colour_RGB = [Colour_R, Colour_G, Colour_B]

# eating
Eat_delay = 7  # seconds between meals

# energy
Movement_energy_loss_rate = 0.05  # units per unit moved
Base_energy_loss_rate = 0.9  # units per second
Max_energy_reserve = 100

Boundry_damage = 8

# sight
Max_view_distance = 40.0
FOV_angle = math.pi/2.0  # radians
# the number of segments of vision (note this will require adapatble number of neurons. Min 1)
Resolution_of_eye = 9

# Mobility
Max_turn_speed = math.pi/1.5  # radians per second
Max_speed = 3.0  # units per second


class Bot:
    """ Defines a Bot with all its attributes """

    def __init__(self, simulator: simulator.Simulator, name="exampleBot", max_speed=Max_speed, FOV_angle=FOV_angle, max_energy=Max_energy_reserve, colour_RGB=Colour_RGB):
        #simulator
        self.simulator = simulator

        # bot attributes
        self.attributes = Attributes()
        self.attributes.name = name
        self.attributes.maxSpeed = max_speed
        self.attributes.maxTurnSpeed = Max_turn_speed
        self.attributes.energyReserveLimit = max_energy

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

        # eye
        self.resolution_of_eye = 9
        self.FOV_angle = FOV_angle
        self.max_view_distance = Max_view_distance
        self.eye = Eye(self)

        # Brain
        inputs = 3 + self.resolution_of_eye*4
        outputs = 3


        self.net = brain.Brain(num_of_neurons = (inputs+outputs)*2)

        self.connectToBrain()

    def connectToBrain(self):
        self.net.num_of_inputs = 0
        self.net.num_of_outputs = 0
        self.net.configureNeurons()
        self.assignBrainInputs()
        self.assignBrainOutputs()

    def assignBrainInputs(self):

        self.net.num_of_inputs = 0

        self.net.setInput("EP",self.getEnergyPercent)
        self.net.setInput("DP",self.getDirectionPercent)
        self.net.setInput("PPx",self.getPPx)
        self.net.setInput("PPy",self.getPPy)

        for segment in self.eye.segments:
            self.net.setInput(segment.name+"Dis",segment.getDisPercent)
            self.net.setInput(segment.name+"R",segment.getRed)
            self.net.setInput(segment.name+"G",segment.getGreen)
            self.net.setInput(segment.name+"B",segment.getBlue)

    def assignBrainOutputs(self):
        def neuronToFactor(neuron_output_function):
            """ Returns a wrapper function which converts
            the 0 to 1 output of a neuron to -1 to 1"""
            def convertedValue():
                """Wrapper function which converts the neuron
                output to the -1 to 1 scale"""
                return neuron_output_function()*2-1
            return convertedValue

        self.net.num_of_outputs = 0

        self.angular_velocity_factor = neuronToFactor(self.net.getOutput("AVF"))
        self.velocity_factor = neuronToFactor(self.net.getOutput("VF"))
        self.eat_action = self.net.getOutput("EA")

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
        self.eye.reset()
        for object in self.simulator.simObjects:
            if object.attributes.name != self.attributes.name:
                self.eye.see(object)
                self.eat(object)
                self.breed(object)

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
        if (distance <= Radius + 1) and self.time_since_last_meal >= Eat_delay and self.eat_action() <= 0.8:
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
        colour_range = 0.1
        result = True
        for i in range(3):
            if self.attributes.colourRGB[i] <= other.attributes.colourRGB[i]+colour_range/2 and self.attributes.colourRGB[i] >= other.attributes.colourRGB[i]-colour_range/2 :
                result = result and True
            else:
                result = False

        return result

    def breed(self, other_bot: Bot):
        """
        the assigned bot will attempt to breed with the given bot providing they are both eligable
        returns the child bot of the two parents.
        """

        if 'bot' in str.lower(other_bot.attributes.name):
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
            childBot = Bot(self.simulator, "new_bot", colour_RGB=domBot.attributes.colourRGB)
            childBot.circleObject.delete()
            childBot.position = domBot.position.copy()
            childBot.attributes.__dict__.update(domBot.attributes.__dict__.copy())
            childBot.circleObject = visualiser.CircleObject(childBot.simulator.worldWindow, childBot.attributes.colourHEX, childBot.position, childBot.attributes.radius)
            childBot.net = domBot.net.copy()
            childBot.eye = Eye(childBot)

            childBot.attributes.name = child_name
            childBot.direction = 2* math.pi * random.random()
            childBot.attributes.generation += 1
            childBot.attributes.familyHistory = domBot.attributes.ownFamilyHistory()

            #give child bot colour
            result_colour_RGB = []
            for i in range(3):
                result_colour_RGB.append(Combine1(domBot.attributes.colourRGB[i],recBot.attributes.colourRGB[i],0,1))
            childBot.attributes.colourRGB = result_colour_RGB
            childBot.attributes.assignRGBtoHEX()

            childBot.circleObject.colourHEX = childBot.attributes.colourHEX
            childBot.circleObject.changeColour()

            i=0
            for neuron in childBot.net.neurons:
                neuron.location[0] = Combine_Wrap(neuron.location[0],recBot.net.neurons[i].location[0],0,childBot.net.side_length)
                neuron.location[1] = Combine_Wrap(neuron.location[1],recBot.net.neurons[i].location[1],0,childBot.net.side_length)
                i+=1

            #childBot.net.configureNeurons()
            childBot.connectToBrain()

            childBot.attributes.maxSpeed = float(
                domBot.attributes.maxSpeed)+(random.random()*0.1-0.05)
            childBot.attributes.maxTurnSpeed = float(
                domBot.attributes.maxTurnSpeed)+(random.random()*0.1-0.05)
            childBot.attributes.maxEnergyReserve = float(domBot.attributes.maxEnergyReserve+(random.random()*0.1-0.05))

            childBot.energy_level = childBot.attributes.maxEnergyReserve
            childBot.total_rewards_collected = 0

            self.simulator.addObject(childBot)

    def move(self):
        # find out the direction which the bot is facing (added onto the current direction)
        self.direction += self.angular_velocity_factor() * \
            self.attributes.maxTurnSpeed*self.simulator.simTimeInterval
        # limit the angle to be within 2*Pi radians or 360 degrees
        self.direction = self.direction % (2*math.pi)
        # find out how far the bot has traveled
        displacement = self.velocity_factor()*self.attributes.maxSpeed*self.simulator.simTimeInterval
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

        self.circleObject.position = self.position
        self.circleObject.move()

    def getPPx(self):
        return self.position[0] / self.simulator.world.width

    def getPPy(self):
        return self.position[1] / self.simulator.world.height

    def think(self):
        self.net.think()

    def getDirectionPercent(self):
        return (self.direction%math.pi)/math.pi

    def calculate_energy(self):
        # how much energy was used
        movement_energy_consumption = self.attributes.maxSpeed * \
            abs(self.velocity_factor()) * \
            Movement_energy_loss_rate * self.simulator.simTimeInterval

        base_energy_consumption = Base_energy_loss_rate*self.simulator.simTimeInterval

        # take from resoviour
        self.energy_level -= movement_energy_consumption + base_energy_consumption

        # limits to 0
        self.dead = self.energy_level <= 0

        # limits above (shouldnt be possible but is somehow)
        if self.energy_level > self.attributes.energyReserveLimit:
            self.energy_level = self.attributes.energyReserveLimit

    def getEnergyPercent(self):
        return self.energy_level/self.attributes.energyReserveLimit

    def saveBrain(self, file_location=None):
        if file_location == None:
            file_location = "brains/" + self.attributes.name+"_brain.txt"

        self.net.save(file_location)

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
            self.colourRGB[i] = max(min(self.colourRGB[i] + (random.random()-0.5)*0.1,1),0)
        self.assignRGBtoHEX()

    def assignRGBtoHEX(self):
        self.colourHEX = visualiser.RGBtoHEX(self.colourRGB)

    def assignHEXtoRGB(self):
        self.colourRGB = visualiser.HEXtoRGB(self.colourHEX)

def Combine1(dom_value, sub_value, min_value, max_value):
    """returns a value close to the dom value towards the sub value
    The amount of pull the sub has is dictated by the probability that
    it is on a particular side of the dom value"""

    prob_less = (dom_value - min_value) / (max_value - min_value)

    mutation_chance = 0.2
    sub_pull = 0.003
    mut_pull = 0.005

    if random.random() <= mutation_chance:
        #mutation occurs
        difference = ((max_value-min_value)*random.random()+min_value) - dom_value
        new_val = dom_value+mut_pull*difference
    else:
        #combine
        difference = sub_value - dom_value
        if sub_value < dom_value:
            new_val = dom_value + sub_pull*difference*(1.1-prob_less)
        else:
            new_val = dom_value + sub_pull*difference*(prob_less+0.1)

    return min(max(new_val,min_value),max_value)

def Combine2(dom_value, sub_value, min_value, max_value):

    mutation_chance = 0.2
    sub_pull = 0.2
    mut_pull = 0.5

    midpoint = (max_value-min_value)/2.0

    mutation_value = ((max_value-min_value)*random.random()+min_value)

    if random.random() <= mutation_chance:
        #mutation occurs
        return min(max(dom_value + mut_pull * mutation_value,min_value),max_value)
    else:
        #combine
        difference = sub_value - midpoint
        return min(max(dom_value + sub_pull * difference,min_value),max_value)

def Combine3(dom_value, sub_value, min_value, max_value):
    """only tries to combine the values if they are within a
    half length of the range of each other"""

    mutation_chance = 0.2
    sub_pull = 0.2
    mut_pull = 0.5

    if random.random() <= mutation_chance:
        #mutation occurs
        return min(max(dom_value + mut_pull * (random.random()*2-1),min_value),max_value)
    else:
        #combine
        quater_length = (max_value-min_value)/2.0

        lower_limit = max(dom_value-quater_length,min_value)
        upper_limit = min(dom_value+quater_length,max_value)

        lower_length = dom_value - lower_limit
        upper_length = upper_limit - dom_value

        difference = sub_value - dom_value

        if sub_value < dom_value and sub_value >= lower_limit:
            movement = difference/lower_length
        elif sub_value > dom_value and sub_value <= upper_limit:
            movement = difference/upper_length
        else:
            """outside of bounds, no movement"""
            return dom_value

        return min(max(dom_value+movement*sub_pull,min_value),max_value)

def Combine_Wrap(dom_val, sub_val, min_bound, max_bound):
    """
    Will try to combine the values, but if the dom and sub are near the bounds it will pull the result around between the two
    """
    mutation_chance = 1/100.0
    sub_pull = 0.05
    mut_pull = 0.05

    len_range = max_bound - min_bound

    if random.random() <= mutation_chance:
        #mutation occurs
        sub_val = len_range*random.random()+min_bound
        sub_pull = mut_pull

    diff = dom_val - sub_val
    wrap_diff = len_range - abs(diff)
    if diff > 0:
        # dom > sub → diff is positive
        wrap_diff = -wrap_diff

    if abs(diff) > abs(wrap_diff):
        # The inverse direction is smaller. Wrap
        diff = wrap_diff

    return (dom_val - sub_pull * diff)%len_range

class Eye:
    class Segment:
        def __init__(self,name,sAngle,eAngle):
            self.name = name
            self.startAngle = sAngle
            self.endAngle = eAngle
            self.disPercent = 0.0
            self.RGB = [0.0,0.0,0.0]

        def reset(self):
            self.disPercent = 0.0
            self.RGB = [0.0,0.0,0.0]

        def getDisPercent(self):
            return self.disPercent

        def getRed(self):
            return self.RGB[0]

        def getGreen(self):
            return self.RGB[1]

        def getBlue(self):
            return self.RGB[2]

    def __init__(self, bot : Bot):
        self.bot = bot
        self.angle_of_left_view_g = 0.0
        self.segment_angle = self.bot.FOV_angle/self.bot.resolution_of_eye
        self.segments:list[Eye.Segment] = []
        for i in range(self.bot.resolution_of_eye):
            self.segments.append(Eye.Segment("Eye Segment"+str(int(i)),i*self.segment_angle,(
                i+1)*self.segment_angle))

    def see(self, object:Bot):
        #determine where the object is in comparison to self
        x_displacement = object.position[0] - self.bot.position[0]
        y_displacement = self.bot.position[1] - object.position[1]
        # check if too far away, if so, skip
        distance_to_object = math.sqrt(
            x_displacement**2 + y_displacement**2)

        if distance_to_object > self.bot.max_view_distance:
            return
        #determine the angle to the object from self in global coords
        angle_to_object_g = math.atan2(y_displacement,x_displacement)
        #determine the angle from the left most side of the bots view
        angle_of_object_in_view = (
            angle_to_object_g-self.angle_of_left_view_g) % (2*math.pi)
        #if the object is outside the field of view skip it
        if angle_of_object_in_view > self.bot.FOV_angle:
            return

        for segment in self.segments:
            if angle_of_object_in_view >= segment.startAngle and angle_of_object_in_view < segment.endAngle:
                distance_percent = 1.0 - distance_to_object/self.bot.max_view_distance
                if segment.disPercent <= distance_percent:
                    segment.disPercent = distance_percent
                    segment.RGB = object.attributes.colourRGB

    def reset(self):
        #resets all the view segments
        for segment in self.segments:
            segment.reset()

        #determine the global angle of the left view
        self.angle_of_left_view_g = (
            self.bot.direction-self.bot.FOV_angle/2) % (2*math.pi)


def main():
    testbot = Bot(simulator.Simulator())
    print(testbot.__dict__)

if __name__ == "__main__":
    main()
