import glm


class Material:
    def __init__(self, name=None, Ka=glm.vec3(1,1,1), Kd=glm.vec3(1,1,1),
                 Ks=glm.vec3(1,1,1), Ns=10.0, texture=None):
        self.name = name
        
        # Ambient colour
        self.Ka = Ka
        # Diffuse colour
        self.Kd = Kd
        # Specular colour
        self.Ks = Ks
        # Specular exponent
        self.Ns = Ns
        
        self.texture = texture
        self.alpha = 1.0
    

class MaterialLibrary:
    def __init__(self):
        self.materials = []
        self.names = {}

    
    def add_material(self, material):
        self.names[material.name] = len(self.materials)
        self.materials.append(material)