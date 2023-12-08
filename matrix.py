import glm

# A static class for useful matrix operations
class Matrix:
    @staticmethod
    def rotate_about_point(p, c, R):
        """
        Parameters
        ----------
        p : vec3
            The point to rotate.
        c : vec3
            The center of rotation.
        R : mat4x4
            The rotation matrix to apply.

        Returns
        -------
        A mat4x4 corresponding to the rotation of p about c.
        """
        
        PC = c - p
        T_PC = glm.translate(PC)
        T_CP = glm.translate(glm.neg(PC))
        
        return T_CP * R * T_PC

    
    @staticmethod
    def decompose(M) -> tuple[3]:
        """
        Decomposes a transformation matrix into position, rotation and scale.
        Used reference [0].
        
        Parameters
        ----------
        M : mat4x4
            The transformation matrix.

        Returns
        -------
        position: vec3, rotation: mat4x4, scale: vec3.
        """
        
        # Last column is position
        position = glm.vec3(M[3])
        
        # Extract scale * rotation by subtracting position
        SR = glm.mat4x4()
        for i in range(0, 3):
            # Copy the first 3 columns
            SR[i] = M[i]
        # "Subtract" the position by setting the 4th column to <0,0,0,1>
        SR[3] = glm.vec4(0,0,0,1)
        # The scale can be extracted from a scale * rotation matrix, by getting
        # the length of each column vector.
        scale = glm.vec3(glm.length(SR[0]), glm.length(SR[1]), glm.length(SR[2]))
        
        # Using the above line of logic, just divide by these lengths to get the
        # rotation matrix.
        rotation = glm.mat4x4()
        for i in range(0, 3):
            rotation[i] = SR[i] / scale[i]
        
        # Return a tuple of the results
        return position, rotation, scale
        
        