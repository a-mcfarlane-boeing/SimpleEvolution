import bot
import time
import reward
import tkinter as tk
import random

# Global Variables
world_width = 50
world_height = 40
max_num_of_bots = 200

simulation_number = 2

number_of_bots = 100
total_number_of_bots = number_of_bots

pixels_per_unit = 15

window_width = world_width * pixels_per_unit
window_height = world_height * pixels_per_unit

frame_rate = 24.0
frame_interval = 1 / frame_rate


#time frame
time_factor = 3

hours = 0
minutes = 5
seconds = 0

time_limit = (hours*60*60 + minutes*60 + seconds)*time_factor

startingX = world_width/2
startingY = world_height/2

#breeding conditions
initiation_max_change = [0.1, 0.5]
breeding_max_change = [0.01, 0.05]
minimum_energy_level = 5
energy_lost = 3

# Create the main window
window = tk.Tk()
window.title("  Simple Evolution")
# Create canvas to show the environment
canvas = tk.Canvas(window, bg='green3', width=window_width, height=window_height)
canvas.pack()

#draw lines to indicate the units
i=0
while i< window_width:
    if i%pixels_per_unit == 0:
        canvas.create_line(i,0,i,window_height,fill='light grey')
    i+=1

i=0
while i< window_height:
    if i%pixels_per_unit == 0:
        canvas.create_line(0,i,window_width,i,fill='light grey')
    i+=1

i=0
while i< window_width:
    if i%(pixels_per_unit*10) == 0:
        canvas.create_line(i,0,i,window_height,fill='orange red')
    i+=1

i=0
while i< window_height:
    if i%(pixels_per_unit*10) == 0:
        canvas.create_line(0,i,window_width,i,fill='orange red')
    i+=1

#rewards
#create the cirlce for the reward
apple = reward.Reward(world_width,world_height, canvas ,pixels_per_unit)

#bots
bots = []
allBots = []
i = 0
while i < number_of_bots:
    bots.append(bot.Bot(name = "bot"+str(i), canvas= canvas, simulation_time = time.time_ns()))
    bots[i].net.loadBrain("brains/brain.txt")
    bots[i].load_attributes("attributes/starter_attributes.txt")
    bots[i].position[0] = startingX
    bots[i].position[1] = startingY
    bots[i].direction = 6.28 * random.random()
    i+=1

#bots[1].net.loadBrain("brains/smart_brain_1.txt")
#bots[1].net.loadBrain("brains/botE_brain.txt")

j=3
while j < number_of_bots:
    k=0
    while k < bots[-1].net.num_of_neurons:
        l=0
        new_weights = []
        while l < bots[-1].net.num_of_connections + 1:
            x = bots[0].net.neurons[k].weights[l]
            change = random.random() * 2 - 1
            difference = x - change
            if random.random() < (number_of_bots/(max_num_of_bots*2.0)):
                #mutation
                new_weights.append(x - initiation_max_change[1] * difference)
            else:
                new_weights.append(x - initiation_max_change[0] * difference)
            l+=1
        bots[j].net.neurons[k].weights = new_weights
        k+=1
    j+=1

# circle to indicate the winning bot
winning_circle = canvas.create_oval(0,0, 1 * 2 * pixels_per_unit, 1 * 2 * pixels_per_unit,fill="cyan")


# get the time when the program starts
Start_time = time.time_ns()
last_print_time = 0

