#!/usr/bin/env python
# -*- coding: utf-8 -*-


from dynamixel_sdk import *  # Uses Dynamixel SDK library
import os


def _map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


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
# ***** (Use only one definition at a time) *****
MY_DXL = 'X_SERIES'       # X330 (5.0 V recommended), X430, X540, 2X430
# MY_DXL = 'MX_SERIES'    # MX series with 2.0 firmware update.
# MY_DXL = 'PRO_SERIES'   # H54, H42, M54, M42, L54, L42
# MY_DXL = 'PRO_A_SERIES' # PRO series with (A) firmware update.
# MY_DXL = 'P_SERIES'     # PH54, PH42, PM54
# MY_DXL = 'XL320'        # [WARNING] Operating Voltage : 7.4V


# Control table address
if MY_DXL == 'X_SERIES' or MY_DXL == 'MX_SERIES':
    ADDR_TORQUE_ENABLE = 64
    ADDR_GOAL_POSITION = 116
    ADDR_PRESENT_POSITION = 132
    # Refer to the Minimum Position Limit of product eManual
    DXL_MINIMUM_POSITION_VALUE = 0
    # Refer to the Maximum Position Limit of product eManual
    DXL_MAXIMUM_POSITION_VALUE = 4095
    BAUDRATE = 1000000
elif MY_DXL == 'PRO_SERIES':
    ADDR_TORQUE_ENABLE = 562       # Control table address is different in DYNAMIXEL model
    ADDR_GOAL_POSITION = 596
    ADDR_PRESENT_POSITION = 611
    # Refer to the Minimum Position Limit of product eManual
    DXL_MINIMUM_POSITION_VALUE = -150000
    # Refer to the Maximum Position Limit of product eManual
    DXL_MAXIMUM_POSITION_VALUE = 150000
    BAUDRATE = 57600
elif MY_DXL == 'P_SERIES' or MY_DXL == 'PRO_A_SERIES':
    # Control table address is different in DYNAMIXEL model
    ADDR_TORQUE_ENABLE = 512
    ADDR_GOAL_POSITION = 564
    ADDR_PRESENT_POSITION = 580
    # Refer to the Minimum Position Limit of product eManual
    DXL_MINIMUM_POSITION_VALUE = -150000
    # Refer to the Maximum Position Limit of product eManual
    DXL_MAXIMUM_POSITION_VALUE = 150000
    BAUDRATE = 57600
elif MY_DXL == 'XL320':
    ADDR_TORQUE_ENABLE = 24
    ADDR_GOAL_POSITION = 30
    ADDR_PRESENT_POSITION = 37
    # Refer to the CW Angle Limit of product eManual
    DXL_MINIMUM_POSITION_VALUE = 0
    # Refer to the CCW Angle Limit of product eManual
    DXL_MAXIMUM_POSITION_VALUE = 1023
    BAUDRATE = 1000000   # Default Baudrate of XL-320 is 1Mbps

# DYNAMIXEL Protocol Version (1.0 / 2.0)
# https://emanual.robotis.com/docs/en/dxl/protocol2/
PROTOCOL_VERSION = 2.0  # Turn into a list for each motor

# Factory default ID of all DYNAMIXEL is 1
DXL_ID = [0, 1, 2]  # Turn into a list for each motor
# ID 1 is base motor for this instance
# ID 3 is bicep and forearm motor for this instance

# Use the actual port assigned to the U2D2.
# ex) Windows: "COM*", Linux: "/dev/ttyUSB*", Mac: "/dev/tty.usbserial-*"
DEVICENAME = 'COM8'  # All the motors share the same port

TORQUE_ENABLE = 1     # Value for enabling the torque
TORQUE_DISABLE = 0     # Value for disabling the torque
DXL_MOVING_STATUS_THRESHOLD = 5    # Dynamixel moving status threshold

