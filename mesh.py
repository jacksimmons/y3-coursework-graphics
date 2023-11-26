from material import Material
import numpy as np

from texture import Texture
import glm


class Mesh:
    '''
    Simple class to hold a mesh data. For now we will only focus on vertices, faces (indices of vertices for each face)
    and normals.
    '''
    def __init__(self, vertices=None, faces=None, normals=None, textureCoords=None, material=Material()):
        '''
        Initialises a mesh object.
        :param vertices: A numpy array containing all vertices
        :param faces: [optional] An int array containing the vertex indices for all faces.
        :param normals: [optional] An array of normal vectors, calculated from the faces if not provided.
        :param material: [optional] An object containing the material information for this object
        '''
        
        self.name = 'Unknown'
        self.vertices = vertices
        self.faces = faces
        self.material = material
        self.colors = None
        self.textureCoords = textureCoords
        self.textures = []
        self.tangents = None
        self.binormals = None

        if vertices is not None:
            print('Creating mesh')
            print('- {} vertices'.format(self.vertices.shape[0]))
            if faces is not None:
                print('- {} faces'.format(self.faces.shape[0]))

        #if faces is not None:
        #    print('- {} vertices per face'.format(self.faces.shape[1]))
            #print('- vertices ID in range [{},{}]'.format(np.min(self.faces.flatten()), np.max(self.faces.flatten())))

        if normals is None:
            if faces is None:
                print('(W) Warning: the current code only calculates normals using the face vector of indices, which was not provided here.')
            else:
                self.calculate_normals()
        else:
            self.normals = normals

        if material.texture is not None:
            self.textures.append(Texture(material.texture))
            #self.textures.append(Texture('lena.bmp'))
    
    
    def safe_normalise(self, arr):
        norm = np.linalg.norm(arr, axis=1, keepdims=True)
        if len(norm) == 1:
            if norm == 0:
                return arr
        else:
            for n in norm:
                if n == 0:
                    return arr
        
        return arr / norm


    def calculate_normals(self):
        '''
        method to calculate normals from the mesh faces.
        TODO WS3: Fix this code to calculate the correct normals
        Use the approach discussed in class:
        1. calculate normal for each face using cross product
        2. set each vertex normal as the average of the normals over all faces it belongs to.
        '''

        self.normals = np.zeros((self.vertices.shape[0], 3), dtype='f')
        if self.textureCoords is not None:
            self.tangents = np.zeros((self.vertices.shape[0], 3), dtype='f')
            self.binormals = np.zeros((self.vertices.shape[0], 3), dtype='f')

        #TODO WS3
        for f in range(self.faces.shape[0]):
            # first calculate the face normal using the cross product of the triangle's sides
            a = self.vertices[self.faces[f, 1]] - self.vertices[self.faces[f, 0]]
            b = self.vertices[self.faces[f, 2]] - self.vertices[self.faces[f, 0]]
            face_normal = np.cross(a, b)

            # tangent
            if self.textureCoords is not None:
                txa = self.textureCoords[self.faces[f, 1], :] - self.textureCoords[self.faces[f, 0], :]
                txb = self.textureCoords[self.faces[f, 2], :] - self.textureCoords[self.faces[f, 2], :]
                
                face_tangent = txb[0]*a - txa[0]*b
                face_binormal = -txb[1]*a + txa[1]*b

            # blend normal on all 3 vertices
            for j in range(3):
                self.normals[self.faces[f, j], :] += face_normal
                if self.textureCoords is not None:
                    self.tangents[self.faces[f, j], :] += face_tangent
                    self.binormals[self.faces[f, j], :] += face_binormal

        # Normalise the arrays (if they have a length)
        self.safe_normalise(self.normals)
            
        if self.textureCoords is not None:
            self.safe_normalise(self.tangents)
            self.safe_normalise(self.binormals)


