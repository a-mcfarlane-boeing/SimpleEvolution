import bot
import time
import reward
import tkinter as tk

# Global Variables
world_width = 20
world_height = 20

pixels_per_unit = 10

window_width = world_width * pixels_per_unit
window_height = world_height * pixels_per_unit

frame_rate = 24.0
frame_interval = 1 / frame_rate

time_factor = 1

startingX = world_width/2
startingY = world_height/2

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
        canvas.create_line(i,0,i,window_height,fill='grey')
    i+=1

i=0
while i< window_height:
    if i%(pixels_per_unit*10) == 0:
        canvas.create_line(0,i,window_width,i,fill='grey')
    i+=1

#bots
number_of_bots = 10
bots = []
i = 0
while i < number_of_bots:
    bots.append(bot.Bot("bot"+str(i)))
    bots[i].position[0] = startingX
    bots[i].position[1] = startingY
    i+=1

exampleBot = bot.Bot("botE")
exampleBot.position[0] = startingX
exampleBot.position[1] = startingY
exampleBot.save_brain()

# create the circles to visualise the bots
robot_circles = []
i=0
while i < number_of_bots:
    robot_circles.append(canvas.create_oval(startingX,startingY,startingX+10,startingY+10,fill="yellow"))
    i+=1

bot = canvas.create_oval(startingX,startingY,startingX+10,startingY+10,fill='cyan')

#rewards
#create the cirlce for the reward
apple = reward.Reward(world_width-1,world_height-1, canvas ,pixels_per_unit)
#apple_visual = canvas.create_oval(apple.position[0], apple.position[1], apple.position[0]+10, apple.position[1]+10, fill="red")

# get the time when the program starts
Start_time = time.time_ns()
last_print_time = 0

while True:
    time_now = time.time_ns()
    elapsed_time = time_now - Start_time
    
    elapsed_time = (elapsed_time*time_factor)/10**9

    difference = elapsed_time - last_print_time

    i = 0
    while i <number_of_bots:
        bots[i].simulate(elapsed_time, apple.position[0], apple.position[1])

        # check if the bot has reached the boundry
        if bots[i].position[0] > world_width - 1:
            bots[i].position[0] = world_width - 1.5
        
        if bots[i].position[1] > world_height - 1:
            bots[i].position[1] = world_height - 1.5
        
        if bots[i].position[0] < 0:
            bots[i].position[0] = 0.5
        
        if bots[i].position[1] < 0:
            bots[i].position[1] = 0.5

        # check if the bot has reached a reward
        if apple.near(bots[i].position[0],bots[i].position[1]):

            bots[i].rewards_collected += 1
            bots[i].save_brain()

            if bots[i].energy_level < 90:
                bots[i].energy_level += 10
            else:
                bots[i].energy_level = 100

        i+=1

    exampleBot.simulate(elapsed_time, apple.position[0], apple.position[1])

    if difference >= frame_interval:
        last_print_time = elapsed_time

        i=0
        while i < number_of_bots:
            canvas.moveto(robot_circles[i], round(bots[i].position[0]*pixels_per_unit), round(bots[i].position[1]*pixels_per_unit))
            i +=1
        
        canvas.moveto(bot,round(exampleBot.position[0]*pixels_per_unit),round(exampleBot.position[1]*pixels_per_unit))
        
        # show the reward
        #canvas.moveto(apple_visual,round(apple.position[0]*pixels_per_unit),round(apple.position[1]*pixels_per_unit))

        text ="Energy: {:.2f} Velocity factor: {:2.3f} Sight neuron: {:2.3f} Position: x:{:.1f} y:{:.1f} Direction: {:1.2f} Rewards: {:2.0f} Time:{:3.0f}"
            
        print(text.format(bots[0].energy_percent, bots[0].velocity_factor, bots[0].net.outputs["i3"], bots[0].position[0], bots[0].position[1] , bots[0].direction, bots[0].rewards_collected, elapsed_time))

        window.update()


def breedBots(bot1,bot2, number_of_bots, bot_list):
    """ the bots dont need to be near one another, 
    they just need to have collected a reward and have enough energy"""
    
    number_of_bots += 1
    minimum_energy_level = 20
    energy_lost = 5

    if bot1.rewards_collected >= 1 and bot2.rewards_collected >= 1:
        if bot1.energy_level >= minimum_energy_level and bot2.energy_level >= minimum_energy_level:
            # the bots will breed under these conditions
            bot1.save_brain()
            bot2.save_brain()

            babyBot1 = bot.Bot("bot"+str(number_of_bots))
            net1 = brain.Brain(file_name = bot1.name +"_brain.txt")