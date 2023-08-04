class Curtain():
    def __init__():
        pass
    
    def close():
        print('curtain closed...')

    def draw():
        print('curtain fully opened')
    
    def open_to(width):
        pass
    

from math import sin, pi
from motor import Motor
class CurtainNew():
    #  always note the units you're working with, rad, degree, m, cm
    def __init__(self, motor_pins, divisions, stage_radius, motor_radius):
        self.motor = Motor(motor_pins)
        angle_per_div = (2 * pi) / divisions
        self.secant_length = (2 * stage_radius) * sin(angle_per_div / 2)
        self.motor_radius = motor_radius

        #test to see if this works
        # To get the angle the motor needs to move to move the curtain along teh secant length
        # each curtain needs to move an angle of angle_per_secant / 2
        self.angle_per_secant = (self.secant_length / motor_radius) * (180 / pi)


    def close(self):
        print('curtain closed...')
        self.motor.rotate_by(self.angle_per_secant / 2, reverse=True)

    def draw(self):
        print('curtain fully opened')
        self.motor.rotate_by(self.angle_per_secant / 2)

    def open_to(self, width, reverse=False):
        print("Moving by" + str(width))
        angle_to_move = (width / self.motor_radius) * (180 / pi)
        self.motor.rotate_by(angle_to_move, reverse)

