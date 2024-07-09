import time
import math
import brain
import tkinter as tk

Max_turn_rate = math.pi/2 # degrees per second
Max_speed = 3 # units per second
Max_energy_loss_rate = 0.4 #units per second
Base_energy_loss_rate = 0.3 #units per second
Max_energy_reserve = 100
Max_view_distance = 20
Max_view_angle = math.pi/2.0
Breed_timer = 5 #seconds
pixels_per_unit = 7
radius = 0.5 # unit

world_width = 80
world_height = 80

class Bot:
    """ Defines a Bot with all its attributes """
    def __init__(self, canvas, simulation_time, name = "exampleBot", max_speed=Max_speed,max_view_angle=Max_view_angle,max_energy=Max_energy_reserve):
        # bot attributes
        #self.brain = brain
        self.name = name
        self.max_speed = max_speed
        self.max_view_angle = max_view_angle
        self.max_view_distance = Max_view_distance
        self.max_energy = max_energy
        self.canvas = canvas

        # bot internal variables
        self.energy_level = self.max_energy
        self.breeding_points = 0
        self.total_rewards_collected = 0
        self.time_since_last_child = 0.0
        self.time_since_last_meal = 0.0
        self.generation = 0

        # world variables
        self.simulation_time = simulation_time
        self.birth_time = -1
        self.age = 0
        self.time_current = 0.0
        self.time_last = 0.0
        self.time_interval = 0.0
        #self.timeInterval(simulation_time)

        # bot enviromental variables
        self.position = [5,5] # x,y
        self.direction = 0.0 # angle from x axis, anti-clockwise

        # outputs from the brain
        self.velocity_factor = 0 # -1 to 1
        self.angular_velocity_factor = 0 # -1 to 1, anti & clockwise
    
        # inputs to brain
        self.energy_percent = 1
        self.view_angle_percent = 0
        self.view_distance_percent = 0
        self.direction_percent = 0
        self.position_percent = [0,0]

        #brain
        self.net = brain.Brain(100,5,7)

        #circle
        self.robot_circle = canvas.create_oval(0,0, radius * 2 * pixels_per_unit, radius * 2 * pixels_per_unit,fill="yellow")

    def setAngularVelocity(self,a_velocity):
        self.angular_velocity_factor = a_velocity

    def setVelocity(self,velocity):
        self.velocity_factor = velocity

    def timeInterval(self, simulation_time):
        if self.birth_time == -1:
            self.birth_time = simulation_time
        self.simulation_time = simulation_time - self.birth_time
        self.time_last = self.time_current
        self.time_current = self.simulation_time
        self.time_interval = (self.time_current - self.time_last)
        self.time_since_last_child += self.time_interval
        self.time_since_last_meal += self.time_interval
        self.age += self.time_interval

    def simulate(self,simulation_time, reward):
        # determine the elapsed time
        self.timeInterval(simulation_time)
        # see the enviroment
        self.see(reward)
        # run calculations through the brain
        self.think()
        # move bot accoringly
        self.move()
        # calculate energy consumption
        self.calculate_energy()

    def move(self):
        # find out the direction which the bot is facing (added onto the current direction)
        self.direction += self.angular_velocity_factor*Max_turn_rate*self.time_interval
        self.direction = self.direction%(2*math.pi)
        # find out how far the bot has traveled
        displacement = self.velocity_factor*self.max_speed*self.time_interval
        # find the displacement along the axis
        x_displacement = math.cos(self.direction)*displacement
        y_displacement = -math.sin(self.direction)*displacement
        # update the position
        if self.energy_percent !=0:
            self.position = [self.position[0]+x_displacement,self.position[1]+y_displacement]
        
        self.position_percent[0] = self.position[0] / world_width
        self.position_percent[1] = self.position[0] / world_height

    def think(self):
        # get inputs
        self.net.outputs["i0"] = self.energy_percent
        self.net.outputs["i1"] = self.position_percent[0]
        self.net.outputs["i2"] = self.position_percent[1]
        self.net.outputs["i3"] = self.view_angle_percent
        self.net.outputs["i4"] = self.view_angle_percent % 0.1
        self.net.outputs["i5"] = self.view_distance_percent
        self.net.outputs["i6"] = self.view_distance_percent % 0.1
        
        # think
        self.net.calculateOutputs()
        # assign to outputs
        self.angular_velocity_factor = (self.net.outputs["n9"]*2) - 1
        self.velocity_factor = (self.net.outputs["n4"]*2)-1
    
    def calculate_energy(self):
        # how much energy was used
        energy_consumption = self.max_speed * abs(self.velocity_factor) * Max_energy_loss_rate * self.time_interval
        # take from resoviour
        self.energy_level -= energy_consumption + Base_energy_loss_rate*self.time_interval
        #
        if self. energy_level < 0:
            self.energy_level = 0
            # bot should die here !!!
            pass
        self.energy_percent = self.energy_level/self.max_energy

    def see(self, obj):
        #determine the angle to the reward
        x_displacement = obj.position[0] - self.position[0]
        y_displacement = self.position[1] - obj.position[1]
        angle_to_reward = math.atan2(y_displacement, x_displacement)

        # find out where in the field of view it is
        #angle
        angle_to_turn_to_reward = angle_to_reward - self.direction
        if angle_to_turn_to_reward > math.pi:
            angle_to_turn_to_reward = -2*math.pi + angle_to_turn_to_reward
        elif angle_to_turn_to_reward < - math.pi:
            angle_to_turn_to_reward = 2*math.pi + angle_to_turn_to_reward
        
        angle_factor = abs(angle_to_turn_to_reward / (self.max_view_angle/2.0))

        if angle_factor > 1:
            angle_factor=1
        
        self.view_angle_percent = 1.0-angle_factor
            
        
        #distance
        distance_to_reward = math.sqrt(x_displacement**2 + y_displacement**2)
        
        self.view_distance_percent = distance_to_reward / self.max_view_distance

        if self.view_distance_percent < 0 :
            self.view_distance_percent = 0
        elif self.view_distance_percent > 1 :
            self.view_distance_percent = 1

    def save_brain(self,file_location = None):
        if file_location == None:
            self.net.summarise("brains/" + self.name+"_brain.txt")
        else:
            self.net.summarise(file_location)
    
    def save_attributes(self):
        attributeFile = open("attributes/"+self.name+"_attributes.txt","w")
        
        attributeFile.write("Name: "+self.name+"\n")
        attributeFile.write("Generation: "+self.generation+"\n")

        attributeFile.close()
    
    def breed(self):
        pass
    
    def move_circle(self):
        self.canvas.moveto(self.robot_circle, round((self.position[0] - radius) * pixels_per_unit), round((self.position[1] - radius) * pixels_per_unit))

    def hide_circle(self):
        self.canvas.moveto(self.robot_circle, -30, -30)

    def eat(self):
        energy_boost = 60
        if self.energy_level < self.max_energy - energy_boost:
            self.energy_level += energy_boost
        else:
            self.energy_level = self.max_energy
        
        self.max_energy -= 1

        self.total_rewards_collected += 1
        self.breeding_points += 2
        self.time_since_last_meal = 0

def main():

    window_width = 100
    window_height = 100

    startingX = 45
    startingY = 45

    # Create the main window
    window = tk.Tk()
    window.title("  Bot Preview")
    # Create canvas to show the environment
    Canvas = tk.Canvas(window, bg='green3', width=100, height=100)
    Canvas.pack()
    
    robot = Bot(canvas=Canvas)
    robot.move_circle()
    robot.save_brain()
    reward = "something"
    reward.position= [6,6]
    robot.see(reward)
    print(robot.view_angle_percent)

    window.mainloop()

if __name__ == "__main__":
    main()