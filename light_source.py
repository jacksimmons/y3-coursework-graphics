import numpy as np


class LightSource:
    def __init__(self, scene, position, Ia=[1,1,1], Id=[1,1,1], Is=[1,1,1]):
        self.scene = scene
        self.position = np.array(position, 'f')
        self.Ia = Ia
        self.Id = Id
        self.Is = Is
    

    def update(self, position=None):
        if position is not None:
            self.position = position