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
        # self.angle_per_cm = 90.56604
        self.angle_per_cm = 90


        #test to see if this works
        # To get the angle the motor needs to move to move the curtain along the secant length
        # each curtain needs to move an angle of angle_per_secant / 2

        # I think this would work better when we know the motor radius
        self.angle_per_secant = (self.secant_length / motor_radius) * (180 / pi)


    def close(self):
        # self.motor.rotate_by(self.angle_per_secant / 2, reverse=True)
        self.open_to(self.secant_length, reverse=True)
        print('curtain closed...')

    def draw(self):
        # self.motor.rotate_by(self.angle_per_secant / 2)
        self.open_to(self.secant_length)
        print('curtain fully opened')

    def open_to(self, width, reverse=False):
        print(f"{'Closing' if reverse else 'Opening'} by" + str(width))
        angle_to_move = width * self.angle_per_cm
        print("Opening by angle", angle_to_move)
        self.motor.rotate_by(angle_to_move, reverse)

# Suggestions by Mr Eniola
# measure the circumference of the gear
# relate circumference to the angle of rotation

# you can rotate the gear maybe 4 times and measure the distance the belt travelled. Then use that estimate
# the distance covered by one rotation(i.e 360 deg)