device_index = 0
index = [0, 0, 0]
dxl_goal_position = [DXL_MINIMUM_POSITION_VALUE,
                     DXL_MAXIMUM_POSITION_VALUE]         # Goal position

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
        device_index += 1
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
        device_index += 1
    else:
        print("Dynamixel", DXL_ID[device_index],
              "has been successfully connected")
        device_index += 1

while 1:
    device_index = 0
    print("Press any key to continue! (or press ESC to quit!)")
    if getch() == chr(0x1b):
        break

    base_motor_goal_degree = int(
        input("Input the goal position for the base motor: "))
    print(base_motor_goal_degree)
    bicep_motor_goal_degree = int(
        input("Input the goal position for the bicep motor: "))
    print(bicep_motor_goal_degree)
    forearm_motor_goal_degree = int(
        input("Input the goal position for the forearm motor: "))
    print(forearm_motor_goal_degree)

    base_motor_position_input = _map(base_motor_goal_degree, 0, 360, 0, 4095)
    bicep_motor_position_input = _map(bicep_motor_goal_degree, 0, 360, 0, 4095)
    forearm_motor_position_input = _map(
        forearm_motor_goal_degree, 0, 360, 0, 4095)

    # Write base_motor_goal position
    device_index = 0
    if (MY_DXL == 'XL320'):  # XL320 uses 2 byte Position Data, Check the size of data in your DYNAMIXEL's control table
        dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(
            portHandler, DXL_ID[device_index], ADDR_GOAL_POSITION, base_motor_position_input)
    else:
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(
            portHandler, DXL_ID[device_index], ADDR_GOAL_POSITION, base_motor_position_input)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

    while 1:
        # Read present position
        if (MY_DXL == 'XL320'):  # XL320 uses 2 byte Position Data, Check the size of data in your DYNAMIXEL's control table
            dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(
                portHandler, DXL_ID[device_index], ADDR_PRESENT_POSITION)
        else:
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

    # Change goal position
    if index[device_index] == 0:
        index[device_index] = 1
    else:
        index[device_index] = 0
    print("The status of the base motor is ", index[device_index])

    # Write bicep_motor_goal position
    device_index = 1
    if (MY_DXL == 'XL320'):  # XL320 uses 2 byte Position Data, Check the size of data in your DYNAMIXEL's control table
        dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(
            portHandler, DXL_ID[device_index], ADDR_GOAL_POSITION, bicep_motor_position_input)
    else:
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(
            portHandler, DXL_ID[device_index], ADDR_GOAL_POSITION, bicep_motor_position_input)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

    while 1:
        # Read present position
        if (MY_DXL == 'XL320'):  # XL320 uses 2 byte Position Data, Check the size of data in your DYNAMIXEL's control table
            dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(
                portHandler, DXL_ID[device_index], ADDR_PRESENT_POSITION)
        else:
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

    # Change goal position
    if index[device_index] == 0:
        index[device_index] = 1
    else:
        index[device_index] = 0
    print("The status of the bicep motor is ", index[device_index])

    # Write forearm_motor_goal position
    device_index = 2
    if (MY_DXL == 'XL320'):  # XL320 uses 2 byte Position Data, Check the size of data in your DYNAMIXEL's control table
        dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(
            portHandler, DXL_ID[device_index], ADDR_GOAL_POSITION, forearm_motor_position_input)
    else:
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(
            portHandler, DXL_ID[device_index], ADDR_GOAL_POSITION, forearm_motor_position_input)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

    while 1:
        # Read present position
        if (MY_DXL == 'XL320'):  # XL320 uses 2 byte Position Data, Check the size of data in your DYNAMIXEL's control table
            dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(
                portHandler, DXL_ID[device_index], ADDR_PRESENT_POSITION)
        else:
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

    # Change goal position
    if index[device_index] == 0:
        index[device_index] = 1
    else:
        index[device_index] = 0
    print("The status of the forearm motor is ", index[device_index])


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

# figure out how to have file take 3 inputs for 3 different motors
# return a value of 1 when entire process is completed and 0 if it isn't
