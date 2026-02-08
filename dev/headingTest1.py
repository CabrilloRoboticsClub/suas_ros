#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np

import math
import os

plt.ion()
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.title("Line Plot with Markers")
plt.plot(np.nan, np.nan, color="green", marker="o", label="angle")
plt.plot(np.nan, np.nan, color="blue", marker="o", label="heading")
plt.plot(np.nan, np.nan, color="red", marker="o", label="bearing")
plt.plot(np.nan, np.nan, color="yellow", marker="o", label="normal'd pos")
plt.legend()

import logging
logging.basicConfig(
    filename=os.getcwd() + '/log/suas_heading_test_output.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)


class msgCls():
    latitude = 0
    longitude = 0

class tmp():
    def __init__(self):
        self.lastPos = {"latitude":0, "longitude":0, "altitude":0}
        self.lastHeading = -1000

    def getHeading(self, msg):
            if self.lastPos["latitude"] != msg.latitude or self.lastPos["longitude"] != msg.longitude:
                
                #https://forum.arduino.cc/t/get-the-direction-using-gps-without-compass/502005/3
                #https://github.com/SlashDevin/NeoGPS/blob/master/src/Location.cpp#L110
                #http://www.movable-type.co.uk/scripts/latlong.html
                
                #math.atan2(msg.latitude - self.lastPos["latitude"], msg.longitude - self.lastPos["longitude"])
                theta = math.atan2(msg.latitude - self.lastPos["latitude"], msg.longitude - self.lastPos["longitude"])

        
                theta = math.degrees(theta)
                #tmp = (tmp + 360) % 360

                beta = (90 - theta) % 360
                #if beta < 0:
                #    beta += 360
                
                self.lastHeading = beta


                #logging.info(f'tan {math.degrees(math.atan(math.sqrt(math.pow( msg.latitude - self.lastPos["latitude"],2) + math.pow(msg.longitude - self.lastPos["longitude"] ,2))))}')
                
                lat1 = self.lastPos["latitude"]
                lat2 = msg.latitude
                long1 = self.lastPos["longitude"]
                long2 = msg.longitude

                y = math.sin(long2 - long1) * math.cos(lat2)
                x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(long2 - long1)
                bearing = math.atan2(y, x)
                logging.info(f"bearing: {math.degrees(bearing)}")
                # bearing is from [-180, 180)
                # theta is from [0, 360)
                # moving red arrow in gazebo to the left is towards true north (~360/0 segrees off of true north)
                # moving red arrow in gazebo to the right is towards true south (~180/-180 degrees off of true north)
                # moving green arrow in gazebo away is towards west
                # moving green arrow in gazebo closer is towards east
                # seems like beta and bearing are counting in opposite directions
                #   when beta is 359.99974057483695, bearing is 0.00017966901917246036
                #   when beta is 89.99987641761386, bearing is -90.0003406425087
                #   when beta is 179.99974056364942, bearing is -179.99982033705527
                #   when beta is 269.99985104334064, bearing is 90.00075672182112

                #   when beta is 219.9971989426276, bearing is 149.8402788532371
                #   when beta is 26.559046348171755, bearing is -19.095648566865947

                # confirmed that when taking a measurement and moving in the same direction without changing angle, 
                #   the measurement by lastHeading and bearing will be the same as the previous measurement
                # not sure if it would be more useful to have angle from north in range [-180, 180) (bearing) or [0, 360) (beta)
                # CONCLUSION FROM GRAPH:
                #   beta works perfectly; angle of 45 degrees from 0 degrees is the same as 45 degrees from north (90 degrees)
                #       while bearing's measurement is all over the place for the same input
                #
                #   with beta (heading), west is 270 degrees, east is 90 degrees, south is 180 degrees, north is 0 degrees

                self.lastPos["latitude"] = msg.latitude
                self.lastPos["longitude"] = msg.longitude
            
                logging.info(f"lastHeading: {self.lastHeading} degrees off of north")

                #tmp = math.atan(math.sqrt(math.pow( msg.latitude - self.lastPos["latitude"],2) + math.pow(msg.longitude - self.lastPos["longitude"] ,2))))


                plt.plot(math.cos(math.radians(self.lastHeading)), math.sin(math.radians(self.lastHeading)), color="blue", marker="o")
                plt.plot(math.cos(bearing)*1.1, math.sin(bearing)*1.1, color="red", marker="o")
                #plt.plot(math.cos(tmp)*1.3, math.sin(tmp)*1.3, color="orange", marker="o")
                #plt.show()
                plt.draw()
                plt.pause(0.1)


instance = tmp()
message = msgCls()

initialPos = [40, 40]

#plottedX = []
#plottedY = []
'''
for i in range(0, 360):
    theta = 45
    message.latitude = initialPos[1]
    message.longitude = initialPos[0]
    plt.plot((message.longitude - 600)/600, (message.latitude - 600)/600, color="yellow", marker="o")

    plt.plot(math.cos(math.radians(theta))  * 1.2, math.sin(math.radians(theta)) * 1.2, color="green", marker="o")
    instance.getHeading(message)
    #plottedX.append(initialPos[0])
    #plottedY.append(initialPos[1])

    

    initialPos[0] += math.cos(math.radians(theta)) * 10
    initialPos[1] += math.sin(math.radians(theta)) * 10
'''


for i in range(0, 360):
    message.latitude = initialPos[1]
    message.longitude = initialPos[0]
    plt.plot((message.longitude - 600)/600, (message.latitude - 600)/600, color="yellow", marker="o")

    plt.plot(math.cos(math.radians(i))  * 1.2, math.sin(math.radians(i)) * 1.2, color="green", marker="o")
    instance.getHeading(message)
    #plottedX.append(initialPos[0])
    #plottedY.append(initialPos[1])

    

    initialPos[0] += math.sin(math.radians(i)) * 10
    initialPos[1] += math.cos(math.radians(i)) * 10




