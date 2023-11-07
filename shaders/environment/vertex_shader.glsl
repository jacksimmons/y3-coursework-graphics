#version 460 core

//=== in attributes are read from the vertex array, one row per instance of the shader
in vec3 position;	// the position attribute contains the vertex position
in vec3 normal;		// store the vertex normal

//=== out attributes are interpolated on the face, and passed on to the fragment shader
out vec3 position_view_space;   // the position of the vertex in view coordinates
out vec3 normal_view_space;     // the normal of the vertex in view coordinates
out vec3 fragment_tex_coord;

uniform mat4 PVM;
uniform mat4 VM;
uniform mat4 VM_it; // V * transpose(inverse(M))
uniform int mode;	// the rendering mode (better to code different shaders!)

void main(void)
{
    // 1. first, we transform the position using PVM matrix.
    // note that gl_Position is a standard output of the
    // vertex shader.
    gl_Position = PVM * vec4(position, 1.0f);

    // 2. calculate vectors used for shading calculations
    // those will be interpolate before being sent to the
    // fragment shader.
    // TODO WS4
    position_view_space = vec3(VM * vec4(position, 1.0f) );
    normal_view_space = normalize(VM_it * vec4(normal, 1.0f)).xyz;
	//fragment_tex_coord = normalize(-VMiT*position);

	//fragment_tex_coord = reflect(-normalize(position), normal);
}
