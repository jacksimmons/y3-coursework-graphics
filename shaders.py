# imports all openGL functions
from OpenGL.GL import *
from OpenGL.GL import shaders
import glm
import numpy as np
from log import Logger


logger = Logger(False, False, True)


class Uniform:
    '''
    We create a simple class to handle uniforms, this is not necessary,
    but allow to put all relevant code in one place
    '''
    def __init__(self, name, value=None):
        '''
        Initialise the uniform parameter
        :param name: the name of the uniform, as stated in the GLSL code
        '''
        self.name = name
        self.value = value
        self.location = -1


    def link(self, program):
        '''
        This function needs to be called after compiling the GLSL program to fetch the location of the uniform
        in the program from its name
        :param program: the GLSL program where the uniform is used
        '''
        self.location = glGetUniformLocation(program=program, name=self.name)
        if self.location == -1:
            logger.warning(f"No uniform {self.name}")
    
    
    def bind_int(self, value: int):
        """Binds an integer uniform."""
        if value is not None:
            self.value = value
            
        try:
            glUniform1i(self.location, self.value)
        except:
            logger.type_error("int", value)
            raise
    
    
    def bind_float(self, value: float):
        """Binds a float uniform."""
        if value is not None:
            self.value = value
            
        try:
            glUniform1f(self.location, self.value)
        except:
            logger.type_error("float", value)
            raise
    
    
    def bind_vec3(self, value: glm.vec3):
        """Binds a 3D vector uniform."""
        if value is not None:
            self.value = value
        
        data = np.array(self.value, "f")
        try:
            glUniform3fv(self.location, 1, data)
        except:
            logger.type_error("vec3", data)
            raise
    
    
    def bind_vec4(self, value: glm.vec4):
        """Binds a 4D vector uniform."""
        if value is not None:
            self.value = value
        
        data = np.array(self.value, "f")
        try:
            glUniform4fv(self.location, 1, data)
        except:
            logger.type_error("vec4", data)
            raise
    
    
    def bind_mat3x3(self, value: glm.mat3x3, transpose=True):
        """Binds a 3x3 matrix uniform."""
        if value is not None:
            self.value = value
        
        data = np.array(self.value, "f")
        try:
            glUniformMatrix3fv(self.location, 1, transpose, data)
        except:
            logger.type_error("mat3x3", data)
            raise
    
    
    def bind_mat4x4(self, value, transpose=True):
        """Binds a 4x4 matrix uniform."""
        if value is not None:
            self.value = value
                
        data = np.array(self.value, "f")
        try:
            glUniformMatrix4fv(self.location, 1, transpose, data)
        except:
            logger.type_error("mat4x4", data)
            raise


class BaseShaderProgram:
    '''
    This is the base class for loading and compiling the GLSL shaders.
    '''
    def __init__(self, name=None, vertex_shader=None, fragment_shader=None):
        '''
        Initialises the shaders
        :param vertex_shader: the name of the file containing the vertex shader GLSL code
        :param fragment_shader: the name of the file containing the fragment shader GLSL code
        '''

        self.name = name
        logger.info(f"Creating shader program: {name}")

        vertex_shader_file = None
        fragment_shader_file = None

        if name is not None:
            fname = name
            if fname == "blinn":
                fname = "phong"
            vertex_shader_file = 'shaders/{}/vertex_shader.glsl'.format(fname)
            fragment_shader_file = 'shaders/{}/fragment_shader.glsl'.format(fname)
            
            logger.info(vertex_shader_file)
            logger.info(fragment_shader_file)

        # load the vertex shader GLSL code
        if vertex_shader_file is not None:
            #print('Load vertex shader from file: {}'.format(vertex_shader))
            with open(vertex_shader_file, 'r') as file:
                self.vertex_shader_source = file.read()

        # load the fragment shader GLSL code
        if fragment_shader_file is not None:
            #print('Load fragment shader from file: {}'.format(fragment_shader))
            with open(fragment_shader_file, 'r') as file:
                self.fragment_shader_source = file.read()

        # in order to simplify extension of the class in the future, we start storing uniforms in a dictionary.
        self.uniforms = {
            "PVM": Uniform("PVM"),
        }


    def add_uniform(self, name):
        self.uniforms[name] = Uniform(name)


    def compile(self):
        '''
        Call this function to compile the GLSL codes for both shaders.
        :return:
        '''
        logger.info(f"Compiling {self.name} shaders...")
        
        try:
            shader_vert = shaders.compileShader(self.vertex_shader_source, shaders.GL_VERTEX_SHADER)
            shader_frag = shaders.compileShader(self.fragment_shader_source, shaders.GL_FRAGMENT_SHADER)
            
            self.program = glCreateProgram()
            glAttachShader(self.program, shader_vert)
            glAttachShader(self.program, shader_frag)
        except RuntimeError as error:
            logger.error(f"An error occured while compiling {self.name} shader:")
            raise error

        glLinkProgram(self.program)

        # Shader info logs
        log = glGetShaderInfoLog(shader_frag)
        logger.info(log)

        log = glGetShaderInfoLog(shader_vert)
        logger.info(log)

        log = glGetProgramInfoLog(self.program)
        logger.info(log)

        # tell OpenGL to use this shader program for rendering
        glUseProgram(self.program)

        # link all uniforms
        for uniform in self.uniforms:
            self.uniforms[uniform].link(self.program)


    def bind(self, model, M):
        '''
        Call this function to enable this GLSL Program (you can have multiple GLSL programs used during rendering!)
        '''
        # tell OpenGL to use this shader program for rendering
        glUseProgram(self.program)

        P = model.scene.P
        V = model.scene.camera.V

        self.uniforms["PVM"].bind_mat4x4(glm.mul(P, glm.mul(V, M)))


