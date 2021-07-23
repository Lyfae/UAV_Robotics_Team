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
ARM_SAFE_HEIGHT = 220
ARM_HEIGHT_STEPS = 40

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
BASE_L_UP= 175
BASE_L_DOWN = 5
BICEP_L_DOWN= 45
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

#Arm offset angles for given motor positions
FOREARM_INST_DIR = 90

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
    #print("init stuff")

#Add all close out tasks here
def do_shutdown():
    portTermination()
    #print("shutdown stuff")

#gets locations from arm
#Takes no arguments
#Returns assumed X-Y-Z as array in that order
def get_XYZ_location():
    #gets current motor angles from motors as an array of 3
    # 0-base,1-bicep,2-forearm
    angles = getAnglesCorrected()
    #angles = [90,90,90]
    results = getXYZ(math.radians(angles[0]),math.radians(angles[1]), math.radians(angles[2]-FOREARM_INST_DIR))
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
        print([Xn,Yn,Zn])
        thetaBicepN=guessBicepFromTriangles(Xn,Yn,Zn)
        thetaForearmN=calcForearmTheta(Zn,thetaBicepN)[0]
        tempPZ = getPZ(thetaBicepN,thetaForearmN)
        #countcycles = 0
        while not(pideal-TOLERANCE)<tempPZ[0]<(pideal+TOLERANCE):
            if tempPZ[0]>(pideal+1):
                thetaBicepN = thetaBicepN+R_INCREMENT
            else:
                thetaBicepN = thetaBicepN-R_INCREMENT
            thetaForearmN=calcForearmTheta(Zn,thetaBicepN)[0]
            tempPZ = getPZ(thetaBicepN,thetaForearmN)
            #countcycles += 1

        thetaBicepND = math.degrees(thetaBicepN)
        thetaForearmND = math.degrees(thetaForearmN)
        thetaBaseND = thetaBaseN[1]
        print('BASE ANGLE = ' + str(thetaBaseND))
        print('BICEP ANGLE = ' + str(thetaBicepND))
        print('FOREARM ANGLE = ' + str(thetaForearmND))
        #print('Number of Cycles For Answer = ' + str(countcycles))
        # XYZtemp = getXYZ(thetaBaseN[0], thetaBicepN, thetaForearmN)
        # print('XYZ Value:'+str(XYZtemp))

        if not(BICEP_L_DOWN<thetaBicepND<BICEP_L_UP):
            print("BICEP Can't Rotate That Far, Current Limits are:"+str(BICEP_L_DOWN)+"-"+str(BICEP_L_UP))
        elif not(FOREARM_L_DOWN<thetaForearmND<FOREARM_L_UP):
            print("FOREARM Can't Rotate That Far, Current Limits are:"+str(FOREARM_L_DOWN)+"-"+str(FOREARM_L_UP))
        else:
            calcSpeedDiff(thetaBicepND, thetaForearmND)
            moveresults = setAnglesCorrected([thetaBaseND,thetaBicepND,thetaForearmND])
            #print('Arm Move Successful = ' + str(moveresults))
    else:
        print('BASE ANGLE = ' + str(thetaBaseN[1]))
        print("Base Can't Rotate That Far, Current Limits are:"+str(BASE_L_DOWN)+"-"+str(BASE_L_UP))

#takes coordinates and maps motion so that it moves to a safe height first, before lateral movement.
#Takes dictionary of "X", "Y", "Z"
#Returns nothing
# 0-base,1-bicep,2-forearm
def set_location_mapped(xyzdict):

    #store relevant data
    XYZold = get_XYZ_location()
    Xn = xyzdict["X"]
    Yn = xyzdict["Y"]
    Zn = xyzdict["Z"]
    print('Attempted X = ' + str(Xn))
    print('Attempted Y = ' + str(Yn))
    print('Attempted Z = ' + str(Zn))
    #move to safe height
    xyzdict["X"] = XYZold[0]
    xyzdict["Y"] = XYZold[1]

    ztemp = XYZold[2] + ARM_HEIGHT_STEPS/2
    while ztemp < ARM_SAFE_HEIGHT:
        xyzdict["Z"]= ztemp
        set_location(xyzdict)
        ztemp= ztemp+ARM_HEIGHT_STEPS
    xyzdict["Z"] = ARM_SAFE_HEIGHT
    set_location(xyzdict)

    #move over target
    xyzdict["X"] = Xn
    xyzdict["Y"] = Yn
    set_location(xyzdict)

    #contact target
    ztemp = ARM_SAFE_HEIGHT - ARM_HEIGHT_STEPS/2
    while ztemp > Zn:
        xyzdict["Z"]= ztemp
        set_location(xyzdict)
        ztemp= ztemp-ARM_HEIGHT_STEPS
    xyzdict["Z"] = Zn
    set_location(xyzdict)


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
    angles = getAnglesCorrected()
    ThetaBi = abs(ThetaBi-angles[1])
    ThetaFo = abs(ThetaFo-angles[2])

    BicepNew = ARM_S_MAX
    ForearmNew = ARM_S_MAX
    if ThetaBi > ThetaFo:
        ForearmNew = int((ThetaFo/ThetaBi)*ARM_S_MAX)
        if ForearmNew == 0:
            ForearmNew = 1
    else:
        BicepNew = int((ThetaBi/ThetaFo)*ARM_S_MAX)
        if BicepNew == 0:
            BicepNew = 1
    #print("Arm Speeds:"+str(ARM_S_MAX)+","+str(BicepNew)+","+str(ForearmNew))
    #print([ARM_S_MAX,BicepNew,ForearmNew])
    dxlSetVelo([ARM_S_MAX,BicepNew,ForearmNew])

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
    print([aside,bside,cside])
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

