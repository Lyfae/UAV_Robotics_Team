#!/usr/bin/env python
# -*- coding: utf-8 -*-

#ALL IMPORTS
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

import math

#arm static definitions
#All units are in mm

#Arm PARAMS
ArmIDs = {"base":0,
         "bicep":1,
         "forearm":2}
ARM_S_MAX = 30
#Windows Params
#ARM_BAUD = 1000000  
#ARM_PORT = 'COM3'
#Linux Params
ARM_BAUD = 57600
ARM_PORT = '/dev/ttyUSB0'

#Arm Measurements
BASE_HEIGHT = 48.9 
BICEP_LENGTH=200
FOREARM_LENGTH=200
END_LENGTH=38.6
END_DEPTH=11.3
END_BIT=7

#Arm Min-Max Angles as per diagram
BASE_L_UP=175 
BASE_L_DOWN = 5
BICEP_L_DOWN=45
BICEP_L_UP = 125
FOREARM_L_UP = 45
FOREARM_L_DOWN = -15

#Arm offset angles for given motor positions
#DIRECTION CURRENTLY UNIMPLEMENTED
BASE_OFFSET = 0
BASE_DIRECTION = 1
BICEP_OFFSET = 0
BICEP_DIRECTION = 1
FOREARM_OFFSET = math.radians(-8)
FOREARM_DIRECTION = 1

#Various Increments
TOLERANCE = 1 #this is how close it will try and get in mm to the target location
R_INCREMENT = math.radians(0.1) #this controls by how much it will try to increment the degrees

#Arm Positions
thetaBaseN = 0
ThetaBicepN = 0
ThetaForearmN = 0

#Arm Positions in degrees
thetaBaseND = 0
ThetaBicepND = 0
ThetaForearmND = 0

#Add all startup tasks here
def do_init():
    portInitialization(ARM_PORT, ARM_BAUD, ArmIDs["base"], ArmIDs["bicep"], ArmIDs["forearm"])
    dxlSetVelo([ARM_S_MAX,ARM_S_MAX,ARM_S_MAX])

#Add all close out tasks here
def do_shutdown():
    portTermination()

#gets locations from arm
#Takes no arguments
#Returns assumed X-Y-Z as array in that order
def get_XYZ_location():
    #gets current motor angles from motors as an array of 3
    # 0-base,1-bicep,2-forearm
    angles = dxlPresAngle()
    results = getXYZ(math.radians(angles[0]),math.radians(angles[1]), math.radians(angles[2]))
    return results

