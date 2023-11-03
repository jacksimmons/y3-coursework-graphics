from multiprocessing import Process
from multiprocessing import Queue
from multiprocessing import Pipe
import numpy as np

from matutils import (translationMatrix, rotationMatrixX, rotationMatrixY,
homog, unhomog, lookAt)


class Camera:
    """
    Class which abstracts the thread behaviour of the camera. Gets the View
    Matrix from the camera thread when it is put() into the shared queue.
    """
    def __init__(self):
        self.V = np.identity(4, dtype="f") # View
        self._R = np.identity(4, dtype="f") # Rotation
        self._M = np.identity(4, dtype="f") # Movement
        
        self._eye = [0, 1, -5]
        self._up = [0, 1, 0]
        self._center = [0, 1, 0]
        
        self._angles = [0, 0]
                
        self.update()
    
    
    def get_angles(self):
        return self._angles
    
    
    def set_angles(self, angles):
        self._angles = angles
        self._R = np.matmul(rotationMatrixX(angles[0]),
                            rotationMatrixY(angles[1]))
    
    
    def add_movement(self, movement):
        self._M = np.matmul(translationMatrix(movement), self._M)
    
    
    def update(self):
        # Rotate center around the eye:
        # Add -eye to center, then rotate around origin
        # Then add eye to the new center
        CE = translationMatrix(np.subtract(self._eye, self._center))
        EC = translationMatrix(np.subtract(self._center, self._eye))
        
        R_center = np.matmul(np.matmul(CE, self._R), EC)
        center = unhomog(np.matmul(self._M, np.matmul(R_center, homog(self._center))))
        
        eye = unhomog(np.matmul(self._M, homog(self._eye)))
        
        up = unhomog(np.matmul(self._R, homog(self._up)))

        self.V = lookAt(eye, center, up)