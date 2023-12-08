import math
import pygame
import glm
import time
from OpenGL.GL import *

from scene import Scene
from model import DrawModelFromMesh
from texture import Texture
from material import Material
from shaders import Shader
from light_source import LightSource
from skybox import SkyBox
from matrix import Matrix


class Program(Scene):
    def __init__(self):
        super().__init__()
        
        # Log how long the program takes to setup
        time_start = time.time()

        # Setup every model in the scene
        self.skybox = SkyBox(folder="skybox", file_format="jpg", scene=self)

        # Contains all non-moving models except for the floor, for conciseness.
        self.add_models_from_obj("models/scene_nofloor.obj", name="scene", shadows=True)
        # All floor objects, separated for environment mapping purposes.
        self.add_models_from_obj("models/floor.obj", name="floor", shadows=True, in_environment=True)

        # The only moving model.
        self.trex_plane_pos = glm.vec3(0,15,0)
        self.trex_plane = self.add_models_from_obj("models/trex_plane.obj", pos=self.trex_plane_pos,
                                 rotation=glm.vec3(-math.pi/16, 0, math.pi/16),
                                 name="TrexOnPlane", in_environment=True)
        
        # Finish logging
        time_end = time.time()
        print(f"\n\nScene loaded after {time_end - time_start}s\n\n")
        
    
    
    """The mainloop, which runs until exit."""
    def run(self):
        print(self.help)
        
        clock = pygame.time.Clock()
        lasttime = pygame.time.get_ticks() # To make debug updates every second
        fps: float = 1
        
        # Animated object properties
        c = glm.vec3(0,0,5)
        rot: glm.quat = glm.angleAxis(0.01, glm.vec3(0,1,0))
        R = glm.mat4_cast(rot)

        self.set_shaders("phong")
        
        while self.running:
            # FPS logging
            clock.tick()
            fps = clock.get_fps()

            for model in self.trex_plane:
                # Plane follows an orbital motion
                omega = 0.05

                if fps == 0:
                    fps = 60
                T = glm.translate(glm.vec3(0,0,1.75) / (fps / 15))
                R = glm.rotate(omega / (fps / 15), glm.vec3(0,1,0))
                model.M *= R * T * R
            
            # Carries out next scene frame
            super().next_frame()
            
            # Debug information
            time = pygame.time.get_ticks()
            if self.settings.updates["stats"] and time - lasttime > 1000:
                V_decomp = Matrix.decompose(self.camera.V)
                lasttime = time
                print(f"""
                      FPS: {str(int(fps))}
                      Render mode: {self.settings.render_modes_verbose[self.settings.render_mode]}
                      Cull mode: {self.settings.cull_modes_verbose[self.settings.cull_mode]}
                      Shading mode: {self.settings.shading_modes[self.settings.shading_mode]}
                      Update Shadows: {self.settings.updates["shadows"]}
                      Update Environment: {self.settings.updates["environment"]}
                      Camera Position: {V_decomp[0]}
                      Camera Pan Velocity: {self.pan_velocity}
                      """)


# Entry point
def main():    
    prog = Program()
    prog.run()
        

if __name__ == "__main__":
    main()