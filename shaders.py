# imports all openGL functions
from OpenGL.GL import *
import glm
import numpy as np


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
            print('(E) Warning, no uniform {}'.format(self.name))
    
    
    def bind_int(self, value):
        if value is not None:
            self.value = value
            
        try:
            glUniform1i(self.location, self.value)
        except:
            print(f"Invalid int: {type(value)}")
    
    
    def bind_float(self, value):
        if value is not None:
            self.value = value
            
        try:
            glUniform1f(self.location, self.value)
        except:
            print(f"Invalid float: {type(value)}")
    
    
    def bind_vec3(self, value):
        if value is not None:
            self.value = value
        
        data = np.array(self.value, "f")
        try:
            glUniform3fv(self.location, 1, data)
        except Exception as e:
            print(f"Invalid vec3.\nType: {type(value)}")
            input(f"Data: {data}")
            print(e)
    
    
    def bind_vec4(self, value):
        if value is not None:
            self.value = value
        
        data = np.array(self.value, "f")
        try:
            glUniform4fv(self.location, 1, data)
        except Exception as e:
            print(f"Invalid vec4.\nType: {type(value)}")
            input(f"Data: {data}")
            print(e)
    
    
    def bind_mat3x3(self, value):
        if value is not None:
            self.value = value
        
        data = np.array(self.value, "f")
        try:
            glUniformMatrix3fv(self.location, 1, True, data)
        except Exception as e:
            print(f"Invalid 3x3 matrix.\nType: {type(value)}")
            input(f"Data: {data}")
            print(e)
    
    
    def bind_mat4x4(self, value):
        if value is not None:
            self.value = value
        
        print(self.location)
        
        data = np.array(self.value, "f")
        try:
            print(data)
            glUniformMatrix4fv(self.location, 1, True, data)
        except Exception as e:
            print(f"Invalid 4x4 matrix.\nType: {type(value)}")
            input(f"Data: {data}")
            print(e)


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
        print('Creating shader program: {}'.format(name) )

        vertex_shader_file = None
        fragment_shader_file = None

        if name is not None:
            vertex_shader_file = 'shaders/{}/vertex_shader.glsl'.format(name)
            fragment_shader_file = 'shaders/{}/fragment_shader.glsl'.format(name)

        # load the vertex shader GLSL code
        if vertex_shader_file is not None:
            #print('Load vertex shader from file: {}'.format(vertex_shader))
            with open(vertex_shader_file, 'r') as file:
                self.vertex_shader_source = file.read()
            # print(self.vertex_shader_source)

        # load the fragment shader GLSL code
        if fragment_shader_file is not None:
            #print('Load fragment shader from file: {}'.format(fragment_shader))
            with open(fragment_shader_file, 'r') as file:
                self.fragment_shader_source = file.read()
            # print(self.fragment_shader_source)

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
        print('Compiling GLSL shaders [{}]...'.format(self.name))
        try:
            shader_vert = shaders.compileShader(self.vertex_shader_source, shaders.GL_VERTEX_SHADER)
            shader_frag = shaders.compileShader(self.fragment_shader_source, shaders.GL_FRAGMENT_SHADER)
            
            self.program = glCreateProgram()
            glAttachShader(self.program, shader_vert)
            glAttachShader(self.program, shader_frag)
        except RuntimeError as error:
            print('(E) An error occured while compiling {} shader:\n {}\n... forwarding exception...'.format(self.name, error)),
            raise error

        glLinkProgram(self.program)

        log = glGetShaderInfoLog(shader_frag)
        print(log)

        log = glGetShaderInfoLog(shader_vert)
        print(log)

        log = glGetProgramInfoLog(self.program)
        print(log)

        # tell OpenGL to use this shader program for rendering
        glUseProgram(self.program)

        for attrib in ["position", "normal", "colour", "tex_coord"]:
            print(attrib + str(glGetAttribLocation(self.program, attrib)))

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
            'light_pos': Uniform('light_pos', glm.vec3(0.,0.,0.)),
            'Ia': Uniform('Ia'),
            'Id': Uniform('Id'),
            'Is': Uniform('Is'),
            'has_texture': Uniform('has_texture'),
            'textureObject': Uniform('textureObject')
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
        if self.P is None or not glm.equal(self.P, _P):
            self.P = _P
            recalculate_P = True
        
        # Camera's view matrix
        _V = model.scene.camera.V
        if self.V is None or not glm.equal(self.V, _V):
            self.V = _V
            recalculate_V = True
        
        # Model matrix
        if self.M is None or not glm.equal(self.M, M):
            self.M = M
            recalculate_M = True
        
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
            #M_it = np.linalg.inv(M)[:3, :3].transpose()
            self.uniforms["M_it"].bind_mat4x4(M_it)
            
            VM_it = glm.inverseTranspose(VM)
            #np.linalg.inv(VM)[:3, :3].transpose()
            self.uniforms["VM_it"].bind_mat4x4(VM_it)


        if recalculate_P or recalculate_M or recalculate_V:
            self.uniforms["PVM"].bind_mat4x4(glm.mul(_P, glm.mul(_V, M)))

        # bind the mode to the program
        self.uniforms['mode'].bind_int(model.scene.mode)

        self.uniforms['alpha'].bind_float(model.mesh.material.alpha)

        if len(model.mesh.textures) > 0:
            # bind the texture(s)
            self.uniforms['textureObject'].bind_int(0)
            self.uniforms['has_texture'].bind_int(1)
        else:
            self.uniforms['has_texture'].bind_int(0)

        # bind material properties
        self.bind_material_uniforms(model.mesh.material)

        # bind the light properties
        self.bind_light_uniforms(model.scene.light, self.V)

    def bind_light_uniforms(self, light, V):
        light_pos_homog = glm.vec4(light.position, 1)
        self.uniforms['light_pos'].bind_vec3(glm.mul(V, light_pos_homog).xyz)
        self.uniforms['Ia'].bind_vec3(light.Ia)
        self.uniforms['Id'].bind_vec3(light.Id)
        self.uniforms['Is'].bind_vec3(light.Is)

    def bind_material_uniforms(self, material):
        self.uniforms['Ka'].bind_vec3(material.Ka)
        self.uniforms['Kd'].bind_vec3(material.Kd)
        self.uniforms['Ks'].bind_vec3(material.Ks)
        self.uniforms['Ns'].bind_float(material.Ns)

    def add_uniform(self, name):
        if name in self.uniforms:
            print('(W) Warning re-defining already existing uniform %s' % name)
        self.uniforms[name] = Uniform(name)

    def unbind(self):
        glUseProgram(0)


class FlatShader(Shader):
    def __init__(self):
        super().__init__(name='flat')


class GouraudShader(Shader):
    def __init__(self):
        super().__init__(name='gouraud')


class PhongShader(Shader):
    def __init__(self):
        super().__init__(name='phong')


class BlinnShader(Shader):
    def __init__(self):
        super().__init__(name='blinn')


class TextureShader(Shader):
    def __init__(self):
        super().__init__(name='texture')

