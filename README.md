# FSM Rotating Stage

## A rotating stage for Theather Art Department

### Features are:
- sectors on the stage are determined during the stage setup
  - the possible divisions are 2,3 and 4 sectors
  - sectors are numbered clockwisely and referenced to the electrical motor's starting point/position
  - should dynamically create FSM states based on the number of stage divisions 
- it is possible to rotate in all directions
- stage is maually controlled or synced with time and events garnered from the play scripts
- finds shortest path to the sector of choice
- two halfs of curtains are controlled in sync with the stage
- stage rotations are done to align/limit the view of the audience to a sector with the aid of the curtains
- rotation value is linked to the number of divisions and a 0 degree reference point
- motor to be used should be able to orient itself in space, i.e be able to know its angular position at any given time

