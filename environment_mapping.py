import time
from threading import Thread

import glm
from OpenGL.GL.framebufferobjects import *

from model import Model, DrawModelFromMesh
from mesh import *
from cube_map import CubeMap
from shaders import *
from framebuffer import Framebuffer


class EnvironmentShader(BaseShaderProgram):
    def __init__(self, name='environment', map=None):
        BaseShaderProgram.__init__(self, name=name)
        self.add_uniform('sampler_cube')
        self.add_uniform('VM')
        self.add_uniform('VMiT')
        self.add_uniform('VT')

        self.map = map

    def bind(self, model, M):
        if self.map is not None:
            #self.map.update(model.scene)
            unit = len(model.mesh.textures)
            glActiveTexture(GL_TEXTURE0)
            self.map.bind()
            self.uniforms['sampler_cube'].bind(0)

        glUseProgram(self.program)

        P = model.scene.P  # get projection matrix from the scene
        V = model.scene.camera.V

        # set the PVM matrix uniform
        self.uniforms['PVM'].bind_mat_4x4(glm.mul(P, glm.mul(V, M)))

        # set the PVM matrix uniform
        self.uniforms['VM'].bind_mat_4x4(glm.mul(V, M))

        # set the PVM matrix uniform
        self.uniforms['VM_it'].bind_mat_4x4(glm.inverseTranspose(glm.mul(V, M)))

        self.uniforms['V_t'].bind_mat_4x4(glm.transpose(V))


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
