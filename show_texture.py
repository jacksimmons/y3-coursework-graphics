from model import DrawModelFromMesh
from mesh import Mesh
from shaders import BaseShaderProgram

import numpy as np
import glm


class ShowTextureShader(BaseShaderProgram):
    '''
    Base class for rendering the flattened cube.
    '''
    def __init__(self):
        BaseShaderProgram.__init__(self, name='show_texture')

        # the main uniform to add is the cube map.
        self.add_uniform('sampler')

class ShowTexture(DrawModelFromMesh):
    '''
    Class for drawing the cube faces flattened on the screen (for debugging purposes)
    '''

    def __init__(self, scene, texture=None):
        '''
        Initialises the
        :param scene: The scene object.
        :param cube: [optional] if not None, the cubemap texture to draw (can be set at a later stage using the set() method)
        '''

        vertices = np.array([

            [-1.0, -1.0, 0.0], # 0 --> left
            [-1.0, 1.0, 0.0],  # 1
            [1.0, -1.0, 0.0],  # 2
            [1.0, 1.0, 0.0],   # 3
        ], dtype='f') / 2

        # set the faces of the square
        faces = np.array([
            [0, 3, 1],
            [0, 2, 3]
        ], dtype=np.uint32)

        textureCoords = np.array([
            [0, 0],  # left
            [0, 1],
            [1, 0],
            [1, 1]
        ], dtype='f')

        # create a mesh from the object
        mesh = Mesh(vertices=vertices, faces=faces, textureCoords=textureCoords)

        # add the CubeMap object if provided (otherwise you need to call set() at a later stage)
        if texture is not None:
            mesh.textures.append(texture)

        # Finishes initialising the mesh
        super().__init__(scene=scene, M=glm.translate(glm.vec3(0,0,1)),
                         mesh=mesh, shader=ShowTextureShader(), visible=False)
