from math import sin, pi
from motor import Motor
from config import CURTAIN_PINS, DIVISIONS, STAGE_RADIUS, MOTOR_RADIUS
from cond import Condition

class Curtain():
    #  always note the units you're working with, rad, degree, m, cm
    motor = Motor(CURTAIN_PINS)
    angle_per_div = (2 * pi) / DIVISIONS
    secant_length = (2 * STAGE_RADIUS) * sin(angle_per_div / 2)
    motor_radius = MOTOR_RADIUS
    # angle_per_cm = 90.56604
    angle_per_cm = 90

    def __init__(self, motor_pins, divisions, stage_radius, motor_radius):
        # self.motor = Motor(motor_pins)
        # angle_per_div = (2 * pi) / divisions
        # self.secant_length = (2 * stage_radius) * sin(angle_per_div / 2)
        # self.motor_radius = motor_radius
        # # self.angle_per_cm = 90.56604
        # self.angle_per_cm = 90


        #test to see if this works
        # To get the angle the motor needs to move to move the curtain along the secant length
        # each curtain needs to move an angle of angle_per_secant / 2

        # I think this would work better when we know the motor radius
        self.angle_per_secant = (self.secant_length / motor_radius) * (180 / pi)


    @classmethod
    def close(cls):
        cls.open_to(cls.secant_length)
        print('curtain closed...')

    @classmethod
    def draw(cls):
        cls.open_to(cls.secant_length, reverse=True)
        print('curtain fully opened')

    @classmethod
    def open_to(cls, width, reverse=False):
        # Condition.change_curtain_done_state(False)

        print(f"{'Opening' if reverse else 'Closing'} by" + str(width))

        angle_to_move = width * cls.angle_per_cm

        print("Rotating by angle", angle_to_move)
        cls.motor.rotate_by(angle_to_move, reverse)

        Condition.change_curtain_done_state(True)



# Suggestions by Mr Eniola
# measure the circumference of the gear
# relate circumference to the angle of rotation

# you can rotate the gear maybe 4 times and measure the distance the belt travelled. Then use that estimate
# the distance covered by one rotation(i.e 360 deg)
