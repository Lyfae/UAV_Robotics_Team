#!/usr/bin/env python
# -*- coding: utf-8 -*-


from dynamixel_sdk import *  # Uses Dynamixel SDK library
import os

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


def _map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

#Checks whether the given angles are within a range of 0-360 degrees. If yes, then valid_angle_array = 1, otherwise 0
def angle_input(angle_values):
    angle_index = 0
    valid_angle_array = [0, 0, 0]
    while angle_index <= 2:
        if (angle_values[angle_index] < 0) or (angle_values[angle_index] > 360):
            print("Goal angle %03d for Dynamixel ID:%03d is out of range (0-360)" % (angle_values[angle_index], DXL_ID[angle_index]))
            valid_angle_array[angle_index] = 0
            angle_index += 1
        else:
            print("Goal angle %03d for Dynamixel ID:%03d is valid" % (angle_values[angle_index], DXL_ID[angle_index]))
            valid_angle_array[angle_index] = 1
            angle_index += 1
    return (valid_angle_array)

#Initializes all the motors
def portInitialization(portname, baudrate, baseID, bicepID, forearmID):
    # Use the actual port assigned to the U2D2.
    # ex) Windows: "COM*", Linux: "/dev/ttyUSB*", Mac: "/dev/tty.usbserial-*"
    global DEVICENAME
    DEVICENAME = portname  # All the motors share the same port
    global PROTOCOL_VERSION
    PROTOCOL_VERSION = 2
    # Initialize PortHandler instance and PacketHandler instance
    global portHandler
    portHandler = PortHandler(DEVICENAME)
    global packetHandler
    packetHandler = PacketHandler(PROTOCOL_VERSION)
    device_index = 0

    if portHandler.openPort():
        print("Succeeded to open the port")
    else:
        print("Failed to open the port")
        print("Press any key to terminate...")
        getch()
        quit()

    global BAUDRATE
    BAUDRATE = baudrate
    # Set port baudrate
    if portHandler.setBaudRate(BAUDRATE):
        print("Succeeded to change the baudrate")
    else:
        print("Failed to change the baudrate")
        print("Press any key to terminate...")
        getch()
        quit()

    # Set memory address for Torque Enable
    global ADDR_TORQUE_ENABLE
    ADDR_TORQUE_ENABLE = 64
    TORQUE_ENABLE = 1

    # Set the motor ID for each dynamixel
    global DXL_ID
    DXL_ID = [baseID, bicepID, forearmID]
    # ID 0 is base motor for this instance
    # ID 1 and 2 is bicep and forearm motor for this instance

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

def dxlPresAngle():
    ADDR_PRESENT_POSITION = 132
    dxl_present_position = [0, 0, 0]
    dxl_present_angle = [0, 0, 0]

    device_index = 0
    while device_index <= 2:
        dxl_present_position[device_index], dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(
            portHandler, DXL_ID[device_index], ADDR_PRESENT_POSITION)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
        device_index += 1

    device_index = 0
    while device_index <= 2:
        dxl_present_angle[device_index] = _map(dxl_present_position[device_index], 0, 4095, 0, 360)
        device_index += 1

    device_index = 0
    while device_index <= 2:
        print("[ID:%03d] PresPos:%03d  PresDeg:%03d" %
            (DXL_ID[device_index], dxl_present_position[device_index], dxl_present_angle[device_index]))
        device_index += 1
    return (dxl_present_angle)

def dxlSetVelo(vel_array):
    global ADDR_PROFILE_VELOCITY
    ADDR_PROFILE_VELOCITY = 112

    device_index = 0
    while device_index <= 2:
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(
        portHandler, DXL_ID[device_index], ADDR_PROFILE_VELOCITY, vel_array[device_index])
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
        else:
            if device_index == 0:
                #print('The velocity of base DXL with ID %03d is sucessfully set to %03d' % (DXL_ID[device_index], vel_array[device_index]))
                print("[ID:%03d]  Base Velocity Sucessfully Set To: %03d" %
                    (DXL_ID[device_index], vel_array[device_index]))
            elif device_index == 1:
                #print('The velocity of bicep DXL with ID %03d is sucessfully set to %03d' % (DXL_ID[device_index], vel_array[device_index]))
                print("[ID:%03d]  Bicep Velocity Sucessfully Set To: %03d" %
                    (DXL_ID[device_index], vel_array[device_index]))
            else:
                #print('The velocity of forearm DXL with ID %03d is sucessfully set to %03d' % (DXL_ID[device_index], vel_array[device_index]))
                print("[ID:%03d]  Bicep Velocity Sucessfully Set To: %03d" %
                    (DXL_ID[device_index], vel_array[device_index]))
        device_index += 1