class Shader(BaseShaderProgram):
    def __init__(self, name: str):
        '''
        Initialises the shaders
        :param vertex_shader: the name of the file containing the vertex shader GLSL code
        :param fragment_shader: the name of the file containing the fragment shader GLSL code
        '''

        super().__init__(name=name)
        
        # Store temp values so that the inverse matrix doesn't need to be
        # calculated when these haven't changed
        self.P = None
        self.V = None
        self.M = None

        # in order to simplify extension of the class in the future, we start storing uniforms in a dictionary.
        self.uniforms = {
            "M": Uniform("M"),
            "V_t": Uniform("V_t"),
            "PV": Uniform("PV"),
            "VM": Uniform("VM"),
            "M_it": Uniform("M_it"),
            "VM_it": Uniform("VM_it"),
            "PVM": Uniform("PVM"),
            'mode': Uniform('mode', 0),  # rendering mode (only for illustration, in general you will want one shader program per mode)
            'alpha': Uniform('alpha', 0),
            'Ka': Uniform('Ka'),
            'Kd': Uniform('Kd'),
            'Ks': Uniform('Ks'),
            'Ns': Uniform('Ns'),
            "tex_scale": Uniform("tex_scale"),
            'light_pos': Uniform('light_pos', glm.vec3(0.,0.,0.)),
            'Ia': Uniform('Ia'),
            'Id': Uniform('Id'),
            'Is': Uniform('Is'),
            'has_texture': Uniform('has_texture'),
            'texture_object': Uniform('texture_object')
            #'textureObject2': Uniform('textureObject2'),
        }
    
    def bind(self, model, M):
        '''
        Call this function to enable this GLSL Program (you can have multiple GLSL programs used during rendering!)
        '''

        # tell OpenGL to use this shader program for rendering
        glUseProgram(self.program)

        recalculate_P = False
        recalculate_V = False
        recalculate_M = False
        
        # Scene's projection matrix
        _P = model.scene.P
        if self.P != _P:
            self.P = _P
            recalculate_P = True
        
        # Camera's view matrix
        _V = model.scene.camera.V
        if self.V != _V:
            self.V = _V
            recalculate_V = True
        
        # Model matrix
        if self.M != M:
            self.M = M
            recalculate_M = True
        
        # Only recalculates matrices if necessary - allows faster
        # frame times when camera is not moving, and environment and shadow
        # maps are disabled.
        
        # Binds the following calculations to shader uniforms.
        if recalculate_M:
            self.uniforms["M"].bind_mat4x4(M)
        
        if recalculate_V:
            self.uniforms["V_t"].bind_mat4x4(glm.transpose(_V))
        
        if recalculate_P or recalculate_V:
            self.uniforms["PV"].bind_mat4x4(glm.mul(_P, _V))

        if recalculate_V or recalculate_M:
            VM = glm.mul(_V, M)
            self.uniforms["VM"].bind_mat4x4(VM)
            
            M_it = glm.inverseTranspose(M)
            self.uniforms["M_it"].bind_mat4x4(M_it)
            
            VM_it = glm.inverseTranspose(VM)
            self.uniforms["VM_it"].bind_mat4x4(VM_it)


        if recalculate_P or recalculate_M or recalculate_V:
            self.uniforms["PVM"].bind_mat4x4(glm.mul(_P, glm.mul(_V, M)))

        # bind the mode to the program
        self.uniforms['mode'].bind_int(model.scene.mode)

        self.uniforms['alpha'].bind_float(model.mesh.material.d)

        if len(model.mesh.textures) > 0:
            self.uniforms['texture_object'].bind_int(0)
            self.uniforms['has_texture'].bind_int(1)
        else:
            self.uniforms['has_texture'].bind_int(0)

        # bind material properties
        self.bind_material_uniforms(model.mesh.material)

        # bind the light properties
        self.bind_light_uniforms(model.scene.light, self.V)

    def bind_light_uniforms(self, light, V):
        """Binds all relevant uniforms for a light to the shader."""
        light_pos_homog = glm.vec4(light.position, 1)
        self.uniforms['light_pos'].bind_vec3(glm.mul(V, light_pos_homog).xyz)
        self.uniforms['Ia'].bind_vec3(light.Ia)
        self.uniforms['Id'].bind_vec3(light.Id)
        self.uniforms['Is'].bind_vec3(light.Is)

    def bind_material_uniforms(self, material):
        """Binds all relevant uniforms for a material to the shader."""
        self.uniforms['Ka'].bind_vec3(material.Ka)
        self.uniforms['Kd'].bind_vec3(material.Kd)
        self.uniforms['Ks'].bind_vec3(material.Ks)
        self.uniforms['Ns'].bind_float(material.Ns)
        self.uniforms["tex_scale"].bind_vec3(material.tex_scale)

    def add_uniform(self, name):
        if name in self.uniforms:
            logger.warning(f"Re-defining existing uniform {name}")
        self.uniforms[name] = Uniform(name)

    def unbind(self):
        glUseProgram(0)


