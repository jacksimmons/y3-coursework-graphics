import glm
from matrix import Matrix


class Camera:
    """
    Class which abstracts the behaviour of the camera.
    """
    def __init__(self):
        self.V = glm.mat4() # View
        self._R = glm.mat4() # Rotation
        self._D = glm.mat4() # Movement
                
        self._eye = glm.vec3(0, 1, -5)
        self._up = glm.vec3(0, 1, 0)
        self._center = glm.vec3(0, 1, 0)
                
        self.update()
    
    
    def add_rotation(self, angles):
        """Adds a rotation to the camera's view matrix."""
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
        self._R = (glm.mat4_cast(rot) * self._R)
        
        self.update()
    
    
    def rotate_vector(self, vector):
        """Rotates a vector by the camera's view matrix."""
        return (self._R * glm.vec4(vector, 1)).xyz

    
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
        z_start = self._center - self._eye
        return glm.normalize(self.rotate_vector(z_start))
    
    
    def move(self, d):
        """
        Creates a matrix from a displacement vector, then multiplies the
        existing displacement matrix (self._D) by it.
        "Stacks" a camera translation on top of previous translations.
        View matrix requires recalculation after this, so calls update().
        
        Parameters
        ----------
        d : vec3
            Displacement vector.
        """
        y_hat = self.get_camera_y_axis()
        z_hat = self.get_camera_z_axis()
        
        m_y = d.y * y_hat
        m_z = d.z * z_hat
        m_x = d.x * self.get_camera_x_axis(y_hat, z_hat)
        
        M_add = glm.translate(m_x + m_y + m_z)
        self._D = M_add * self._D
        
        self.update()
    
    
    def update(self):
        """
        1. Rotate center around the eye ("Universe rotates around camera")
            (Translate center by -eye, then rotate it around origin with R)
            (Then translate the new center by eye)
        2. Translate the eye with the displacement matrix (Camera movement)
        3. Rotate the up vector around origin with R.
        Combining these gives the view matrix.
        """
        
        rot_center_about_eye: glm.mat4x4 =\
            Matrix.rotate_about_point(self._center, -self._eye, self._R)
        center = (self._D * rot_center_about_eye * glm.vec4(self._center, 1)).xyz
        
        eye = (self._D * glm.vec4(self._eye, 1)).xyz
        up = (self._R * glm.vec4(self._up, 1)).xyz

        self.V = glm.lookAt(eye, center, up)
