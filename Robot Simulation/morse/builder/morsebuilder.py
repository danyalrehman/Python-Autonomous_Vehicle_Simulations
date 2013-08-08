from morse.builder.abstractcomponent import *
import logging; logger = logging.getLogger("morsebuilder." + __name__)
import math


class Robot(Component):

    """
    This class sets up the Robot itself and imports it when atrv() is called. The following functions
    also allows to set up other forms of middleware e.g sockets (default setting), ros (robot operating
    system) and others.

    The add default interface function is created to add sockets.
    The add stream function focuses on other forms of middleware such as YARP or ROS.

    The entire process of setting up the middlewares comes from matching their tags.

    """

    def __init__(self, filename):
        Component.__init__(self, 'robots', filename)
        self.properties(Robot_Tag = True)

    def add_default_interface(self, stream):
        """ Permits the use of sockets or other forms of middleware. This is the function
        that allows use of ROS.
        """
        for child in self.children:
            if child.is_morseable():
                child.add_interface(stream)


    def make_external(self):
        self._bpy_object.game.properties['Robot_Tag'].name = 'External_Robot_Tag'

class WheeledRobot(Robot):
    def __init__(self, filename):
        Robot.__init__(self, filename)

    def append(self, obj):
        """ Overloading this function allows you to add different robots to the scene.
        """

        # Correct the rotation of the object
        old = obj._bpy_object.rotation_euler
        obj._bpy_object.rotation_euler = (old[0], old[1], old[2]+math.pi/2)

        # Switch the values of X and Y location
        tmp_x = obj._bpy_object.location[0]
        obj._bpy_object.location[0] = -obj._bpy_object.location[1]
        obj._bpy_object.location[1] = tmp_x

        Robot.append(self, obj, 2)


class Sensor(Component):

    """ This class allows the constructor to be able to set the properties of the current ATRV.
    Then it configures the default sensors unless one prefers to work with others e.g accelerometers,
    imus etc. """
    def __init__(self, filename):
        Component.__init__(self, 'sensors', filename)
        self.properties(Component_Tag = True)

class Actuator(Component):
    """
    This class sets up the component properties in the constructor to match a default setting.
    """
    def __init__(self, filename):
        Component.__init__(self, 'actuators', filename)
        self.properties(Component_Tag = True)

