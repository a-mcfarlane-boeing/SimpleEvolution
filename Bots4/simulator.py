import math
from os import path
import bot
import time
import reward
import random
import visualiser as vis
import brain_vis

num_of_simulations_total = 5
num_of_simulations = 0

hours = 0
minutes = 10
seconds = 0
#time frame
time_factor = 2.0

# Global Variables
# World
World_width = 100
World_height = 100
# Collisions
EnableCollisions = False
# Number of bots
Bots_per_square_unit = 5/100
Absolute_max_num_of_bots = 200

total_number_of_connections_per_bot = bot.Num_of_neurons*bot.Num_of_connections

max_num_of_connections = 25000

Absolute_max_num_of_bots = max_num_of_connections/total_number_of_connections_per_bot

Max_num_of_bots = min(World_width*World_height*Bots_per_square_unit,Absolute_max_num_of_bots)

Initial_number_of_bots = int(Max_num_of_bots*0.5)

frame_rate = 24.0
frame_interval = 1 / frame_rate

bot_radius = bot.Radius

def printBotDetails(bot):
    text ="Name: "+str(bot.name)+" |Energy: {:3.0f} |Brain outputs [vf,avf,e]: [{: 2.3f}, {: 2.3f}, {: 2.2f}] |Sight neuron: {:2.3f} |Pos: x:{:.1f} y:{:.1f} |Dir: {:1.2f} Rwds: {:2.0f} BP: {:1.0f} Gen: {:2.0f}"
    print(text.format(bot.energy_level, bot.velocity_factor, bot.angular_velocity_factor, bot.eat_action, bot.net.dict_all_values["i3"], bot.position[0], bot.position[1] , bot.direction, bot.total_rewards_collected, bot.breeding_points, bot.generation))

def printSimStatus():
    text ="Sim Time: {:2.0f} Real Time (s): {:2.0f}/"+str(real_time_limit)+" - {:3.0f}% NOB: {:3.0f}/{:3.0f}"
    print(text.format(simulation_elapsed_time, real_elapsed_time, (simulation_elapsed_time/(time_limit*1.0))*100, number_of_bots_alive,Max_num_of_bots))


def createBotDict(new_bot):
    """
    Returns a dictionary with a bot and a circle initialised in the visualiser
    """
    circle_object = visWin._createCircle(0,0,bot.Radius,new_bot.colour)
    return {"bot": new_bot,"circle_object":circle_object}

def botCollisionCheck(bot1:bot.Bot, bot2:bot.Bot):
    """
    This function checks if the two bots have overlapped eachother,
    if they have then the first bot will be bumped back from the second bot.
    """
    # make sure not checking that the bot is coliding with itself
    if bot1.name != bot2.name:
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


