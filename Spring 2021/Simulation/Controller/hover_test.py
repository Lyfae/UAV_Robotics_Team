#Import required libraries
from tkinter import *
#Create an instance of tkinter frame
win= Tk()
#Define the geometry of the window
win.geometry("750x250")
#Define functions
def on_enter(e):
   button.config(background='OrangeRed3', foreground= "white")

def on_leave(e):
   button.config(background= 'SystemButtonFace', foreground= 'black')
#Create a Button
button= Button(win, text= "Click Me", font= ('Helvetica 13 bold'))
button.pack(pady= 20)

#Bind the Enter and Leave Events to the Button
button.bind('<Enter>', on_enter)
button.bind('<Leave>', on_leave)
win.mainloop()