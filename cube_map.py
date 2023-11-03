import os

from texture import *
from mesh import Mesh
from model import DrawModelFromMesh
from matutils import *
from shaders import *


class FlattenedCubeShader(BaseShaderProgram):
    '''
    Base class for rendering the flattened cube.
    '''
    def __init__(self):
        BaseShaderProgram.__init__(self, name='flattened_cube')

        # the main uniform to add is the cube map.
        self.add_uniform('sampler_cube')


class FlattenCubeMap(DrawModelFromMesh):
    '''
    Class for drawing the cube faces flattened on the screen (for debugging purposes)
    '''

    def __init__(self, scene, cube=None):
        '''
        Initialises the
        :param scene: The scene object.
        :param cube: [optional] if not None, the cubemap texture to draw (can be set at a later stage using the set() method)
        '''

        vertices = np.array([

            [-2.0, -1.0, 0.0],  # 0 --> left
            [-2.0,  0.0, 0.0],  # 1
            [-1.0, -1.0, 0.0],   # 2
            [-1.0,  0.0, 0.0],   # 3

            [-1.0, -1.0, 0.0],  # 2 --> front
            [-1.0, 0.0, 0.0],  # 3
            [0.0, -1.0, 0.0],   # 4`
            [0.0, 0.0, 0.0],    # 5

            [0.0, -1.0, 0.0],  # 4` --> right
            [0.0, 0.0, 0.0],  # 5
            [1.0, -1.0, 0.0],   # 6
            [1.0, 0.0, 0.0],    # 7

            [1.0, -1.0, 0.0],  # 6 --> back
            [1.0, 0.0, 0.0],  # 7
            [2.0, -1.0, 0.0],   # 8
            [2.0, 0.0, 0.0],    # 9

            [-1.0, 0.0, 0.0],  # 10
            [-1.0, 1.0, 0.0],  # 3  --> top
            [0.0, 0.0, 0.0],  # 11
            [0.0, 1.0, 0.0],  # 5

            [-1.0, -2.0, 0.0],   # 12
            [-1.0, -1.0, 0.0],  # 2 ---> bottom
            [0.0, -2.0, 0.0],   # 13
            [0.0, -1.0, 0.0],  # 4`

        ], dtype='f')/2

        # set the faces of the flattened cube
        faces = np.zeros(vertices.shape, dtype=np.uint32)
        for f in range(int(vertices.shape[0]/4)):
            faces[2 * f + 0, :] = [0 + f*4, 3 + f*4, 1 + f*4]
            faces[2 * f + 1, :] = [0 + f*4, 2 + f*4, 3 + f*4]

        # and set the texture coordinates to index in the cube map texture
        textureCoords = np.array([
            [-1, +1, -1],  # left
            [-1, -1, -1],
            [-1, +1, +1],
            [-1, -1, +1],

            [-1, +1, +1],  # front
            [-1, -1, +1],
            [+1, +1, +1],
            [+1, -1, +1],

            [+1, +1, +1],  # right
            [+1, -1, +1],
            [+1, +1, -1],
            [+1, -1, -1],

            [+1, +1, -1],  # back
            [+1, -1, -1],
            [-1, +1, -1],
            [-1, -1, -1],

            [-1, -1, +1],  # top
            [-1, -1, -1],
            [+1, -1, +1],
            [+1, -1, -1],

            [-1, +1, -1],  # bottom
            [-1, +1, +1],
            [+1, +1, -1],
            [+1, +1, +1],
        ], dtype='f')

        # create a mesh from the object
        mesh = Mesh(vertices=vertices, faces=faces, textureCoords=textureCoords)

        # add the CubeMap object if provided (otherwise you need to call set() at a later stage)
        if cube is not None:
            mesh.textures.append(cube)

        # Finishes initialising the mesh
        DrawModelFromMesh.__init__(self, scene=scene, M=poseMatrix(position=[0,0,+1]), mesh=mesh, shader=FlattenedCubeShader(), visible=False)

    def set(self, cube):
        '''
        Set the cube map to display
        :param cube: A CubeMap texture
        '''
        self.mesh.textures = [cube]


class CubeMap(Texture):
    '''
    Class for handling a cube map texture.

    '''
    def __init__(self, name=None, files=None, wrap=GL_CLAMP_TO_EDGE, sample=GL_LINEAR, format=GL_RGBA, type=GL_UNSIGNED_BYTE, file_format="jpg"):
        '''
        Initialise the cube map texture object
        :param name: If a name is provided, the function will load the faces of the cube from files on the disk in a
        folder of this name
        :param files: If provided, a dictionary containing for each cube face ID the file name to load the texture from
        :param wrap: Which texture wrapping method to use. Default is GL_CLAMP_TO_EDGE which is best for cube maps
        :param sample: Which sampling to use, default is GL_LINEAR
        :param format: The pixel format of the image and texture (GL_RGBA). Do not change.
        :param type: The data format for the texture. Default is GL_UNSIGNED_BYTE (should not be changed)
        '''
        self.name = name
        self.format = format
        self.type = type
        self.wrap = wrap
        self.sample = sample
        self.target = GL_TEXTURE_CUBE_MAP # we set the texture target as a cube map

        # This dictionary contains the file name for each face, if loading from disk (otherwise ignored)
        self.files = {
            GL_TEXTURE_CUBE_MAP_NEGATIVE_X: f'left.{file_format}',
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z: f'back.{file_format}',
            GL_TEXTURE_CUBE_MAP_POSITIVE_X: f'right.{file_format}',
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: f'front.{file_format}',
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y: f'bottom.{file_format}',
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: f'top.{file_format}',
        }

        # generate the texture.
        self.textureid = glGenTextures(1)

        # bind the texture
        self.bind()

        # if name is provided, load cube faces from images on disk
        if name is not None:
            self.set(name, files)

        # set what happens for texture coordinates outside [0,1]
        glTexParameteri(self.target, GL_TEXTURE_WRAP_S, wrap)
        glTexParameteri(self.target, GL_TEXTURE_WRAP_T, wrap)

        # set how sampling from the texture is done.
        glTexParameteri(self.target, GL_TEXTURE_MAG_FILTER, sample)
        glTexParameteri(self.target, GL_TEXTURE_MIN_FILTER, sample)

        # unbind the texture
        self.unbind()

    def set(self, name, files=None):
        '''
        Load the cube's faces from images on the disk
        :param name: The folder in which the images are.
        :param files: A dictionary containing the file name for each face.
        '''

        if files is not None:
            self.files = files

        for (key, value) in self.files.items():
            print('Loading texture: texture/{}/{}'.format(name, value))            
            img = ImageWrapper('{}/{}'.format(name, value))

            # convert the python image object to a plain byte array for passing to OpenGL
            glTexImage2D(key, 0, self.format, img.width(), img.height(), 0, self.format, self.type, img.data(self.format))

    def update(self, scene):
        '''
        Used to update the texture, does not do anything at the moment, but could be extended for the environment mapping.
        '''
        pass

