
print "Start simulator (SITL)"
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative
import dronekit_sitl
sitl = dronekit_sitl.start_default()
connection_string = sitl.connection_string()

# Import DroneKit-Python

# Connect to the Vehicle.
print("Connecting to vehicle on: %s" % (connection_string,))
vehicle = connect(connection_string, wait_ready=True)


# Get some vehicle attributes (state)
print "Get some vehicle attribute values:"
print " GPS: %s" % vehicle.gps_0
print " Battery: %s" % vehicle.battery
print " Last Heartbeat: %s" % vehicle.last_heartbeat
print " Is Armable?: %s" % vehicle.is_armable
print " System status: %s" % vehicle.system_status.state
print " Mode: %s" % vehicle.mode.name    # settable

def arm_and_takeoff(aTargetAltitude):
#take off to target altitude
    print("Basic pre-arm checks")
    while not vehicle.is_armable:
        print("waiting to initialize")
        time.sleep(1)

    print("Arming motors")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True
    while not vehicle.mode.name == 'GUIDED':
        print("wait")
        time.sleep(1)

    while not vehicle.armed:
        print("Waiting for vehicle to arm....")
        time.sleep(1)

    print("Taking off")
    vehicle.simple_takeoff(aTargetAltitude)
    while True:
        print("Altitude: ", vehicle.location.global_relative_frame.alt)
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * .95:
            print("Altitude reached")
            break
        time.sleep(1)
arm_and_takeoff(10)
# Close vehicle object before exiting script
vehicle.close()


# Shut down simulator
sitl.stop()
print("Completed")