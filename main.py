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

        self.shaders = "phong"

        self.light = LightSource(self, position=[3., 4., -3.])
        self.show_light = DrawModelFromMesh(scene=self, M=poseMatrix(position=self.light.position, scale=0.2), mesh=Sphere(material=Material(Ka=[10,10,10])), shader=FlatShader())

        # for shadow map rendering
        self.shadows = ShadowMap(light=self.light)
        self.show_shadow_map = ShowTexture(self, self.shadows)

        _floor_mesh = load_obj_file('models/concrete.obj')
        floor = [DrawModelFromMesh(scene=self, M=translationMatrix([0,0,0]), mesh=mesh, shader=FlatShader()) for mesh in _floor_mesh]
        self.add_models(floor)

        _table_mesh = load_obj_file('models/quad_table.obj')
        table = [DrawModelFromMesh(scene=self, M=translationMatrix([0, 0, 5]), mesh=mesh, shader=FlatShader(), name='table') for mesh in _table_mesh]
        self.add_models(table)
        
        _boxobj = load_obj_file('models/fluid_border.obj')
        box = [DrawModelFromMesh(scene=self, M=translationMatrix([0,1,0]), mesh=mesh, shader=self.shaders, name='box') for mesh in _boxobj]

        _bigben_mesh = load_obj_file('models/bigben.obj')
        bigben = [DrawModelFromMesh(scene=self, M=translationMatrix([10,0,0]), mesh=mesh, shader=FlatShader()) for mesh in _bigben_mesh]
        self.add_models(bigben)

        #https://sketchfab.com/3d-models/dinosaur-texture-by-pop-obj-f6009a7bedb648f688f18e9bc03cc6ab#download
        _diplo_mesh = load_obj_file("models/red_dino.obj")
        diplo = [DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([5,0,5]), scaleMatrix([0.1,0.1,0.1])), mesh=mesh, shader=FlatShader()) for mesh in _diplo_mesh]
        self.add_models(diplo)
        
        _cube_mesh = load_obj_file("models/cube.obj")
        cube = [DrawModelFromMesh(scene=self, M=translationMatrix([2,1,0]), mesh=mesh, shader=PhongShader()) for mesh in _cube_mesh]
        self.add_models(cube)

        # draw a skybox for the horizon
        self.skybox = SkyBox(scene=self)

        self.environment = EnvironmentMappingTexture(width=400, height=400)

        self.sphere = DrawModelFromMesh(scene=self, M=poseMatrix(), mesh=Sphere(), shader=EnvironmentShader(map=self.environment))

        # this object allows to visualise the flattened cube
        self.flattened_cube = FlattenCubeMap(scene=self, cube=self.environment)

        self.show_texture = ShowTexture(self, Texture('lena.bmp'))

        self.has_shadows = [*table]
        self.has_reflection = []


    def draw_shadow_map(self):
        # first we need to clear the scene, we also clear the depth buffer to handle occlusions
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        for item in self.has_shadows:
            item.draw()


    def draw_reflections(self):
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
            self.show_texture.draw()
            self.show_shadow_map.draw()

        # then we loop over  all models in the list and draw them
        for model in self.models:
            model.draw()

        self.show_light.draw()

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