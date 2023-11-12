import glm


class Camera:
    """
    Class which abstracts the thread behaviour of the camera. Gets the View
    Matrix from the camera thread when it is put() into the shared queue.
    """
    def __init__(self):
        self.V = glm.mat4() # View
        self._R = glm.mat4() # Rotation
        self._M = glm.mat4() # Movement
        
        self._eye = glm.vec3(0, 1, -5)
        self._up = glm.vec3(0, 1, 0)
        self._center = glm.vec3(0, 1, 0)
                
        self.update()
    
    
    def rotate_about_point(self, a, b):
        """
        Parameters
        ----------
        a : vec3
            The point to rotate.
        b : vec3
            The center of rotation.

        Returns
        -------
        A mat4 corresponding to the rotation of a about b.
        """
        
        ab: glm.vec3 = glm.sub(b, a)
        T_AB = glm.translate(ab)
        T_BA = glm.translate(glm.neg(ab))
        
        return glm.mul( glm.mul(T_BA, self._R), T_AB )
        #return np.matmul(np.matmul(T_BA, self._R), T_AB)
    
    
    def add_rotation(self, angles):      
        self._R = glm.mul(glm.rotate(angles.x, glm.vec3(1,0,0)),
                          glm.mul(
                              glm.rotate(angles.y, glm.vec3(0,1,0)),
                              glm.mul(
                                        glm.rotate(angles.z, glm.vec3(0,0,1)),
                                        self._R
                                           )
                                 )
                         )
    
    
    def normalise_vector(self, vector):
        if glm.equal(vector, glm.vec3(0, 0, 0)):
            return vector
        return glm.normalise(vector)
    
    
    def rotate_vector(self, vector):
        return glm.mul(self._R, glm.vec4(vector, 1)).xyz
    

    # def rotate_around(self, point, normal, speed=1):
    #     center_point_dir = np.subtract(point, self._center)
    #     center_point_dir /= np.linalg.norm(center_point_dir)
    #     new_dir = np.cross(normal, center_point_dir)
    #     return np.add(point, np.multiply(speed, new_dir))
    
    def rotate_around(self, point, normal, speed=1):
        center_point_dir = glm.normalize(glm.sub(point, self._center))
        new_dir = glm.cross(normal, center_point_dir)
        return glm.add(point, glm.mul(speed, new_dir))

    
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
        x_start = glm.cross(y_hat, z_hat)
        return glm.normalize(x_start)
    
    
    def get_camera_y_axis(self):
        y_start = self._up
        return self.rotate_vector(self.normalise_vector(y_start))
    
    
    def get_camera_z_axis(self):
        z_start = glm.sub(self._center, self._eye)
        return self.rotate_vector(self.normalise_vector(z_start))
    
    
    def add_movement(self, movement):    
        y_hat = self.get_camera_y_axis()
        z_hat = self.get_camera_z_axis()
        
        m_y = glm.mul(movement[1], y_hat)
        m_z = glm.mul(movement[2], z_hat)
        m_x = glm.mul(movement[0], self.get_camera_x_axis(y_hat, z_hat))
        
        M_add = glm.translate(glm.add(glm.add(m_x, m_y), m_z))
        
        self._M = glm.mul(M_add, self._M)
    
    
    def update(self):
        # Rotate center around the eye:
        # Add -eye to center, then rotate around origin
        # Then add eye to the new center
        
        R_center = self.rotate_about_point(self._center, glm.neg(self._eye))
        center = glm.mul(self._M, glm.mul(R_center, glm.vec4(self._center, 1))).xyz
        
        eye = glm.mul(self._M, glm.vec4(self._eye, 1)).xyz
        up = glm.mul(self._R, glm.vec4(self._up, 1)).xyz

        self.V = glm.lookAt(eye, center, up)