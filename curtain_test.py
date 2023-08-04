from curtain import CurtainNew
from config import PINS


if __name__ == "__main__":
    print("HEYYY")
    stage_curtain = CurtainNew(PINS, 4, 15, 0.7)
    stage_curtain.open_to(100)
