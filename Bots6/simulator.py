import time
import visualiser as vis
import world
import brain_vis
import random
import copy

num_of_simulations_total = 1
num_of_simulations = 0

hours = 0
minutes = 5
seconds = 0
#time frame
time_factor = 1.0

# Global Variables
# World
World_width = 50
World_height = 40
# Collisions
EnableCollisions = False
# Number of bots
Bots_per_square_unit = 5.0/100
Absolute_max_num_of_bots = 200

Max_num_of_bots = min(World_width*World_height*Bots_per_square_unit,Absolute_max_num_of_bots)

Initial_number_of_bots = int(Max_num_of_bots*0.5)

frame_rate = 24.0
frame_interval = 1 / frame_rate

#object.radius = bot.Radius


"""START



def printBotDetails(bot):
    text ="Name: "+str(bot.name)+" |Energy: {:3.0f} |Brain outputs [vf,avf,e]: [{: 2.3f}, {: 2.3f}, {: 2.2f}] |Sight neuron: {:2.3f} |Pos: x:{:.1f} y:{:.1f} |Dir: {:1.2f} Rwds: {:2.0f} BP: {:1.0f} Gen: {:2.0f}"
    print(text.format(bot.energy_level, bot.velocity_factor, bot.angular_velocity_factor, bot.eat_action, bot.net.dict_all_values["i3"], bot.position[0], bot.position[1] , bot.direction, bot.total_rewards_collected, bot.breeding_points, bot.generation))

def printSimStatus():
    text ="Sim Time: {:2.0f} Real Time (s): {:2.0f}/"+str(real_time_limit)+" - {:3.0f}% NOB: {:3.0f}/{:3.0f}"
    print(text.format(simulation_elapsed_time, real_elapsed_time, (simulation_elapsed_time/(time_limit*1.0))*100, number_of_bots_alive,Max_num_of_bots))

def createBotDict(new_bot):
    #Returns a dictionary with a bot and a circle initialised in the visualiser
    circle_object = visWin._createCircle(0,0,bot.Radius,new_bot.attributes.colourHEX)
    return {"bot": new_bot,"circle_object":circle_object}

def botCollisionCheck(bot1:bot.Bot, bot2:bot.Bot):
    #This function checks if the two bots have overlapped eachother,
    #if they have then the first bot will be bumped back from the second bot.

    # make sure not checking that the bot is coliding with itself
    if bot1.attributes.name != bot2.attributes.name:
        # get distances between bots on the two axis ( bot 1 from bot 2 )
        X_Displacement = bot1.getPosition()[0] - bot2.getPosition()[0]
        Y_Displacement = bot1.getPosition()[1] - bot2.getPosition()[1]

        # if this distance is less than the combined radius of the two bots then they must be coliding
        distance = math.sqrt(X_Displacement**2 +Y_Displacement**2)

        if distance < bot.Radius*2:
            if X_Displacement < 0:
                #bot 1 is to the left
                bot1.position[0] -= bot.Radius*2.0 + X_Displacement
            else:
                #bot 1 is to the right
                bot1.position[0] += bot.Radius*2.0 - X_Displacement

            if Y_Displacement < 0:
                #bot 1 is above
                bot1.position[1] -= bot.Radius*2.0 + Y_Displacement
            else:
                #bot 1 is below
                bot1.position[1] += bot.Radius*2.0 - Y_Displacement

END"""