#takes coordinates and sends angles to motors
#Takes dictionary of "X", "Y", "Z"
#Returns nothing
# 0-base,1-bicep,2-forearm
def set_location(xyzdict):
    Xn = xyzdict["X"]
    Yn = xyzdict["Y"]
    Zn = xyzdict["Z"]

    #Calculate the ideal projection on the x-y plane
    pideal = calcDist(Xn,Yn)

    #calculate the theta for the base
    thetaBaseN = calcBaseTheta(Xn,Yn)

    if BASE_L_DOWN <= thetaBaseN[1] <= BASE_L_UP :
        #guessBicepFromTriangles is an optimization variable that helps reduce the number of cycles.
        thetaBicepN=guessBicepFromTriangles(Xn,Yn,Zn)
        thetaForearmN=calcForearmTheta(Zn,thetaBicepN)[0]
        tempPZ = getPZ(thetaBicepN,thetaForearmN)
        countcycles = 0
        while not(pideal-TOLERANCE)<tempPZ[0]<(pideal+TOLERANCE):
            if tempPZ[0]>(pideal+1):
                thetaBicepN = thetaBicepN+R_INCREMENT
            else:
                thetaBicepN = thetaBicepN-R_INCREMENT
            thetaForearmN=calcForearmTheta(Zn,thetaBicepN)[0]
            tempPZ = getPZ(thetaBicepN,thetaForearmN)
            countcycles += 1

        thetaBicepND = math.degrees(thetaBicepN)    
        thetaForearmND = math.degrees(thetaForearmN)
        thetaBaseND = thetaBaseN[1]
        print('BASE ANGLE = ' + str(thetaBaseND))
        print('BICEP ANGLE = ' + str(thetaBicepND))
        print('FOREARM ANGLE = ' + str(thetaForearmND))
        print('Number of Cycles For Answer = ' + str(countcycles))
        # XYZtemp = getXYZ(thetaBaseN[0], thetaBicepN, thetaForearmN)
        # print('XYZ Value:'+str(XYZtemp))

        if not(BICEP_L_DOWN<thetaBicepND<BICEP_L_UP):
            print("BICEP Can't Rotate That Far, Current Limits are:"+str(BICEP_L_DOWN)+"-"+str(BICEP_L_UP))
        elif not(FOREARM_L_DOWN<thetaForearmND<FOREARM_L_UP):
            print("FOREARM Can't Rotate That Far, Current Limits are:"+str(FOREARM_L_DOWN)+"-"+str(FOREARM_L_UP))
        #else:
            calcSpeedDiff(thetaBicepND, thetaForearmND)
            moveresults = motorRunWithInputs([thetaBaseND,thetaBicepND,thetaForearmND])
            print('Arm Move Successful = ' + str(moveresults))
    else:
        print('BASE ANGLE = ' + str(thetaBaseN[1]))
        print("Base Can't Rotate That Far, Current Limits are:"+str(BASE_L_DOWN)+"-"+str(BASE_L_UP))

#takes camera x/y diff and turn to coodinates
#accepts a dictionary of X, Y, Z values 
#Returns a dictionary with new coordinates in overall system
def translate_diff(xyzdiffdict):
    Xd = xyzdiffdict["X"]
    Yd = xyzdiffdict["Y"]
    Zd = xyzdiffdict["Z"]
    curLocation = get_XYZ_location()
    newdict = {"X":curLocation[0]+Xd,
            "Y":curLocation[1]+Yd,
            "Z":curLocation[2]+Zd}
    
#predefined locations for z down
#TO DO
def drop_load():  
    print("drop_load not implemented")

#predefined locations for x-y-z up
#TO DO
def grab_load():
    print("grab_load not implemented")

#this method returns P and Z 
# where P is the 'roe' the projection of the distance on the x-y plane
# Z is the height above the x-y plane
def getPZ(ThetaBi, ThetaFo):
    P = END_LENGTH+FOREARM_LENGTH*math.cos(ThetaFo-FOREARM_OFFSET)+BICEP_LENGTH*math.cos(ThetaBi-BICEP_OFFSET)
    Z = BASE_HEIGHT-END_DEPTH-END_BIT+FOREARM_LENGTH*math.sin(-(ThetaFo-FOREARM_OFFSET))+BICEP_LENGTH*math.sin(ThetaBi+BICEP_OFFSET)
    return([P, Z])

#this method returns the theoretical X-Y-Z based on P and Z
#Input is the degrees in radians
#Output is an array of the X-Y-Z location in mm.
# 0-base,1-bicep,2-forearm
def getXYZ(ThetaBa, ThetaBi, ThetaFo):
    ThetaXYPlane = ThetaBa - math.radians(90) - BASE_OFFSET
    tempPZ = getPZ(ThetaBi, ThetaFo)
    Zres = tempPZ[1]
    Xres = tempPZ[0]*math.cos(ThetaXYPlane)
    Yres = tempPZ[0]*math.sin(ThetaXYPlane)
    return([Xres,Yres,Zres])

#This method returns the calculated base theta based on measurements of the arm
# It takes the arguements of X and Y
# It returns an array of the radian measurement and the degree measurement in that order
def calcBaseTheta(X,Y):
    thetaBaseR = math.atan(Y/X) + math.pi/2 + BASE_OFFSET
    thetaBaseD = math.degrees(thetaBaseR)
    return ([thetaBaseR,thetaBaseD])

