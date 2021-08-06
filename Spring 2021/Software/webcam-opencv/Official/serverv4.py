#!/usr/bin/env python3

import socket
import json
import sys
from _thread import *
import threading
import movearmv3 as arm #Library for arm movement defined commands
import multiprocessing as multi
import time

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
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

#These globals are for the current states of the Arm and Server
global newData
global state
