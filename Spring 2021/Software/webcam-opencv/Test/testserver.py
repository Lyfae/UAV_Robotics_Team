import socket
import json
import struct
import time
from datetime import datetime
import sys	#for exit

def readblob(the_socket,timeout=2):
    #make socket non blocking
    the_socket.setblocking(0)
    
    #total data partwise in an array
    total_data=[]
    data=''
    
    #beginning time
    begin=time.time()
    while 1:
        #if you got some data, then break after timeout
        if total_data and time.time()-begin > timeout:
            break
        
        #if you got no data at all, wait a little longer, twice the timeout
        elif time.time()-begin > timeout*2:
            break
        
        #recv something
        try:
            data = the_socket.recv(8192)
            if data:
                total_data.append(data)
                #change the beginning time for measurement
                begin=time.time()
            else:
                #sleep for sometime to indicate a gap
                time.sleep(0.1)
        except:
            pass
    
    #join all parts to make final string
    return total_data

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 8009        # Port to listen on (non-privileged ports are > 1023)
BUFFER_SIZE = 4096

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
    s.bind((HOST, PORT)) #Bind system socket
    s.listen(3) #Listen for up to 3 connections
    print("Listening on %s:%s..." % (HOST, str(PORT)))

    while True:

        conn, addr = s.accept() 
        with conn:
            print('Connected by', addr)
            data = readblob(conn)
            jdata = ''
            for i in data:
                jdata += i.decode('utf-8')

            # datetime object containing current date and time
            now = datetime.now()
            # dd-mm-YY_at_H-M-S
            dt_string = now.strftime("%d-%m-%Y_at_%H-%M-%S")
            jFile = open(dt_string+".json","w")
            jFile.write(jdata)
            jFile.close()


            print("Connection received from %s..." % str(addr))
            conn.sendall('OK'.encode("ascii"))
            conn.close() 