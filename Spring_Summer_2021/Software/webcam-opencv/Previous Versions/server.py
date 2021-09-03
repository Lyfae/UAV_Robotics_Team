import sys
import socket
import tkinter as tk
import random
import math
import time
import datetime
import json
from PIL import Image, ImageTk
from _thread import *
import threading  

HOST = '127.0.0.1'
PORT = 8009
BUFFER_SIZE = 4096

# GLOBAL VARIABLES
global data_recv
data_recv = {}

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

def read_async(connIn, addr): 
    print(f"[NEW CONNECTION] {addr} connected to r-w-a thread.")
    global data_recv
    while True:
        try:
            data_recv = connIn.recv(8162).decode('utf-8')
            print(f"Recieved: {data_recv}")
        except: 
            print(f"Packet receive attempt to {addr} failed. Closing connection.")
            connIn.close()
            break

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT)) #Bind system socket
s.listen(3) #Listen for up to 3 connections
s.settimeout(5) 
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