class PhongShader(Shader):
    """
    A shader which can use Phong or Blinn-Phong shading based on parameters.
    """
    def __init__(self, blinn, name=None):
        if name is None:
            if blinn:
                name = "blinn"
            else:
                name = "phong"
        
        super().__init__(name)
        self.add_uniform("blinn")
        
        self.blinn = blinn
    
    
    def bind(self, model, M):
        super().bind(model, M)
        
        if self.blinn:
            self.uniforms["blinn"].bind_int(1)
        else:
            self.uniforms["blinn"].bind_int(0)


class EnvironmentShader(BaseShaderProgram):
    """
    A shader for environment mapping.
    """
    def __init__(self, env_map=None):
        super().__init__(name="environment")
        self.add_uniform('sampler_cube')
        self.add_uniform('VM')
        self.add_uniform('VM_it')
        self.add_uniform('V_t')
        self.add_uniform("alpha")

        self.map = env_map


    def bind(self, model, M):        
        unit = len(model.mesh.textures)

        glActiveTexture(GL_TEXTURE0)
        self.map.bind()
        
        glUseProgram(self.program)
        
        self.uniforms['sampler_cube'].bind_int(0)

        P = model.scene.P  # get projection matrix from the scene
        V = model.scene.camera.V

        # set the PVM matrix uniform
        self.uniforms['PVM'].bind_mat4x4(glm.mul(P, glm.mul(V, M)))
        self.uniforms['VM'].bind_mat4x4(glm.mul(V, M))
        self.uniforms['VM_it'].bind_mat4x4(glm.inverseTranspose(glm.mul(V, M)))
        self.uniforms['V_t'].bind_mat4x4(glm.transpose(V))
        self.uniforms['alpha'].bind_float(model.mesh.material.d)


class ShadowMappingShader(PhongShader):
    """
    A shader for shadow mapping combined with Phong/Blinn-Phong shading.
    """
    def __init__(self, shadow_map=None):
        super().__init__(blinn=True, name='shadow_mapping')
        self.add_uniform('shadow_map')
        self.add_uniform('light_PV')
        
        self.shadow_map = shadow_map

    def bind(self, model, M):
        super().bind(model, M)
        
        self.uniforms['shadow_map'].bind_int(1)
        
        # Bind the shadow map to a different texture slot
        glActiveTexture(GL_TEXTURE1)
        self.shadow_map.bind()
        glActiveTexture(GL_TEXTURE0)
        
        V = model.scene.camera.V
        V_i = glm.inverse(V)

        # Clip coordinates = P_s V_s V_vi
        # Range is [-1, 1]
        # Translate to move it to [0, 2]
        # Scale it by 1/2 to move it to [0, 1]
        light_PV = glm.scale(glm.vec3(0.5,0.5,0.5))\
                * glm.translate(glm.vec3(1,1,1))\
                * self.shadow_map.P * self.shadow_map.V * V_i
                
        self.uniforms["light_PV"].bind_mat4x4(light_PV)