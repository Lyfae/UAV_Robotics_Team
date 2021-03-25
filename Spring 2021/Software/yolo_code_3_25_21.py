import os
import time
import re
import math
import serial

arduinoData = serial.Serial('COM9',9600)	    # set correct port Name and data transfer speed

### the code was programmed by python language
### if you want to change python into other programming languages, the link below would be helpful
### http://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_sdk/sample_code/python_clear_multi_turn_protocol_2_0/


######## Get the information we input by keyboard and translate them into a appropriate form. #####

if os.name == 'nt':                                 # The os-module lets us run different code dependent on which operating system the code is running  nt = windows 
    import msvcrt				    # msvcrt —a module Useful routines from the MS VC++ runtime  only work on windows.
    def getch():				    # define a function to get the information we input by keyboard
        return msvcrt.getch().decode()		    # get character- is a function get an input from the keyboard. decode the returned value to a string
else:
    import sys, tty, termios			    # get modules on other system
    fd = sys.stdin.fileno()			    # get the statue (an integer) of the file
    old_settings = termios.tcgetattr(fd)	    # get the attributes for the file descriptor
    def getch():				    # define the function
        try:					
            tty.setraw(sys.stdin.fileno())	    # Change the mode of the file descriptor fd to raw
            ch = sys.stdin.read(1)		    # get information in a line
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings) 	# reset the attributes
        return ch


from dynamixel_sdk import *                    	    # Uses Dynamixel SDK library


