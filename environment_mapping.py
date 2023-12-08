import time
from threading import Thread

import glm
from OpenGL.GL import *
from OpenGL.GL.framebufferobjects import *

from model import Model, DrawModelFromMesh
from mesh import *
from cube_map import CubeMap
from framebuffer import Framebuffer


class EnvironmentMappingTexture(CubeMap):
    def __init__(self, width=400, height=400):
        CubeMap.__init__(self)

        self.done = False

        self.width = width
        self.height = height

        # Assign the fbos (frame buffer objects)
        self.fbos = {
            GL_TEXTURE_CUBE_MAP_NEGATIVE_X: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_POSITIVE_X: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z: Framebuffer()
        }

        # Define the faces of the cube map
        t = 0.0
        v = glm.vec3(0, 0, t)
        T = glm.translate(v)
        pi = glm.pi()
        self.views = {
            GL_TEXTURE_CUBE_MAP_NEGATIVE_X: glm.mul(T, glm.rotate(-pi/2.0, glm.vec3(0,1,0))),
            GL_TEXTURE_CUBE_MAP_POSITIVE_X: glm.mul(T, glm.rotate(+pi/2.0, glm.vec3(0,1,0))),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: glm.mul(T, glm.rotate(-pi/2.0, glm.vec3(1,0,0))),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y: glm.mul(T, glm.rotate(+pi/2.0, glm.vec3(1,0,0))),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: glm.mul(T, glm.rotate(-pi, glm.vec3(0,1,0))),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z: T,
        }

        # Prepare the fbos
        self.bind()
        for (face, fbo) in self.fbos.items():
            glTexImage2D(face, 0, self.format, width, height, 0, self.format, self.type, None)
            fbo.prepare(self, face)
        self.unbind()


    def update(self, scene):
        if self.done:
            return

        self.bind()

        Pscene = scene.P
        Vscene = scene.camera.V

        # Create env map projection
        scene.P = glm.frustum(-1.0, +1.0, -1.0, +1.0, 1.0, 20.0)
        # Create viewport for environment map
        glViewport(0, 0, self.width, self.height)
        for (face, fbo) in self.fbos.items():
            fbo.bind()

            # For every face, temporarily set the camera's view matrix
            # And then draw the scene reflections.
            scene.camera.V = self.views[face]
            scene.draw_reflections()
            # Revert view matrix
            scene.camera.V = Vscene
            
            fbo.unbind()

        # Revert viewport and projection matrix
        glViewport(0, 0, scene.window_size[0], scene.window_size[1])
        scene.P = Pscene

        self.unbind()



#class EnvironmentBox(DrawModelFromMesh):
#    def __init__(self, scene, shader=EnvironmentShader(), width=200, height=200):
#        self.done = False

        #self.map = EnvironmentMappingTexture(width, height)

        #DrawModelFromMesh.__init__(self, scene=scene, M=poseMatrix(), mesh=CubeMesh(shader.map), shader=shader, visible=False)
