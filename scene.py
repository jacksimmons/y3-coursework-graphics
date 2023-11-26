from OpenGL.GL import *

import pygame
import glm

from blender import Obj
from camera import Camera
from model import *
from shaders import Shader
from environment_mapping import EnvironmentMappingTexture
from matutils import (frustumMatrix, translationMatrix, scaleMatrix,
                      poseMatrix, rotationMatrix)
from light_source import LightSource


class Settings:
    def __init__(self, scene):
        self.scene = scene

        self.render_mode: int
        self.render_modes: list =\
            [GL_POINT, GL_LINE, GL_FILL]
        self.render_modes_verbose: list =\
            ["Point", "Line", "Fill"]
        self.set_render_mode(2)

        self.cull_mode: int
        self.cull_modes: list =\
            [GL_BACK, GL_FRONT]
        self.cull_modes_verbose: list =\
            ["Back face", "Front face"]
        self.set_cull_mode(1)

        # Must be set before vertex colours, as vertex colours needs
        # self.shaders.
        self.shading_mode: int = 0
        self.shading_modes: list =\
            ["flat"]
        
        self.is_shown = {"shadows": True, "reflections": True, "fps": False}
    

    def set_render_mode(self, value: int):
        self.render_mode = value
        glPolygonMode(GL_FRONT_AND_BACK, self.render_modes[value])


    def set_cull_mode(self, value: int):
        self.cull_mode = value
        glEnable(GL_CULL_FACE)
        glCullFace(self.cull_modes[value])
    

    def next(self, value: int, length: int):
        value += 1
        if value >= length:
            value = 0
        return value
    

    def next_render_mode(self):
        self.set_render_mode(self.next(self.render_mode, len(self.render_modes)))
        print("Changed render mode to: " + self.render_modes_verbose[self.render_mode])
    

    def next_cull_mode(self):
        self.set_cull_mode(self.next(self.cull_mode, len(self.cull_modes)))
        print("Changed cull mode to: " + self.cull_modes_verbose[self.cull_mode])
    

    def next_shading_mode(self):
        self.set_shading_mode(self.next(self.shading_mode, len(self.shading_modes)))
        print("Changed shading mode to: " + self.shading_modes[self.shading_mode])


    def toggle_shown(self, key):
        self.is_shown[key] = not self.is_shown[key]
        if self.is_shown[key]:
            output = "Enabled "
        else:
            output = "Disabled "
        print(output + key)


