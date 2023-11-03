#version 130		// required to use OpenGL core standard

//=== in attributes are read from the vertex array, one row per instance of the shader
in vec3 position;	// the position attribute contains the vertex position
in vec3 normal;		// store the vertex normal
in vec3 tangent;
in vec3 binormal;
in vec3 color; 		// store the vertex colour
in vec2 texCoord;

//=== out attributes are interpolated on the face, and passed on to the fragment shader
out vec2 fragment_texCoord;
out vec3 view_normal;
out vec3 view_tangent;
out vec3 view_binormal;

//=== uniforms
uniform mat4 PVM; 	// the Perspective-View-Model matrix is received as a Uniform
uniform mat3 VMiT;


void main(){
    // 1. first, we transform the position using PVM matrix.
    // note that gl_Position is a standard output of the
    // vertex shader.
    gl_Position = PVM * vec4(position, 1.0f);


    // 2. forward the texture coordinates.
    fragment_texCoord = texCoord;
}
