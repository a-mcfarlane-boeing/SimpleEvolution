import math
import brain
import random

#bot simulation constants
#breeding
Min_energy_to_breed = 10 # below this energy level the bot is too tired to breed
Min_breed_delay = 20 # seconds between "sessions"
Min_age_to_breed = 18 # seconds
Energy_lost_from_breeding = 2.5
Norm_neuron_max_change = 0.2
Mutation_neuron_max_change = Norm_neuron_max_change*3
Chance_of_mutation = 1/25.0

#apperance
Radius = 0.5 # unit (size of the bot)
Colour = "yellow"

#eating
Eat_delay = 7 # seconds between meals

#energy
Movement_energy_loss_rate = 0.05 # units per unit moved
Base_energy_loss_rate = 0.15 # units per second
Max_energy_reserve = 100

#sight
Max_view_distance = 100
Max_view_angle = math.pi/2.0 # radians
View_angle_overlap = math.pi/4.0 #radians how much of the central vision which overlaps

# bot initial variables (can change with generations)
Max_turn_speed = math.pi/1.5 # radians per second
Max_speed = 3 # units per second

#brain variables
Num_of_neurons = 30
Num_of_connections = 10
Num_of_brain_inputs = 7

# ouput neurons
O_neuron_eat = "n0"
O_neuron_RFactor = "n1"
O_neuron_VFactor = "n2"

#input neurons
I_neuron_Energy = "i0" # energy percentage (1 when full, 0 when empty)
I_neuron_Xpos = "i1" # X position in world (0 when to the left, 1 when to the right)
I_neuron_YPos = "i2" # Y position in world
I_neuron_SightCWA = "i3" # clockwise angle from the target (angle from mid point of vision, 0 when at edge, 1 when centred)
I_neuron_SightACWA = "i4" # anitclockwise angle from the target
I_neuron_SightDis = "i5" # distance from the target (1 when close, 0 when beyond range)
I_neuron_Clock = "i6" # internal clock (0 to 1 each simulated second)

internal_clock_range = 10.0 # how long it takes for the clock input neuron go from 0 to 1 (simulated seconds)

