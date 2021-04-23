from __future__ import print_function
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative
from pointCollection import pointCollection
from Data_Converter import port_init, getLiDAR_data

currentVelocity = ()  # form of: (x,y,z,xyAngle,zAngle)
dimension = 5
start = 0

# Set up option parsing to get connection string
import argparse

from pymavlink import mavutil

parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
parser.add_argument('--connect',
                    help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
sitl = None


# Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()


# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)


def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto
    #  (otherwise the command after Vehicle.simple_takeoff will execute
    #   immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


def send_ned_velocity(velocity_x, velocity_y, velocity_z, duration):
    """
    Move vehicle in direction based on specified velocity vectors.
    """
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
        0b0000111111000111, # type_mask (only speeds enabled)
        0, 0, 0, # x, y, z positions (not used)
        velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
        0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
    # send command to vehicle on 1 Hz cycle
    for x in range(0,duration):
        vehicle.send_mavlink(msg)
        time.sleep(1)

def condition_yaw(heading, relative=False):
    if relative:
        is_relative=1 #yaw relative to direction of travel
    else:
        is_relative=0 #yaw is an absolute angle
    # create the CONDITION_YAW command using command_long_encode()
    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_CONDITION_YAW, #command
        0, #confirmation
        heading,    # param 1, yaw in degrees
        0,          # param 2, yaw speed deg/s
        1,          # param 3, direction -1 ccw, 1 cw
        is_relative, # param 4, relative offset 1, absolute angle 0
        0, 0, 0)    # param 5 ~ 7 not used
    # send command to vehicle
    vehicle.send_mavlink(msg)

def begin():
    sock = port_init()
    print("are we fucked")
    points = getLiDAR_data(sock)
    print("we fucked")
    print(len(points))
    converter = pointCollection.py(30, points)
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
                    specificSubset.append(p)
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


arm_and_takeoff(10)

print("Set default/target airspeed to 3")
vehicle.airspeed = 3

begin()

# print("Going towards first point for 30 seconds ...")
# point1 = LocationGlobalRelative(-35.361354, 149.165218, 20)
# vehicle.simple_goto(point1)

# sleep so we can see the change in map
time.sleep(30)

# print("Going towards second point for 30 seconds (groundspeed set to 10 m/s) ...")
# point2 = LocationGlobalRelative(-35.363244, 149.168801, 20)
# vehicle.simple_goto(point2, groundspeed=10)

# sleep so we can see the change in map
time.sleep(30)

print("Returning to Launch")
vehicle.mode = VehicleMode("RTL")

# Close vehicle object before exiting script
print("Close vehicle object")
vehicle.close()

# Shut down simulator if it was started.
if sitl:
    sitl.stop()