def getAnglesCorrected():
    angles = dxlPresAngle()
    angles = ([angles[0],angles[1],angles[2]-FOREARM_INST_DIR])
    return angles

def setAnglesCorrected(angles):
    moveresults = motorRunWithInputs([angles[0],angles[1],angles[2]+FOREARM_INST_DIR])
    return moveresults

#******MOTOR DRIVE FUNCTIONS*******
#this is where we will put hardware team functions

#motor drive functions
#this is where we will put hardware team functions

def _map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

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

    #List of all the addresses from the Control Table that is used for operation
    global ADDR_PRESENT_POSITION
    ADDR_PRESENT_POSITION = 132 #Address of the positions of the motors
    global ADDR_PROFILE_VELOCITY
    ADDR_PROFILE_VELOCITY = 112 #Address of the velocity of the motors
    global ADDR_GOAL_POSITION
    ADDR_GOAL_POSITION = 116 #Address of goal position
    global ADDR_MOVING
    ADDR_MOVING = 122 #Address of value that states if motor is moving or not
    global DXL_MOVING_STATUS_THRESHOLD
    DXL_MOVING_STATUS_THRESHOLD = 10    # Dynamixel moving status threshold
    global LEN_GOAL_POSITION
    LEN_GOAL_POSITION = 4 #Byte Length of goal position
    global LEN_PRESENT_POSITION
    LEN_PRESENT_POSITION = 4 #Byte length of present position

    if portHandler.openPort(): #Enables communication between computer and motors
        print("Succeeded to open the port")
    else:
        print("Failed to open the port")
        getch()
        quit()

    global BAUDRATE
    BAUDRATE = baudrate
    # Set port baudrate
    if portHandler.setBaudRate(BAUDRATE): #Sets rate of information transfer
        print("Succeeded to change the baudrate")
    else:
        print("Failed to change the baudrate")
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

    return (dxl_present_angle)

#Sets the velocity for each motor. If velocity is too high, robotic arm may suffer damage
#Input is an array of 3 values between 0-200 that set the velocity of the motors. Do not exceed 50 to avoid damage
#There is no output
def dxlSetVelo(vel_array):
    device_index = 0
    while device_index <= 2:
        WriteMotorData(device_index, ADDR_PROFILE_VELOCITY, vel_array[device_index])
        device_index += 1

#Reads the current velocity of each motor. If velocity is too high, robotic arm may suffer damage. Range is between 0-200. Do not exceed 50 to avoid damage
#There is no input
#Output is an array of the velocity values of the motors.
def dxlGetVelo():
    dxl_present_velocity = [0, 0, 0]

    device_index = 0
    while device_index <= 2:
        dxl_present_velocity[device_index] = ReadMotorData(device_index, ADDR_PROFILE_VELOCITY)
        device_index += 1

    return (dxl_present_velocity)

