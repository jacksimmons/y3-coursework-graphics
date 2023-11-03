from model import Model
from matutils import poseMatrix
# imports all openGL functions
from OpenGL.GL import *
import numpy as np
from mesh import Mesh
from material import Material
from texture import Texture


class Sphere(Mesh):
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