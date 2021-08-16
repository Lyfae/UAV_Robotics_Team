# Import Libraries
import sys
import time
import json
import socket
import tkinter as tk
from _thread import *
import threading

# Custom Files
import simlocation

# Initalize Socket information (For use in localhost only)
HOST = '127.0.0.1'
PORT = 8009
BUFFER_SIZE = 8162
TIME_OUT = 5
CONNECTIONS = 1
ARM_TIME_OUT = 20

def tkinter(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected to tk thread.")
    
    # TKINTER DEFAULT VARIABLES
    HEIGHT = 400
    WIDTH = 400
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
    main()