def dxlGetVelo():
    global ADDR_PROFILE_VELOCITY
    ADDR_PROFILE_VELOCITY = 112
    dxl_present_velocity = [0, 0, 0]

    device_index = 0
    while device_index <= 2:
        dxl_present_velocity[device_index], dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(
            portHandler, DXL_ID[device_index], ADDR_PROFILE_VELOCITY)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
        else:
            if device_index == 0:
                #print('The current velocity of base DXL with ID %03d is: %03d' % (DXL_ID[device_index], dxl_present_velocity[device_index]))
                print("[ID:%03d]  Current Base Velocity: %03d" %
                    (DXL_ID[device_index], dxl_present_velocity[device_index]))
            elif device_index == 1:
                #print('The current velocity of bicep DXL with ID %03d is: %03d' % (DXL_ID[device_index], dxl_present_velocity[device_index]))
                print("[ID:%03d]  Current Bicep Velocity: %03d" %
                    (DXL_ID[device_index], dxl_present_velocity[device_index]))
            else:
                #print('The current velocity of forearm DXL with ID %03d is: %03d' % (DXL_ID[device_index], dxl_present_velocity[device_index]))
                print("[ID:%03d]  Current Forearm Velocity: %03d" %
                    (DXL_ID[device_index], dxl_present_velocity[device_index]))

        device_index += 1
    return (dxl_present_velocity)

def motorRunWithInputs(angle_inputs):
    global ADDR_GOAL_POSITION
    ADDR_GOAL_POSITION = 116 #Address of goal position

    global ADDR_PRESENT_POSITION
    ADDR_PRESENT_POSITION = 132 #Address of present position

    global DXL_MOVING_STATUS_THRESHOLD
    DXL_MOVING_STATUS_THRESHOLD = 10    # Dynamixel moving status threshold

    global LEN_GOAL_POSITION
    LEN_GOAL_POSITION = 4 #Byte Length of goal position

    global LEN_PRESENT_POSITION
    LEN_PRESENT_POSITION = 4 #Byte length of present position

    #Format is [base, bicep, forearm]
    dxl_goal_angle = angle_inputs
    dxl_goal_inputs = [0, 0, 0]
    dxl_present_position = [0, 0, 0]
    dxl_present_angle = [0, 0, 0]
    dxl_end_position = [0, 0, 0]
    dxl_end_angle = [0, 0, 0]
    dxl_addparam_result = [0, 0, 0]
    dxl_getdata_result = [0, 0, 0]
    index = [0, 0, 0]

    #Initialization for simultaneous movement of bicep and forearm motors
    motor_sync_write = GroupSyncWrite(portHandler, packetHandler, ADDR_GOAL_POSITION, LEN_GOAL_POSITION)
    motor_sync_read = GroupSyncRead(portHandler, packetHandler, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)

    # ------------------Start to execute motor rotation------------------------

    #Create parameter storage for bicep and forearm motors' present position value
    device_index = 1
    while device_index <= 2:
        dxl_addparam_result = motor_sync_read.addParam(DXL_ID[device_index])
        if dxl_addparam_result != True:
            print("[ID:%03d] groupSyncRead addparam failed" % DXL_ID[device_index])
            quit()
        device_index += 1

    while 1:
        device_index = 0
        print("Press any key to continue! (or press ESC to quit!)")
        if getch() == chr(0x1b):
            break

        valid_angle_array = angle_input(angle_inputs)
        print(valid_angle_array)

        #Convert angle inputs into step units for movement
        device_index = 0
        while device_index <= 2:
            dxl_goal_inputs[device_index] = _map(
                dxl_goal_angle[device_index], 0, 360, 0, 4095)
            device_index += 1

        print("The position inputs for the base, bicep, and forearm are: ", dxl_goal_inputs)
        print("The degree inputs for the base, bicep, and forearm are: ", dxl_goal_angle)

        # Base Motor Procedure
        # ------------------------------------------------------------------------------------------------------------------------------------------------------
        #Write goal position for base motor
        device_index = 0
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(
            portHandler, DXL_ID[device_index], ADDR_GOAL_POSITION, dxl_goal_inputs[device_index])
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))

        #Read position for base motor
        dxl_end_position[device_index], index[device_index] = motor_check(device_index, dxl_goal_inputs[device_index])
        dxl_end_angle[device_index] = _map(dxl_end_position[device_index], 0, 4095, 0, 360)

        # ------------------------------------------------------------------------------------------------------------------------------------------------------

        # Bicep and forearm procedure
        # ------------------------------------------------------------------------------------------------------------------------------------------------------

        #Allocate goal position values into 4-byte array for bicep and forearm motors. Dynamixel motors use either 2-bytes or 4-bytes
        device_index = 1
        param_goal_bicep_position = [DXL_LOBYTE(DXL_LOWORD(dxl_goal_inputs[device_index])), DXL_HIBYTE(DXL_LOWORD(dxl_goal_inputs[device_index])),DXL_LOBYTE(DXL_HIWORD(dxl_goal_inputs[device_index])), DXL_HIBYTE(DXL_HIWORD(dxl_goal_inputs[device_index]))]
        device_index += 1
        param_goal_forearm_position = [DXL_LOBYTE(DXL_LOWORD(dxl_goal_inputs[device_index])), DXL_HIBYTE(DXL_LOWORD(dxl_goal_inputs[device_index])),DXL_LOBYTE(DXL_HIWORD(dxl_goal_inputs[device_index])), DXL_HIBYTE(DXL_HIWORD(dxl_goal_inputs[device_index]))]

        #Add goal position input values of bicep and forearm motors to Syncwrite parameter storage
        device_index = 1
        dxl_addparam_result = motor_sync_write.addParam(DXL_ID[device_index], param_goal_bicep_position)
        if dxl_addparam_result != True:
            print("[ID:%03d] groupSyncWrite addparam failed" % DXL_ID[device_index])
            quit()
        device_index += 1

        dxl_addparam_result = motor_sync_write.addParam(DXL_ID[device_index], param_goal_forearm_position)
        if dxl_addparam_result != True:
            print("[ID:%03d] groupSyncWrite addparam failed" % DXL_ID[device_index])
            quit()

        #Syncwrite goal position to bicep and forearm motors
        dxl_comm_result = motor_sync_write.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))

        #Clear syncwrite parameter storage
        motor_sync_write.clearParam()

        #Read bicep motor position
        device_index = 1
        dxl_end_position[device_index], index[device_index] = motor_check(device_index, dxl_goal_inputs[device_index])
        dxl_end_angle[device_index] = _map(dxl_end_position[device_index], 0, 4095, 0, 360)

        #Read forearm motor position
        device_index = 2
        dxl_end_position[device_index], index[device_index] = motor_check(device_index, dxl_goal_inputs[device_index])
        dxl_end_angle[device_index] = _map(dxl_end_position[device_index], 0, 4095, 0, 360)
        # ------------------------------------------------------------------------------------------------------------------------------------------------------

        #Print out details of each motor
        device_index = 0
        while device_index <= 2:
            print("For Dynamixel [%03d], Status:%03d, GoalPos:%03d  GoalDeg:%03d  PresPos:%03d  PresDeg:%03d " %
                (DXL_ID[device_index], index[device_index], dxl_goal_inputs[device_index], dxl_goal_angle[device_index], dxl_present_position[device_index], dxl_present_angle[device_index]))
            device_index += 1

        #Data to be sent out
        # ------------------------------------------------------------------------------------------------------------------------------------------------------
        return index