"""START

# makes so can run simulation multiple times
while num_of_simulations < num_of_simulations_total:
    

    number_of_bots_alive = Initial_number_of_bots
    total_number_of_bots = Initial_number_of_bots


    

    real_time_limit = hours*60*60 + minutes*60 + seconds

    time_limit = (hours*60*60 + minutes*60 + seconds)*time_factor

    startingX = World_width/2
    startingY = World_height/2

    # list of all the bots that were generated, a bot is added when they die
    all_bots = []

    # create a visualiser
    visWin = vis.Display(World_width, World_height)

    #rewards
    #create the cirlce the reward
    apple = reward.Reward(World_width,World_height)
    vis_apple = visWin._createCircle(apple.position[0],apple.position[1],reward.Radius,reward.Colour)

    # genereate the initial group of bots
    initialising_time = 0
    alive_bots = []
    i = 0
    while i < number_of_bots_alive:
        colour_RGB = [(0.5+((random.random()*0.2)-0.1)),(0.5+((random.random()*0.2)-0.1)),(0.5+((random.random()*0.2)-0.1))]

        initial_bot = bot.Bot(initialising_time,"bot"+str(i),world_width=World_width,world_height=World_height,colour_RGB=colour_RGB)

        initial_bot.net.load("brains/starter_brain.txt")
        initial_bot.attributes.load("attributes/starter_attributes.txt")
        initial_bot.attributes.name = "bot"+str(i)
        initial_bot.position[1] = World_height/2.0 + World_height*0.1*(random.random()*2-1)
        initial_bot.position[0] = World_width/2.0 + World_width*0.1*(random.random()*2-1)
        initial_bot.direction = 6.28 * random.random()

        if i >=5:
            initial_bot.attributes.mutate()
            for neuron in initial_bot.net.neurons:
                neuron.location[0] = bot.Combine2(neuron.location[0], neuron.location[0],9,1)
                neuron.location[1] = bot.Combine2(neuron.location[1], neuron.location[1],9,1)

        alive_bots.append(createBotDict(initial_bot))

        i+=1
    
    #alive_bots.append({"bot":apple})

    initial_generation = alive_bots[0]["bot"].attributes.generation


    # get the time when the program starts
    Start_time = time.time_ns()*1.0
    last_print_time = 0.0

    
    #create brain visualiser for the first bot
    brain_screen = brain_vis.BrainDisplay(alive_bots[0]["bot"].net)

    # simulation begins here -----------------------------------------------
    sim_status = True
    while sim_status:
        time_now = time.time_ns()*1.0
        real_elapsed_time = time_now - Start_time

        real_elapsed_time = real_elapsed_time/10.0**9

        simulation_elapsed_time = real_elapsed_time*time_factor

        difference = real_elapsed_time - last_print_time
        
        # cycles through each of the bots
        i = 0
        while i < number_of_bots_alive:
            
            object.simulate(simulation_elapsed_time, [apple]) #[bot["bot"] for bot in alive_bots]

            # cycle through all the other bots to interact with
            j=i+1
            while j < number_of_bots_alive:
                # see if there is room for new bots
                if number_of_bots_alive < Max_num_of_bots:
                    # attempt to breed
                    child_bot = object.breed(alive_bots[j]["bot"], "bot"+str(total_number_of_bots+1), simulation_elapsed_time)

                    #check if breeding was successful
                    if child_bot != None:
                        total_number_of_bots += 1
                        number_of_bots_alive += 1
                        alive_bots.append(createBotDict(child_bot))
                
                #prevent from checking if coliding with itself
                if i != j and EnableCollisions:
                    botCollisionCheck(object,alive_bots[j]["bot"])

                j+=1

            # check if the bot has reached the boundry
            Boundry_damage = 8
            # Right boundry
            if object.position[0] > World_width - object.radius:
                object.energy_level -= Boundry_damage
                object.position[0] = World_width - 1
            # Bottom boundry
            if object.position[1] > World_height - object.radius:
                object.energy_level -= Boundry_damage
                object.position[1] = World_height - 1
            # Left boundry
            if object.position[0] < object.radius:
                object.energy_level -= Boundry_damage
                object.position[0] = 1
            # Top boundry
            if object.position[1] < object.radius:
                object.energy_level -= Boundry_damage
                object.position[1] = 1

            # bot attempts to eat the reward
            object.eat(apple)

            #bot dies
            if object.energy_level <= 0:
                all_bots.append(object)
                visWin.deleteObject(alive_bots[i]["circle_object"])
                alive_bots.remove(alive_bots[i])
                number_of_bots_alive -= 1

            i+=1
    
        # end of simulation conditions---------------------------------------------------
        if number_of_bots_alive <= 1 or simulation_elapsed_time >= time_limit:
            #move rest of bots into the all bots list
            for bots in alive_bots:   
                bots["bot"].time_since_birth = simulation_elapsed_time - bots["bot"].birth_time
                all_bots.append(bots['bot'])
            
            print("all bots results:")
            for thisBot in all_bots:
                print(thisBot.attributes.name+ "  Rewards collected: "+ str(thisBot.total_rewards_collected) + " Gen: "+str(thisBot.attributes.generation))
            #find the best bot
            i=0
            max_carry_factor = 1
            index = -1
            while i < len(all_bots):
                # the bot with the highest carry factor will go onto the next simulation
                #carry_factor = all_bots[i].total_rewards_collected/(all_bots[i].time_since_birth*1.0)
                carry_factor = all_bots[i].total_rewards_collected
                if carry_factor >= max_carry_factor and all_bots[i].attributes.generation != 0:
                    max_carry_factor = carry_factor
                    index = i
                i+=1
            
            #record the results of the simulation
            if index != -1:
                record = open("record.txt","a")
                record.write("the bot which colllected the most rewards was "+all_bots[index].attributes.name + " RPM: "+str(all_bots[index].total_rewards_collected/(all_bots[index].time_since_birth/60.0))+" Gen: "+ str(all_bots[index].attributes.generation)+" with "+str(all_bots[index].total_rewards_collected)+" Max Speed: "+str(all_bots[index].attributes.maxSpeed)+"\n")
                record.close()
                #show results to the screen
                print("the bot which colllected the most rewards was "+all_bots[index].attributes.name + " RPM: "+str(all_bots[index].total_rewards_collected/(all_bots[index].time_since_birth/60.0))+" Gen: "+ str(all_bots[index].attributes.generation)+" with "+str(all_bots[index].total_rewards_collected))
                all_bots[index].saveBrain('brains/starter_brain.txt')
                all_bots[index].attributes.save('attributes/starter_attributes.txt')
                #save the second best bot
            else:
                print("no bots passed the initial requirements for improvement")
            
            print("End of simulation, the total number of bots was " +str(total_number_of_bots))
            sim_status = False

        if difference >= frame_interval:
            last_print_time = real_elapsed_time

            printSimStatus()
            
            # update the position of all the alive bots on screen
            i=0
            while i < number_of_bots_alive:
                visWin.moveBot(alive_bots[i])
                i += 1
            
            # update the position of the reward
            visWin.moveCircleFromCenter(vis_apple,apple.position[0],apple.position[1])
            
            visWin.update()
            brain_screen.connected_brain = alive_bots[0]["bot"].net
            brain_screen.update()

    num_of_simulations +=1

print("Holding...")
input('Press any button to exit-')


END """


