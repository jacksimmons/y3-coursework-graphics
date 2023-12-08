from enum import Enum
import glm


class Material:
    def __init__(self, name=None, Ka=glm.vec3(1,1,1), Kd=glm.vec3(1,1,1),
                 Ks=glm.vec3(1,1,1), Ns=10.0, texture=None):
        self.name = name
        
        # Ambient, diffuse and specular colour components
        self.Ka = Ka
        self.Kd = Kd
        self.Ks = Ks

        # Specular exponent
        self.Ns = Ns
        
        # `illum` property, determines what type of shading was used in
        # blender. E.g. illum 3 = environment mapping
        self.illumination: int = 0

        self.texture = texture
        self.tex_scale = glm.vec3(1, 1, 1) # Texture scaling, from .mtl "-s"
        
        # Visibility (alpha) of the material
        self.d: float = 1.0
            
    

class MaterialLibrary:
    def __init__(self):
        self.materials = []
        self.names = {}

    
    def add_material(self, material):
        self.names[material.name] = len(self.materials)
        self.materials.append(material)