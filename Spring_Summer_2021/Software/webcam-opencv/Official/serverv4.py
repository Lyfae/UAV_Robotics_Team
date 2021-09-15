#!/usr/bin/env python3

import socket
import json
import sys
from _thread import *
import threading
import movearmv4 as arm #Library for arm movement defined commands
import multiprocessing as multi
import time
import ipaddress

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 8009        # Port to listen on (non-privileged ports are > 1023)
BUFFER_SIZE = 8162 
TIME_OUT = 5
SENSOR_COUNT=1
ARM_TIME_OUT = 20

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

#This is for the current arm status codes
#1-Moving
#2-Waiting
#3-Error
ARM_NAME = "Arm1"
#Arm code moved to connection daemon

def init_globes():
    global cameraInput
    cameraInput = {
        "name":"Camera1", 
        "command":3,
        "dX":0, 
        "dY":0}

def init_addr(ipaddr):
    HOST=ipaddr

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
            read_thread.daemon = True
            read_thread.start()
        except KeyboardInterrupt: 
            if conn:
                print("Closing Client Connection")
                conn.close() 
            if s:
                print("Closing Server Socket")
                s.close()
            print("Exiting")
            sys.exit(1)
        except:
            pass

def read_async(connIn, addr): 
    print(f"[NEW CONNECTION] {addr} connected to r-w-a thread.")
    newData = False
    armStatusCode = 2
    state = 3
    while True:
        try:
            data_recv = connIn.recv(BUFFER_SIZE).decode('utf-8')
            data_recv = json.loads(data_recv)
            print(f"Recieved: {data_recv}, attempting load...")
            newData = load_data(data_recv,armStatusCode)
            arm.do_init()
            if newData:
                newData = False
                armStatusCode = 1
                '''worker_thread = multi.Process(target = stateMachineWorker, args = ())
                worker_thread.start()
                time.sleep(1)
                worker_thread.join(timeout=ARM_TIME_OUT)
                worker_thread.terminate()'''
                state = stateMachineWorker(state)
            armStatusCode = 2
            connIn.sendall(json.dumps({"arm_name":ARM_NAME, "code":armStatusCode}).encode('utf-8')) # encode the dict to JSON
        except:
            armStatusCode = 3
            connIn.sendall(json.dumps({"arm_name":ARM_NAME, "code":armStatusCode}).encode('utf-8')) # encode the dict to JSON
            break

def load_data(data_recv, code):
    #Validate data
    newData = False
    global cameraInput
    if(code==2):
        if(data_recv["name"]==cameraInput["name"]):
            cameraInput["command"] = data_recv["command"]
            cameraInput["dX"] = data_recv["dX"]
            cameraInput["dY"] = data_recv["dY"]
            #Set New Data Flag
            newData=True
    else:
        print(f"Data NOT loaded, ignoring arm status {code}" )
    return newData

def stateMachineWorker(state):
    global cameraInput
    print("Data loaded, initiating command.")
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
    return state

if __name__ == '__main__':
    init_globes()
    if sys.argv[1]:
        try:
            socket.inet_aton(sys.argv[1])
            init_addr(sys.argv[1])
        except socket.error:
            pass     
    main()