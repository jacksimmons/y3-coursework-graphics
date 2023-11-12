from OpenGL.GL import *

import pygame
import numpy as np
import math
from queue import Queue

from enum import Enum

from blender import load_obj_file
from camera import Camera
from model import *
from shaders import FlatShader
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
        self.set_cull_mode(0)

        # Must be set before vertex colours, as vertex colours needs
        # self.shaders.
        self.shading_mode: int = 0
        self.shading_modes: list =\
            ["flat", "gouraud", "phong", "blinn", "texture"]
        #self.set_shading_mode(0)
    

    def set_render_mode(self, value: int):
        self.render_mode = value
        glPolygonMode(GL_FRONT_AND_BACK, self.render_modes[value])


    def set_cull_mode(self, value: int):
        self.cull_mode = value
        glEnable(GL_CULL_FACE)
        glCullFace(self.cull_modes[value])


    def set_shading_mode(self, value: int):
        self.shading_mode = value
        self.scene.shaders = self.shading_modes[value]
        for model in self.scene.models:
            model.bind_shader(self.shading_modes[value])
    

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
        # glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnable(GL_DEPTH_TEST)

        # For text transparency
        #glEnable(GL_BLEND)
        #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Projective Transform
        # - Clipping Planes
        near = 1.5
        far = 1000
        left = -1.0
        right = 1.0
        top = -1.0
        bottom = 1.0

        self.P = frustumMatrix(left, right, top, bottom, near, far)

        self.pan_velocity = [0, 0, 0]
        self.scroll_stop_timer = -1
        self.pan_speed = 0.1
        self.mouse_mvt = None

        self.mode = 0

        self.shaders = "flat"

        self.camera: Camera = Camera()
        
        self.has_shadows = []
        self.has_reflection = []


    def add_model(self, model):
        model.bind_shader(self.shaders)
        self.models.append(model)
    

    def add_models(self, models):
        for model in models:
            self.add_model(model)
    
    
    def add_models_from_obj(self, obj_file: str, pos=[0,0,0], scale=1,
                            rotation=[0,0,0], shader=FlatShader(), 
                            has_shadows=False, has_reflection=False, name=""):
        meshes = load_obj_file(obj_file)
        P = translationMatrix(pos)
        S = scaleMatrix(scale)
        R = rotationMatrix(*rotation)
        
        print(P)
        print(S)
        print(R)
        
        M = np.matmul(P, np.matmul(S, R))
        models = [DrawModelFromMesh(scene=self, M=M, mesh=mesh,
                  shader=shader, name=name) for mesh in meshes]
        if has_shadows:
            self.has_shadows.extend(models)
        if has_reflection:
            self.has_reflection.extend(models)
        self.add_models(models)
    

    def handle_key_event(self, key: int, keydown: bool):
        press_direction = -1

        # Pressed-only events
        if keydown:
            press_direction = 1
            if key == pygame.K_ESCAPE:
                pygame.quit()
                quit()
            # elif key == pygame.K_p or key == pygame.K_f:
            #     print("Using perspective (frustum) projection")
            #     self.P = self.frustum_proj
            # elif key == pygame.K_o:
            #     print("Using orthographic projection")
            #     self.P = self.ortho_proj
            
            elif key == pygame.K_1:
                self.settings.next_render_mode()
            elif key == pygame.K_2:
                self.settings.next_cull_mode()
            elif key == pygame.K_3:
                self.settings.next_shading_mode()
            
        if key == pygame.K_a:
            self.pan_velocity[0] += press_direction * self.pan_speed
        elif key == pygame.K_d:
            self.pan_velocity[0] -= press_direction * self.pan_speed
        elif key == pygame.K_w:
            self.pan_velocity[1] += press_direction * self.pan_speed
        elif key == pygame.K_s:
            self.pan_velocity[1] -= press_direction * self.pan_speed
        elif key == pygame.K_q:
            self.pan_velocity[2] += press_direction * self.pan_speed
        elif key == pygame.K_e:
            self.pan_velocity[2] -= press_direction * self.pan_speed


    def handle_mouse_scroll_event(self, button):
        # self.scroll_stop_timer = 10
        # if button == 4:
        #     self.pan_velocity[2] = self.pan_speed
        # elif button == 5:
        #     self.pan_velocity[2] = -self.pan_speed
        pass

    
    def handle_event(self, event):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            self.handle_key_event(event.key, True)
        elif event.type == pygame.KEYUP:
            self.handle_key_event(event.key, False)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_scroll_event(event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.handle_mouse_scroll_event(event.button)
        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[2]:
                if self.mouse_mvt is not None:
                    self.mouse_mvt = pygame.mouse.get_rel()
                    angles = [0, 0, 0]
                    angles[0] -= 5*(float(self.mouse_mvt[0]) / self.window_size[0])
                    angles[1] -= 5*(float(self.mouse_mvt[1]) / self.window_size[1])
                    self.camera.add_rotation(angles)
                else:
                    self.mouse_mvt = pygame.mouse.get_rel()
            else:
                self.mouse_mvt = None


    """Draws all models in the scene."""
    def draw(self):
        # First, clear the scene, and the depth buffer to handle occlusion
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Ensure camera view matrix is up to date
        self.camera.update()

        for model in self.models:
            model.draw(Mp=poseMatrix())

        # self.draw_text(0, 0, f"Distance: {str(self.camera.distance)}")
        # self.draw_text(0, 35, f"Rotation: [{str(round(self.camera.phi, 3))}, {str(round(self.camera.psi, 3))}]")
        # self.draw_text(0, 70, f"Position: {str(np.round(self.camera.center, 3))}")

        # Flip the two buffers - double buffering
        # We draw on a different buffer to the one we display,
        # then flip the two buffers once finished drawing.
        pygame.display.flip()


    """Draws the scene until exit."""
    def run(self):
        # Gameloop
        self.running = True
        clock = pygame.time.Clock()
        while self.running:                
            for event in pygame.event.get():
                self.handle_event(event)
            
            if self.scroll_stop_timer != -1:
                self.scroll_stop_timer -= 1
                if self.scroll_stop_timer == 0:
                    self.scroll_stop_timer = -1
                    self.pan_velocity[2] = 0
            
            # self.light.update(np.array(self.camera.rotate_around([*self.light.position], [1,0,0], 1), dtype="f"))
            # self.show_light.set_position(self.light.position)

            self.draw()

            if np.any(self.pan_velocity):
                self.camera.add_movement(self.pan_velocity)
                        
            clock.tick()
            ticks = pygame.time.get_ticks()
            if ticks % 10 == 0:
                print(str(int(clock.get_fps())) + " FPS")