#This method returns the calculated bicep theta based on measurements of the arm
# It takes the arguements of the ideal rho or 'P' and ForearmTheta
# It returns an array of the radian measurement and the degree measurement in that order
def calcBicepTheta(P,thetaForearm):
    thetaBicepR=(math.acos((P-END_LENGTH-FOREARM_LENGTH*math.cos(thetaForearm-FOREARM_OFFSET))/BICEP_LENGTH))+BICEP_OFFSET
    thetaBicepD=math.degrees(thetaBicepR)
    return ([thetaBicepR,thetaBicepD])

#This method returns the calculated forearm theta based on measurements of the arm
# It takes the arguements of the ideal z and BicepTheta
# It returns an array of the radian measurement and the degree measurement in that order
def calcForearmTheta(Z,thetaBicep):
    thetaForearmR=-1*math.asin((Z-BASE_HEIGHT+END_DEPTH+END_BIT-BICEP_LENGTH*math.sin(thetaBicep-BICEP_OFFSET))/FOREARM_LENGTH)+FOREARM_OFFSET
    thetaForearmD=math.degrees(thetaForearmR)
    return ([thetaForearmR,thetaForearmD])

#This method calculates the new speed of the bicep and forearm and sets the motor speeds
# It takes the arguements of theta bicep and Theta forearm 
# It returns nothing
def calcSpeedDiff(ThetaBi, ThetaFo):
    BicepNew = ARM_S_MAX
    ForearmNew = ARM_S_MAX
    if ThetaBi > ThetaFo:
        ForearmNew = (ThetaFo/ThetaBi)*ARM_S_MAX
    else:
        BicepNew = (ThetaBi/ThetaFo)*ARM_S_MAX
    #dxlSetVelo([ARM_S_MAX,BicepNew,ForearmNew])

#This method gives a close approximation for the bicep angle
# It takes the arguements of X, Y, Z
# It returns the angle of the bicep
def guessBicepFromTriangles(X,Y,Z):
    Ztemp = Z - BASE_HEIGHT+ END_DEPTH + END_BIT
    Ptemp = calcDist(X,Y)
    refthetaCorrection = 1
    if Ztemp<0:
        refthetaCorrection = -1
        Ztemp = abs(Ztemp)
    aside = FOREARM_LENGTH+END_LENGTH
    bside = BICEP_LENGTH
    cside = calcDist(Ptemp,Ztemp)
    thetaA = findATriangleAngle(aside,bside,cside)
    thetaRef = math.atan(Ztemp/Ptemp)
    return thetaA + refthetaCorrection*thetaRef
    
#This method calculates the projection of distance on the X Y plane given an X and Y
# It takes the arguments of X and Y in mm
# It Returns P
def calcDist(X,Y):
    return  math.sqrt((X**2)+(Y**2))

#this method calculates the angle opposed to side A
# It takes the arguments of A,B,C the sides of the triangle in mm
# It returns the angle of the opposed to A
def findATriangleAngle(A,B,C):
    thetaA = math.acos((B**2+C**2-A**2)/(2*B*C))
    return thetaA

#******MOTOR DRIVE FUNCTIONS*******
#this is where we will put hardware team functions

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
        # print("Press any key to continue! (or press ESC to quit!)")
        # if getch() == chr(0x1b):
        #     break

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



##Old Test Cases
# portInitialization(portname, baudrate, baseID, bicepID, forearmID):
# portInitialization('COM3', 1000000, 1, 3, 1)

# dxlSetVelo([0,0,0])
# dxl_current_velocity = dxlGetVelo()
# print(dxl_current_velocity)

# angles_before = dxlPresAngle()
# print(angles_before)

# motorRunWithInputs([0,0,0])

# angles_after = dxlPresAngle()
# print(angles_after)

# portTermination()
