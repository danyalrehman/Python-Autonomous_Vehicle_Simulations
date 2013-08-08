import logging; logger = logging.getLogger("morsebuilder." + __name__)
import os
import json
from morse.builder.morsebuilder import *

class Environment(Component):


    multinode_distribution = dict()

    def __init__(self, filename, fastmode = False):

        Component.__init__(self, 'environments', filename)
        AbstractComponent.components.remove(self)

        self._rename_components()

        self.fastmode = fastmode

        self._created = False
        self._camera_location = [5, -5, 5]
        self._camera_rotation = [0.7854, 0, 0.7854]
        self._environment_file = filename
        self._multinode_configured = False
        self._display_camera = None
        self.is_material_mode_custom = False

        if not 'Scene_Script_Holder' in bpymorse.get_objects():

            base = Component('props', 'basics')
        self.set_blender_object(bpymorse.get_object('Scene_Script_Holder'))


    def _write_multinode(self, node_name):

        if not self._multinode_configured:
            return
        if not node_name in self.multinode_distribution.keys():
            logger.warning("Node " + node_name + " is not defined in the " + \
                "env.multinode_distribution dict. It will manage no robot!")
            self.multinode_distribution[node_name] = []
        for obj in bpymorse.get_objects():
            p = obj.game.properties

            if obj.name in self.multinode_distribution[node_name]:
                if not 'Robot_Tag' in p:
                    logger.warning(obj.name + " is not a robot!." + \
                        " Will not be published by this MORSE node.")
                else:
                    logger.info("Node " + node_name + \
                        " will publish robot" + obj.name)

            if 'Robot_Tag' in p:
                if not obj.name in self.multinode_distribution[node_name]:
                    logger.debug("Node " + node_name + \
                        " will not publish robot " + obj.name)
                    p['Robot_Tag'].name = 'External_Robot_Tag'

                    obj.game.physics_type = 'STATIC'

        node_config = { 'protocol': self._protocol,
                        'node_name': node_name,
                        'server_address': self._server_address,
                        'server_port': self._server_port,}

        if not 'multinode_config.py' in bpymorse.get_texts.keys():
            bpymorse.new_text()
            bpymorse.get_last_text().name = 'multinode_config.py'
        cfg = bpymorse.get_text('multinode_config.py')
        cfg.clear()
        cfg.write('node_config = ' + json.dumps(node_config, indent=1) )
        cfg.write('\n')

    def _rename_components(self):

        import inspect
        try:
            frame = inspect.currentframe()
            builderscript_frame = inspect.getouterframes(frame)[2][0]

            for name, component in builderscript_frame.f_locals.items():
                if isinstance(component, AbstractComponent):

                    if hasattr(component, "parent"):
                        continue

                    if not component.basename:
                        component.basename = name

                    def renametree(cmpt, fqn):
                        if not cmpt.basename:
                            raise SyntaxError("You need to assign the component of type %s to a variable" %
                                             cmpt)
                        fqn.append(cmpt.basename)
                        new_name = '.'.join(fqn)
                        Configuration.update_name(cmpt.name, new_name)
                        cmpt._bpy_object.name = '.'.join(fqn)
                        for child in cmpt.children:
                            renametree(child, fqn[:])

                    renametree(component, [])
        finally:
            del builderscript_frame
            del frame