class Scene:
    def __init__(self, width:int=800, height:int=600, shaders:str=None):
        self.window_size = (width, height)

        # Objects to be rendered
        self.models: list = []

        # Initialise pygame
        pygame.init()
        pygame.display.set_caption("Jurassic Park")
        screen = pygame.display.set_mode(self.window_size, pygame.OPENGL | pygame.DOUBLEBUF, 24)
        
        glViewport(0, 0, *self.window_size)
        glClearColor(0.4, 0.4, 1.0, 1.0)
        
        # Settings
        self.settings = Settings(self)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnable(GL_DEPTH_TEST)

        # For text transparency
        #glEnable(GL_BLEND)
        #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Projective Transform
        # - Clipping Planes
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

        self.shaders = "flat"

        self.camera: Camera = Camera()
        self.environment = EnvironmentMappingTexture(width=400, height=400)
        
        self.has_shadows = []
        self.mirrors = []


    def add_model(self, model):
        self.models.append(model)
    

    def add_models(self, models):
        for model in models:
            self.add_model(model)
    
    
    def add_models_from_obj(self, obj_file: str, pos=glm.vec3(),
                            scale=glm.vec3(1,1,1), rotation=glm.vec3(0,0,0),
                            name=""):
        meshes = Obj(obj_file).load_obj_file()
        
        P = glm.translate(pos)
        S = glm.scale(scale)
        R = glm.mat4()
        
        M = glm.mul(P, glm.mul(S, R))
        
        models = []
        for mesh in meshes:
            model = DrawModelFromMesh(scene=self, M=M, mesh=mesh, name=name)
            if model.shader.name == "environment":
                model.shader.map = self.environment
                self.mirrors.extend(models)
            models.append(model)
                
        self.add_models(models)
    

    def handle_key_event(self, key: int, keydown: bool):
        press_direction = -1

        # Pressed-only events
        if keydown:
            press_direction = 1
            # elif key == pygame.K_p or key == pygame.K_f:
            #     print("Using perspective (frustum) projection")
            #     self.P = self.frustum_proj
            # elif key == pygame.K_o:
            #     print("Using orthographic projection")
            #     self.P = self.ortho_proj
            
            match key:
                case pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
                case pygame.K_1:
                    self.settings.next_render_mode()
                case pygame.K_2:
                    self.settings.next_cull_mode()
                case pygame.K_3:
                    self.settings.toggle_shown("shadows")
                case pygame.K_4:
                    self.settings.toggle_shown("reflections")
                case pygame.K_5:
                    self.settings.toggle_shown("fps")
                case pygame.K_6:
                    self.settings.next_depth_func()
            
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

    
    def handle_event(self, event):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            self.handle_key_event(event.key, True)
        elif event.type == pygame.KEYUP:
            self.handle_key_event(event.key, False)
        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[2]:
                if self.mouse_mvt is not None:
                    self.mouse_mvt = pygame.mouse.get_rel()
                    angles = glm.vec3()
                    angles.x -= 5*(float(self.mouse_mvt[1]) / self.window_size[1])
                    angles.y -= 5*(float(self.mouse_mvt[0]) / self.window_size[0])
                    self.camera.add_rotation(angles)
                else:
                    self.mouse_mvt = pygame.mouse.get_rel()
            else:
                self.mouse_mvt = None
    
    
    def draw_shadow_map(self):
        # first we need to clear the scene, we also clear the depth buffer to handle occlusions
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        for item in self.has_shadows:
            item.draw()


    def draw_reflections(self):
        self.skybox.draw()
        # DON'T clear the scene
        for model in self.mirrors:
            model.draw()


    """Draws all models in the scene."""
    def draw(self, framebuffer=False):
        '''
        Draw all models in the scene
        :return: None
        '''
        # first we need to clear the scene, we also clear the depth buffer to handle occlusions
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # first, we draw the skybox
        self.skybox.draw()

        # render the shadows
        if self.settings.is_shown["shadows"]:
            self.shadows.render(self)

        # when rendering the framebuffer we ignore the reflective object
        if not framebuffer:
            if self.settings.is_shown["reflections"]:
                self.environment.update(self)            
            self.flattened_cube.draw()
            if self.settings.is_shown["shadows"]:
                self.show_shadow_map.draw()

        # then we loop over  all models in the list and draw them
        for model in self.models:
            model.draw()

        # once we are done drawing, we display the scene
        # Note that here we use double buffering to avoid artefacts:
        # we draw on a different buffer than the one we display,
        # and flip the two buffers once we are done drawing.
        if not framebuffer:
            pygame.display.flip()


    """Draws the scene until exit."""
    def run(self):
        # Gameloop
        self.running = True
        clock = pygame.time.Clock()
        while self.running:                
            for event in pygame.event.get():
                self.handle_event(event)
            
            # if self.scroll_stop_timer != -1:
            #     self.scroll_stop_timer -= 1
            #     if self.scroll_stop_timer == 0:
            #         self.scroll_stop_timer = -1
            #         self.pan_velocity.y = 0
            
            # self.light.update(np.array(self.camera.rotate_around([*self.light.position], [1,0,0], 1), dtype="f"))
            # self.show_light.set_position(self.light.position)

            self.draw()

            if self.pan_velocity != glm.vec3(0,0,0):
                self.camera.move(self.pan_velocity)
                        
            clock.tick()
            ticks = pygame.time.get_ticks()
            if self.settings.is_shown["fps"]:
                print(str(int(clock.get_fps())) + " FPS")