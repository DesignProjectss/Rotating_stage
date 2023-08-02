from machine import Pin
from time import sleep

class Motor:
    def __init__(self, motorPins):
        self.motor_pins = motorPins
        # 28BY7-48 motor has 2048 steps in one revolution
        self.steps_per_rev = 2048 ## i.e we take 2048 steps to rotate 360deg

        self.last_step_i = 3 # initialize to 3 so next step would be 0th item of the sequence
        self.clk_sequence = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]
        self.anti_clk_sequence = [[0,0,0,1], [0,0,1,0], [0,1,0,0], [1,0,0,0]]

        self.moving = False #reject any command to rotate when a rotation is taking place

    def one_step(self, reverse):
        step = None

        next_step = 0 if self.last_step_i == 3 else self.last_step_i + 1
        if reverse:
            step = self.anti_clk_sequence[next_step]
        else:
            step = self.clk_sequence[next_step]

        if step is not None:
            for j in range(len(self.motor_pins)):
                self.motor_pins[j].value(step[j])
                sleep(0.001)

        self.last_step_i = next_step


    def move_one_step(self, reverse=False):
        if self.moving:
            print("An action is going on!")
            return

        self.moving = True

        self.one_step(reverse)

        self.moving = False


    def rotate_by(self, angle, reverse=False):
        # make it multiple of 45deg(i.e 45, 90, 180 etc)
        # - To prevent round error in calculating number of steps
        if self.moving:
            print("An action is going on!")
            return
        self.moving = True

        print(f"Rotating by: {angle}deg")

        steps_to_take = round((angle * self.steps_per_rev) / 360)
        for i in range(steps_to_take):
            self.one_step(reverse)

        self.moving = False

        print(f"Rotated {angle}deg in {steps_to_take}")
        print("\n-----------------------------\n")
