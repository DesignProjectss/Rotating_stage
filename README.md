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

# Connecting from the FSM app to the Blender app

The process of achieving this is detailed here: https://gist.github.com/DraTeots/e0c669608466470baa6c.

## Linux Server

### Create virtual ports
- socat -d -d pty,rawer,echo=0 pty,rawer,echo=0
- 
### Connect network port to (virtual) serial port
- ser2net -d -C "7778:telnet:0:/dev/pts/2:115200 8DATABITS NONE 1STOPBIT remctl"

The other port is connected to the serial code of the app

## Linux Client

### Create virtual ports
- socat -d -d pty,rawer,echo=0 pty,rawer,echo=0

### Connect one of the serial ports to the network port
- socat /dev/pts/2,b115200,raw,echo=0 TCP:10.147.19.112:7778

The other port is connected to the serial code of the app

## STDIO to PTY or TCP
- socat STDIO /dev/pts/3,raw,echo=0,crlf

## Create a network between the server and the client using zerotier
- https://docs.zerotier.com/getting-started/getting-started/
