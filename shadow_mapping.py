from OpenGL.GL import *
import glm

from mesh import Mesh
from model import DrawModelFromMesh
from texture import Texture
from framebuffer import Framebuffer


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
        self.wrap = GL_CLAMP
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

        self.set_sampling_parameter(self.sample)
        self.set_wrap_parameter(self.wrap)
        self.set_shadow_comparison()

        self.fbo = Framebuffer(attachment=GL_DEPTH_ATTACHMENT, texture=self)

        self.V = None


    def render(self, scene):
        if self.light is not None:
            scale = glm.length(self.light.position)

            # Shadow projection and view matrices
            self.P = glm.frustum(-1, +1, -1.4, +1.1, 1.5, 775)
            self.V = glm.lookAt(self.light.position, glm.vec3(), glm.vec3(0,1,0))
            
            # Store and set camera view matrix
            Vscene = scene.camera.V
            scene.camera.V = self.V
            
            # Render shadows to shadow map
            glViewport(0, 0, self.width, self.height)
            self.fbo.bind()
            scene.draw_shadow_map()
            self.fbo.unbind()

            # Revert viewport and camera view matrix
            glViewport(0, 0, scene.window_size[0], scene.window_size[1])
            scene.camera.V = Vscene