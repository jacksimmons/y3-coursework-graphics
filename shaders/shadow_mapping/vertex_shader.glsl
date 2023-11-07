#version 130		// required to use OpenGL core standard

//=== in attributes are read from the vertex array, one row per instance of the shader
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
layout (location = 2) in vec2 tex_coord;

//=== out attributes are interpolated on the face, and passed on to the fragment shader
out vec3 fragment_pos;   // the position of the vertex in view coordinates
out vec3 fragment_normal;     // the normal of the vertex in view coordinates
out vec2 fragment_tex_coord;

//=== uniforms
uniform mat4 PVM;
uniform mat4 VM;
uniform mat4 VM_it; // V * transpose(inverse(M))
uniform int mode;	// the rendering mode (better to code different shaders!)


void main() {
    // 1. first, we transform the position using PVM matrix.
    // note that gl_Position is a standard output of the
    // vertex shader.
    gl_Position = PVM * vec4(position, 1.0f);

    // 2. calculate vectors used for shading calculations
    // those will be interpolate before being sent to the
    // fragment shader.
    fragment_pos = vec3(VM * vec4(position,1.0f));
    fragment_normal = normalize(VM_it * normal);

    // 3. forward the texture coordinates.
    fragment_tex_coord = texCoord;
}