#Will set and move the base, bicep, and forearm motors to their required positions. Base will move first. Bicep/forearm move simultaneously
#Input is an array of the angles that the motors need to move to. The format is ([base_angle,bicep_angle,forearm_angle])
#Output is an array that indicates the status of movement for the motors. A 1 is successful movement and 0 is failed movement
def motorRunWithInputs(angle_inputs):

    #Format is [base, bicep, forearm]
    dxl_goal_angle = angle_inputs
    dxl_goal_inputs = [0, 0, 0]
    dxl_end_position = [0, 0, 0]
    dxl_end_angle = [0, 0, 0]
    index = [0, 0, 0]


    # ------------------Start to execute motor rotation------------------------
    while 1:
        device_index = 0
        while device_index <= 2: #Convert angle inputs into step units for movement
            dxl_goal_inputs[device_index] = _map(
                dxl_goal_angle[device_index], 0, 360, 0, 4095)
            device_index += 1

        # Base Motor Procedure
        # ------------------------------------------------------------------------------------------------------------------------------------------------------

        #Write goal position for base motor
        device_index = 0
        WriteMotorData(device_index, ADDR_GOAL_POSITION, dxl_goal_inputs[device_index])

        #Read position for base motor and set status of motor
        dxl_end_position[device_index], index[device_index] = motor_check(device_index, dxl_goal_inputs[device_index]) #Read position for base motor
        dxl_end_angle[device_index] = _map(dxl_end_position[device_index], 0, 4095, 0, 360)
        # ------------------------------------------------------------------------------------------------------------------------------------------------------

        # Bicep and forearm procedure
        # ------------------------------------------------------------------------------------------------------------------------------------------------------

        #Simultaneously write goal position for bicep and forearm motors
        SimultaneousMovement(dxl_goal_inputs)

        #Read bicep motor position
        device_index = 1
        dxl_end_position[device_index], index[device_index] = motor_check(device_index, dxl_goal_inputs[device_index])
        dxl_end_angle[device_index] = _map(dxl_end_position[device_index], 0, 4095, 0, 360)

        #Read forearm motor position
        device_index = 2
        dxl_end_position[device_index], index[device_index] = motor_check(device_index, dxl_goal_inputs[device_index])
        dxl_end_angle[device_index] = _map(dxl_end_position[device_index], 0, 4095, 0, 360)
        # ------------------------------------------------------------------------------------------------------------------------------------------------------

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

#Procedure for simultaneous movement of bicep and forearm motors
#There is no input
#There is no output
def SimultaneousMovement(dxl_goal_inputs):

    #Intializate simultaneous motor movement
    motor_sync_write = GroupSyncWrite(portHandler, packetHandler, ADDR_GOAL_POSITION, LEN_GOAL_POSITION)
    motor_sync_read = GroupSyncRead(portHandler, packetHandler, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)

    #Create parameter storage for present positions
    device_index = 1
    while device_index <= 2: #Create parameter storage for bicep and forearm motors' present position value
        dxl_addparam_result = motor_sync_read.addParam(DXL_ID[device_index])
        if dxl_addparam_result != True:
            print("[ID:%03d] groupSyncRead addparam failed" % DXL_ID[device_index])
        device_index += 1

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

    device_index = 2
    dxl_addparam_result = motor_sync_write.addParam(DXL_ID[device_index], param_goal_forearm_position)
    if dxl_addparam_result != True:
        print("[ID:%03d] groupSyncWrite addparam failed" % DXL_ID[device_index])

    #Syncwrite goal position to bicep and forearm motors
    dxl_comm_result = motor_sync_write.txPacket()
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))

    #Clear syncwrite parameter storage
    motor_sync_write.clearParam()

#Checks the position of a motor.
#Input is the ID of the motor and the goal position that motor should move to
#Output is the present position of the motor and its status. If the status = 1, successful movement. If status = 0, failed movement
def motor_check(motor_index, goal_position):
    motor_repetition_status = 0
    motor_status = 0
    while motor_status < 1:
        #Read moving status of motor. If status = 1, motor is still moving. If status = 0, motor stopped moving
        motor_present_position = ReadMotorData(motor_index, ADDR_PRESENT_POSITION)
        motor_moving_status = ReadMotorData(motor_index, ADDR_MOVING)
        if motor_moving_status == 0:
            motor_status = 1

        #Checks the present position of the motor and compares it to the goal position
        motor_threshold = abs(goal_position - motor_present_position)
        motor_status = check_position(motor_threshold)

        #Kicker method. This method checks to see if the motors are infinitely looping
        motor_new_position = ReadMotorData(motor_index, ADDR_PRESENT_POSITION)
        if motor_new_position == motor_present_position:
            motor_repetition_status += 1
        else:
            motor_repetition_status = 0
        if motor_repetition_status >= 10:
            motor_status = 1

    return (motor_present_position, motor_status)

#Checks if the motor has stopped moving. If yes, then status = 1. If not, then status = 0
#Input is the threshold value to compare to if the motor has stopped moving
#Output is the status of the motor
def check_position(motor_threshold):
    #Check if base motor has stopped moving. If yes, status index = 1, otherwise 0
    if (motor_threshold >= DXL_MOVING_STATUS_THRESHOLD):
        status_motor = 0
    else:
        status_motor = 1
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
