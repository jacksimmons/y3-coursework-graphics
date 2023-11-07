#version 130		// required to use OpenGL core standard

//=== in attributes are read from the vertex array, one row per instance of the shader
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
layout (location = 2) in vec3 colour;
layout (location = 3) in vec3 tex_coord;

//=== out attributes are interpolated on the face, and passed on to the fragment shader
out vec2 fragment_tex_coord;
out vec3 view_normal;
out vec3 view_tangent;
out vec3 view_binormal;

//=== uniforms
uniform mat4 PVM;


void main(){
    // 1. first, we transform the position using PVM matrix.
    // note that gl_Position is a standard output of the
    // vertex shader.
    gl_Position = PVM * vec4(position, 1.0f);


    // 2. forward the texture coordinates.
    fragment_tex_coord = tex_coord;
}
