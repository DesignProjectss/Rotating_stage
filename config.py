from machine import Pin

M_IN1 = Pin(26,Pin.OUT)
M_IN2 = Pin(25,Pin.OUT)
M_IN3 = Pin(33,Pin.OUT)
M_IN4 = Pin(32,Pin.OUT)

MOTOR_PINS = [M_IN1, M_IN2, M_IN3, M_IN4]

C_IN1 = Pin(5, Pin.OUT)
C_IN2 = Pin(18, Pin.OUT)
C_IN3 = Pin(19, Pin.OUT)
C_IN4 = Pin(21, Pin.OUT)

CURTAIN_PINS = [C_IN1, C_IN2, C_IN3, C_IN4]

STAGE_RADIUS = 8 # unit = cm
MOTOR_RADIUS = 2 # unit = cm

DIVISIONS = 4
