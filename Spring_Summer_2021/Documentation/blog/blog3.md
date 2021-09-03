# Label Robot

**Update: May 7 - May 28, 2021**

*Summary*

Hello Everyone! Water here! Sorry for being gone for a couple of weeks. The team had finals and so we decided to but the brakes on this project in order to focus on our finals. Now that finals are down and we don't have any more distractions, we are going full speed ahead! Since the team took a break to focus on finals, there wasn't much that was done during this time but we did manage to progress a little in both the hardware and software team.  

For the next update, it will be consistent or every two weeks since we won't have anything that will keep up us from posting on time. If there is something that should arise, I wil let you know!

*Hardware Updates*
* The hardware team has been playing with *Dynamixel XM430-W350R* and had a problem with the serial ports. After some extensive research, one of the members found out that there was a problem with the Baud Rate. For the motor, he said that that it would turn if you set the Baud Rate to 1 million instead of 57,600 which is assumed to be the default. 

* From here on out, the hardware team will finish the CAD design and print out the parts for the robotic arm. We aren't sure when this will be accomplished but the group is in the process of finishing it up. 


*Software Updates* 
* The software team has made great progress with their code and optimizing it so the camera detection works better in the previous versions. 

* With the creation of *officialv4.py* we were able to fine-tune our code and update the GUI so that it looks better than the previous one. 

* Changes to the software: 

    * The code has been optimized so that it will only detect the smallest object when the random point simulation is tested. Before, when there were multiple objects inside of the frame, any center point of any object that reached the target location will successfully end the code. In the previous versions, this would be a problem since other objects beside the label could successfully return true that the label has reached it's destination. So we made it so that it will only detect the smallest object, and the center of the smallest object would only be able to return true once it reaches its designated point.

    * THe GUI has has been updated so the the user can toggle between the different states and the modified track bar would enable the users to change the `HSV` (Hue Saturation and Value) so the webcam can pick up a distinct color at a time. By allowing the user to change the `HSV` we are able to detect different colored objects and fade out the colors that we don't want the webcam to pick up.


    * If you would like to visit our GitHub page . . . click [Here](https://github.com/Lyfae/UAV_Robotics_Team)

* If you would like to see some of our test images, you can follow this path here:`UAV_Robotics_Team > Spring 2021 > Software > webcam-opencv > Official > data > images `.

 * Here is the path for the `officialv4.py` : `UAV_Robotics_Team > Spring 20201 > Software > webcam-opencv > Official `

 * If you would like to use access the `Tag link` to our fourth version, please click [Here](https://github.com/Lyfae/UAV_Robotics_Team/releases/tag/v0.4)

 *Goals* 
 * Hardware:
    * The goal for the hardware team in the next coming weeks it to play around with the *Dynamixel XM430-W350R* and calculate the measurements for it so we can slowly incorporate it with the software. 

* Software: 
    * The goal for the software is trying to create a server so we can send the commands that the webcam picks up to the server which will give directions to the hardware - telling it how it should move. We are also planning to automate the entire process so we don't have to manually use the remote control to manually input directions. 

This is what I have for this week! See you next time!

Edited by [P.T]