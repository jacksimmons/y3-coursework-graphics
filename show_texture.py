from model import *

def normalize(v):
    '''
    Normalise a vector
    :param v: a vector
    :return: normalised vector
    '''
    return v / np.linalg.norm(v)


def lookAt(eye, center, up=np.array([0, 1, 0])):
    '''
    Calculate the view matrix for a camera at position eye, looking towards the center
    :param eye: The position of the camera
    :param center: The position the camera is looking at
    :param up: A vector setting where up is. Default is (0,1,0), no reason to change it.
    :return: The corresponding view matrix
    '''

    f = normalize(center - eye)
    u = normalize(up)

    # Note: the normalization is missing in the official glu manpage: /: /: /
    s = normalize(np.cross(f, u))
    u = np.cross(s, f)

    return np.matmul(
        np.array([
            [s[0], s[1], s[2], 0],
            [u[0], u[1], u[2], 0],
            [-f[0], -f[1], -f[2], 0],
            [0, 0, 0, 1]
        ]),
        translationMatrix(-eye)
    )


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
        DrawModelFromMesh.__init__(self, scene=scene, M=poseMatrix(position=[0, 0, 1]), mesh=mesh, shader=ShowTextureShader(), visible=False)
