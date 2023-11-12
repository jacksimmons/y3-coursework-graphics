import glm


class LightSource:
    def __init__(self, scene, position, Ia=glm.vec3(1,1,1), Id=glm.vec3(1,1,1),
                 Is=glm.vec3(1,1,1)):
        self.scene = scene
        self.position = position
        self.Ia = Ia
        self.Id = Id
        self.Is = Is
    

    def update(self, position=None):
        if position is not None:
            self.position = position