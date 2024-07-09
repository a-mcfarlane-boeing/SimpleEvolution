import time
import math
import brain

Max_turn_rate = math.pi/12 # degrees per second
Max_speed = 1 # units per second
Max_energy_loss_rate = 1 #units per second
Base_energy_loss_rate = 0.2 #units per second
Max_energy_reserve = 100
Max_view_distance = 20
Max_view_angle = math.pi/2

class Bot:
    """ Defines a Bot with all its attributes """
    def __init__(self,name = "exampleBot", max_speed=Max_speed,max_view_angle=Max_view_angle,max_energy=Max_energy_reserve):
        # bot attributes
        #self.brain = brain
        self.name = name
        self.max_speed = max_speed
        self.max_view_angle = max_view_angle
        self.max_view_distance = Max_view_distance
        self.max_energy = max_energy

        # bot internal variables
        self.energy_level = self.max_energy
        self.rewards_collected = 0

        # world variables
        self.simulation_time = 0
        self.time_current = 0
        self.time_last = 0
        self.time_interval = 0

        # bot enviromental variables
        self.position = [0,0] # x,y
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
        self.net = brain.Brain(51,10,5)

    def setAngularVelocity(self,a_velocity):
        self.angular_velocity_factor = a_velocity

    def setVelocity(self,velocity):
        self.velocity_factor = velocity

    def timeInterval(self):
        self.time_last = self.time_current
        self.time_current = self.simulation_time
        self.time_interval = (self.time_current - self.time_last)

    def simulate(self,simulation_time, x_pos, y_pos):
        # get the time
        self.simulation_time = simulation_time
        # determine the elapsed time
        self.timeInterval()
        # see the enviroment
        self.see(x_pos, y_pos)
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
        
        self.position_percent[0] = self.position[0] / 50
        self.position_percent[1] = self.position[0] / 50

    def think(self):
        # get inputs
        self.net.outputs["i0"] = self.energy_percent
        self.net.outputs["i1"] = self.position_percent[0]
        self.net.outputs["i2"] = self.position_percent[1]
        self.net.outputs["i3"] = self.view_angle_percent
        self.net.outputs["i4"] = self.view_distance_percent

        # think
        self.net.calculateOutputs()
        # assign to outputs
        self.angular_velocity_factor = (self.net.outputs["n50"]*2) - 1
        self.velocity_factor = (self.net.outputs["n10"]*2)-1
    
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

    def see(self, reward_pos_x, reward_pos_y):
        #determine the angle to the reward
        x_displacement = reward_pos_x - self.position[0]
        y_displacement = self.position[1] - reward_pos_y
        angle_to_reward = math.atan2(y_displacement, x_displacement)

        # find out where in the field of view it is
        # angle
        left_most_angle = self.direction - self.max_view_angle/2.0
        angle_from_left = angle_to_reward - left_most_angle

        self.view_angle_percent = angle_from_left / self.max_view_angle

        if self.view_angle_percent < 0 :
            self.view_angle_percent = 0
        elif self.view_angle_percent > 1 :
            self.view_angle_percent = 1
        
        #distance
        distance_to_reward = math.sqrt(x_displacement**2 + y_displacement**2)
        
        self.view_distance_percent = distance_to_reward / self.max_view_distance

        if self.view_distance_percent < 0 :
            self.view_distance_percent = 0
        elif self.view_distance_percent > 1 :
            self.view_distance_percent = 1

    def save_brain(self):
        self.net.summarise("brains/" + self.name + "_brain.txt")
    
    def breed(self):
        self.save_brain()

def main():
    robot = Bot()
    robot.see(6,-6)
    print(robot.view_angle_percent)

if __name__ == "__main__":
    main()
