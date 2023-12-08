from OpenGL.GL import *


class Settings:
    """
    A class for changing certain program attributes.
    Abstracts changing render mode, cull mode, etc.
    """
    def __init__(self, scene):
        self.scene = scene

        self.render_mode: int
        self.render_modes: list =\
            [GL_POINT, GL_LINE, GL_FILL]
        self.render_modes_verbose: list =\
            ["Point", "Line", "Fill"]
        self.set_render_mode(2)

        self.cull_mode: int
        self.cull_modes: list =\
            [GL_BACK, GL_FRONT]
        self.cull_modes_verbose: list =\
            ["Back face", "Front face"]
        self.set_cull_mode(0)


        self.shading_mode: int = 0
        self.shading_modes: list =\
            ["default", "phong", "blinn"]
        
        self.updates = {"shadows": True, "environment": True, "stats": False}
    

    def set_render_mode(self, value: int):
        self.render_mode = value
        glPolygonMode(GL_FRONT_AND_BACK, self.render_modes[value])


    def set_cull_mode(self, value: int):
        self.cull_mode = value
        glEnable(GL_CULL_FACE)
        glCullFace(self.cull_modes[value])
    
    
    def set_shading_mode(self, value: int):
        self.shading_mode = value
        self.scene.set_shaders(self.shading_modes[value])
    

    def next(self, value: int, length: int):
        """Returns the next index in a list from its length.
        Wraps around to 0 after length - 1."""
        value += 1
        if value >= length:
            value = 0
        return value
    

    def next_render_mode(self):
        self.set_render_mode(self.next(self.render_mode, len(self.render_modes)))
        print("Changed render mode to: " + self.render_modes_verbose[self.render_mode])
    

    def next_cull_mode(self):
        self.set_cull_mode(self.next(self.cull_mode, len(self.cull_modes)))
        print("Changed cull mode to: " + self.cull_modes_verbose[self.cull_mode])
    

    def next_shading_mode(self):
        self.set_shading_mode(self.next(self.shading_mode, len(self.shading_modes)))
        print("Changed shading mode to: " + self.shading_modes[self.shading_mode])


    def toggle_update(self, key):
        self.updates[key] = not self.updates[key]
        if self.updates[key]:
            output = "Enabled updates for "
        else:
            output = "Disabled updates for "
        print(output + key)