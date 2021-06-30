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


def angle_input(motor_id):
    InRange = False
    while not InRange:
        try:
            if motor_id == 0:
                goal_angle = int(
                    input("Input the goal angle for the base motor in degree (0-360): "))
            elif motor_id == 1:
                goal_angle = int(
                    input("Input the goal angle for the bicep motor in degree (0-360): "))
            else:
                goal_angle = int(
                    input("Input the goal angle for the forearm motor in degree (0-360): "))
        except ValueError:
            print("Goal angle input needs to be an integer.")
            continue
        else:
            if (goal_angle < 0) or (goal_angle > 360):
                print("Goal angle is out of range (0-360). Retry.")
                InRange = False
            else:
                if motor_id == 0:
                    print("Goal angle input for the base motor is %2d" %
                          (goal_angle))
                elif motor_id == 1:
                    print("Goal angle input for the bicep motor is %2d" %
                          (goal_angle))
                else:
                    print("Goal angle input for the forearm motor is %2d" %
                          (goal_angle))
                InRange = True
    return goal_angle


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
        else:
            dxl_present_angle[device_index] = _map(dxl_present_position[device_index], 0, 4095, 0, 360)

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


def motorRunWithInputs():
    ADDR_GOAL_POSITION = 116
    ADDR_PRESENT_POSITION = 132
    DXL_MOVING_STATUS_THRESHOLD = 5    # Dynamixel moving status threshold

    # ------------------Start to execute motor rotation------------------------
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

        base_motor_position_input = _map(
            base_motor_goal_degree, 0, 360, 0, 4095)
        bicep_motor_position_input = _map(
            bicep_motor_goal_degree, 0, 360, 0, 4095)
        forearm_motor_position_input = _map(
            forearm_motor_goal_degree, 0, 360, 0, 4095)

        # Write base_motor_goal position
        # ------------------------------------------------------------------------------------------------------------------------------------------------------
        device_index = 0
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(
            portHandler, DXL_ID[device_index], ADDR_GOAL_POSITION, base_motor_position_input)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))

        while 1:
            # Read present position
            dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(
                portHandler, DXL_ID[device_index], ADDR_PRESENT_POSITION)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % packetHandler.getRxPacketError(dxl_error))

            print("[ID:%03d] GoalPos:%03d  GoalDeg:%03d  PresPos:%03d  PresDeg:%03d" %
                  (DXL_ID[device_index], base_motor_position_input, base_motor_goal_degree, dxl_present_position, _map(dxl_present_position, 0, 4095, 0, 360)))

            if not abs(base_motor_position_input - dxl_present_position) > DXL_MOVING_STATUS_THRESHOLD:
                break
        # ------------------------------------------------------------------------------------------------------------------------------------------------------

        # Write bicep_motor_goal position
        # ------------------------------------------------------------------------------------------------------------------------------------------------------
        device_index = 1
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(
            portHandler, DXL_ID[device_index], ADDR_GOAL_POSITION, bicep_motor_position_input)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))

        while 1:
            # Read present position
            dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(
                portHandler, DXL_ID[device_index], ADDR_PRESENT_POSITION)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % packetHandler.getRxPacketError(dxl_error))

            print("[ID:%03d] GoalPos:%03d  GoalDeg:%03d  PresPos:%03d  PresDeg:%03d" %
                  (DXL_ID[device_index], bicep_motor_position_input, bicep_motor_goal_degree, dxl_present_position, _map(dxl_present_position, 0, 4095, 0, 360)))

            if not abs(bicep_motor_position_input - dxl_present_position) > DXL_MOVING_STATUS_THRESHOLD:
                break
        # ------------------------------------------------------------------------------------------------------------------------------------------------------

        # Write forearm_motor_goal position
        # ------------------------------------------------------------------------------------------------------------------------------------------------------
        device_index = 2
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(
            portHandler, DXL_ID[device_index], ADDR_GOAL_POSITION, forearm_motor_position_input)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))

        while 1:
            # Read present position
            dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(
                portHandler, DXL_ID[device_index], ADDR_PRESENT_POSITION)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % packetHandler.getRxPacketError(dxl_error))

            print("[ID:%03d] GoalPos:%03d  GoalDeg:%03d  PresPos:%03d  PresDeg:%03d" %
                  (DXL_ID[device_index], forearm_motor_position_input, forearm_motor_goal_degree, dxl_present_position, _map(dxl_present_position, 0, 4095, 0, 360)))

            if not abs(forearm_motor_position_input - dxl_present_position) > DXL_MOVING_STATUS_THRESHOLD:
                break
        # ------------------------------------------------------------------------------------------------------------------------------------------------------


#'/dev/ttyUSB0' or 'COM8'
# portInitialization(portname, baudrate, baseID, bicepID, forearmID):
portInitialization('COM8', 1000000, 0, 1, 2)

dxlSetVelo([0,0,0])
dxlGetVelo()

angles_before = dxlPresAngle()
print(angles_before)

motorRunWithInputs()

angles_after = dxlPresAngle()
print(angles_after)

portTermination()
