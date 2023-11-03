from OpenGL.GL import *
from matutils import *

from mesh import Mesh
from model import DrawModelFromMesh
from shaders import BaseShaderProgram, Shader
from texture import Texture
from framebuffer import Framebuffer


class ShowTextureShader(BaseShaderProgram):
    '''
    Base class for rendering the flattened cube.
    '''
    def __init__(self):
        BaseShaderProgram.__init__(self, name='show_texture')

        # the main uniform to add is the cube map.
        self.add_uniform('sampler')


class ShadowMappingShader(Shader):
    def __init__(self, shadow_map=None):
        Shader.__init__(self, name='shadow_mapping')
        self.add_uniform('shadow_map')
        #self.add_uniform('old_map')
        self.add_uniform('shadow_map_matrix')
        self.shadow_map = shadow_map

    def bind(self, model, M):
        Shader.bind(self, model, M)
        self.uniforms['shadow_map'].bind(1)
        #self.uniforms['old_map'].bind(2)

        glActiveTexture(GL_TEXTURE1)
        self.shadow_map.bind()

        #glActiveTexture(GL_TEXTURE2)
        #self.shadow_map.bind()

        glActiveTexture(GL_TEXTURE0)

        # setup the shadow map matrix
        V = model.scene.camera.V
        VsT = np.linalg.inv(V)
        self.SM = np.matmul(self.shadow_map.V, VsT)
        self.SM = np.matmul(self.shadow_map.P, self.SM)
        self.SM = np.matmul(translationMatrix([1, 1, 1]), self.SM)
        self.SM = np.matmul(scaleMatrix(0.5), self.SM)
        self.uniforms['shadow_map_matrix'].bind(self.SM)


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

            [-1.0, -1.0, 0.0],  # 0 --> left
            [-1.0, 1.0, 0.0],  # 1
            [1.0, -1.0, 0.0],   # 2
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


class ShadowMap(Texture):
    def __init__(self, light=None, width=1000, height=1000):

        # In order to call parent constructor I would need to change it to allow for an empty texture object (poor design)
        # Texture.__init__(self, "shadow", img=None, wrap=GL_CLAMP_TO_EDGE, sample=GL_NEAREST, format=GL_DEPTH_COMPONENT, type=GL_FLOAT, target=GL_TEXTURE_2D)

        # we save the light source
        self.light = light

        # we'll just copy and modify the code here
        self.name = 'shadow'
        self.format = GL_DEPTH_COMPONENT
        self.type = GL_FLOAT
        self.wrap = GL_CLAMP_TO_EDGE
        self.sample = GL_LINEAR
        self.target = GL_TEXTURE_2D
        self.width = width
        self.height = height

        # create the texture
        self.textureid = glGenTextures(1)

        print('* Creating texture {} at ID {}'.format(self.name, self.textureid))

        # initialise the texture memory
        self.bind()
        glTexImage2D(self.target, 0, self.format, self.width, self.height, 0, self.format, self.type, None)
        self.unbind()

        self.set_wrap_parameter(self.wrap)
        self.set_sampling_parameter(self.sample)
        self.set_shadow_comparison()

        self.fbo = Framebuffer(attachment=GL_DEPTH_ATTACHMENT, texture=self)

        self.V = None
        

    def render(self, scene, target=[0, 0, 0]):
        # backup the view matrix and replace with the new one
        if self.light is not None:
            #self.P = frustumMatrix(-1.0, +1.0, -1.0, +1.0, 1.0, 20.0)
            self.P = scene.P
            self.V = lookAt(np.array(self.light.position), np.array(target))
            scene.camera.V = self.V

            # update the viewport for the image size
            glViewport(0, 0, self.width, self.height)

            self.fbo.bind()
            scene.draw_shadow_map()
            self.fbo.unbind()

            # reset the viewport to the windows size
            glViewport(0, 0, scene.window_size[0], scene.window_size[1])

            # restore the view matrix
            scene.camera.update()