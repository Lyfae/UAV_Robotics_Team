import movearmv2 as arm
import time

#RUN TEST 1
while 1:
        arm.do_init()
        home = {"X":90,
                "Y":50,
                "Z":100}
        arm.set_location(home)
        time.sleep(3)

        home = {"X":200,
                "Y":-100,
                "Z":170}
        arm.set_location(home)
        time.sleep(3)

        home = {"X":120,
                "Y":150,
                "Z":80}
        arm.set_location(home)
        time.sleep(3)

        home = {"X":170,
                "Y":170,
                "Z":170}
        arm.set_location(home)
        time.sleep(3)

        home = {"X":90,
                "Y":-200,
                "Z":80}
        arm.set_location(home)
        time.sleep(3)

        home = {"X":190,
                "Y":0,
                "Z":190}
        arm.set_location(home)
        time.sleep(3)

        position = arm.get_XYZ_location()
        print('Final Position = X:' + str(position[0])+', Y:'+str(position[1])+', Z:' +str(position[2]))
        arm.do_shutdown()