def portTermination():
    TORQUE_DISABLE = 0
    # Disable Dynamixel Torque
    device_index = 0
    while device_index <= 2:
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(
            portHandler, DXL_ID[device_index], ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
        else:
            print("Dynamixel", DXL_ID[device_index],
                  "has been successfully disconnected")
        device_index += 1

    # Close port
    portHandler.closePort()

def motor_check(motor_index, goal_position):
    motor_repetition_status = 0
    motor_status = 0
    while motor_status < 1:
        #Read current position of  motor
        motor_present_position = read_position(motor_index)

        #Assign a check value to determine if the code is looping infinitely
        motor_threshold_previous = abs(goal_position - motor_present_position)

        #Check if base motor has stopped moving. If yes, motor_status = 1, otherwise 0
        motor_status = check_position(motor_threshold_previous)

        #Assign a second check value to compare with the first to determine if the code is looping infinitely
        motor_present_position = read_position(motor_index)
        motor_threshold_current = abs(goal_position - motor_present_position)

        #If there is no change in motor position after 10 checks, this will force break out of the loop
        if (motor_threshold_previous == motor_threshold_current):
            motor_repetition_status += 1
        else:
            motor_reptition_status = 0
        if (motor_repetition_status == 10):
            break

    return (motor_present_position, motor_status)

def read_position(motor_index):
    #Read current position of base motor
    motor_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(
        portHandler, DXL_ID[motor_index], ADDR_PRESENT_POSITION)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    return motor_present_position

def check_position(motor_threshold):
    #Check if base motor has stopped moving. If yes, status index = 1, otherwise 0
    if not (motor_threshold > DXL_MOVING_STATUS_THRESHOLD):
        status_motor = 1
    else:
        status_motor = 0
    return status_motor

# portInitialization(portname, baudrate, baseID, bicepID, forearmID):
portInitialization('COM3', 1000000, 1, 3, 1)

dxlSetVelo([0,0,0])
dxl_current_velocity = dxlGetVelo()
print(dxl_current_velocity)

angles_before = dxlPresAngle()
print(angles_before)

motorRunWithInputs([0,0,0])

angles_after = dxlPresAngle()
print(angles_after)

portTermination()