# makes so can run simulation multiple times
while num_of_simulations < num_of_simulations_total:
    

    number_of_bots_alive = Initial_number_of_bots
    total_number_of_bots = Initial_number_of_bots


    

    real_time_limit = hours*60*60 + minutes*60 + seconds

    time_limit = (hours*60*60 + minutes*60 + seconds)*time_factor

    startingX = World_width/2
    startingY = World_height/2

    #breeding conditions
    initiation_max_change = [0.5, 1]

    # list of all the bots that where generated, a bot is added when they die
    all_bots = []

    # create a visualiser
    visWin = vis.Display(World_width, World_height)

    #rewards
    #create the cirlce for the reward
    apple = reward.Reward(World_width,World_height)
    vis_apple = visWin._createCircle(apple.position[0],apple.position[1],reward.Radius,reward.Colour)

    # genereate the initial group of bots
    initialising_time = 0
    alive_bots = []
    i = 0
    while i < number_of_bots_alive:
        brainNum ="_yellow"
        colour = 'yellow'
        if i%2 == 0:
            brainNum = "_blue"
            colour = 'blue'

        initial_bot = bot.Bot(initialising_time,"bot"+str(i),world_width=World_width,world_height=World_height,colour=colour)

        alive_bots.append(createBotDict(initial_bot))

        alive_bots[i]["bot"].net.loadBrain("brains/starter_brain"+brainNum+".txt")
        alive_bots[i]["bot"].loadAttributes("attributes/starter_attributes"+brainNum+".txt")
        alive_bots[i]["bot"].position[1] = World_height/2.0 + World_height*0.1*(random.random()*2-1)
        alive_bots[i]["bot"].position[0] = World_width/2.0 + World_width*0.1*(random.random()*2-1)
        alive_bots[i]["bot"].direction = 6.28 * random.random()
        i+=1

    initial_generation = alive_bots[0]["bot"].generation

    # randomises the weights in the bots brains slightly
    # cycle through the bots
    # first 10 are left normal
    j=9
    while j < number_of_bots_alive:
        # cycle through the neurons
        k=0
        while k < alive_bots[-1]["bot"].net.num_of_neurons:
            # cycle through each connection
            l=0
            new_weights = []
            while l < alive_bots[-1]["bot"].net.num_of_connections + 1:
                x = alive_bots[0]["bot"].net.neurons[k].weights[l]
                change = random.random() * 2 - 1
                difference = x - change
                if random.random() < (number_of_bots_alive/(Max_num_of_bots*2.0)):
                    #mutation
                    new_weights.append(x - initiation_max_change[1] * difference)
                else:
                    new_weights.append(x - initiation_max_change[0] * difference)
                l+=1
            
            alive_bots[j]["bot"].net.neurons[k].setWeights(new_weights)
            k+=1
        j+=1



    # get the time when the program starts
    Start_time = time.time_ns()*1.0
    last_print_time = 0.0

    
    #create brain visualiser for the first bot
    brain_screen = brain_vis.Display(alive_bots[0]["bot"].net)

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
            
            alive_bots[i]["bot"].simulate(simulation_elapsed_time, apple)

            # cycle through all the other bots to interact with
            j=0
            while j < number_of_bots_alive:
                # see if there is room for new bots
                if number_of_bots_alive < Max_num_of_bots:
                    # attempt to breed
                    child_bot = alive_bots[i]["bot"].breed(alive_bots[j]["bot"], "bot"+str(total_number_of_bots+1),simulation_elapsed_time)

                    #check if breeding was successful
                    if child_bot != None:
                        total_number_of_bots += 1
                        number_of_bots_alive += 1
                        alive_bots.append(createBotDict(child_bot))
                
                

                #prevent from checking if coliding with itself
                if i != j and EnableCollisions:
                    botCollisionCheck(alive_bots[i]["bot"],alive_bots[j]["bot"])




                j+=1

            # check if the bot has reached the boundry
            boundry_damage = 8
            # Right boundry
            if alive_bots[i]["bot"].position[0] > World_width - bot_radius:
                alive_bots[i]["bot"].energy_level -= boundry_damage
                alive_bots[i]["bot"].position[0] = World_width - 1
            # Bottom boundry
            if alive_bots[i]["bot"].position[1] > World_height - bot_radius:
                alive_bots[i]["bot"].energy_level -= boundry_damage
                alive_bots[i]["bot"].position[1] = World_height - 1
            # Left boundry
            if alive_bots[i]["bot"].position[0] < bot_radius:
                alive_bots[i]["bot"].energy_level -= boundry_damage
                alive_bots[i]["bot"].position[0] = 1
            # Top boundry
            if alive_bots[i]["bot"].position[1] < bot_radius:
                alive_bots[i]["bot"].energy_level -= boundry_damage
                alive_bots[i]["bot"].position[1] = 1

            # bot attempts to eat the reward
            alive_bots[i]["bot"].eat(apple)


            #bot dies
            if alive_bots[i]["bot"].energy_level <= 0:
                all_bots.append(alive_bots[i]["bot"])
                visWin.deleteObject(alive_bots[i]["circle_object"])
                alive_bots.remove(alive_bots[i])
                number_of_bots_alive -= 1
            i+=1

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
            brain_screen.update()

            # end of simulation conditions---------------------------------------------------
            if number_of_bots_alive <= 1 or simulation_elapsed_time >= time_limit:
                #move rest of bots into the all bots list
                for bots in alive_bots:   
                    bots["bot"].time_since_birth = simulation_elapsed_time - bots["bot"].birth_time
                    all_bots.append(bots['bot'])
                
                print("all bots results:")
                for thisBot in all_bots:
                    print(thisBot.name+ "  Rewards collected: "+ str(thisBot.total_rewards_collected) + " Gen: "+str(thisBot.generation))

                #find the best bot (yellow)
                i=0
                max_carry_factor = 1
                max_age = 0
                index_yellow = -1
                while i < len(all_bots):
                    # the bot with the highest carry factor will go onto the next simulation
                    #carry_factor = all_bots[i].total_rewards_collected/(all_bots[i].time_since_birth*1.0)
                    carry_factor = all_bots[i].total_rewards_collected
                    if carry_factor >= max_carry_factor and all_bots[i].generation > initial_generation and all_bots[i].colour == "yellow":
                        max_carry_factor = carry_factor
                        index_yellow = i
                    i+=1

                i=0
                max_carry_factor = 1
                max_age = 0
                index_blue = -1
                while i < len(all_bots):
                    # the bot with the highest carry factor will go onto the next simulation
                    #carry_factor = all_bots[i].total_rewards_collected/(all_bots[i].time_since_birth*1.0)
                    carry_factor = all_bots[i].total_rewards_collected
                    if carry_factor >= max_carry_factor and all_bots[i].generation > initial_generation and all_bots[i].colour == "blue":
                        max_carry_factor = carry_factor
                        index_blue = i
                    i+=1
                
                #record the results of the simulation
                if index_yellow != -1:
                    record = open("record.txt","a")
                    record.write("the yellow bot which colllected the most rewards was "+all_bots[index_yellow].name + " RPM: "+str(all_bots[index_yellow].total_rewards_collected/(all_bots[index_yellow].time_since_birth/60.0))+" Gen: "+ str(all_bots[index_yellow].generation)+" with "+str(all_bots[index_yellow].total_rewards_collected)+" Max Speed: "+str(all_bots[index_yellow].max_speed)+"\n")
                    record.close()
                    #show results to the screen
                    print("the yellow bot which colllected the most rewards was "+all_bots[index_yellow].name + " RPM: "+str(all_bots[index_yellow].total_rewards_collected/(all_bots[index_yellow].time_since_birth/60.0))+" Gen: "+ str(all_bots[index_yellow].generation)+" with "+str(all_bots[index_yellow].total_rewards_collected))
                    all_bots[index_yellow].saveBrain('brains/starter_brain_yellow.txt')
                    all_bots[index_yellow].saveAttributes('attributes/starter_attributes_yellow.txt')
                    #save the second best bot
                else:
                    print("no yellow bots passed the initial requirements for improvement")

                if index_blue != -1:
                        print("the blue bot which colllected the most rewards was "+all_bots[index_blue].name + " RPM: "+str(all_bots[index_blue].total_rewards_collected/(all_bots[index_blue].time_since_birth/60.0))+" Gen: "+ str(all_bots[index_blue].generation)+" with "+str(all_bots[index_blue].total_rewards_collected))
                        all_bots[index_blue].saveBrain('brains/starter_brain_blue.txt')
                        all_bots[index_blue].saveAttributes('attributes/starter_attributes_blue.txt')
                
                print("End of simulation, the total number of bots was " +str(total_number_of_bots))
                sim_status = False


    num_of_simulations +=1

print("Holding...")
input('Press any button to exit-')