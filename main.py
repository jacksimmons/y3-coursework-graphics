import math
import pygame
import glm
import time
from OpenGL.GL import (glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT)

from matutils import poseMatrix, translationMatrix, scaleMatrix
from scene import Scene
from mesh import CubeMesh, SphereMesh
from model import DrawModelFromMesh
from texture import Texture
from material import Material
from shaders import Shader
from light_source import LightSource
from cube_map import FlattenCubeMap
from shadow_mapping import ShadowMap, ShadowMappingShader, ShowTexture
from skybox import SkyBox


class MyScene(Scene):
    def __init__(self):
        super().__init__()
        
        time_start = time.time()

        self.shaders = "flat"
        
        # https://www.cleanpng.com/png-cube-mapping-skybox-reflection-mapping-texture-map-1274504/
        self.skybox = SkyBox(folder="skybox", file_format="jpg", scene=self)

        # this object allows to visualise the flattened cube
        self.flattened_cube = FlattenCubeMap(scene=self, cube=self.environment)

        self.light = LightSource(self, position=glm.vec3(0, 150, 0),
                                 Ia=glm.vec3(0.2,0.2,0.2),
                                 Id=glm.vec3(1,1,1),
                                 Is=glm.vec3(1,1,1))
        self.show_light = DrawModelFromMesh(self, 
                                            glm.translate(self.light.position),
                                            SphereMesh(), "Sun", Shader("flat"))
        self.add_model(self.show_light)

        # for shadow map rendering
        self.shadows = ShadowMap(light=self.light)
        self.show_shadow_map = ShowTexture(self, self.shadows)
        
        
        # === Floor
        # WATER: https://www.freepik.com/free-photo/summer-background-sea-water_4433027.htm#query=water%20texture&position=1&from_view=keyword&track=ais"Image by kdekiara</a> on Freepik
        # Concrete Texture / Road: https://sketchfab.com/3d-models/old-street-pack-a633537bfc7c4d99a3a618662513cbf9
        # Tower Bridge: Giimann. www.wirecase.com
        # TREX: https://sketchfab.com/3d-models/mama-scarface-ac51ce40425545dcac70c3e34b9a0105#download
        # SHARK: https://sketchfab.com/3d-models/megalodon-a311be02d8fe4e86a33edc7426245e03
        # BIG BEN: https://sketchfab.com/3d-models/big-ben-58064c3815f34b759a5bbb75fb8d8eb2
        # BUS (edited): https://free3d.com/3d-model/tourist-bus-with-open-top-v2--502214.html
        # CITY BUILDINGS: https://sketchfab.com/3d-models/low-poly-city-buildings-e0209ac5bb684d2d85e5ade96c92d2ff && textures.com
        self.add_models_from_obj("models/scene.obj", name="scene")
        
        self.add_models_from_obj("models/pterodactyl.obj",
                                 pos=glm.vec3(-20,100,-10),
                                 name="Pterodactyl1")
        self.add_models_from_obj("models/pterodactyl.obj",
                                 pos=glm.vec3(-10,100,0),
                                 name="Pterodactyl2")
        self.add_models_from_obj("models/pterodactyl.obj",
                                 pos=glm.vec3(0,100,-14),
                                 name="Pterodactyl3")
        
        #TREX: https://sketchfab.com/3d-models/dinosaur-texture-by-pop-obj-f6009a7bedb648f688f18e9bc03cc6ab#download        
        #PLANE: https://sketchfab.com/3d-models/low-poly-plane-76230052903540e9aeb46b7db35329e4#download
        self.add_models_from_obj("models/trex_plane.obj", pos=glm.vec3(4,11,4),
                                 rotation=glm.vec3(-math.pi/16, 0, math.pi/16),
                                 name="TrexOnPlane")
        
        time_end = time.time()
        print(f"\n\nScene loaded after {time_end - time_start}s\n\n")


def main():
    scene = MyScene()
    scene.run()
        

if __name__ == "__main__":
    main()