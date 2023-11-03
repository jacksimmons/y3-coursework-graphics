from model import Model, DrawModelFromMesh
from mesh import *
from matutils import *
from texture import *
from shaders import *
from cube_map import CubeMap


class SkyBoxShader(BaseShaderProgram):
    def __init__(self, name='skybox'):
        super().__init__(name=name)
        self.add_uniform('sampler_cube')

    def bind(self, model, M):
        super().bind(model, M)
        P = model.scene.P  # get projection matrix from the scene
        V = model.scene.camera.V  # get view matrix from the camera

        self.uniforms['PVM'].bind(np.matmul(P, np.matmul(V, M)))


class SkyBox(DrawModelFromMesh):
    def __init__(self, scene):
        super().__init__(scene=scene, M=poseMatrix(scale=100.0),
                         mesh=CubeMesh(texture=CubeMap(name='skybox/ame_ash', file_format="bmp"), inside=True),
                         shader=SkyBoxShader(), name='skybox')

    def draw(self):
        glDepthMask(GL_FALSE)
        super().draw()
        glDepthMask(GL_TRUE)

