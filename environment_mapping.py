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
    def __init__(self, width=200, height=200):
        CubeMap.__init__(self)

        self.done = False

        self.width = width
        self.height = height

        self.fbos = {
            GL_TEXTURE_CUBE_MAP_NEGATIVE_X: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_POSITIVE_X: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z: Framebuffer()
        }

        t = 0.0
        v = glm.vec3(0, 0, t)
        T = glm.translate(v)
        pi = glm.pi()
        self.views = {
            GL_TEXTURE_CUBE_MAP_NEGATIVE_X: glm.mul(T, glm.rotate(-pi/2.0, glm.vec3(0,1,0))),
            GL_TEXTURE_CUBE_MAP_POSITIVE_X: glm.mul(T, glm.rotate(+pi/2.0, glm.vec3(0,1,0))),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: glm.mul(T, glm.rotate(+pi/2.0, glm.vec3(1,0,0))),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y: glm.mul(T, glm.rotate(-pi/2.0, glm.vec3(1,0,0))),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: glm.mul(T, glm.rotate(-pi, glm.vec3(0,1,0))),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z: T,
        }

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

        scene.P = glm.frustum( -1.0, +1.0, -1.0, +1.0, 1.0, 20.0 )

        glViewport(0, 0, self.width, self.height)

        for (face, fbo) in self.fbos.items():
            fbo.bind()

            scene.camera.V = self.views[face]
            scene.draw_reflections()
            scene.camera.update()
            
            fbo.unbind()

        # reset the viewport
        glViewport(0, 0, scene.window_size[0], scene.window_size[1])

        scene.P = Pscene

        self.unbind()



#class EnvironmentBox(DrawModelFromMesh):
#    def __init__(self, scene, shader=EnvironmentShader(), width=200, height=200):
#        self.done = False

        #self.map = EnvironmentMappingTexture(width, height)

        #DrawModelFromMesh.__init__(self, scene=scene, M=poseMatrix(), mesh=CubeMesh(shader.map), shader=shader, visible=False)
