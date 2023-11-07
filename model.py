from OpenGL.GL import *
from OpenGL.GLU import *

import numpy as np

from mesh import Mesh
from material import Material
from matutils import poseMatrix, translationMatrix
from shaders import Shader


class Model:
    """Base class for all models."""
    def __init__(self, scene, M, mesh=Mesh(), colour=[1,1,1], primitive=GL_TRIANGLES, visible=True):
        self.visible = visible
        
        self.scene = scene

        self.primitive = primitive
        self.color = colour

        self.shader = None

        self.mesh = mesh
        if self.mesh.textures == 1:
            self.mesh.textures.append(Texture("lena.bmp"))

        self.name = self.mesh.name

        self.vao = glGenVertexArrays(1)
        self.vbos = {}
        self.missing_attributes = []

        # Will store indices if using shared vertex representation
        self.index_buffer = None

        self.attributes = {}

        self.M = M


    def initialise_vbo(self, name, data):
        #print(f"Initialising VBO for attribute {name}.")

        if data is None:
            print(f"Warning in {self.__class__.__name__}.initialise_vbo: Data array for attribute \
{name} is None.")
            self.missing_attributes.append(name)
            return
        
        # Bind location of attribute in GLSL program to the next index (which is len(self.vbos))
        # Location name must correspond to an "in" variable in the GLSL vertex shader code
        self.attributes[name] = len(self.vbos) + len(self.missing_attributes)
        
        # Create a buffer object
        self.vbos[name] = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbos[name])

        # Enable attrib (using location of attribute)
        glEnableVertexAttribArray(self.attributes[name])

        # Associate bound buffer to corresponding input location in shader
        # Every vertex shader instance gets one row of the array, so can be processed in parallel
        print(name)
        print(data.shape[1])
        print("At index " + str(self.attributes[name]))
        glVertexAttribPointer(index=self.attributes[name], size=data.shape[1], type=GL_FLOAT,
            normalized=False, stride=0, pointer=None)

        glBufferData(GL_ARRAY_BUFFER, data, GL_STATIC_DRAW)


    def bind_shader(self, shader):
        """
        When a new shader is bound, we need to re-link it to ensure attributes are correctly
        linked.
        """

        if self.shader is not None and self.shader.name is shader:
            return
        
        if isinstance(shader, str):
            self.shader = Shader(shader)
        else:
            self.shader = shader
                
        # Bind all attributes and compile it
        self.shader.compile()


    def bind(self):
        """
        Stores vertex data in a Vertex Buffer Object (VBO) which can be uploaded to the GPU
        at render time
        """
        glBindVertexArray(self.vao)

        if self.mesh.vertices is None:
            print("Warning - No vertices")
        
        # Initialise vertex VBOs and link to shader attributes
        self.initialise_vbo("position", self.mesh.vertices)
        self.initialise_vbo("normal", self.mesh.normals)
        self.initialise_vbo("colour", self.mesh.colors)
        self.initialise_vbo("tex_coord", self.mesh.textureCoords)
        # self.initialise_vbo('tangent', self.mesh.tangents)
        # self.initialise_vbo('binormal', self.mesh.binormals)

        if self.mesh.faces is not None:
            self.index_buffer = glGenBuffers(1)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.mesh.faces, GL_STATIC_DRAW)

        # Unbind VAO and VBO to avoid side effects
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)


    def draw(self, Mp=poseMatrix()):
        """
        Draw using OpenGL functions.
        """
        if not self.visible:
            return

        if self.mesh.vertices is None:
            print(f"(W) Warning in {self.__class__.__name__}.draw(): No vertex array!")

        self.shader.bind(
            model=self,
            M=np.matmul(Mp, self.M)
        )

        # Bind vao
        glBindVertexArray(self.vao)

        # Bind all textures. Shader must handle each texture with a sampler object.
        for unit, tex in enumerate(self.mesh.textures):
            glActiveTexture(GL_TEXTURE0 + unit)
            tex.bind()

        # Check whether stored as vertex or index array
        if self.mesh.faces is not None:
            glDrawElements(self.primitive, self.mesh.faces.flatten().shape[0], GL_UNSIGNED_INT, None)
        else:
            glDrawArrays(self.primitive, 0, self.mesh.vertices.shape[0])

        # Unbind vao
        glBindVertexArray(0)
    

    def set_position(self, position):
        self.M = translationMatrix(position)


    def __del__(self):
        """Destructor."""
        for vbo in self.vbos.items():
            glDeleteBuffers(1, vbo)
        
        glDeleteVertexArrays(self.vao)


class DrawModelFromMesh(Model):
    '''
    Base class for all models, inherit from this to create new models
    '''

    def __init__(self, scene, M, mesh, name=None, shader=None, visible=True):
        '''
        Initialises the model data
        '''
        super().__init__(scene=scene, M=M, mesh=mesh, visible=visible)

        if name is not None:
            self.name = name

        if self.mesh.faces.shape[1] == 3:
            self.primitive = GL_TRIANGLES
        elif self.mesh.faces.shape[1] == 4:
            self.primitive = GL_QUADS
        else:
            print(f"(E) Error in DrawModelFromObjFile.__init__(): index array must have 3 (triangles) or 4 (quads) columns, found {self.indices.shape[1]}!")
            raise

        self.bind()

        if shader is not None:
            self.bind_shader(shader)