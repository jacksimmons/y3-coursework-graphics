#version 330 core

//=== in attributes are read from the vertex array, one row per instance of the shader
// Forgoes glBindAttribLocation call
// https://www.khronos.org/opengl/wiki/Layout_Qualifier_(GLSL)
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
layout (location = 2) in vec3 colour;
layout (location = 3) in vec2 tex_coord;

//=== out attributes are interpolated on the face, and passed on to the fragment shader
out vec3 fragment_color;        // the output of the shader will be the colour of the vertex
out vec3 fragment_normal;
out vec3 fragment_pos;   // the position of the vertex in view coordinates
out vec2 fragment_tex_coord;

//=== uniforms
uniform mat4 PVM;
uniform mat4 VM;
uniform mat4 VM_it;
uniform int mode;	// the rendering mode (better to code different shaders!)

void main(){
    // 1. first, we transform the position using PVM matrix.
    // note that gl_Position is a standard output of the
    // vertex shader.
    gl_Position = PVM * vec4(position, 1.0f);

    // 2. calculate vectors used for shading calculations
    // those will be interpolate before being sent to the
    // fragment shader.
    fragment_pos = vec3(VM * vec4(position, 1.0f));
    fragment_normal = vec3(VM_it * vec4(normalize(normal), 1.0f));
    fragment_tex_coord = tex_coord;
}   
