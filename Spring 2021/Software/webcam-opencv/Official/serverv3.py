#!/usr/bin/env python3

import socket
import json
import sys
from _thread import *
import threading
import movearmv4 as arm #Library for arm movement defined commands
import tkinter as tk
import multiprocessing as multi
import time

HOST = '192.168.0.126'  # Standard loopback interface address (localhost)
PORT = 8009        # Port to listen on (non-privileged ports are > 1023)
BUFFER_SIZE = 8162 
TIME_OUT = 5
SENSOR_COUNT=1
ARM_TIME_OUT = 20

def init_globes():
    global armStatus
    global cameraInput
    global newData
    global state
    armStatus = {"arm_name":"Arm1", "code":2}
    cameraInput = {
        "name":"Camera1", 
        "command":3,
        "dX":0, 
        "dY":0}
    newData = False
    state = 3

#this is for the set home location
HOME = {"X":190,
        "Y":0,
        "Z":100}

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
#3-Error
global armStatus 
armStatus = {}

#This is for the current arm location
# global armLocation 
# armLocation = {}

global newData
global state


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
    global newData
    global armStatus
    global cameraInput
    if(armStatus["code"]==2):
        if(data_recv["name"]==cameraInput["name"]):
            cameraInput["command"] = data_recv["command"]
            cameraInput["dX"] = data_recv["dX"]
            cameraInput["dY"] = data_recv["dY"]
            #Set New Data Flag
            newData=True
    else:
        print(f"Data NOT loaded, ignoring arm status " + str(armStatus["code"]))
    
def stateMachineWorker():
    global state
    global newData
    global cameraInput
    print("Data loaded, initiating command.")
    newData = False
    if cameraInput["command"]==3:
        print("Home command, processing.")
        if state == 1:
            print("Dropping load.")
            arm.drop_load()
        print("Going home.")
        arm.set_location_mapped(HOME)
        state = 3
    elif cameraInput["command"]==1:
        print("Move command, processing.")
        new_location=arm.translate_diff(cameraInput)
        if state == 3:
            print("Grabbing load.")
            arm.grab_load()
        print("Going to differential location.")
        arm.set_location_mapped(new_location)
        state = 1
    elif cameraInput["command"]==2:
        print("Dropping load.")
        arm.drop_load()
        state=2 
    elif cameraInput["command"]==4:
        print("Grabbing load.")
        arm.grab_load()
        state=4
    elif cameraInput["command"]==5:
        print("Test Packet Move.")
        cameraInput["Z"] = int(190)
        cameraInput["X"] = int(cameraInput["dX"])
        cameraInput["Y"] = int(cameraInput["dY"])
        arm.set_location_mapped(cameraInput)
        state = 5    

def read_async(connIn, addr): 
    print(f"[NEW CONNECTION] {addr} connected to r-w-a thread.")
    global armStatus
    global cameraInput
    global newData
    while True:
        try:
            data_recv = connIn.recv(BUFFER_SIZE).decode('utf-8')
            data_recv = json.loads(data_recv)
            print(f"Recieved: {data_recv}, attempting load...")
            load_data(data_recv)
            arm.do_init()
            if newData:
                armStatus["code"] = 1
                '''worker_thread = multi.Process(target = stateMachineWorker, args = ())
                worker_thread.start()
                time.sleep(1)
                worker_thread.join(timeout=ARM_TIME_OUT)
                worker_thread.terminate()'''
                stateMachineWorker()
            armStatus["code"] = 2
            connIn.sendall(json.dumps(armStatus).encode('utf-8')) # encode the dict to JSON
        except:
            armStatus["code"] = 3
            connIn.sendall(json.dumps(armStatus).encode('utf-8')) # encode the dict to JSON
            break

def main():    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT)) #Bind system socket
    s.listen(SENSOR_COUNT) #Listen for up to SENSOR_COUNT connections
    s.settimeout(TIME_OUT) 
    print("Listening on %s:%s..." % (HOST, str(PORT)))
    conn= 0
    addr= 0
    while True:
        try:
            conn, addr = s.accept()
            print(f"Connection from {addr} has been established!")
            # Begin data reading thread
            read_thread = threading.Thread(target = read_async, args = (conn, addr))
            read_thread.start()
            # Begin tkinter thread
            # thread_tk = threading.Thread(target = tkinter, args = (conn, addr))
            # thread_tk.start()\
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
    init_globes()
    main()