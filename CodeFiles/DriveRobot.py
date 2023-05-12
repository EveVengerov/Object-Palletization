
from pyfirmata import Arduino, SERVO
from time import sleep

port = 'COM9'
board = Arduino(port)
pinJaw = 5

pin5 = 6
pin4 = 7
pin3 = 8
pin2 = 9
pin1 = 10

board.digital[pin1].mode = SERVO
board.digital[pin2].mode = SERVO
board.digital[pin3].mode = SERVO
board.digital[pin4].mode = SERVO
board.digital[pin5].mode = SERVO
board.digital[pinJaw].mode = SERVO

pin = [pin1, pin2, pin3, pin4, pin5, pinJaw]

station_config = [68, 89, 179, 93, 0, 110]
station_config2 = [68, 85, 150, 93, 0, 110]

nextTarget = [92, 57, 141, 95, 0, 110]

home_config = [90, 110, 110, 90, 90, 20]

for i in range(0, 5):
    board.digital[pin[i]].write(home_config[i])

jaw_open = 110
jaw_close = 20


def getTargetConfig(ik):
    target_config = [0, 0, 0, 0, 0, 0]

    for i in range(0, 4):
        target_config[i] = int(ik[i+1].item()*180/3.14 + 90 ) #  adding an offset of 90 degrees to account for servo motor angles
    target_config[1] = target_config+20
    target_config[2] = target_config+20

    target_config[5] = jaw_open
    return target_config


def rotateRobot(pin1, pin2, pin3, pin4, pin5, pinJaw, local_target_config, local_current_config, move_speed = 3):
    delay = move_speed/5
    pin = [pin1, pin2, pin3, pin4, pin5]
    while True:
        for c in range(0, 5):
            print(c)
            if local_current_config[c] < local_target_config[c]:
                for i in range(local_current_config[c], local_target_config[c]):
                    print("Status of configuration of : %s " % [pin[c], i])
                    rotateServo(pin[c], i)
            else:
                for i in range(local_current_config[c], local_target_config[c], -1):
                    print("Status of configuration of: %s " % [pin[c], i])
                    rotateServo(pin[c], i)
            print(c)
        break

def returnHome(pin1, pin2, pin3, pin4, pin5, pinJaw, local_target_config, local_current_config, move_speed = 3):
    delay = move_speed/5
    pin = [pin1, pin2, pin3, pin4, pin5]
    while True:
        for c in range(4, 0,-1):
            print(c)
            if local_current_config[c] < local_target_config[c]:
                for i in range(local_current_config[c], local_target_config[c]):
                    print("Status of configuration of : %s " % [pin[c], i])
                    rotateServo(pin[c], i)
            else:
                for i in range(local_current_config[c], local_target_config[c], -1):
                    print("Status of configuration of: %s " % [pin[c], i])
                    rotateServo(pin[c], i)
            print(c)
        break

def jawNext(status, pinjaw):
    if  status == 1:
        for i in range(20,jaw_open):
            rotateServo(pinJaw, i)
            sleep(0.015)
    elif status == -1:
        for i in range(jaw_open,jaw_close,-1):
            rotateServo(pinJaw, i)
            sleep(0.015)

def rotateServo(pin, angle, delay=0.015):
    board.digital[pin].write(angle)
    sleep(delay)


def drive2Position(target_config):
    current_config = home_config

    print("Current Configuration in degrees: %s " % [configcurr for configcurr in current_config[:]])
    print("Target Configuration in degrees: %s " % [config for config in target_config[:]])

    jawNext(1,pinJaw) #jaw open
    rotateRobot(pin1, pin2, pin3, pin4, pin5, pinJaw, target_config, current_config)
    jawNext(-1,pinJaw) #jawclose
    print("Trajectory Completed")


    current_config = target_config

    print("Returning to Home Configuration...")
    sleep(1)
    # jawNext(-1,pinJaw)
    returnHome(pin1, pin2, pin3, pin4, pin5, pinJaw, home_config, current_config)
    current_config = home_config


