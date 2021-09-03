#!/usr/bin/env python
# -*- coding: utf-8 -*-


from dynamixel_sdk import *  # Uses Dynamixel SDK library
import os


def _map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def angle_input(motor_id):
    InRange = False
    while not InRange:
        try:
            if motor_id == 0:
                goal_angle = int(input("Input the goal angle for the base motor in degree (0-360): "))
            elif motor_id == 1:
                goal_angle = int(input("Input the goal angle for the bicep motor in degree (0-360): "))
            else:
                goal_angle = int(input("Input the goal angle for the forearm motor in degree (0-360): "))
        except ValueError:
            print("Goal angle input needs to be an integer.")
            continue
        else:
            if (goal_angle < 0) or (goal_angle > 360):
                print("Goal angle is out of range (0-360). Retry.")
                InRange = False
            else:
                if motor_id == 0:
                    print("Goal angle input for the base motor is %2d" % (goal_angle))
                elif motor_id == 1:
                    print("Goal angle input for the bicep motor is %2d" % (goal_angle))
                else:
                    print("Goal angle input for the forearm motor is %2d" % (goal_angle))
                InRange = True
    return goal_angle


if os.name == 'nt':
    import msvcrt

    def getch():
        return msvcrt.getch().decode()
else:
    import sys
    import tty
    import termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


# ********* DYNAMIXEL Model definition *********
MY_DXL = 'X_SERIES'       # XM430


# Control table address for XM430
ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_POSITION = 116
ADDR_PRESENT_POSITION = 132
ADDR_PROFILE_VELOCITY = 112
# Refer to the Minimum Position Limit of product eManual
DXL_MINIMUM_POSITION_VALUE = 0
# Refer to the Maximum Position Limit of product eManual
DXL_MAXIMUM_POSITION_VALUE = 4095
BAUDRATE = 57600

# DYNAMIXEL Protocol Version (1.0 / 2.0)
PROTOCOL_VERSION = 2.0  # Turn into a list for each motor
# Factory default ID of all DYNAMIXEL is 1

DXL_ID = [0, 1, 2]  # Turn into a list for each motor
# ID 0 is base motor for this instance
# ID 1 and 2 is bicep and forearm motor for this instance

# Use the actual port assigned to the U2D2.
# ex) Windows: "COM*", Linux: "/dev/ttyUSB*", Mac: "/dev/tty.usbserial-*"
DEVICENAME = '/dev/ttyUSB0'  # All the motors share the same port

TORQUE_ENABLE = 1     # Value for enabling the torque
TORQUE_DISABLE = 0     # Value for disabling the torque
DXL_MOVING_STATUS_THRESHOLD = 20    # Dynamixel moving status threshold

device_index = 0
index = [0, 0, 0]
#dxl_goal_position = [DXL_MINIMUM_POSITION_VALUE, DXL_MAXIMUM_POSITION_VALUE]

# Initialize PortHandler instance
# Set the port path
# Get methods and members of PortHandlerLinux or PortHandlerWindows
# Since all motors share the same port, they share same portHandler
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
# Set the protocol version
# Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
# Since all motors use the same protocol, they share same packetHandler
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    getch()
    quit()

# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    getch()
    quit()

# Enable Dynamixel Torque
while device_index <= 2:
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(
        portHandler, DXL_ID[device_index], ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        print("Dynamixel", DXL_ID[device_index],
              "has been successfully connected")
    device_index += 1


# Set the profile velicity
goal_velocity = 20
device_index = 0
while device_index <= 2:
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(
        portHandler, DXL_ID[device_index], ADDR_PROFILE_VELOCITY, goal_velocity)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    device_index += 1


#------------------Start to execute motor rotation------------------------
while 1:
    device_index = 0
    print("Press any key to continue! (or press ESC to quit!)")
    if getch() == chr(0x1b):
        break

    base_motor_goal_degree = angle_input(0)
    #print("Base: " + str(base_motor_goal_degree))
    bicep_motor_goal_degree = angle_input(1)
    #print("Bicep: " + str(bicep_motor_goal_degree))
    forearm_motor_goal_degree = angle_input(2)
    #print("Forearm: " + str(forearm_motor_goal_degree))

    base_motor_position_input = _map(base_motor_goal_degree, 0, 360, 0, 4095)
    bicep_motor_position_input = _map(bicep_motor_goal_degree, 0, 360, 0, 4095)
    forearm_motor_position_input = _map(
        forearm_motor_goal_degree, 0, 360, 0, 4095)


    # Write base_motor_goal position
    #------------------------------------------------------------------------------------------------------------------------------------------------------
    device_index = 0
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_ID[device_index], ADDR_GOAL_POSITION, base_motor_position_input)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

    while 1:
        # Read present position
        dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, DXL_ID[device_index], ADDR_PRESENT_POSITION)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))

        print("[ID:%03d] GoalPos:%03d  GoalDeg:%03d  PresPos:%03d  PresDeg:%03d" %
              (DXL_ID[device_index], base_motor_position_input, base_motor_goal_degree, dxl_present_position, _map(dxl_present_position, 0, 4095, 0, 360)))

        if not abs(base_motor_position_input - dxl_present_position) > DXL_MOVING_STATUS_THRESHOLD:
            break
    #------------------------------------------------------------------------------------------------------------------------------------------------------  

    # Write bicep_motor_goal position
    #------------------------------------------------------------------------------------------------------------------------------------------------------ 
    device_index = 1
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_ID[device_index], ADDR_GOAL_POSITION, bicep_motor_position_input)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

    while 1:
        # Read present position
        dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, DXL_ID[device_index], ADDR_PRESENT_POSITION)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))

        print("[ID:%03d] GoalPos:%03d  GoalDeg:%03d  PresPos:%03d  PresDeg:%03d" %
              (DXL_ID[device_index], bicep_motor_position_input, bicep_motor_goal_degree, dxl_present_position, _map(dxl_present_position, 0, 4095, 0, 360)))

        if not abs(bicep_motor_position_input - dxl_present_position) > DXL_MOVING_STATUS_THRESHOLD:
            break
    #------------------------------------------------------------------------------------------------------------------------------------------------------ 


    # Write forearm_motor_goal position
    #------------------------------------------------------------------------------------------------------------------------------------------------------ 
    device_index = 2
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_ID[device_index], ADDR_GOAL_POSITION, forearm_motor_position_input)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

    while 1:
        # Read present position
        dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, DXL_ID[device_index], ADDR_PRESENT_POSITION)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))

        print("[ID:%03d] GoalPos:%03d  GoalDeg:%03d  PresPos:%03d  PresDeg:%03d" %
              (DXL_ID[device_index], forearm_motor_position_input, forearm_motor_goal_degree, dxl_present_position, _map(dxl_present_position, 0, 4095, 0, 360)))

        if not abs(forearm_motor_position_input - dxl_present_position) > DXL_MOVING_STATUS_THRESHOLD:
            break
    #------------------------------------------------------------------------------------------------------------------------------------------------------ 


# Disable Dynamixel Torque
device_index = 0
while device_index <= 2:
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(
        portHandler, DXL_ID[device_index], ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        device_index += 1
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
        device_index += 1
    else:
        print("Dynamixel", DXL_ID[device_index],
              "has been successfully disconnected")
        device_index += 1


# Close port
portHandler.closePort()
