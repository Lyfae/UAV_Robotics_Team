#arm static definitions
#All units are in mm

import math

#Arm Measurements
BASE_HEIGHT = 48.9 
BICEP_LENGTH=200
FOREARM_LENGTH=200
END_LENGTH=38.6
END_DEPTH=11.3
END_BIT=7

#Arm Min-Max Angles as per diagram
BASE_L_UP=175 
BASE_L_DOWN = 5
BICEP_L_DOWN=45
BICEP_L_UP = 125
FOREARM_L_UP = 45
FOREARM_L_DOWN = -15

#Arm offset angles for given motor positions
#DIRECTION CURRENTLY UNIMPLEMENTED
BASE_OFFSET = 0
BASE_DIRECTION = 1
BICEP_OFFSET = 0
BICEP_DIRECTION = 1
FOREARM_OFFSET = math.radians(-8)
FOREARM_DIRECTION = 1

#Various Increments
TOLERANCE = 1 #this is how close it will try and get in mm to the target location
R_INCREMENT = math.radians(0.1) #this controls by how much it will try to increment the degrees

#Arm Positions
thetaBaseN = 0
ThetaBicepN = 0
ThetaForearmN = 0
#Arm Positions in degrees
thetaBaseND = 0
ThetaBicepND = 0
ThetaForearmND = 0

#gets locations from arm
# 0-base,1-bicep,2-forearm
def get_location():
    #gets current motor angles from w/e as an array of 3
    #(base, bicep, forearm)
    print("getting location not implemented")


#takes coordinates and sends angles to motors
# 0-base,1-bicep,2-forearm
def set_location(xyzdict):
    Xn = xyzdict["X"]
    Yn = xyzdict["Y"]
    Zn = xyzdict["Z"]

    #Calculate the ideal projection on the x-y plane
    pideal = math.sqrt((Xn**2)+(Yn**2))

    #calculate the theta for the base
    thetaBaseN = calcBaseTheta(Xn,Yn)

    if BASE_L_DOWN <= thetaBaseN[1] <= BASE_L_UP :
        scrollTest = 1
        if pideal< FOREARM_LENGTH:
            scrollTest = -1
        thetaBicepN=calcBicepTheta(pideal+scrollTest,0)[0]
        thetaForearmN=calcForearmTheta(Zn,thetaBicepN)[0]
        tempPZ = getPZ(thetaBicepN,thetaForearmN)
        countcycles = 0
        while not(pideal-TOLERANCE)<tempPZ[0]<(pideal+TOLERANCE):
            if tempPZ[0]>(pideal+1):
                thetaBicepN = thetaBicepN+R_INCREMENT
            else:
                thetaBicepN = thetaBicepN-R_INCREMENT
            thetaForearmN=calcForearmTheta(Zn,thetaBicepN)[0]
            tempPZ = getPZ(thetaBicepN,thetaForearmN)
            countcycles += 1

        thetaBicepND = math.degrees(thetaBicepN)    
        thetaForearmND = math.degrees(thetaForearmN)
        thetaBaseND = thetaBaseN[1]
        print('BASE ANGLE = ' + str(thetaBaseND))
        print('BICEP ANGLE = ' + str(thetaBicepND))
        print('FOREARM ANGLE = ' + str(thetaForearmND))
        print('Number of Cycles For Answer = ' + str(countcycles))
        XYZtemp = getXYZ(thetaBaseN[0], thetaBicepN, thetaForearmN)
        print('XYZ Value:'+str(XYZtemp))

        if not(BICEP_L_DOWN<thetaBicepND<BICEP_L_UP):
            print("BICEP Can't Rotate That Far, Current Limits are:"+str(BICEP_L_DOWN)+"-"+str(BICEP_L_UP))
        elif not(FOREARM_L_DOWN<thetaForearmND<FOREARM_L_UP):
            print("FOREARM Can't Rotate That Far, Current Limits are:"+str(FOREARM_L_DOWN)+"-"+str(FOREARM_L_UP))
        #else:
        # moveresults = domsfunction(anglesArray)
    else:
        print('BASE ANGLE = ' + str(thetaBaseN[1]))
        print("Base Can't Rotate That Far, Current Limits are:"+str(BASE_L_DOWN)+"-"+str(BASE_L_UP))





#takes camera x/y diff and turn to coodinates
def translate_diff():
    print("translate_diff not implemented")
#predefined locations for z down
def drop_load():  
    print("drop_load not implemented")
#predefined locations for x-y-z up
def grab_load():
    print("grab_load not implemented")

#this method returns P and Z 
# where P is the 'roe' the projection of the distance on the x-y plane
# Z is the height above the x-y plane
def getPZ(ThetaBi, ThetaFo):
    P = END_LENGTH+FOREARM_LENGTH*math.cos(ThetaFo-FOREARM_OFFSET)+BICEP_LENGTH*math.cos(ThetaBi-BICEP_OFFSET)
    Z = BASE_HEIGHT-END_DEPTH-END_BIT+FOREARM_LENGTH*math.sin(-(ThetaFo-FOREARM_OFFSET))+BICEP_LENGTH*math.sin(ThetaBi+BICEP_OFFSET)
    return([P, Z])


#this method returns the theoretical X-Y-Z based on P and Z
def getXYZ(ThetaBa, ThetaBi, ThetaFo):
    ThetaXYPlane = ThetaBa - math.radians(90) - BASE_OFFSET
    tempPZ = getPZ(ThetaBi, ThetaFo)
    Zres = tempPZ[1]
    Xres = tempPZ[0]*math.cos(ThetaXYPlane)
    Yres = tempPZ[0]*math.sin(ThetaXYPlane)
    return([Xres,Yres,Zres])

#This method returns the calculated base theta based on measurements of the arm
# It takes the arguements of X and Y
# It returns an array of the radian measurement and the degree measurement in that order
def calcBaseTheta(X,Y):
    thetaBaseR = math.atan(Y/X) + math.pi/2 + BASE_OFFSET
    thetaBaseD = math.degrees(thetaBaseR)
    return ([thetaBaseR,thetaBaseD])

#This method returns the calculated bicep theta based on measurements of the arm
# It takes the arguements of the ideal rho or 'P' and ForearmTheta
# It returns an array of the radian measurement and the degree measurement in that order
def calcBicepTheta(P,thetaForearm):
    thetaBicepR=(math.acos((P-END_LENGTH-FOREARM_LENGTH*math.cos(thetaForearm-FOREARM_OFFSET))/BICEP_LENGTH))+BICEP_OFFSET
    thetaBicepD=math.degrees(thetaBicepR)
    return ([thetaBicepR,thetaBicepD])

#This method returns the calculated forearm theta based on measurements of the arm
# It takes the arguements of the ideal z and BicepTheta
# It returns an array of the radian measurement and the degree measurement in that order
def calcForearmTheta(Z,thetaBicep):
    thetaForearmR=-1*math.asin((Z-BASE_HEIGHT+END_DEPTH+END_BIT-BICEP_LENGTH*math.sin(thetaBicep-BICEP_OFFSET))/FOREARM_LENGTH)+FOREARM_OFFSET
    thetaForearmD=math.degrees(thetaForearmR)
    return ([thetaForearmR,thetaForearmD])

#motor drive functions
#this is where we will put hardware team functions

