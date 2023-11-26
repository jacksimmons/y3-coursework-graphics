import glm


class Camera:
    """
    Class which abstracts the thread behaviour of the camera. Gets the View
    Matrix from the camera thread when it is put() into the shared queue.
    """
    def __init__(self):
        self.V = glm.mat4() # View
        self._R = glm.mat4() # Rotation
        self._D = glm.mat4() # Movement
                
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
        # Get the camera's axes
        y_hat = self.get_camera_y_axis()
        z_hat = self.get_camera_z_axis()
        x_hat = self.get_camera_x_axis(y_hat, z_hat)
        
        # Get a quaternion rotation for each camera axis
        y_rot: glm.quat = glm.angleAxis(angles.y, y_hat)
        z_rot: glm.quat = glm.angleAxis(angles.z, z_hat)
        x_rot: glm.quat = glm.angleAxis(angles.x, x_hat)
        
        # The final, additional rotation quaternion
        rot = y_rot * z_rot * x_rot
        
        # Apply the additional rotation to our matrix by multiplication
        self._R = glm.mul(glm.mat4_cast(rot), self._R)
    
    
    def rotate_vector(self, vector):
        return glm.mul(self._R, glm.vec4(vector, 1)).xyz
    
    
    def rotate_around(self, point, normal, speed=1):
        center_point_dir = glm.normalize(glm.sub(point, self._center))
        new_dir = glm.cross(normal, center_point_dir)
        return glm.add(point, glm.mul(speed, new_dir))

    
    def get_camera_x_axis(self, y_hat, z_hat):
        """
        Gets the current x axis (x hat) according to the camera (ie view space)
        Requires y and z axes (see below).
        Note: No rotation is needed, as the rotation should be already applied
        to the y and z directions, and x = y x z.

        Parameters
        ----------
        y_hat : vec3
            The current y axis of the view coordinate space.
        z_hat : vec3
            The current z axis of the view coordinate space.
        """
        x_start = glm.cross(y_hat, z_hat)
        return glm.normalize(x_start)
    
    
    def get_camera_y_axis(self):
        """
        Gets the y axis of the view coordinate space.
        """
        y_start = self._up
        return glm.normalize(self.rotate_vector(y_start))
    
    
    def get_camera_z_axis(self):
        """
        Gets the z axis of the view coordinate space.
        """
        z_start = glm.sub(self._center, self._eye)
        return glm.normalize(self.rotate_vector(z_start))
    
    
    def move(self, d):
        """
        Creates a matrix from a displacement vector, then multiplies the
        existing displacement matrix (self._D) by it.
        "Stacks" a camera translation on top of previous translations.
        
        Parameters
        ----------
        d : vec3
            Displacement vector.
        """
        y_hat = self.get_camera_y_axis()
        z_hat = self.get_camera_z_axis()
        
        m_y = glm.mul(d.y, y_hat)
        m_z = glm.mul(d.z, z_hat)
        m_x = glm.mul(d.x, self.get_camera_x_axis(y_hat, z_hat))
        
        M_add = glm.translate(m_x + m_y + m_z)
        self._D = glm.mul(M_add, self._D)
    
    
    def update(self):
        """
        1. Rotate center around the eye ("Universe rotates around camera")
            (Translate center by -eye, then rotate it around origin with R)
            (Then translate the new center by eye)
        2. Translate the eye with the displacement matrix (Camera movement)
        3. Rotate the up vector around origin with R.
        Combining these gives the view matrix.
        """
        
        rot_center_about_eye: glm.mat4x4 = self.rotate_about_point(self._center, glm.neg(self._eye))
        center = glm.mul(self._D, glm.mul(rot_center_about_eye, glm.vec4(self._center, 1))).xyz
        
        eye = glm.mul(self._D, glm.vec4(self._eye, 1)).xyz
        up = glm.mul(self._R, glm.vec4(self._up, 1)).xyz

        self.V = glm.lookAt(eye, center, up)