# The following functions allow the camera to be positioned in blender choice.
# This also permits the user to set the values of the Euler Angles of the camera in order to
        # conclude where the robot (atrv) should be seen from.


    def place_camera(self, location):
        """
        This function produces the camera and sets it at a default location.
        The following functions permit the changing of Euler angles to place the camera where
        the user requires it to be set.
        """

        self._camera_location = location

    def aim_camera(self, rotation):

        """
        This function places the camera at the angles specified by the user. It varies each the x,
        y and z coordinates in order to optimize the direction of aim of the camera.
        """

        self._camera_rotation = rotation

    def set_camera_clip(self, clip_start=0.1, clip_end=100):

        camera_fp = bpymorse.get_object('CameraFP')

        camera_fp.data.clip_start = clip_start
        camera_fp.data.clip_end = clip_end

    def create(self, name=None):

        try:

            for component in AbstractComponent.components:
                if hasattr(component, "after_renaming"):
                    component.after_renaming()

            if name == None:
                try:
                    name = os.environ["MORSE_NODE"]
                except KeyError:
                    name = os.uname()[1]

            Configuration.write_config()
            self._write_multinode(name)

            if self._display_camera:
                self._set_scren_mat()

            self.properties(environment_file = str(self._environment_file))

            camera_fp = bpymorse.get_object('CameraFP')
            camera_fp.location = self._camera_location
            camera_fp.rotation_euler = self._camera_rotation

            if self.fastmode:
                self.set_material_mode('SINGLETEXTURE')
                self.set_viewport("WIREFRAME")
            elif not self.is_material_mode_custom:

                self.set_material_mode('GLSL')

            bpymorse.get_context_scene().unit_settings.system = 'METRIC'

            bpymorse.get_context_scene().game_settings.frame_type = 'EXTEND'

            bpymorse.get_context_scene().game_settings.show_mouse = True


            bpymorse.deselect_all()
            camera_fp.select = True
            bpymorse.get_context_scene().objects.active = camera_fp
            bpymorse.get_context_scene().camera = camera_fp

            self._created = True
        except BaseException:
            logger.error("Your MORSE Builder script is invalid!")
            import traceback
            traceback.print_exc()
            os._exit(-1)

    def set_horizon_color(self, color=(0.05, 0.22, 0.4)):

        bpymorse.get_context_scene().world.horizon_color = color

    def show_debug_properties(self, value=True):

        if isinstance(value, bool):
            bpymorse.get_context_scene().game_settings.show_debug_properties = value

    def show_framerate(self, value=True):

        if isinstance(value, bool):
            bpymorse.get_context_scene().game_settings.show_framerate_profile = value

    def show_physics(self, value=True):

        if isinstance(value, bool):
            bpymorse.get_context_scene().game_settings.show_physics_visualization = value

    def set_gravity(self, gravity=9.81):

        if isinstance(gravity, float):
            bpymorse.get_context_scene().game_settings.physics_gravity = gravity

    def set_material_mode(self, material_mode='GLSL'):

        bpymorse.get_context_scene().game_settings.material_mode = material_mode
        self.is_material_mode_custom = True

    def set_viewport(self, viewport_shade='WIREFRAME'):

        for area in bpymorse.get_context_window().screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.viewport_shade = viewport_shade

    def set_auto_start(self, auto_start=True):
        bpymorse.get_context_scene().render.engine = 'BLENDER_GAME'
        bpymorse.get_context_scene().game_settings.use_auto_start = auto_start

    def set_debug(self, debug=True):
        bpymorse.set_debug(debug)

    def set_stereo(self, mode='ANAGLYPH', eye_separation=0.1, stereo='STEREO'):

        bpymorse.get_context_scene().game_settings.stereo = stereo
        bpymorse.get_context_scene().game_settings.stereo_mode = mode
        bpymorse.get_context_scene().game_settings.stereo_eye_separation = eye_separation

    def set_animation_record(self, record=True):

        bpymorse.get_context_scene().game_settings.use_animation_record = record

    def configure_multinode(self, protocol='socket',
            server_address='localhost', server_port='65000', distribution=None):

        self._protocol = protocol
        self._server_address = server_address
        self._server_port = server_port
        if distribution != None:
            self.multinode_distribution = distribution
        self._multinode_configured = True

    def configure_service(self, datastream):
        logger.warning("configure_service is deprecated, use add_service instead")
        return self.add_service(datastream)

    def add_service(self, datastream):

        AbstractComponent.add_service(self, datastream, "simulation")
        self._display_camera = robot_camera

    def _set_scren_mat(self):

        camera = None
        screen = bpymorse.get_object('Screen')
        caption = bpymorse.get_object('CameraID_text')
        blender_component = self._display_camera._bpy_object
        for child in blender_component.children:
            if 'CameraMesh' in child.name:
                camera = child
                break
        if not camera:
            logger.warning("BUILDER WARNING: Argument to 'select_display_camera' is not a camera (%s). Camera display will not work" % self._display_camera.name)
            return
        for mat in camera.material_slots:
            if "ScreenMat" in mat.name:
                material = mat.material
                break
        logger.debug ("Setting material %s for the Screen" % material)
        screen.active_material = material

        screen.game.properties['Visible'].value = True

        caption.game.properties['Text'].value = self._display_camera.name

    def save(self, filepath=None, check_existing=False):

        bpymorse.save(filepath=filepath, check_existing=check_existing)

    def __del__(self):
        if not self._created:
            self.create()
