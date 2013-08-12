from morse.builder import*

# Uploads the robot.
atrv = ATRV()

# Sets the position of the robot.
pose = Pose()
pose.translate(z = 0.75)
atrv.append(pose)

# Allows the velocity and angular velocity of the robot to be manipulated.
motion = MotionVW()
atrv.append(motion)
imu = IMU()

# Configures the socket middleware that can be changed to ROS.
motion.add_default_interface('socket')
pose.add_default_interface('socket')
imu.translate(x=0.9, y=0.0,z=0.2)
atrv.append(imu)

# Creates the environment for the robot to function in.
env = Environment('outdoors')
# Adds the camera and varies its angle.
env.place_camera([5,-5,6])
env.aim_camera([1.0470,0,0.7854])