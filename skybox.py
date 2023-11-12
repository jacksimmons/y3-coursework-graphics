import glm

from OpenGL.GL import glDepthMask, GL_FALSE, GL_TRUE
from model import DrawModelFromMesh
from mesh import CubeMesh
from shaders import BaseShaderProgram


class SkyBoxShader(BaseShaderProgram):
    def __init__(self, name='skybox'):
        super().__init__(name=name)
        self.add_uniform('sampler_cube')

    def bind(self, model, M):
        super().bind(model, M)
        P = model.scene.P  # get projection matrix from the scene
        V = model.scene.camera.V  # get view matrix from the camera

        self.uniforms['PVM'].bind_mat4x4(glm.mul(P, glm.mul(V, M)))


class SkyBox(DrawModelFromMesh):
    def __init__(self, scene):
        super().__init__(scene=scene, M=glm.scale(glm.vec3(100,100,100)),
                         mesh=CubeMesh(texture=None, inside=True),
                         shader=SkyBoxShader(), name='skybox')

    def draw(self):
        glDepthMask(GL_FALSE)
        super().draw()
        glDepthMask(GL_TRUE)

