from multiprocessing import Process
from multiprocessing import Queue
from multiprocessing import Pipe
import numpy as np

from matutils import (translationMatrix, rotationMatrixX, rotationMatrixY,
rotationMatrixZ, homog, unhomog, lookAt)


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
                
        self.update()
    
    
    def rotate_about_point(self, a, b):
        """
        Parameters
        ----------
        a : list[3]
            The point to rotate.
        b : list[3]
            The center of rotation.

        Returns
        -------
        A matrix corresponding to the rotation of a about b.
        """
        ab = np.subtract(b, a)
        T_AB = translationMatrix(ab)
        T_BA = translationMatrix(-ab)
        return np.matmul(np.matmul(T_BA, self._R), T_AB)
    
    
    def add_rotation(self, angles):
        self._R = np.matmul(rotationMatrixX(angles[0]),
                            np.matmul(rotationMatrixY(angles[1]),
                                      np.matmul(rotationMatrixZ(angles[2]),
                                                self._R)))
    
    
    def normalise_vector(self, vector):
        if not np.any(vector):
            return vector
        norm = np.linalg.norm(vector)
        return np.divide(vector, norm)
    
    
    def rotate_vector(self, vector):
        return unhomog(np.matmul(self._R, homog(vector)))
    

    def rotate_around(self, point, normal, speed=1):
        center_point_dir = np.subtract(point, self._center)
        center_point_dir /= np.linalg.norm(center_point_dir)
        new_dir = np.cross(normal, center_point_dir)
        return np.add(point, np.multiply(speed, new_dir))

    
    def get_camera_x_axis(self, y_hat, z_hat):
        """
        Gets the current x axis (x hat) according to the camera.
        Requires the y and z axes, which must be accurate to the current
        perspective.
        Note: No rotation is needed, as the rotation should be already applied
        to the y and z directions, and x = y x z.

        Parameters
        ----------
        y_hat : list[3]
            The current y direction of the camera.
        z_hat : list[3]
            The current z direction of the camera.

        Returns
        -------
        TYPE list[3]

        """
        x_start = np.cross(y_hat, z_hat)
        return self.normalise_vector(x_start)
    
    
    def get_camera_y_axis(self):
        y_start = self._up
        return self.rotate_vector(self.normalise_vector(y_start))
    
    
    def get_camera_z_axis(self):
        z_start = np.subtract(self._center, self._eye)
        return self.rotate_vector(self.normalise_vector(z_start))
    
    
    def add_movement(self, movement):    
        y_hat = self.get_camera_y_axis()
        z_hat = self.get_camera_z_axis()
        
        m_y = np.multiply(movement[1], y_hat)
        m_z = np.multiply(movement[2], z_hat)
        m_x = np.multiply(movement[0], self.get_camera_x_axis(y_hat, z_hat))
        
        M_add = translationMatrix(np.add(np.add(m_x, m_y), m_z))
        
        self._M = np.matmul(M_add, self._M)
    
    
    def update(self):
        # Rotate center around the eye:
        # Add -eye to center, then rotate around origin
        # Then add eye to the new center
        
        R_center = self.rotate_about_point(self._center, np.negative(self._eye))
        center = unhomog(np.matmul(self._M, np.matmul(R_center, homog(self._center))))
        
        eye = unhomog(np.matmul(self._M, homog(self._eye)))
        up = unhomog(np.matmul(self._R, homog(self._up)))

        self.V = lookAt(eye, center, up)