def main():
    # Control table address
    ADDR_PRO_TORQUE_ENABLE       = 64               # RAM address decimal number for Dynamixel model xm430-w350-R
    ADDR_PRO_GOAL_POSITION       = 116		    # check them on the e-manual if you using a different Dynamixel 
    ADDR_PRO_PRESENT_POSITION    = 132		    # http://emanual.robotis.com/docs/en/dxl/x/xm430-w350/
    ADDR_PRO_VELOCITY_PROFILE    = 112
    PRESENT_CURRENT              = 126
    GOAL_CURRENT                 = 102

    # Protocol version
    PROTOCOL_VERSION             = 2.0              # See which protocol version is used in the Dynamixel


    # Default value setting 
    DXL_ID0                      = 0		    
    DXL_ID1                      = 1  		    # declare three Dynamixels 					 
    DXL_ID2                      = 2		    # the order of Daynamiels can be found on the labels 
    BAUDRATE                     = 57600            # Dynamixel default baudrate : 57600   
                                                    # have a range Baud Rate 9,600 [bps] ~ 4.5 [Mbps]
    DEVICENAME                   = 'COM3'    	    # Check which port is being used on your controller
                                                    # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

    TORQUE_ENABLE                = 1                # Value for enabling the torque
    TORQUE_DISABLE               = 0           	    # Value for disabling the torque
    VELOCITY_PROFILE0            = 20
    VELOCITY_PROFILE1            = 20		    # set up how fast the actuator rotate the unit is depended on the Operating mode 
    VELOCITY_PROFILE2            = 20		    # check e-manual for more detail
    
    
    DXL_MINIMUM_POSITION_VALUE0  = 2046             # Dynamixel will rotate between this value  
                                                    # value Range 0 ~ 4,095(1 rotation)
                                                    # unit 0.088 [°]
    DXL_MAXIMUM_POSITION_VALUE0  = 2080             # and this value (note that the Dynamixel would not move when the position value is out of movable range. Check e-manual about the range of the Dynamixel you use.)
    DXL_MINIMUM_POSITION_VALUE1  = 2550             # Dynamixel will rotate between this value
    DXL_MAXIMUM_POSITION_VALUE1  = 1650             # and this value (note that the Dynamixel would not move when the position value is out of movable range. Check e-manual about the range of the Dynamixel you use.)
    DXL_MINIMUM_POSITION_VALUE2  = 2000             # Dynamixel will rotate between this value
    DXL_MAXIMUM_POSITION_VALUE2  = 2400             # and this value (note that the Dynamixel would not move when the position value is out of movable range. Check e-manual about the range of the Dynamixel you use.)
    DXL_MOVING_STATUS_THRESHOLD  = 20               # Dynamixel moving status threshold      # more detail seaching moving threshold


    index = 0

    dxl_goal_position0 = [DXL_MINIMUM_POSITION_VALUE0, DXL_MAXIMUM_POSITION_VALUE0]         # set up the range of Goal position in the form of position values of 3 actuators
    dxl_goal_position1 = [DXL_MINIMUM_POSITION_VALUE1, DXL_MAXIMUM_POSITION_VALUE1]	    
    dxl_goal_position2 = [DXL_MINIMUM_POSITION_VALUE2, DXL_MAXIMUM_POSITION_VALUE2]

    # Initialize PortHandler instance
    # Set the port path
    # Get methods and members of PortHandlerLinux or PortHandlerWindows
    
    portHandler = PortHandler(DEVICENAME)

    # Initialize PacketHandler instance
    # Set the protocol version
    # Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler

    packetHandler = PacketHandler(PROTOCOL_VERSION)

    # Open port 
    # A feedback to check if the port is connected well

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
 
    # Enable Dynamixel Torque and set the speed each actuator rotate.

    dxl_comm_result0, dxl_error0 = packetHandler.write1ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_TORQUE_ENABLE, TORQUE_ENABLE)
    dxl_comm_result1, dxl_error1 = packetHandler.write1ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_TORQUE_ENABLE, TORQUE_ENABLE)
    dxl_comm_result2, dxl_error2 = packetHandler.write1ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_TORQUE_ENABLE, TORQUE_ENABLE)
    dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_VELOCITY_PROFILE, VELOCITY_PROFILE0)
    dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_VELOCITY_PROFILE, VELOCITY_PROFILE1)
    dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_VELOCITY_PROFILE, VELOCITY_PROFILE2)

    
    # check if the settings above work well

    if dxl_comm_result0 != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result0))
    elif dxl_error0 != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error0))
    else:
        print("Dynamixel0 has been successfully connected")

    if dxl_comm_result1 != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result1))
    elif dxl_error1 != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error1))
    else:
        print("Dynamixel1 has been successfully connected")

    if dxl_comm_result2 != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result2))
    elif dxl_error2 != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error2))
    else:
        print("Dynamixel2 has been successfully connected")
    
	
    # show the present position for each actuator. seems like we can only read the value of position, cannot be able to refine the values.
    # the first time runing will show the inital position of each actuator. 
    
    def displaylocation ():
        dxl_present_position0, dxl_comm_result0, dxl_error0 = packetHandler.read4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_PRESENT_POSITION)
        dxl_present_position1, dxl_comm_result1, dxl_error1 = packetHandler.read4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_PRESENT_POSITION)
        dxl_present_position2, dxl_comm_result2, dxl_error2 = packetHandler.read4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_PRESENT_POSITION)
        print("[ID:%03d] GoalPos0:%03d  PresPos0:%03d" % (DXL_ID0, dxl_goal_position0[index], dxl_present_position0))
        print("[ID:%03d] GoalPos1:%03d  PresPos1:%03d" % (DXL_ID1, dxl_goal_position1[index], dxl_present_position1))
        print("[ID:%03d] GoalPos2:%03d  PresPos2:%03d" % (DXL_ID2, dxl_goal_position2[index], dxl_present_position2))

  
    while True:
        # Get x y coordinates from YOLO
        with open("result.txt", "rb") as f:
            first = f.readline()        # Read the first line.
            f.seek(-2, os.SEEK_END)     # Jump to the second last byte.
            while f.read(1) != b"\n":   # Until EOL is found...
                f.seek(-2, os.SEEK_CUR) # ...jump back the read byte plus one more. -4=graphene 2, -3=electrolyte, -2=graphene 1
            last = f.readline()        	# Read last line.
            first = f.readline()        # Read the first line.
            f.seek(-2, os.SEEK_END)     # Jump to the second last byte.
            while f.read(1) != b"\n":   # Until EOL is found...
                f.seek(-3, os.SEEK_CUR) # ...jump back the read byte plus one more. -4=graphene 2, -3=electrolyte, -2=graphene 1
            secondtolast = f.readline()        
            first = f.readline()        # Read the first line.
            f.seek(-2, os.SEEK_END)     # Jump to the second last byte.
            while f.read(1) != b"\n":   # Until EOL is found...
                f.seek(-4, os.SEEK_CUR) # ...jump back the read byte plus one more. -4=graphene 2, -3=electrolyte, -2=graphene 1
            thirdtolast = f.readline()      
            a=last
            b=secondtolast
            c=thirdtolast    
            if 'Stainless_steel'.encode() in a or 'Stainless_steel'.encode() in b or 'Stainless_steel'.encode() in c:  
                if 'Stainless_steel'.encode() in a or 'Stainless_steel'.encode() in b or 'Stainless_steel'.encode() in c: 
                    s4 = re.findall(b"[\w']+", last)[3]
                s5 = re.findall(b"[\w']+", last)[5]
                s6 = re.findall(b"[\w']+", last)[9]
                if 'Stainless_steel'.encode() in a or 'Stainless_steel'.encode() in b or 'Stainless_steel'.encode() in c: 
                    s4 = int(s4)
                s5 = int(s5)
                s6 = int(s6)
                print('Stainless_steel_bot left_x: ',s4, 'top_y: ',s5, 'height: ',s6)
            if 'Graphene_paper'.encode() in a or 'Graphene_paper'.encode() in b or 'Graphene_paper'.encode() in c :
                if 'Graphene_paper'.encode() in a or 'Graphene_paper'.encode() in b or 'Graphene_paper'.encode() in c : 
                    s1 = re.findall(b"[\w']+", secondtolast)[3]
                s2 = re.findall(b"[\w']+", secondtolast)[5]
                s3 = re.findall(b"[\w']+", secondtolast)[9]
                if 'Graphene_paper'.encode() in a or 'Graphene_paper'.encode() in b or 'Graphene_paper'.encode() in c : 
                    s1 = int(s1)
                s2 = int(s2)
                s3 = int(s3)
                print('Graphene_paper left_x: ',s1, 'top_y: ',s2, 'height: ',s3)        
            if 'Stainless_steel'.encode() in a or 'Stainless_steel'.encode() in b or 'Stainless_steel'.encode() in c:  
                try:
                    if 'Stainless_steel'.encode() in a or 'Stainless_steel'.encode() in b or 'Stainless_steel'.encode() in c: 
                        s7 = re.findall(b"[\w']+", thirdtolast)[3]
                    s8 = re.findall(b"[\w']+", thirdtolast)[5]
                    s9 = re.findall(b"[\w']+", thirdtolast)[9]
                    if 'Stainless_steel'.encode() in a or 'Stainless_steel'.encode() in b or 'Stainless_steel'.encode() in c: 
                        s7 = int(s7)
                    s8 = int(s8)
                    s9 = int(s9)
                    print('Stainless_steel_top left_x: ',s7, 'top_y: ',s8, 'height: ',s9)
                except:
                    pass
            time.sleep(1)
            break
	

    # go back to inital position and disable the torque.

    def close ():
        dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
        dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 2650)
        dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 2000)
        time.sleep(3)
        dxl_comm_result0, dxl_error0 = packetHandler.write1ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_TORQUE_ENABLE, TORQUE_DISABLE)
        dxl_comm_result1, dxl_error1 = packetHandler.write1ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_TORQUE_ENABLE, TORQUE_DISABLE)
        dxl_comm_result2, dxl_error2 = packetHandler.write1ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_TORQUE_ENABLE, TORQUE_DISABLE)
        # Close port
        portHandler.closePort()
        print("done!")

    
	# movement 1-7 is used to assemle the capacitor in the case that conponents' original positon is at the different place on the workspace. according to the code, they should be placed at a specific order.
	# mtr1 and mtr2 should be the value got by calculation.

    def movement1 ():
        print('movement1')
        dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
        dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 1600)
        dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 1600)
        time.sleep(2)
        
        mtr1 =  1250        
        mtr2 =  1700      
        state=0
        try:        
            # Arm control
            # Move the arm to the left (electrolyte)
            if state == 0:
                print("state 0")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2190)  
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, mtr1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, mtr2)
                displaylocation()
                time.sleep(3)
                arduinoData.write(b'1')
                state = 1
                time.sleep(3)


            if state == 1:
                print("state 1")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 2000)
                time.sleep(1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 2000)
                displaylocation()
                state = 2
                time.sleep(3)

            # Move the arm to the right (graphene 2) and stack it on top
            if state == 2:
                print("state 2")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 1880)  
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, mtr1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, mtr2)
                time.sleep(3)
                arduinoData.write(b'0')
                displaylocation()
                state = 3
                time.sleep(3)
     
            if state == 3:
                print("state 3")
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, mtr1)
                time.sleep(1)
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 1800)
                time.sleep(1)
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                displaylocation()
                state = 4
                time.sleep(2)

            # Move the arm to the middle (graphane 1)
            if state == 4:
                print("state 4")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, mtr1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, mtr2)
                time.sleep(3)
                arduinoData.write(b'1')
                displaylocation()
                state = 5
                time.sleep(3)

            if state == 5:
                print("state 5")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 2000)
                time.sleep(1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 2000)
                displaylocation()
                state = 6
                time.sleep(3)

            # Move the arm to the right and stack it on top of both
            if state == 6:
                print("state 6")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 1880)  
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, mtr1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, mtr2)
                time.sleep(3)
                arduinoData.write(b'0')
                displaylocation()
                state = 7
                time.sleep(3)

            if state == 7:
                print("state 7")
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, mtr1)
                time.sleep(1)
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 1800)
                time.sleep(1)
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                displaylocation()
                state = 0
                time.sleep(3)

        except KeyboardInterrupt:
            pass

    # 2250
    # 1850
    def movement2 ():
        print('movement2')
        dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
        dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 1600)
        dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 1600)
        time.sleep(2)
        mtr1 =1400
        mtr2 =  1970
        state=0
        try:        
            # Arm control
            # Move the arm to the left (electrolyte)
            if state == 0:
                print("state 0")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2250)  
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, mtr1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, mtr2)
                displaylocation()
                time.sleep(3)
                arduinoData.write(b'1')
                state = 1
                time.sleep(3)


            if state == 1:
                print("state 1")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 2000)
                time.sleep(1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 2000)
                displaylocation()
                state = 2
                time.sleep(3)

            # Move the arm to the right (graphene 2) and stack it on top
            if state == 2:
                print("state 2")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 1830)  
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, mtr1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, mtr2)
                time.sleep(3)
                arduinoData.write(b'0')
                displaylocation()
                state = 3
                time.sleep(3)
     
            if state == 3:
                print("state 3")
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 1800)
                time.sleep(2)
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 1800)
                time.sleep(1)
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                displaylocation()
                state = 4
                time.sleep(2)

            # Move the arm to the middle (graphane 1)
            if state == 4:
                print("state 4")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 1390)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 2160)
                time.sleep(3)
                arduinoData.write(b'1')
                displaylocation()
                state = 5
                time.sleep(3)

            if state == 5:
                print("state 5")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 2000)
                time.sleep(1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 2000)
                displaylocation()
                state = 6
                time.sleep(3)

            # Move the arm to the right and stack it on top of both
            if state == 6:
                print("state 6")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 1830)  
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, mtr1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, mtr2)
                time.sleep(3)
                arduinoData.write(b'0')
                displaylocation()
                state = 7
                time.sleep(3)

            if state == 7:
                print("state 7")
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, mtr1)
                time.sleep(1)
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 1800)
                time.sleep(1)
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                displaylocation()
                state = 0
                time.sleep(3)

        except KeyboardInterrupt:
            pass

    # 2300
    # 1800
    def movement3 ():
        print('movement3')
        dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
        dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 1800)
        dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 1800)
        time.sleep(2)
        mtr1 = 1530
        mtr2 = 2190
        state=0
        try:        
            # Arm control
            # Move the arm to the left (electrolyte)
            if state == 0:
                print("state 0")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2300)  
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, mtr1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, mtr2)
                displaylocation()
                time.sleep(3)
                arduinoData.write(b'1')
                state = 1
                time.sleep(3)

            if state == 1:
                print("state 1")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 2000)
                time.sleep(1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 1800)
                displaylocation()
                state = 2
                time.sleep(3)

            # Move the arm to the right (graphene 2) and stack it on top
            if state == 2:
                print("state 2")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 1740)  
                time.sleep(2)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, mtr2)
                time.sleep(2)
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, mtr1)
                time.sleep(3)
                arduinoData.write(b'0')
                displaylocation()
                state = 3
                time.sleep(3)
     
            if state == 3:
                print("state 3")
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 1800)
                time.sleep(0.2)
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 2200)
                time.sleep(1)
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                displaylocation()
                state = 4
                time.sleep(2)

            # Move the arm to the middle (graphane 1)
            if state == 4:
                print("state 4")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                time.sleep(1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, mtr2)
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, mtr1)
                time.sleep(3)
                arduinoData.write(b'1')
                displaylocation()
                state = 5
                time.sleep(3)

            if state == 5:
                print("state 5")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 2000)
                time.sleep(1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 2000)
                displaylocation()
                state = 6
                time.sleep(3)

            # Move the arm to the right and stack it on top of both
            if state == 6:
                print("state 6")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 1740)  
                time.sleep(2)
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, mtr1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, mtr2)
                time.sleep(3)
                arduinoData.write(b'0')
                displaylocation()
                state = 7
                time.sleep(3)

            if state == 7:
                print("state 7")
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 1800)
                time.sleep(0.2)
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 2200)
                time.sleep(1)
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                displaylocation()
                state = 0
                time.sleep(3)

        except KeyboardInterrupt:
            pass

    # 2320
    # 1780
    def movement4 ():
        print('movement4')
        dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
        dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 1600)
        dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 1600)
        time.sleep(2)
        mtr1 = 1600
        mtr2 = 2250
        state=0
        try:        
            # Arm control
            # Move the arm to the left (electrolyte)
            if state == 0:
                print("state 0")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2320)  
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, mtr1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, mtr2)
                displaylocation()
                time.sleep(3)
                arduinoData.write(b'1')
                state = 1
                time.sleep(3)

            if state == 1:
                print("state 1")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 2000)
                time.sleep(1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 2000)
                displaylocation()
                state = 2
                time.sleep(3)

            # Move the arm to the right (graphene 2) and stack it on top
            if state == 2:
                print("state 2")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 1755)  
                time.sleep(2)
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, mtr1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, mtr2)
                time.sleep(3)
                arduinoData.write(b'0')
                displaylocation()
                state = 3
                time.sleep(3)
     
            if state == 3:
                print("state 3")
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 2000)
                time.sleep(3)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 2450)
                time.sleep(1)
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                displaylocation()
                state = 4
                time.sleep(2)

            # Move the arm to the middle (graphane 1)
            if state == 4:
                print("state 4")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                time.sleep(2)
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, mtr1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, mtr2)
                time.sleep(3)
                arduinoData.write(b'1')
                displaylocation()
                state = 5
                time.sleep(3)

            if state == 5:
                print("state 5")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 2000)
                time.sleep(1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 2000)
                displaylocation()
                state = 6
                time.sleep(3)

            # Move the arm to the right and stack it on top of both
            if state == 6:
                print("state 6")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 1755)  
                time.sleep(2)
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, mtr1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, mtr2)
                time.sleep(3)
                arduinoData.write(b'0')
                displaylocation()
                state = 7
                time.sleep(3)

            if state == 7:
                print("state 7")
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 2250)
                time.sleep(0.5)
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 2000)
                time.sleep(1)
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                displaylocation()
                state = 0
                time.sleep(3)

        except KeyboardInterrupt:
            pass

    # 2400
    # 1700
    def movement5 ():
        print('movement5')
        dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
        dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 2200)
        dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 2200)
        time.sleep(2)
        mtr1 = 1640
        mtr2 = 2340
        state=0
        try:        
            # Arm control
            # Move the arm to the left (electrolyte)
            if state == 0:
                print("state 0")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2400)  
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, mtr1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, mtr2)
                displaylocation()
                time.sleep(3)
                arduinoData.write(b'1')
                state = 1
                time.sleep(3)

            if state == 1:
                print("state 1")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 2200)
                time.sleep(1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 2200)
                displaylocation()
                state = 2
                time.sleep(3)

            # Move the arm to the right (graphene 2) and stack it on top
            if state == 2:
                print("state 2")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 1600)  
                time.sleep(2)
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, mtr1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, mtr2)
                time.sleep(3)
                arduinoData.write(b'0')
                displaylocation()
                state = 3
                time.sleep(3)
     
            if state == 3:
                print("state 3")
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 2300)
                time.sleep(1)
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 2300)
                time.sleep(1)
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                displaylocation()
                state = 4
                time.sleep(2)

            # Move the arm to the middle (graphane 1)
            if state == 4:
                print("state 4")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                time.sleep(2)
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, mtr1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, mtr2)
                time.sleep(3)
                arduinoData.write(b'1')
                displaylocation()
                state = 5
                time.sleep(3)

            if state == 5:
                print("state 5")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 2200)
                time.sleep(1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 2200)
                displaylocation()
                state = 6
                time.sleep(3)

            # Move the arm to the right and stack it on top of both
            if state == 6:
                print("state 6")
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 1600)  
                time.sleep(2)
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, mtr1)
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, mtr2)
                time.sleep(3)
                arduinoData.write(b'0')
                displaylocation()
                state = 7
                time.sleep(3)

            if state == 7:
                print("state 7")
                dxl_comm_result2, dxl_error2 = packetHandler.write4ByteTxRx(portHandler, DXL_ID2, ADDR_PRO_GOAL_POSITION, 2300)
                time.sleep(1)
                dxl_comm_result1, dxl_error1 = packetHandler.write4ByteTxRx(portHandler, DXL_ID1, ADDR_PRO_GOAL_POSITION, 2300)
                time.sleep(1)
                dxl_comm_result0, dxl_error0 = packetHandler.write4ByteTxRx(portHandler, DXL_ID0, ADDR_PRO_GOAL_POSITION, 2080)  
                displaylocation()
                state = 0
                time.sleep(3)



    # the following code is used to show the position of the capacitor conponents and make judge which movement we need to implement.
    ### according the code shown below, we find the position data we got from the camera is only one number. whatever the number is for 
    ### x-axis or y-axis, it is impossible to foucu a point by one value, the code here makes no sense. when we demo the code for other 
    ### people, we have to place the capacitors on a fix position with a fix order and block some code in order to show a perfect performance to others.
    
    ### Here may is a useful proposal to make the following code meaningful. 
    ### we posibly use two cameras placing them in a different place to detect the position of each object. by this way, we may get two numbers for the position
    ### of each object. 

  
	


        except KeyboardInterrupt:
            pass
    def run ():
        try:
            print('Graphene_paper s1:', s1)
        except:
            pass
        try: 
            print('Stainless_steel_bot s4:', s4)
        except:
            pass
        try:
            print('Stainless_steel_top s7:', s7)
        except:
            pass

        try: 
            print('try#1')
            if s1 <= 40 or s4 <= 40 or s7 <= 40 :
                movement1()
            elif 155 >= s1 > 40 or 155 >= s4 > 40 or 155 >= s7 > 40:
                movement2()
            elif 240 >= s1 > 155  or 240 >= s4 > 155  or 240 >= s7 > 155:
                movement3()
            elif 300 >= s1 > 240 or 300 >= s4 > 240 or 300 >= s7 > 240 :
                movement4()
            elif s1 > 300 or s4 > 300 or s7 > 300:
                movement5()
            else:
                print('nothing detected')
            pass
        except:
            pass
            try: 
                print('try#2') #if failed to detect all objects then try #2,#3,#4
                if s1 <= 40:
                    movement1()
                elif 155 >= s1 > 40:
                    movement2()
                elif 240 >= s1 > 155:
                    movement3()
                elif 300 >= s1 > 240:
                    movement4()
                elif s1 > 300:
                    movement5()
                else:
                    print('nothing detected')
                pass
            except:
                try: 
                    print('try#2')
                    if s4 <= 40:
                        movement1()
                    elif 155 >= s4 > 40:
                        movement2()
                    elif 240 >= s4 > 155:
                        movement3()
                    elif 300 >= s4 > 240:
                        movement4()
                    elif s4 > 300:
                        movement5()
                    else:
                        print('nothing detected')
                    pass
                except:
                    try: 
                        print('try#3')
                        if s7 <= 40:
                            movement1()
                        elif 155 >= s7 > 40:
                            movement2()
                        elif 240 >= s7 > 155:
                            movement3()
                        elif 300 >= s7 > 240:
                            movement4()
                        elif s7 > 300:
                            movement5()
                        else:
                            print('nothing detected')
                        pass
                    except:
                        pass
            pass
        close()
    run()


while True:
    main()
    if input("Repeat the program? (Y/N)").strip().upper() != 'Y':
        print('Done!')
        break




# movement1()
# movement2()
# movement3()
# movement4()
# movement5()