class CubeMesh(Mesh):
    def __init__(self, texture=None, inside=False):

        vertices = np.array([

            [-1.0, -1.0, -1.0],  # 0
            [+1.0, -1.0, -1.0],  # 1

            [-1.0, +1.0, -1.0],  # 2
            [+1.0, +1.0, -1.0],  # 3

            [-1.0, -1.0, +1.0],  # 4
            [-1.0, +1.0, +1.0],  # 5

            [+1.0, -1.0, +1.0],  # 6
            [+1.0, +1.0, +1.0]  # 7

        ], dtype='f')

        faces = np.array([

            # back
            [1, 0, 2],
            [1, 2, 3],

            # right
            [2, 0, 4],
            [2, 4, 5],

            # left
            [1, 3, 7],
            [1, 7, 6],

            # front
            [5, 4, 6],
            [5, 6, 7],

            # bottom
            [0, 1, 4],
            [4, 1, 6],

            # top
            [2, 5, 3],
            [5, 7, 3],

        ], dtype=np.uint32)

        if inside:
            faces = faces[:, np.argsort([0, 2, 1])]

        textureCoords = None # np.array([], dtype='f')

        super().__init__(vertices=vertices, faces=faces, textureCoords=textureCoords)

        if texture is not None:
            self.textures = [
                texture
            ]


class SphereMesh(Mesh):
    def __init__(self, nvert=10, nhoriz=20, material=Material(Ka=[0.5,0.5,0.5], Kd=[0.6,0.6,0.9], Ks=[1.,1.,0.9], Ns=15.0)):
        n = (nvert-1)*nhoriz+2
        vertices = np.zeros((n, 3), 'f')
        vertex_colors = np.zeros((n, 3), 'f')

        vslice = np.pi/nvert
        hslice = 2.*np.pi/nhoriz
        vertices[0,:] = [0., 1., 0.]
        vertices[-1, :] = [0., -1., 0.]

        # texture coordinates
        textureCoords = np.zeros((n, 2), 'f')

        # start by creating vertices
        for i in range(nvert-1):
            y = np.cos((i+1) * vslice)
            r = np.sin((i+1) * vslice)
            for j in range(nhoriz):
                v = 1+i*nhoriz+j
                vertices[v, 0] = r * np.cos(j*hslice)
                vertices[v, 1] = y
                vertices[v, 2] = r * np.sin(j*hslice)
                vertex_colors[v, 0] = float(i) / float(nvert)
                vertex_colors[v, 1] = float(j) / float(nhoriz)
                textureCoords[v, 1] = float(i) / float(nvert)
                textureCoords[v, 0] = float(j) / float(nhoriz)

        nfaces = nhoriz*2 + (nvert-2)*(nhoriz)*2
        indices = np.zeros((nfaces, 3), dtype=np.uint32)
        k = 0

        for i in range(nhoriz-1):

            # top
            indices[k, 0] = 0
            indices[k, 2] = i + 1
            indices[k, 1] = i + 2
            k+=1

            # bottom
            lastrow = n - nhoriz - 2
            indices[k, 0] = lastrow + i + 2
            indices[k, 2] = lastrow + i + 1
            indices[k, 1] = n-1
            k+=1

        # last triangle at the top
        indices[k, :] = [0, 1, nhoriz]

        # last triangle at the bottom
        indices[k + 1, :] = [lastrow + 1, n - 1, n-2]
        k+=2

        for j in range(1, nvert-1):
            for i in range(nhoriz-1):
                lastrow = nhoriz*(j-1)+1
                row = nhoriz*j+1
                indices[k, 0] = row + i
                indices[k, 2] = row + i + 1
                indices[k, 1] = lastrow + i
                k += 1

                indices[k, 0] = row + i + 1
                indices[k, 2] = lastrow + i + 1
                indices[k, 1] = lastrow + i
                k += 1

            # last two triangles on this row
            indices[k, :] = [row + nhoriz - 1, lastrow + nhoriz - 1, row]
            k += 1
            indices[k, :] = [row, lastrow + nhoriz - 1, lastrow]
            k += 1

        Mesh.__init__(self,
                      vertices=vertices,
                      faces=indices,
                      textureCoords=textureCoords,
                      material=material
                      )
