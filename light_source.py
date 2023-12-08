import glm


class LightSource:
    """A class which represents a light in the scene."""
    def __init__(self, scene, position, Ia=glm.vec3(1,1,1), Id=glm.vec3(1,1,1),
                 Is=glm.vec3(1,1,1)):
        self.scene = scene
        self.position = position

        # Ambient, diffuse and specular intensities
        # These are colours, so e.g. Ia = <1, 0, 0> would give a red light.
        self.Ia = Ia
        self.Id = Id
        self.Is = Is