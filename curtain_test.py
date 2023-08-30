from curtain import Curtain
from config import CURTAIN_PINS, MOTOR_PINS
from motor import Motor

motor = Motor(MOTOR_PINS)

if __name__ == "__main__":
    print("HEYYY")
    stage_curtain = Curtain(CURTAIN_PINS, 4, 15, 0.7)
#     stage_curtain.open_to(10, True)

    stage_curtain.open_to(1, True)
    #motor.rotate_by(10)
    #print("HEYYY", motor.rotate_by)

