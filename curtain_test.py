from curtain import Curtain
from config import CURTAIN_PINS


if __name__ == "__main__":
    print("HEYYY")
    stage_curtain = Curtain(CURTAIN_PINS, 4, 15, 0.7)
    stage_curtain.open_to(1, True)