num_of_simulations = 1

minutes = 5.0/60
#time frame
time_factor = 1.0

# Collisions
EnableCollisions = False
# Number of bots
Bots_per_square_unit = 5.0/100
Absolute_max_num_of_bots = 200


Initial_number_of_bots = int(Max_num_of_bots*0.5)

frame_rate = 24.0
frame_interval = 1 / frame_rate

class Simulator:
    def __init__(self, run_time_minutes = minutes, sim_time_factor = 1.0, world = world.World()):
        self.maxRunTime = run_time_minutes*60
        self.runTime = 0.0
        self.simTime = 0.0
        self.simTimeFactor = sim_time_factor
        self.maxSimTime = self.maxRunTime * self.simTimeFactor
        self.simTimeInterval = 0.0
        self.startTime = 0.0

        self.world = world

        self.maxNumOfObjects = 100
        self.minNumOfBots = 2
        self.simObjects = []
        self.totalNumOfObjects = 0
        self.allObjects = []

        self.worldWindow = vis.Display(self.world)

        self.brainWindow = brain_vis.BrainDisplay()

        self.frameInterval = 1.0/frame_rate

        self.status = False

    def addObject(self, object):
        if len(self.simObjects) >= self.maxNumOfObjects:
            print("Cant add any more objects")
            return
        self.totalNumOfObjects+=1
        self.simObjects.append(object)
        self.allObjects.append(object)

    def run(self):
        last_print_time = 0.0
        real_time_interval = 0.0
        self.startTime = now()
        last_real_time = 0.0
        self.status = True
        while self.status:
            self.brainWindow.connected_brain = [bot.net for bot in self.simObjects if "bot" in bot.attributes.name][-1]
            self.simTime += self.simTimeInterval
            real_time_interval = self.runTime - last_real_time
            last_real_time = self.runTime
            self.simTimeInterval = min(real_time_interval*self.simTimeFactor,1.0)

            self.simulate()

            if len(self.simObjects) <=3:
                self.status = False

            if (self.runTime - last_print_time) >= self.frameInterval:
                last_print_time = self.runTime
                self.worldWindow.update()
                self.brainWindow.update()

            self.status = self.runTime < self.maxRunTime and self.status
            self.runTime = now() - self.startTime
        print("The simulation has ended")

    def simulate(self):
        """
        run all the simulation conditions within this sub
        """
        for object in self.simObjects:
            object.simulate()
    
    def endOfSimulation(self):
        from bot import Bot
        print("all bots results:")
        bestBots:list[Bot] = []
        for object in self.allObjects:
            if "bot" in object.attributes.name:
                print(object.attributes.name+ "  Rewards collected: "+ str(object.total_rewards_collected) + " Gen: "+str(object.attributes.generation))
                if object.total_rewards_collected >= 3 and object.attributes.generation != 0:
                    isUnique = True
                    if len(bestBots) == 0:
                        bestBots.append(object)
                    else:
                        for bot in bestBots:
                            if object.sameSpecies(bot):
                                isUnique = False
                                print("same species")
                                if object.total_rewards_collected >= bot.total_rewards_collected:
                                    bot = object
                                break
                        
                        if isUnique:
                            bestBots.append(object)
        if len(bestBots) == 0:
            print("no bots passed the conditions")
            return


        #record the results of the simulation
        bestbot = bestBots[0]
        for bot in bestBots:
            if bot.total_rewards_collected > bestbot.total_rewards_collected:
                bestbot = bot

            text = "The "+bot.attributes.colourHEX+" bot which colllected the most rewards was "+bot.attributes.name + " RPM: "+str(bot.total_rewards_collected/(bot.age/60.0))+" Gen: "+ str(bot.attributes.generation)+" with "+str(bot.total_rewards_collected)+" Max Speed: "+str(bot.attributes.maxSpeed)
            #show results to the screen
            print(text)
            bot.saveBrain('brains/'+bot.attributes.colourHEX+'starter_brain.txt')
            bot.attributes.save('attributes/'+bot.attributes.colourHEX+'starter_attributes.txt')
        
        with open("starting_species.txt","w") as specs:
            for bot in bestBots:
                specs.write(f"{bot.attributes.colourHEX},")

        text = "The absolute best was "+bestbot.attributes.colourHEX+" bot "+bestbot.attributes.name + " RPM: "+str(bestbot.total_rewards_collected/(bestbot.age/60.0))+" Gen: "+ str(bestbot.attributes.generation)+" with "+str(bestbot.total_rewards_collected)+" Max Speed: "+str(bestbot.attributes.maxSpeed)
        record = open("record.txt","a")
        record.write(text+"\n")
        record.close()
        #show results to the screen
        print(text)
        bestbot.saveBrain('brains/starter_brain.txt')
        bestbot.attributes.save('attributes/starter_attributes.txt')
        
             

