from morse.builder import *

"""
Simply adds a 4-wheeled outdoor robot that will be used.
"""
atrv = ATRV()


"""
The following methods allow one to manipulate v(velocity) and omega(angular velocity)
of the robot.

(Also functions as the actuator)
"""

motion = MotionVW()
motion.translate(z=0.3)
atrv.append(motion)

"""
Now we append a sensor that will be used with the robot.

(x,y,z) coordinates are part of the data that is sent back. {Yaw, Pitch & Roll}
"""

pose = Pose()
pose.translate(z=0.83)
atrv.append(pose)

pose.add_stream('socket')
pose.add_service('socket')
motion.add_service('socket')

env = Environment('data/environments/land-1/buildings_1')
env.place_camera([5, -5, 6])
env.aim_camera([1.0470, 0, 0.7854])