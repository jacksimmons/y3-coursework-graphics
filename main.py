import math
import pygame
import numpy as np
from OpenGL.GL import (glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT)

from blender import load_obj_file
from matutils import poseMatrix, translationMatrix, scaleMatrix
from scene import Scene
from sphere_mesh import Sphere
from model import DrawModelFromMesh
from texture import Texture
from material import Material
from shaders import FlatShader, PhongShader
from light_source import LightSource
from cube_map import FlattenCubeMap
from shadow_mapping import ShadowMap, ShadowMappingShader, ShowTexture
from environment_mapping import EnvironmentMappingTexture, EnvironmentShader
from skybox import SkyBox


class MyScene(Scene):
    def __init__(self):
        Scene.__init__(self)

        self.shaders = "flat"
        
        # draw a skybox for the horizon
        self.skybox = SkyBox(scene=self)
        self.environment = EnvironmentMappingTexture(width=400, height=400)

        # this object allows to visualise the flattened cube
        self.flattened_cube = FlattenCubeMap(scene=self, cube=self.environment)

        self.light = LightSource(self, position=[0, 60, 90],
                                 Ia=[0.2,0.2,0.2],
                                 Id=[1,1,1],
                                 Is=[1,1,1])
        self.show_light = DrawModelFromMesh(self, poseMatrix(self.light.position),
        Sphere(), "Sun", FlatShader())
        self.add_model(self.show_light)

        # for shadow map rendering
        self.shadows = ShadowMap(light=self.light)
        self.show_shadow_map = ShowTexture(self, self.shadows)
        
        self.add_models_from_obj("models/floor.obj", pos=[0,0,0], scale=100,
                                 name="Floor")

        # self.add_models_from_obj("models/fluid_border.obj", pos=[0,1.5,0],
        #                          has_shadows=True,
        #                          name="Box")
        # self.add_models_from_obj("models/quad_table.obj", pos=[0,1.5,0],
        #                          name="Table")
        
        #https://sketchfab.com/3d-models/big-ben-58064c3815f34b759a5bbb75fb8d8eb2
        self.add_models_from_obj("models/bigger_ben.obj", pos=[10,0,0],
                                 scale=2,
                                 name="Ben")

        #https://sketchfab.com/3d-models/dinosaur-texture-by-pop-obj-f6009a7bedb648f688f18e9bc03cc6ab#download        
        #https://sketchfab.com/3d-models/low-poly-plane-76230052903540e9aeb46b7db35329e4#download
        self.add_models_from_obj("models/trex_plane.obj", pos=[4,11,4],
                                 rotation=[-math.pi/16, math.pi, math.pi/16],
                                 name="Gangsta")


    def draw_shadow_map(self):
        # first we need to clear the scene, we also clear the depth buffer to handle occlusions
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        for item in self.has_shadows:
            item.draw()


    def draw_reflections(self):
        self.skybox.draw()
        # DON'T clear the scene     
        
        # Takes 90% reflection time for some reason!
        # for model in self.table:
        #     model.draw()
        for model in self.has_reflection:
            model.draw()


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
        self.shadows.render(self)

        # when rendering the framebuffer we ignore the reflective object
        if not framebuffer:
            self.environment.update(self)
            self.flattened_cube.draw()
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


def main():
    scene = MyScene()
    scene.run()
        

if __name__ == "__main__":
    main()