def now():
    return time.time_ns()/10.0**9


def main():
    for x in range(3,8):
        bots_per_species = 10

        import bot
        import reward

        plane = world.World(5*x,5*x)
        simulator = Simulator(3,1.5,plane)

        simulator.addObject(reward.Reward(simulator))
        simulator.addObject(reward.Reward(simulator))
        #simulator.addObject(reward.Reward(simulator))

        with open("starting_species.txt") as ss:
            starting_species = ss.read().split(',')

        for species_name in starting_species:
            for i in range(bots_per_species):
                initial_bot = bot.Bot(simulator)

                initial_bot.net.load(fr"brains\{species_name}starter_brain.txt")
                #initial_bot.connectToBrain()
                initial_bot.attributes.load(fr"attributes\{species_name}starter_attributes.txt")

                initial_bot.attributes.name = "bot"+str(i)
                initial_bot.circleObject.colourHEX = initial_bot.attributes.colourHEX
                initial_bot.circleObject.changeColour()

                initial_bot.position[0] = plane.width/2.0 + plane.width*0.2*(random.random()*2-1)
                initial_bot.position[1] = plane.height/2.0 + plane.height*0.2*(random.random()*2-1)
                initial_bot.direction = 6.28 * random.random()

                if i >=5:
                    initial_bot.attributes.mutate()
                    initial_bot.circleObject.colourHEX = initial_bot.attributes.colourHEX
                    initial_bot.circleObject.changeColour()
                    for neuron in initial_bot.net.neurons:
                        neuron.location[0] = bot.Combine1(neuron.location[0], neuron.location[0],0,initial_bot.net.side_length)
                        neuron.location[1] = bot.Combine1(neuron.location[1], neuron.location[1],0,initial_bot.net.side_length)
                    
                initial_bot.connectToBrain()
                simulator.addObject(initial_bot)

        simulator.brainWindow.connected_brain = [bot.net for bot in simulator.simObjects if "bot" in bot.attributes.name][0]

        simulator.run()

        simulator.endOfSimulation()

if __name__ == "__main__":
    main()