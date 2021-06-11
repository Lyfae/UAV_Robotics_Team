#!/usr/bin/env python3

import socket
import json
import struct
import time
from _thread import *
import threading
#import movearm.py
import tkinter as tk
from datetime import datetime

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 8009        # Port to listen on (non-privileged ports are > 1023)
BUFFER_SIZE = 8162 
TIME_OUT = 5
SENSOR_COUNT=1

def init_globes():
    armStatus = {"arm_name":"Arm1", "code":2}
    cameraInput = {
        "camera":"Camera1", 
        "command":3,
        "dX":0, 
        "dY":0}
    newData = False
    state = 3

#this is for the set home location
home = {"x":170,
        "y":0,
        "z":170}

#GLOBAL VARIABLES
#this is for the main visual detection controller
global cameraInput
#1- move
#2- drop
#3- home
#4- pickup
#5- query location
cameraInput = {}

#This is for the current arm status
#1-Moving
#2-Waiting
global armStatus 
armStatus = {}

#This is for the current arm location
# global armLocation 
# armLocation = {}

global newData
global state

init_globes()


def tkinter(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected to tk thread.")
    
    # TKINTER DEFAULT VARIABLES
    HEIGHT = 480
    WIDTH = 360
    REFRESH_RATE = 50

    # GLOBAL VARIABLES

    # INITIALIZATION
    # Creation of the program window (root)
    root = tk.Tk()
    root.resizable(False, False)
    main_canv = tk.Canvas(root, height=HEIGHT, width=WIDTH, bg='black', highlightthickness=0)
    main_canv.pack()

    # CONST LABELS
    title = tk.Label(main_canv, text="LabelBot Info", font=('courier new',24,'bold'), justify='center', bg='black', fg='#037f51')
    title.place(relx=0.5,rely=0.085,anchor='center')

    # BUTTONS
    exitButton = tk.Button(main_canv, text="EXIT", font=('courier new',18,'bold'), command=exit, justify='center', padx=40, pady=10, bg='black', fg='red')
    exitButton.place(relx=0.5,rely=.9,anchor='center')

    # UPDATE FUNCTION
    # Will assign random numbers to values whenever called.
    def updateData():
        # Recursive function to update values.



        root.after(REFRESH_RATE, updateData)

    # UPDATE / REFRESH
    root.after(REFRESH_RATE, updateData)

    # END
    root.mainloop()

def load_data(data_recv):
    #Validate data
    if(armStatus['code']==2):
        if(data_recv["camera"]==cameraInput["camera"]):
            cameraInput["command"] = data_recv["command"]
            cameraInput["dX"] = data_recv["dX"]
            cameraInput["dY"] = data_recv["dY"]
            #Set New Data Flag
            newData=True
    else:
        print(f"Data NOT loaded, ignoring")
    
    

def read_async(connIn, addr): 
    print(f"[NEW CONNECTION] {addr} connected to r-w-a thread.")
    while True:
        try:
            data_recv = connIn.recv(BUFFER_SIZE).decode('utf-8')
            data_recv = json.loads(data_recv)
            print(f"Recieved: {data_recv}, attempting load...")
            load_data(data_recv)
            if(newData):
                armStatus["code"] = 1
                print("Data loaded, initiating command.")
                newData = False
                if(cameraInput["command"]==3):
                    print("Home command, processing.")
                    if(state == 1):
                        print("Dropping load.")
                        #drop_load()
                    print("Going home.")
                    #set_Location(home)
                    state = 3
                elif(cameraInput["command"]==1):
                    print("Move command, processing.")
                    if(state == 3):
                        print("Grabbing load.")
                        #grab_load()
                    #new_location=translate_diff(cameraInput)
                    #set_location(new_location)
                    print("Going to differential location.")
                    state = 1
                elif(cameraInput["command"]==2):
                    print("Dropping load.")
                    #drop_load()
                    state=2 
                elif(cameraInput["command"]==4):
                    print("Grabbing load.")
                    #grab_load()
                    state=4
            armStatus["code"] = 2

        except:
            print(f"Packet receive attempt to {addr} failed. Closing connection.")
            connIn.close()
            break
            
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT)) #Bind system socket
s.listen(SENSOR_COUNT) #Listen for up to SENSOR_COUNT connections
s.settimeout(TIME_OUT) 
print("Listening on %s:%s..." % (HOST, str(PORT)))

while True:
    try:
        conn, addr = s.accept()
        print(f"Connection from {addr} has been established!")
        # Begin data reading thread
        read_thread = threading.Thread(target = read_async, args = (conn, addr))
        read_thread.start()
        # Begin tkinter thread
        thread_tk = threading.Thread(target = tkinter, args = (conn, addr))
        thread_tk.start()
    except:
        pass
