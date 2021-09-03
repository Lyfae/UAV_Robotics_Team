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

# List of all the primary functions that will be used to run the robotic arm
# ------------------------------------------------------------------------------------------------------------------------------------------------------

#Initializes and enables all the motors
#Input is portname, baudrate, and Dynamixel motor IDs
#Portname is the serial port assigned to the U2D2. Windows: "COM*", Linux: "/dev/ttyUSB*", Mac: "/dev/tty.usbserial-*"
#To check portname, please refer to either the Dynamixel Wizard or "Serial Ports" in Device Manager
#Baudrate is the rate of information transfer via serial ports. Linux is 57600 and Windows is 1000000
#Dynamixel motor IDs can be found by using the Dynamixel Wizard.
#There is no output from this function
def portInitialization(portname, baudrate, baseID, bicepID, forearmID):
    global DEVICENAME
    DEVICENAME = portname  # All the motors share the same port when connected in series
    global PROTOCOL_VERSION #Dynamixel SDK has two operating modes: Protocol 1 or 2. This code uses 2
    PROTOCOL_VERSION = 2 # Initialize PortHandler instance and PacketHandler instance
    global portHandler
    portHandler = PortHandler(DEVICENAME)
    global packetHandler
    packetHandler = PacketHandler(PROTOCOL_VERSION)
    device_index = 0

    if portHandler.openPort(): #Enables communication between computer and motors
        print("Succeeded to open the port")
    else:
        print("Failed to open the port")
        print("Press any key to terminate...")
        getch()
        quit()

    global BAUDRATE
    BAUDRATE = baudrate
    # Set port baudrate
    if portHandler.setBaudRate(BAUDRATE): #Sets rate of information transfer
        print("Succeeded to change the baudrate")
    else:
        print("Failed to change the baudrate")
        print("Press any key to terminate...")
        getch()
        quit()

    global ADDR_TORQUE_ENABLE # Set memory address for Torque Enable
    ADDR_TORQUE_ENABLE = 64
    TORQUE_ENABLE = 1

    global DXL_ID # Set the motor ID for each dynamixel. ID 0,1,2 is base/bicep/forearm motors
    DXL_ID = [baseID, bicepID, forearmID]

    while device_index <= 2: # Enable Dynamixel Torque
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

#Reads the present angle of all motors and returns the data as a 3 piece array
#There is no input
#Output is an array of present angles of the motors
def dxlPresAngle():
    ADDR_PRESENT_POSITION = 132 #Address of the positions of the motors
    dxl_present_position = [0, 0, 0]
    dxl_present_angle = [0, 0, 0]

    device_index = 0
    while device_index <= 2: #Reads the current position of the motor
        dxl_present_position[device_index] = ReadMotorData(device_index, ADDR_PRESENT_POSITION)
        device_index += 1

    device_index = 0
    while device_index <= 2: #Converts the position into angles
        dxl_present_angle[device_index] = _map(dxl_present_position[device_index], 0, 4095, 0, 360)
        device_index += 1

    device_index = 0
    while device_index <= 2: #States the location of the motor in both position and angles
        print("[ID:%03d] PresPos:%03d  PresDeg:%03d" %
            (DXL_ID[device_index], dxl_present_position[device_index], dxl_present_angle[device_index]))
        device_index += 1
    return (dxl_present_angle)

#Sets the velocity for each motor. If velocity is too high, robotic arm may suffer damage
#Input is an array of 3 values between 0-200 that set the velocity of the motors. Do not exceed 50 to avoid damage
#There is no output
def dxlSetVelo(vel_array):
    global ADDR_PROFILE_VELOCITY #Address of the velocity of the motors
    ADDR_PROFILE_VELOCITY = 112

    device_index = 0
    while device_index <= 2:
        WriteMotorData(device_index, ADDR_PROFILE_VELOCITY, vel_array[device_index])
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

#Reads the current velocity of each motor. If velocity is too high, robotic arm may suffer damage. Range is between 0-200. Do not exceed 50 to avoid damage
#There is no input
#Output is an array of the velocity values of the motors.
def dxlGetVelo():
    global ADDR_PROFILE_VELOCITY #Address of the velocity of the motors
    ADDR_PROFILE_VELOCITY = 112
    dxl_present_velocity = [0, 0, 0]

    device_index = 0
    while device_index <= 2:
        dxl_present_velocity[device_index] = ReadMotorData(device_index, ADDR_PROFILE_VELOCITY)
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

