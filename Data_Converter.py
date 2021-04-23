import math
import socket

#Point class Initializer ----------------------------------------------------
class Point:

    def __init__(self, distance, azimuth_angle, vertical_angle, *args):
        self.d = float(distance)
        self.alpha = float(azimuth_angle)
        self.omega = float(vertical_angle)
        #self.pointnum = float(point_number)
        self.x = self.d*math.cos(math.radians(self.omega))*math.sin(math.radians(self.alpha))
        self.y = self.d*math.cos(math.radians(self.omega))*math.cos(math.radians(self.alpha))
        self.z = self.d*math.sin(math.radians(self.omega))
        self.edgeNum = -1
        self.angle = self.calcAngle()
        if len(args) == 2:
            self.x = float(args[0])
            self.y = float(args[1])
            self.angle = self.calcAngle()

    def setEdgeNum(self, EdgeNum):
        self.edgeNum = EdgeNum

    def getEdgeNum(self):
        return self.edgeNum

    def getDistance(self):
        return self.d

    def getAzimuth(self):
        return self.alpha

    def getVertical(self):
        return self.omega

    def getX(self):
        return self.x

    def setX(self, newX):
        self.x = newX
        self.angle = self.calcAngle()
        return self.x

    def getY(self):
        return self.y

    def setY(self, newY):
        self.y = newY
        self.angle = self.calcAngle()
        return self.y

    def getZ(self):
        return self.z

    def getAngle(self):
        return float(self.angle)

    def calcAngle(self):
        if(self.x>0.0 and self.y>=0.0):
            return(math.degrees(math.atan(self.y/self.x)))
        if(self.x>0.0 and self.y<0.0):
            return(math.degrees(math.atan(self.y/self.x))+360)
        if(self.x<0.0):
            return(math.degrees(math.atan(self.y/self.x))+180)
        if(self.x==0.0):
            if(self.y<0.0):
                return(270.0)
            if(self.y>0.0):
                return(90.0)
            if(self.y == 0.0):
                return(0.0)

    def __str__(self):
        return ("Distnance is " + str(self.d) + " mm, azimuth angle is " + str(self.alpha) + " deg, verical angle is " + str(self.omega) + " deg, X is: " + str(self.x) + ", Y is: " + str(self.y) + ", edge number is: " + str(self.edgeNum) + ", angle is: " + str(self.angle) + ".")

    #def cartCoord(self,d,alpha,omega):
    #self.x = self.d*math.cos(math.radians(self.omega))*math.sin(math.radians(self.alpha))
    #self.y = self.d*math.cos(math.radians(self.omega))*math.cos(math.radians(self.alpha))
    #self.z = self.d*math.sin(math.radians(self.omega))

def append_hex(a, b):
    sizeof_b = 0

    # get size of b in bits
    while((b >> sizeof_b) > 0):
        sizeof_b += 1

    # align answer to nearest 4 bits (hex digit)
    sizeof_b += sizeof_b % 4

    return (a << sizeof_b) | b

#-----------------------------------------------------------------------------
#This will create a test string for the LiDAR data and convert ensure that it can be converted to decimal
#at the moment we are using an example packet as the test data
#The lidar data will be called here instead

def port_init():

    UDP_IP = "192.168.1.77"      #LiDAR IP address. This should not change
    UDP_PORT = 2368              #LiDAR Port address. This is defualt to the LiDAR itself

    print("UDP target IP: %s" % UDP_IP)
    print("UDP target port: %s" % UDP_PORT)


    #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    #sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))                           #This binds the port. Can only be done once, returns error if done twice

    return sock
    #while loopvar_data < length :

    #hexi = data[loopvar_data]
    #deci = int(hexi, 16)
    #data_deci.append(deci)

    #loopvar_data = loopvar_data + 1
    #data = "ffee"
    #print("received message: %s" % data)
    #print(data)
#-----------------------------------------------------------------------------
#This will create pointclass for a single data packet of 1200 byte length
def getLiDAR_data(sock):

    print("0")
    data, addr = sock.recvfrom(1248) # buffer size is 1248 bytes
    print("1")
    length = len(data)
    print("2")
    data_deci = list()

    for loopvar_data in data:
        print("something")
        data_deci.append(ord(loopvar_data))

    loopvar0 = 0
    loopvar1 = 0
    loopvar_360 = 0

    lidar_laser_angles = [-15, 1, -13, 3, -11, 5, -9, 7, -7, 9, -5, 11, -3, 13, -1, 15] #index of array refers to number of laser
    lidar_points = list()

    while loopvar_360 < 76: #This is how many times it takes to get a full 360 field of view of points

        while loopvar0 < 12 :
            while loopvar1 < 34 :

                if loopvar1 < 2 :
                    indexer = loopvar0*100 + loopvar1*2
                    if data_deci[indexer] != '0xFF' :

                        tempA = data_deci[indexer+1]
                        tempB = data_deci[indexer]

                        #tempAA = int(tempA, 16)
                        #tempBB = int(tempB, 16)

                        tempC = (hex(append_hex(tempA, tempB)))
                        azimuth = int(tempC, 16) / 100

                elif loopvar1 == 2:
                    indexer = loopvar0*100 + loopvar1*2
                    tempA = data_deci[indexer+1]
                    tempB = data_deci[indexer]

                    #tempAA = int(tempA, 16)
                    #tempBB = int(tempB, 16)

                    tempC = (hex(append_hex(tempA, tempB)))
                    distance = int(tempC, 16) * 2
                    lidar_points.append( Point(distance, azimuth, lidar_laser_angles[0]))

                elif loopvar1 < 18:
                    indexer = indexer + 3
                    tempA = data_deci[indexer+1]
                    tempB = data_deci[indexer]

                    #tempAA = int(tempA, 16)
                    #tempBB = int(tempB, 16)

                    tempC = (hex(append_hex(tempA, tempB)))
                    distance = int(tempC, 16) * 2
                    lidar_points.append( Point(distance, azimuth, lidar_laser_angles[(loopvar1-2)]))

                elif loopvar1 < 34 :
                    indexer = indexer + 3
                    tempA = data_deci[indexer+1]
                    tempB = data_deci[indexer]

                    #tempAA = int(tempA, 16)
                    #tempBB = int(tempB, 16)

                    tempC = (hex(append_hex(tempA, tempB)))
                    distance = int(tempC, 16) * 2
                    lidar_points.append( Point(distance, azimuth, lidar_laser_angles[(loopvar1-18)]))

                loopvar1 = loopvar1 + 1


            loopvar1 = 0
            loopvar0 = loopvar0 + 1
        loopvar0 = 0
        loopvar_360 = loopvar_360 + 1
    loopvar_360 = 0
    return lidar_points