class Bot:
    """ Defines a Bot with all its attributes """
    def __init__(self, initial_time, name = "exampleBot", max_speed=Max_speed,max_view_angle=Max_view_angle,max_energy=Max_energy_reserve, world_width=10, world_height=10, colour = Colour):
        # bot attributes
        self.name = name
        self.max_speed = max_speed
        self.max_turn_speed = Max_turn_speed
        self.max_view_angle = max_view_angle
        self.max_view_distance = Max_view_distance
        self.max_energy = max_energy
        self.generation = 0
        self.family_history = "None"
        self.colour = colour
        

        # bot internal variables
        self.energy_level = self.max_energy
        self.breeding_points = 0
        self.total_rewards_collected = 0
        self.time_since_last_child = 0.0
        self.time_since_last_meal = 0.0
        

        # world variables
        self.birth_time = initial_time
        self.time_since_birth = 0.0
        self.time_last = 0.0
        self.time_interval = 0.0
        self.world_width = world_width
        self.world_height = world_height

        # bot enviromental variables
        self.position = [5,5] # x,y
        self.direction = 0.0 # angle from x axis, anti-clockwise, radians

        # outputs from the brain
        self.velocity_factor = 0 # -1 to 1, forward and reverse
        self.angular_velocity_factor = 0 # -1 to 1, anti & clockwise
        self.eat_action = 0 # 0 to 1, triggers eating when >= 0.5
    
        # inputs to brain
        self.energy_percent = 1.0
        self.right_angle_percent = 0.0
        self.left_angle_percent = 0.0
        self.view_distance_percent = 0.0
        self.direction_percent = 0.0
        self.position_percent = [0.0,0.0]

        # outputs to simulator
        self.eat_success= False # tells the simulator if the bot was successful at eating in the last simulation run

        #brain
        self.net = brain.Brain(Num_of_neurons,Num_of_connections,num_of_inputs=Num_of_brain_inputs)

    def setAngularVelocity(self,a_velocity):
        self.angular_velocity_factor = a_velocity

    def setVelocity(self,velocity):
        self.velocity_factor = velocity

    def calculateTimeInterval(self, current_simulation_time):
        # how long the bot has been alive
        self.time_since_birth = current_simulation_time - self.birth_time      
        # finds the length of time since the last time this function was run
        self.time_interval = self.time_since_birth - self.time_last
        # rewrites the last time the time interval was calculated
        self.time_last = self.time_since_birth

        # updates internal clocks accordingly
        self.time_since_last_child += self.time_interval
        self.time_since_last_meal += self.time_interval

    def simulate(self,simulation_time, reward):
        # determine the elapsed time
        self.calculateTimeInterval(simulation_time)
        # see the enviroment
        self.see(reward)
        # run calculations through the brain
        self.think()
        # move bot accoringly
        self.move()
        # attempts to eat if the eat_action neuron is triggered
        self.eat(reward)
        # calculate energy consumption
        self.calculate_energy()

    def move(self):
        # find out the direction which the bot is facing (added onto the current direction)
        self.direction += self.angular_velocity_factor*self.max_turn_speed*self.time_interval
        #limit the angle to be within 2*Pi radians or 360 degrees
        self.direction = self.direction%(2*math.pi)
        # find out how far the bot has traveled
        displacement = self.velocity_factor*self.max_speed*self.time_interval
        # find the displacement along the axis
        x_displacement = math.cos(self.direction)*displacement
        y_displacement = -math.sin(self.direction)*displacement
        # update the position
        self.position = [self.position[0]+x_displacement,self.position[1]+y_displacement]

    def get_position_percent(self):
        #calculates and returns the percent indicators of the position of the bot within the world
        self.position_percent = [self.position[0] / self.world_width, self.position[1] / self.world_height]
        return self.position_percent

    def think(self):
        self.assign_brain_inputs()
        # think
        self.net.calculateOutputs()
        # assign to outputs
        self.angular_velocity_factor = (self.net.dict_all_values[O_neuron_RFactor]*2) - 1
        self.velocity_factor = (self.net.dict_all_values[O_neuron_VFactor]*2)-1
        self.eat_action = self.net.dict_all_values[O_neuron_eat]
    
    def calculate_energy(self):
        # how much energy was used
        movement_energy_consumption = self.max_speed * abs(self.velocity_factor) * Movement_energy_loss_rate * self.time_interval
        base_energy_consumption = Base_energy_loss_rate*self.time_interval
        
        # take from resoviour
        self.energy_level -= movement_energy_consumption + base_energy_consumption
        
        # limits to 0
        if self. energy_level < 0:
            self.energy_level = 0
        
        # limits above ( shouldnt be possible but is somehow)
        if self.energy_level > self.max_energy:
            self.energy_level = self.max_energy

    def assign_brain_inputs(self):
        '''
        calculates the inputs for the brain then assigns them to designated neurons
        '''
        self.energy_percent = self.energy_level/self.max_energy
        self.net.dict_all_values[I_neuron_Energy] = self.energy_percent
        self.net.dict_all_values[I_neuron_Xpos,I_neuron_YPos] = self.get_position_percent()
        self.net.dict_all_values[I_neuron_SightCWA] = self.right_angle_percent
        self.net.dict_all_values[I_neuron_SightACWA] = self.left_angle_percent
        self.net.dict_all_values[I_neuron_SightDis] = self.view_distance_percent
        self.net.dict_all_values[I_neuron_Clock] = (self.time_since_birth%internal_clock_range)/internal_clock_range

    def see(self, obj):
        #determine the angle to the reward
        x_displacement = obj.position[0] - self.position[0]
        y_displacement = self.position[1] - obj.position[1]
        angle_to_obj = math.atan2(y_displacement, x_displacement)

        # find out where in the field of view it is
        #angle
        angle_to_turn_to_reward = angle_to_obj - self.direction
        if angle_to_turn_to_reward > math.pi:
            angle_to_turn_to_reward = -2*math.pi + angle_to_turn_to_reward
        elif angle_to_turn_to_reward < - math.pi:
            angle_to_turn_to_reward = 2*math.pi + angle_to_turn_to_reward
        
        if angle_to_turn_to_reward <= 0:
            angle_percent = abs(angle_to_turn_to_reward / (self.max_view_angle/2.0))
            if angle_percent > 1:
                angle_percent=1
            self.right_angle_percent = 1.0 - angle_percent
        
        if angle_to_turn_to_reward >=0:
            angle_percent = abs(angle_to_turn_to_reward / (self.max_view_angle/2.0))
            if angle_percent > 1:
                angle_percent=1
            self.left_angle_percent = 1.0 - angle_percent
        
        #distance
        # check if within view
        if self.left_angle_percent>0 and self.right_angle_percent >0:
            distance_to_reward = math.sqrt(x_displacement**2 + y_displacement**2)

            view_distance_factor = distance_to_reward / self.max_view_distance

            self.view_distance_percent = 1.0 - view_distance_factor

            if self.view_distance_percent < 0 :
                self.view_distance_percent = 0
                self.left_angle_percent = 0
                self.right_angle_percent = 0
        else:
            self.view_distance_percent=0

    def saveBrain(self,file_location = None):
        if file_location == None:
            file_location = "brains/" + self.name+"_brain.txt"

        self.net.saveBrain(file_location)
    
    def saveAttributes(self, file_location = None):
        if file_location == None:
            file_location = "attributes/"+self.name+"_attributes.txt"
        
        attributeFile = open(file_location,"w")
        
        attributeFile.write("Name: "+self.name+"\n")
        attributeFile.write("Generation: "+str(self.generation)+"\n")
        attributeFile.write("Family History: "+str(self.family_history)+"~"+self.name+"\n")
        attributeFile.write("Max Speed: "+str(self.max_speed)+"\n")
        attributeFile.write("Max Turn Speed: "+str(self.max_turn_speed)+"\n")

        attributeFile.close()

    
    def loadAttributes(self,file_location):
        attributeFile = open(file_location,"r")
        
        name = attributeFile.readline()
        generation = attributeFile.readline()
        family_history = attributeFile.readline()
        max_speed = attributeFile.readline()
        max_turn_speed = attributeFile.readline()
        #print(name,generation,family_history)

        generation = generation.strip()
        family_history = family_history.strip()
        #print(name,generation,family_history)

        name = name.replace("Name: ","")
        generation = generation.replace("Generation: ","")
        family_history = family_history.replace("Family History: ","")
        max_speed = max_speed.replace("Max Speed: ","")
        max_turn_speed = max_turn_speed.replace("Max Turn Speed: ","")
        #print(name,generation,family_history)
        
        self.generation = int(generation)
        self.family_history = family_history
        self.max_speed = float(max_speed)+(random.random()*0.1-0.05)
        self.max_turn_speed = float(max_turn_speed)+(random.random()*0.1-0.05)

        attributeFile.close()
    
    def breed(self, other_bot, child_name, sim_time_now):
        """
        the assigned bot will attempt to breed with the given bot providing they are both eligable
        returns the child bot of the two parents.
        """
        # check all conditions
        different_bots = False
        self_willing = False
        other_willing = False
        same_species = False
        #check if not trying to breed with self (eww)
        if self.name != other_bot.name:
            different_bots = True
        
        #check if this bot is eligable to breed
        if self.breeding_points >= 1 and self.energy_level >= Min_energy_to_breed and self.time_since_last_child >= Min_breed_delay and self.time_since_birth >= Min_age_to_breed:
            self_willing = True
        
        # check if the given bot is eligable to breed
        if other_bot.breeding_points >= 1 and other_bot.energy_level >= Min_energy_to_breed and other_bot.time_since_last_child >= Min_breed_delay and other_bot.time_since_birth >= Min_age_to_breed:
            other_willing = True
        
        # check if the bots are of the same species
        if self.colour == other_bot.colour:
            same_species = True
        
        if different_bots and same_species and self_willing and other_willing:
            
            print(self.name+" mated with "+other_bot.name+" to create "+child_name)
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
                domBot = self # dominate traits
                recBot = other_bot # recessive traits
            else:
                recBot = self
                domBot = other_bot
            # make love (generate the child bot)
            childBot = Bot(name = child_name, initial_time = sim_time_now, world_width=self.world_width,world_height=self.world_height, colour=domBot.colour)
            # child comes from the dominate bot
            childBot.position[0] = domBot.position[0]
            childBot.position[1] = domBot.position[1]
            childBot.direction = 6.28 * random.random()
            # give the child a family history or genetic code
            if domBot.family_history != "None":
                childBot.family_history = domBot.family_history + domBot.name +"~" +str(domBot.generation)+"|"
            else:
                childBot.family_history = domBot.name +"~" +str(domBot.generation)+"|"
            
            # create the brain for the child bot
            childBot.net.loadBrain("brains/starter_brain.txt")
            k=0
            #go through each neuron
            while k < childBot.net.num_of_neurons:
                l=0
                new_weights = []
                #replace each weight
                while l < childBot.net.num_of_connections + 1:
                    domWeight = domBot.net.neurons[k].weights[l]
                    recWeight = recBot.net.neurons[k].weights[l]
                    difference = domWeight - recWeight
                    # divided by two because the maximum potential difference is 2 (-1 to 1)
                    differenceFactor = difference / 2.0
                    if random.random() < Chance_of_mutation:
                        #mutation
                        difference = domWeight - (random.random()*2 -1)
                        differenceFactor = difference / 2.0
                        new_weights.append(domWeight- Mutation_neuron_max_change * differenceFactor)
                    else:
                        #normal adjustment
                        new_weights.append(domWeight - Norm_neuron_max_change * differenceFactor)
                    l+=1
                childBot.net.neurons[k].weights = new_weights
                childBot.net.neurons[k].calculateWeightTotals()
                k+=1
            
            childBot.generation = max(domBot.generation,recBot.generation)+1
            childBot.max_speed = float(domBot.max_speed)+(random.random()*0.1-0.05)
            childBot.max_turn_speed = float(domBot.max_turn_speed)+(random.random()*0.1-0.05)
            
            return childBot

    def eat(self,target):
        """
        Bot will attept to eat from the target. Will only succeed if close enough
        updates the bot's energy level
        Returns True if successfull, otherwise False.
        """
        self.eat_success = False
        target_x_pos = target.getPosition()[0]
        target_y_pos = target.getPosition()[1]

        # check the distance from the target
        distance = math.sqrt((self.position[0]-target_x_pos)**2+(self.position[1]-target_y_pos)**2)

        # will eat if;
        # - within range
        # - hasn't eaten recently
        # - wants to (neuron)
        if (distance <= Radius + 1) and self.time_since_last_meal >= Eat_delay and self.eat_action <=0.8:
            print(self.name+" took a nibble")

            # adds an energy boost to the energy level upto the maximum energy level
            energy_boost = 30
            self.energy_level += energy_boost
            if self.energy_level > self.max_energy:
                self.energy_level = self.max_energy        

            # makes the bot "age" and have less vitality
            if self.max_energy >= 30:
                self.max_energy -= 2

            # the rewards for getting a reward
            self.total_rewards_collected += 1
            self.breeding_points += 2
            self.time_since_last_meal = 0
            
            # flag for the simulator
            self.eat_success = True

            target.consumed()

        # eating will consume a bit of energy, decentivising the bots from attempting to eat continuously
        self.energy_level -= 0.001

    def takeEnergy(self,other_bot):
        """
        The two bots will share their energy if close enough.
        Takes some of the energy from the target bot
        """
        energy_transfered= 0.5
        self.energy_level += energy_transfered
        other_bot.energy_level -= energy_transfered

        
    
    def getPosition(self):
        '''
        Returns the [x,y] position of the bot
        '''
        return self.position

def main():
    newBot = Bot(0)

    newBot.saveBrain()
    pass

if __name__ == "__main__":
    main()