#Will set and move the base, bicep, and forearm motors to their required positions. Base will move first. Bicep/forearm move simultaneously
#Input is an array of the angles that the motors need to move to. The format is ([base_angle,bicep_angle,forearm_angle])
#Output is an array that indicates the status of movement for the motors. A 1 is successful movement and 0 is failed movement
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
    device_index = 1
    while device_index <= 2: #Create parameter storage for bicep and forearm motors' present position value
        dxl_addparam_result = motor_sync_read.addParam(DXL_ID[device_index])
        if dxl_addparam_result != True:
            print("[ID:%03d] groupSyncRead addparam failed" % DXL_ID[device_index])
        device_index += 1

    while 1:
        device_index = 0
        valid_angle_array = angle_input(angle_inputs) #Check if input angles are between 0-360

        device_index = 0
        while device_index <= 2: #Convert angle inputs into step units for movement
            dxl_goal_inputs[device_index] = _map(
                dxl_goal_angle[device_index], 0, 360, 0, 4095)
            device_index += 1

        # Base Motor Procedure
        # ------------------------------------------------------------------------------------------------------------------------------------------------------

        device_index = 0 #Write goal position for base motor
        WriteMotorData(device_index, ADDR_GOAL_POSITION, dxl_goal_inputs[device_index])

        #Read position for base motor and set status of motor
        dxl_end_position[device_index], index[device_index] = motor_check(device_index, dxl_goal_inputs[device_index]) #Read position for base motor
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

        device_index += 1
        dxl_addparam_result = motor_sync_write.addParam(DXL_ID[device_index], param_goal_forearm_position)
        if dxl_addparam_result != True:
            print("[ID:%03d] groupSyncWrite addparam failed" % DXL_ID[device_index])

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

#Disable the motors. The motors position can't be changed/read unless motors are enabled
#There are no inputs
#There are no outputs
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

#List of all the sub functions used that the main functions call upon
# ------------------------------------------------------------------------------------------------------------------------------------------------------

#Equation used to convert from angle degrees to positional units and vice versa
#To go from angles to units, order of values is 0, 360, 0, 4095
#To go from units to degrees, order of values is 0, 4095, 0, 360
#Inputs are angles or units you want to convert.
#Outputs are the converted values of angles or units
def _map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

#Checks whether the given angles are within a range of 0-360 degrees. If yes, then valid_angle_array = 1, otherwise 0
#Input is an array of 3 angle values
#Output is an array that states whether each angle is valid or not. 1 is valid and 0 is not valid
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

#Reads the data of one motor in a given address. Dynamixel XM430-W350-R has most data in 4 bytes
#Input is (ID of motor to be read, address where data resides)
#Output is the data value that was read
def ReadMotorData(device_index, data_address):
    data_value, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(
        portHandler, DXL_ID[device_index], data_address)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    return data_value

#Writes data to one motor at a given address. Dynamixel XM430-W350-R has most data in 4 bytes
#Input is (ID of motor to be read, address where data resides, data you want to write)
#There is no output
def WriteMotorData(device_index, data_address, data_inputs):
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(
    portHandler, DXL_ID[device_index], data_address, data_inputs)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

#Checks the position of a motor.
#Input is the ID of the motor and the goal position that motor should move to
#Output is the present position of the motor and its status. If the status = 1, successful movement. If status = 0, failed movement
def motor_check(motor_index, goal_position):
    motor_repetition_status = 0
    motor_status = 0
    while motor_status < 1:
        #Read current position of  motor
        motor_present_position = ReadMotorData(motor_index, ADDR_PRESENT_POSITION)

        #Assign a check value to determine if the code is looping infinitely
        motor_threshold_previous = abs(goal_position - motor_present_position)

        #Check if base motor has stopped moving. If yes, motor_status = 1, otherwise 0
        motor_status = check_position(motor_threshold_previous)

        #Assign a second check value to compare with the first to determine if the code is looping infinitely
        motor_present_position = ReadMotorData(motor_index, ADDR_PRESENT_POSITION)
        motor_threshold_current = abs(goal_position - motor_present_position)

        #If there is no change in motor position after 10 checks, this will force break out of the loop
        if (motor_threshold_previous == motor_threshold_current):
            motor_repetition_status += 1
        else:
            motor_reptition_status = 0
        if (motor_repetition_status == 10):
            break

    return (motor_present_position, motor_status)

#Checks if the motor has stopped moving. If yes, then status = 1. If not, then status = 0
#Input is the threshold value to compare to if the motor has stopped moving
#Output is the status of the motor
def check_position(motor_threshold):
    #Check if base motor has stopped moving. If yes, status index = 1, otherwise 0
    if not (motor_threshold > DXL_MOVING_STATUS_THRESHOLD):
        status_motor = 1
    else:
        status_motor = 0
    return status_motor

# Procedure of how the code runs. Normally only run in the command terminal. Will not be used when integrated into server code
# ------------------------------------------------------------------------------------------------------------------------------------------------------

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