while True:
    time_now = time.time_ns()
    real_elapsed_time = time_now - Start_time
    
    real_elapsed_time = real_elapsed_time/10**9

    simulation_elapsed_time = real_elapsed_time*time_factor

    difference = real_elapsed_time - last_print_time

    i = 0
    while i < number_of_bots:
        bots[i].simulate(simulation_elapsed_time, apple)

        # breed
        j=0
        while j < number_of_bots:
            if bots[i].breeding_points >= 1 and bots[i].energy_level >= minimum_energy_level and bots[i].time_since_last_child >= 10 and number_of_bots < max_num_of_bots and bots[i].age >=40:
                if bots[j].breeding_points >= 1 and bots[j].energy_level >= minimum_energy_level and bots[j].time_since_last_child >= 11 and bots[i].name != bots[j].name and number_of_bots < max_num_of_bots and bots[i].age >=40:
                      
                    # the bots will breed under these conditions
                    total_number_of_bots += 1
                    number_of_bots +=1

                    print(bots[i].name+" mated with "+bots[j].name+" to create bot"+str(total_number_of_bots))

                    bots[i].time_since_last_child=0
                    bots[j].time_since_last_child=0

                    bots[i].breeding_points -= 1
                    bots[j].breeding_points -= 1

                    bots[i].energy_level -= energy_lost
                    bots[j].energy_level -= energy_lost

                    if bots[i].total_rewards_collected < bots[j].total_rewards_collected:
                        bot1 = bots[i]
                        bot2 = bots[j]
                    else:
                        bot2 = bots[i]
                        bot1 = bots[j]
                    

                    newBot = bot.Bot(name = "bot"+str(total_number_of_bots-1), canvas = canvas, simulation_time = time_now)
                    newBot.position[0] = bot1.position[0]
                    newBot.position[1] = bot1.position[1]
                    newBot.direction = 6.28 * random.random()
                    newBot.simulation_time = time_now

                    if bot1.family_history != "None":
                        newBot.family_history = bot1.family_history +" "+str(simulation_number)+"~"+ bot1.name +"~" +str(bot1.generation)
                    else:
                        newBot.family_history = str(simulation_number)+"~"+ bot1.name +"~" +str(bot1.generation)

                    #newBot.net.loadBrain("brains/starter_brain.txt")
                        
                    k=0
                    #go through each neuron
                    while k < newBot.net.num_of_neurons:
                        l=0
                        new_weights = []
                        #replace each weight
                        while l < newBot.net.num_of_connections + 1:
                            x = bot1.net.neurons[k].weights[l]
                            y = bot2.net.neurons[k].weights[l]
                            difference = x - y
                            if random.random() < (number_of_bots/1000.0):
                                #mutation
                                difference = x - (random.random()*2 -1)
                                new_weights.append(x- breeding_max_change[1] * difference)
                            else:
                                new_weights.append(x - breeding_max_change[0] * difference)
                            l+=1
                        newBot.net.neurons[k].weights = new_weights
                        k+=1
                
                    if bot1.generation < bot2.generation:
                        newBot.generation = bot1.generation + 1
                    else:
                        newBot.generation = bot2.generation + 1
                
                    bots.append(newBot)
                    bots[-1].simulate(simulation_elapsed_time, apple)

            j+=1
        
        # check if the bot has reached the boundry
        boundry_damage = 8
        if bots[i].position[0] > world_width - 0.5:
            bots[i].energy_level -= boundry_damage
            bots[i].position[0] = world_width - 1
        
        if bots[i].position[1] > world_height - 0.5:
            bots[i].energy_level -= boundry_damage
            bots[i].position[1] = world_height - 1
        
        if bots[i].position[0] < 0.5:
            bots[i].energy_level -= boundry_damage
            bots[i].position[0] = 1
        
        if bots[i].position[1] < 0.5:
            bots[i].energy_level -= boundry_damage
            bots[i].position[1] = 1

        # check if the bot has reached a reward
        if apple.isNear(bots[i]) and bots[i].time_since_last_meal >= 20:
            bots[i].eat()
            #first gets two slices
            if apple.slices >=14:
                bots[i].eat()

            apple.consumed()

        #bot dies
        if bots[i].energy_level <= 0:
            allBots.append(bots[i])
            bots[i].hide_circle()
            bots.remove(bots[i])
            number_of_bots -= 1
        i+=1

    if difference >= frame_interval:
        last_print_time = real_elapsed_time

        i=0
        current_most_rewards = 0
        index = 0
        while i < number_of_bots:
            bots[i].move_circle()

            if bots[i].total_rewards_collected >= current_most_rewards:
                current_most_rewards = bots[i].total_rewards_collected
                index = i

            i += 1
        
        canvas.moveto(winning_circle, round((bots[index].position[0] - 1) * pixels_per_unit), round((bots[index].position[1] - 1) * pixels_per_unit))
        
        text ="Name: "+str(bots[index].name)+" Energy: {:3.0f} RF: {: 2.3f} Sight neuron: {:2.3f} Pos: x:{:.1f} y:{:.1f} Dir: {:1.2f} R: {:2.0f} BP: {:1.0f} G: {:2.0f} Sim Time: {:2.0f} Real Time: {:2.0f} {:3.0f}% NOB: {:3.0f}"
        print(text.format(bots[index].energy_level, bots[index].angular_velocity_factor, bots[index].net.outputs["i3"], bots[index].position[0], bots[index].position[1] , bots[index].direction, bots[index].total_rewards_collected, bots[index].breeding_points, bots[index].generation, simulation_elapsed_time, real_elapsed_time, (simulation_elapsed_time/(time_limit*1.0))*100, number_of_bots))



        # end of simulation conditions
        if number_of_bots <= 1 or simulation_elapsed_time >= time_limit:

            for bot in bots:   
                bot.age = simulation_elapsed_time - bot.birth_time
                allBots.append(bot)
            i=0
            max_carry_factor = 0
            index = 0
            while i < len(allBots):
                # the bot with the highest carry factor will go onto the next simulation
                #carry_factor = allBots[i].total_rewards_collected/(allBots[i].age*1.0)
                carry_factor = allBots[i].total_rewards_collected

                if carry_factor >= max_carry_factor and allBots[i].age >=100 and allBots[i].generation != 0:
                    max_carry_factor = carry_factor
                    print(allBots[i].name+ "  "+ str(allBots[i].total_rewards_collected) + " G: "+str(allBots[i].generation))
                    index = i
                i+=1
            record = open("record.txt","a")
            record.write("the bot which colllected the most rewards was "+allBots[index].name + " RPM: "+str(allBots[index].total_rewards_collected/(allBots[index].age/60.0))+" Gen: "+ str(allBots[index].generation)+" with "+str(allBots[index].total_rewards_collected)+"\n")
            record.close()
            print("the bot which colllected the most rewards was "+allBots[index].name + " RPM: "+str(allBots[index].total_rewards_collected/(allBots[index].age/60.0))+" Gen: "+ str(allBots[index].generation)+" with "+str(allBots[index].total_rewards_collected))
            allBots[index].save_brain('brains/starter_brain.txt')
            allBots[index].save_attributes('attributes/starter_attributes.txt')
            input("All the bots have died :( the maximum number of bots was " +str(total_number_of_bots))

        window.update()