import time
from pointCollection import pointCollection
from Data_Converter import port_init, getLiDAR_data
import pickle
#from dronekit import connect, VehicleMode

currentVelocity = ()  # form of: (x,y,z,xyAngle,zAngle)
dimension = 5
start = 0


def begin():
    sock = port_init()
    points = getLiDAR_data(sock)
    print(len(points))
    converter = pointCollection(30, points)
    callMethods(sock, converter)


def callMethods(sock, converter):
    INTERRUPT = 'FALSE'
    # count = 0
    global start
    start = time.time()

    while INTERRUPT == 'FALSE':
        print("call obstacle avoidance algorithm")
        points = getLiDAR_data(sock)
        # temp = startAvoidance(points)
        # if temp is not None:
        #     #send_ned_velocity(temp[0].x * -1, temp[0].y * -1, [0].z * -1, .5)
        #     start = time.time() - .5  # ensures .5 second delay before pathing alters the drone path again
        time.sleep(0.1)

        # When 1 sec or more has elapsed...
        if time.time() - start > 1:
            start = time.time()
            # This will be called once per second
            print("call pathing algorithm")
            #       if(count >= 0):
            points2 = []
            i = 0
            for point in points:
                i += 1
                if point.getVertical()==1:
                   points2.append(point)

            with open('test.txt', 'wb') as file:
                pickle.dump(points2,file)
                file.close()
            with open('test.txt', 'rb') as file:
                temp = pickle.load(file)
                file.close()
                print(len(temp))



            testTime = (time.time())
            converter.setNewPoints(points2)

            print(converter.findDirectionTo(0, 1000))
            print(time.time()-testTime)

        #  pointCollection.findDirectionTo(dx,dy)


# call this method and it will call the others
def startAvoidance(pointList):
    global currentVelocity
    currentVelocity = vehicle.velocity
    specificSubset = avoidRectangular(currentVelocity.x, currentVelocity.y, currentVelocity.z, pointList)  # efficient method to shrink the list by limiting points to only those in range of velocity components
    return avoidPolar(specificSubset)  # uses the smaller list, if not empty, to detect possible collision


# inputs: x,y,z components of velocity and the list of points from the most recent lidar scan
def avoidRectangular(x, y, z, pointList):
    specificSubset = []
    for p in pointList:
        if (0 < x < p.x) or (0 > x > p.x):
            if (0 < y < p.y) or (0 > y > p.y):
                if (0 < z < p.z) or (0 > z > p.z):
                    specificSubset.add(p)
    return specificSubset

    # find all points with x in a range between 0m and the x component of velocity, eliminate all others. repeat with y and z
    # if the list of points is not empty, then check the angle of each point


def avoidPolar(specificSubset):
    collisionPoints = []
    for p in specificSubset:
        # calculate if the angles collide. if they do, stop or reverse movement
        if currentVelocity.xyAngle - dimension < p.azimuth < currentVelocity.xyAngle + dimension:
            if currentVelocity.zAngle - dimension < p.azimuth < currentVelocity.zAngle + dimension:
                # following line to be replaced with an output: 0 if no change, or intended change in velocity if
                # collision is detected
                collisionPoints.append(p)
    return collisionPoints
    # actual behavior of the avoidance to be determined, though this is a simple solution that would work


begin()
