# Import Libraries
import sys
import time
import json
import socket
import tkinter as tk
from _thread import *
import threading

from numpy.core.numeric import moveaxis

# Initalize Socket information (For use in localhost only)
HOST = '127.0.0.1'
PORT = 8009
BUFFER_SIZE = 8162
TIME_OUT = 5
CONNECTIONS = 1
ARM_TIME_OUT = 20

def tkinter():
    print(f"[NEW CONNECTION] tkinter window connected to tk thread.")
    
    # TKINTER DEFAULT VARIABLES
    HEIGHT = 600
    WIDTH = 400
    REFRESH_RATE = 10

    # GLOBAL VARIABLES

    # Base Functions
    def refresh_json():
        global location
        with open('simlocation.json') as read_file:
                location = json.load(read_file)

    # Local Variables
    global location
    location = {}
    refresh_json()

    # Moving Varialbes
    global movePressed
    global reachedLabel
    global reachedBox
    movePressed = False
    reachedLabel = False
    reachedBox = False

    global moveX
    global moveY
    moveX=1
    moveY=1

    global xCounter
    global yCounter
    xCounter=0
    yCounter=0

    # Homing Variables
    homex = 50
    homey = 180

    # INITIALIZATION
    # Creation of the program window (root)
    root = tk.Tk()
    root.resizable(False, False)
    main_canv = tk.Canvas(root, height=HEIGHT, width=WIDTH, bg='black', highlightthickness=0)
    main_canv.pack()

    # Title
    title = tk.Label(main_canv, text="LabelBot Simulation", font=('garamond',24,'bold'), justify='center', bg='black', fg='green')
    title.place(relx=0.5, y=50, anchor='center')

    # Divider Lines
    main_canv.create_line(0, 100, 400, 100, fill='white', width=5)
    main_canv.create_line(0, 500, 400, 500, fill='white', width=5)

    # Main Section Canvas
    sim_canv = tk.Canvas(main_canv, height=380, width=400, bg='white', highlightthickness=0)
    sim_canv.place(relx=0.5, rely=0.5, anchor='center')

    # Initialize Objects
    '''box_canv = tk.Canvas(sim_canv, height=120, width=75, bg='brown', highlightthickness=0)
    box_canv.place(x=location['bxpos'], y=location['bypos'], anchor='center')

    label_canv = tk.Canvas(sim_canv, height=40, width=25, bg='yellow', highlightcolor='black', highlightbackground= 'black', highlightthickness=2)
    label_canv.place(x=location['lxpos'], y=location['lypos'], anchor='center')

    arm_canv = tk.Canvas(sim_canv, height = 10, width = 20, bg='black', highlightthickness=0)
    arm_canv.place(x=homex,y=homey,anchor='center')'''

    # Box coordinates
    boxTLx = location['bxpos']
    boxTLy = location['bypos']
    boxWidth = 75
    boxHeight = 120

    # Label coordinates
    labelTLx = location['lxpos']
    labelTLy = location['lypos']
    labelWidth = 20
    labelHeight = 40

    # Arm coordinates
    armTLx = homex
    armTLy = homey
    armWidth = 20  
    armHeight = 10

    box = sim_canv.create_rectangle(boxTLx,boxTLy,boxTLx+boxWidth,boxTLy+boxHeight,fill='brown', outline='black', width=2)

    label = sim_canv.create_rectangle(labelTLx,labelTLy,labelTLx+labelWidth,labelTLy+labelHeight,fill='yellow', outline='black', width=2)

    arm = sim_canv.create_rectangle(armTLx,armTLy,armTLx+armWidth,armTLy+armHeight,fill='black', outline='black', width=2)

    # Initialize Info Label
    info_label = tk.Label(sim_canv, text="Current State: ", font=('courier new',12,'bold'), justify='left', bg='white', fg='black')
    info_label.place(relx=0.03,rely=0.95,anchor='w')

    state_label = tk.Label(sim_canv, text="#3 (Home)", font=('courier new',12,'bold'), justify='left', bg='white', fg='green')
    state_label.place(relx=0.4,rely=0.95,anchor='w')

    # Button Commands
    def move():
        print("Moving!")
        global movePressed
        movePressed = True

    # BUTTONS
    refreshButton = tk.Button(main_canv, text="Refresh", font=('garamond',18,'bold'), command=refresh_json, justify='center', padx=40, pady=10, bg='black', fg='red')
    refreshButton.place(relx=0.75,y=550,anchor='center')

    moveButton = tk.Button(main_canv, text="Move", font=('garamond',18,'bold'), command=move, justify='center', padx=40, pady=10, bg='black', fg='green')
    moveButton.place(relx=0.25,y=550,anchor='center')

    # UPDATE FUNCTION
    def updateData():
        # Recursive function to update values.

        global movePressed
        global reachedLabel
        global reachedBox

        global xCounter
        global yCounter

        global moveX
        global moveY

        if movePressed:
            if not reachedLabel:
                # Calculate trajectory taken (Arm to Label)
                dALx = (location['lxpos'] + labelWidth/2 - homex + armWidth/2) - labelWidth
                dALy = (location['lypos'] + labelHeight/2 - homey + armHeight/2) - labelHeight/4
                
                print(f"dALx: {dALx} || dALy: {dALy}")

                state_label['text'] = '#1 (Picking up Label)'
                state_label['fg'] = 'orange'

                if dALx < 0:
                    moveX *= -1
                if dALy < 0:
                    moveY *= -1
                
                if xCounter != dALx:
                    sim_canv.move(arm, moveX, 0)
                    xCounter += moveX
                elif xCounter == dALx and yCounter != dALy:
                    sim_canv.move(arm, 0, moveY)
                    yCounter += moveY
                else:
                    reachedLabel = True
                    xCounter = 0
                    yCounter = 0

            elif not reachedBox:
                # Calculate trajectory taken (Label to Box)
                dLBx = int((location['bxpos'] + boxWidth/2 - location['lxpos'] + labelWidth/2) - boxWidth/4)
                dLBy = int((location['bypos'] + boxHeight/2 - location['lypos'] + labelHeight/2) - boxHeight/4)

                print(f"dLBx: {dLBx} || dLBy: {dLBy}")

                state_label['text'] = '#2 (Dropping off Label)'
                state_label['fg'] = 'red'

                if dLBx < 0:
                    moveX *= -1
                if dLBy < 0:
                    moveY *= -1
                
                if xCounter != dLBx:
                    sim_canv.move(arm, moveX, 0)
                    sim_canv.move(label, moveX, 0)
                    xCounter += moveX
                elif xCounter == dLBx and yCounter != dLBy:
                    sim_canv.move(arm, 0, moveY)
                    sim_canv.move(label, 0, moveY)
                    yCounter += moveY
                else:
                    reachedBox = True
                    xCounter = 0
                    yCounter = 0
            else:
                # Calculate trajectory taken (Box to Home)
                dBHx = int((homex - location['bxpos'] - boxWidth/2))
                dBHy = int((homey - location['bypos'] - boxHeight/2))
                
                print(f"dBHx: {dBHx} || dBHy: {dBHy}")

                state_label['text'] = '#3 (Going Home)'
                state_label['fg'] = 'green'

                if dBHx < 0:
                    moveX *= -1
                if dBHy < 0:
                    moveY *= -1

                if xCounter != dBHx:
                    sim_canv.move(arm, moveX, 0)
                    xCounter += moveX
                elif xCounter == dBHx and yCounter != dBHy:
                    sim_canv.move(arm, 0, moveY)
                    yCounter += moveY
                else:
                    xCounter = 0
                    yCounter = 0
                    movePressed = False
                    reachedLabel = False
                    reachedBox = False
            
            moveX = 1
            moveY = 1

        root.after(REFRESH_RATE, updateData)

    # UPDATE / REFRESH
    root.after(REFRESH_RATE, updateData)

    # END
    root.mainloop()

def main(): 
    # Create socket connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(CONNECTIONS)
    s.settimeout(TIME_OUT)
    print("Listening on %s:%s..." % (HOST, str(PORT)))
    while True:
        try:
            conn, addr = s.accept()
            print(f"Connection from {addr} has been established!")
            # Begin tkinter thread
            thread_tk = threading.Thread(target = tkinter, args = (conn, addr))
            thread_tk.start()
        except KeyboardInterrupt: 
            if conn:
                print(f"Closing Client Connection")
                conn.close() 
            if s:
                print(f"Closing Server Socket")
                s.close()
            print(f"Exiting")
            sys.exit(1)
        except:
            pass

if __name__ == '__main__':
    # main()
    tkinter()