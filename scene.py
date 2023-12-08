from OpenGL.GL import *

import pygame
import glm

from settings import Settings
from blender import Obj
from camera import Camera
from mesh import CubeMesh, SphereMesh
from model import *
from shaders import ShadowMappingShader
from cube_map import FlattenCubeMap
from environment_mapping import EnvironmentMappingTexture
from shadow_mapping import ShadowMap
from light_source import LightSource


class Scene:
    """Handles the rendering of all objects."""
    def __init__(self, width:int=800, height:int=600, shaders:str=None):
        self.window_size = (width, height)

        # Objects to be rendered
        self.models: list = []

        # Initialise pygame
        pygame.init()
        pygame.display.set_caption("Jurassic Park")
        screen = pygame.display.set_mode(self.window_size, pygame.OPENGL | pygame.DOUBLEBUF, 24)
        
        # Setup the viewport
        glViewport(0, 0, *self.window_size)
        glClearColor(0.4, 0.4, 1.0, 1.0)
        
        # Settings
        self.settings = Settings(self)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnable(GL_DEPTH_TEST)

        # Enable transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Frustum projection matrix
        left = -1.0
        right = 1.0
        bottom = -1.0
        top = 1.0
        near = 1.5
        far = 1000
        self.P = glm.frustum(left, right, bottom, top, near, far)

        self.pan_acceleration = 1.25
        self.pan_velocity = glm.vec3()
        self.pan_speed = 0.1
        self.mouse_mvt = None

        self.mode = 0
        
        self.camera: Camera = Camera()
        self.light = LightSource(self, position=glm.vec3(10, 100, -100),
                                 Ia=glm.vec3(0.25,0.25,0.25),
                                 Id=glm.vec3(1,1,1),
                                 Is=glm.vec3(1,1,1))
        
        # Display the light source with a sphere
        sun_mesh = SphereMesh()
        self.show_light = DrawModelFromMesh(scene=self,
                                        M=glm.translate(self.light.position + glm.vec3(0,5,0)),
                                        name="Sun", mesh=sun_mesh)
        self.add_model(self.show_light)

        # Environment mapping
        self.environment = EnvironmentMappingTexture(width=800, height=800)
        self.in_environment = [] # Models to be rendered as part of the environment
        
        # Shadow mapping
        self.shadows = ShadowMap(light=self.light)

        # When this is made false, the mainloop breaks and program ends
        self.running = True

        self.help = \
        """
        ===== CONTROLS =====
        ----- Settings -----
        0 - Every second, prints useful info about the program.
        1 - Change Render Mode
        2 - Change Cull Mode
        3 - Toggle Shadow Updates (Shadow Mapping)
        4 - Toggle Environment Updates (Environment Mapping)
        5 - Change Shader Mode

        ----- Camera -----
        A/D - Pan X
        W/S - Pan Y
        Q/E - Pan Z
        Right Click and Drag - Rotate
        Up/Down arrows - Increase/Decrease Pan Speed

        ----- Other -----
        ESC - Quit
        H - Displays this help message
        """


    def add_model(self, model: Model) -> None:
        """Adds a model to the scene."""
        self.models.append(model)
    

    def add_models(self, models: list[Model]) -> None:
        """Adds a list of models to the scene."""
        for model in models:
            self.add_model(model)
    
    
    def add_models_from_obj(self, obj_file: str, pos=glm.vec3(),
                            scale=glm.vec3(1,1,1), rotation=glm.vec3(0,0,0),
                            name="", shadows=False, in_environment=False) -> None:
        meshes = Obj(obj_file).load_obj_file()
        
        P = glm.translate(pos)
        S = glm.scale(scale)
        
        x_rot: glm.quat = glm.angleAxis(rotation.x, glm.vec3(1,0,0))
        y_rot: glm.quat = glm.angleAxis(rotation.y, glm.vec3(0,1,0))
        z_rot: glm.quat = glm.angleAxis(rotation.z, glm.vec3(0,0,1))
        R = glm.mat4_cast(y_rot * z_rot * x_rot)
        
        M = P * R * S
        
        models = []
        
        shadow_map = None
        if shadows:
            shadow_map = self.shadows
        env_map = self.environment
        
        for mesh in meshes:
            model = DrawModelFromMesh(scene=self, M=M, mesh=mesh,
                                      env_map=env_map, shadows=shadow_map,
                                      name=name)
            models.append(model)
                
        self.add_models(models)

        if in_environment:
            self.in_environment.extend(models)

        return models
    

    def handle_key_event(self, key: int, keydown: bool) -> None:
        """Handles all keyboard input events."""
        # Direction of the press; -1 is keyup, 1 is keydown
        press_direction = -1

        # Keydown-only events
        if keydown:
            press_direction = 1
            
            match key:
                case pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
                case pygame.K_h:
                    print(self.help)
                case pygame.K_0:
                    self.settings.toggle_update("stats")
                case pygame.K_1:
                    self.settings.next_render_mode()
                case pygame.K_2:
                    self.settings.next_cull_mode()
                case pygame.K_3:
                    self.settings.toggle_update("shadows")
                case pygame.K_4:
                    self.settings.toggle_update("environment")
                case pygame.K_5:
                    self.settings.next_shading_mode()

        # Other events (keyup/keydown)
        match key:
            case pygame.K_a:
                self.pan_velocity.x += press_direction * self.pan_speed
            case pygame.K_d:
                self.pan_velocity.x -= press_direction * self.pan_speed
            case pygame.K_w:
                self.pan_velocity.y += press_direction * self.pan_speed
            case pygame.K_s:
                self.pan_velocity.y -= press_direction * self.pan_speed
            case pygame.K_q:
                self.pan_velocity.z += press_direction * self.pan_speed
            case pygame.K_e:
                self.pan_velocity.z -= press_direction * self.pan_speed
            case pygame.K_UP:
                self.pan_speed *= self.pan_acceleration
                self.pan_velocity *= self.pan_acceleration
                print(f"Increased pan speed to {self.pan_speed}")
            case pygame.K_DOWN:
                self.pan_speed /= self.pan_acceleration
                self.pan_velocity /= self.pan_acceleration
                print(f"Decreased pan speed to {self.pan_speed}")

    
    def handle_event(self, event) -> None:
        """Handles all pygame events."""
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            # Pass the event to key event handler
            self.handle_key_event(event.key, True)
        elif event.type == pygame.KEYUP:
            # Pass the event to key event handler
            self.handle_key_event(event.key, False)
        elif event.type == pygame.MOUSEMOTION:
            # Camera rotation - if holding RMB update mouse_mvt and apply rotation
            # If not holding RMB (right click), reset mouse_mvt for next time
            if pygame.mouse.get_pressed()[2]:
                # Check mouse movement
                if self.mouse_mvt is not None:
                    self.mouse_mvt = pygame.mouse.get_rel()
                    # Convert mouse movement to angles, based on motion relative
                    # to screen width.
                    angles = glm.vec3()
                    angles.x -= 5*(float(self.mouse_mvt[1]) / self.window_size[1])
                    angles.y -= 5*(float(self.mouse_mvt[0]) / self.window_size[0])

                    # Apply these angles as rotation to the camera
                    self.camera.add_rotation(angles)
                else:
                    self.mouse_mvt = pygame.mouse.get_rel()
            else:
                self.mouse_mvt = None
    
        
    def set_shaders(self, name: str) -> None:
        """For every model, uses the shader of type `name`, if it has one."""
        for model in self.models:
            model.set_shader(name)
    
    
    def draw_shadow_map(self) -> None:
        """Draw the shadows to the shadow map."""
        glClear(GL_DEPTH_BUFFER_BIT)
        
        for item in self.models:
            item.draw()


    def draw_reflections(self) -> None:
        """Draw the reflection in an environment-mapped object."""
        self.skybox.draw()
        
        for model in self.in_environment:
            model.draw()


    def draw(self) -> None:
        """Handles all drawing in the scene."""
        
        # Clears the colour and depth bits from previous frame
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Draw skybox - gives impression of increased scale.
        self.skybox.draw()
        
        # Render/store depth of scene in shadow map texture
        if self.settings.updates["shadows"]:
            self.shadows.render(self)
        
        # Render the environment map
        if self.settings.updates["environment"]:
            self.environment.update(self) 
        
        # Render the scene as normal
        for model in self.models:
            model.draw()

        # Double-buffering; flip the buffer.
        pygame.display.flip()


    def next_frame(self) -> None:
        """Carries out one frame of the scene."""
        for event in pygame.event.get():
            self.handle_event(event)

        self.draw()

        # Move the camera, if there is a pan velocity
        if self.pan_velocity != glm.vec3(0,0,0):
            self.camera.move(self.pan_velocity)